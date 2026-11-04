---
name: collect-requirements
description: >
  Write one feature's requirements into the fstack workspace.
  Use only when the human explicitly invokes /collect-requirements.
  Never start this skill from another skill, a schedule, or a guess that a feature needs requirements.
disable-model-invocation: true
---

# Collect requirements

This skill runs only when the human invokes `/collect-requirements`. Other skills point the human here. They do not open this skill themselves.

## When to use

The human typed `/collect-requirements` and wants a feature started. That invocation is the whole trigger.

## Steps

1. Read `fstack.yaml`. If it is missing, or `models.resolution` is not `resolved`, follow `skills/setup-project/SKILL.md`, then continue. The human already started this run.

2. Agree a feature slug with the human: lowercase letters, digits, and hyphens. The workspace folder is `<workspace>/<slug>/` from `fstack.yaml`. When that folder already exists, ask whether to continue it or pick another slug. Do not overwrite an existing `requirements.md`.

3. Create the folder from the plugin templates when the files are absent. Find templates from the plugin root, the directory that contains `.cursor-plugin/plugin.json` with `"name": "fstack"`. Replace `{{feature}}` with the slug and `{{max_calls}}` with `advisors.max_calls_per_feature` from `fstack.yaml`.

   - `requirements.md` from `templates/feature/requirements.md`
   - `questions.md` from `templates/feature/questions.md`
   - `plan.md` from `templates/feature/plan.md`
   - `decisions.md` from `templates/feature/decisions.md`
   - `advisors.md` from `templates/feature/advisors.md`
   - `chunks/`, `prompts/`, and `verification/` as empty directories

   The chunk template stays in the plugin until `split-into-chunks` writes a chunk file.

4. Fill `requirements.md` from what the human said: problem, people, outcome, constraints, out of scope, and feature acceptance. Where a section is still unknown, ask one concrete question and wait. Write answers into the file. Follow `skills/build-context/SKILL.md` so `prompts/collect-requirements.md` matches the latest text.

5. Rewrite the requirements as a short confirmation with `skills/tldr/SKILL.md` and show it to the human. Continue only after they confirm it matches what they want. On a correction, edit the file and ask again.

6. Append a row to `decisions.md`: the human confirmed the requirements. Quote the confirmation.

## Writes

The feature folder listed above, with `requirements.md` filled in.

## Next

Follow `skills/gap-analysis/SKILL.md`. The human already opened this feature by invoking this skill. Do not start a second feature in the same run.
