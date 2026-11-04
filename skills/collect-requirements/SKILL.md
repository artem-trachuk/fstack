---
name: collect-requirements
description: >
  Write one feature's requirements and ask the human to confirm the file.
  Use only when the human explicitly invokes /collect-requirements.
  Never start this skill from another skill, a schedule, or a guess that a feature needs requirements.
disable-model-invocation: true
---

# Collect requirements

This skill runs only when the human invokes `/collect-requirements`.

## When to use

The human typed `/collect-requirements` and wants a feature started.

## Steps

1. Read `fstack.yaml`. If it is missing, or `.fstack/resolved.yaml` is missing, follow `setup-project`, then continue.

2. Agree a feature slug: lowercase letters, digits, and hyphens. Create the feature folder from `.fstack/templates/feature/` if it is absent. Replace `{{feature}}` and `{{max_calls}}` and `{{reserve}}`. Do not copy a blank question into `questions.md`.

   With `state.backend: git`, create the orphan branch `fstack/<slug>/state` and a worktree at `.fstack-worktrees/<slug>/`, and put the feature folder there. Do not put that folder on a chunk branch. With `state.backend: local`, use `.fstack/local/<slug>/` and tell the human the state stays on this machine.

   If the folder already has a confirmed requirements file, ask whether to continue that feature or pick another slug.

3. Fill `requirements.md` from the human: problem, people, outcome, constraints, out of scope, and feature acceptance. Leave `feature.yaml` `requirements_status: draft` and `feature_status: requirements_draft`. Record `save_requirements` in `events/`.

4. Ask the human to confirm the file. The message names the file path and uses the question card `Q-<slug>-requirements`. A 120-word summary is not the thing they confirm. Follow the `tldr` skill, and keep the path and the question id verbatim. End the turn if you are waiting.

5. On a correction, edit the file and ask again. On yes, approve, or approved, set `requirements_status: confirmed` and `feature_status: requirements_confirmed`, quote them in the event, and record `confirm_requirements`.

## Events

- `save_requirements`
- `confirm_requirements`

## Next

Hand the feature slug to a new orchestrator agent and stop. Do not implement product code in this chat. Tell that agent to read `state/transitions.yaml` and run gap analysis. Do not start a second feature.
