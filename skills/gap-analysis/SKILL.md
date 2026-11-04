---
name: gap-analysis
description: >
  Find the open questions in a feature's requirements and send the human a question card.
  Use when requirements.md exists and the human has confirmed it, and before the feature is split into chunks.
  Stop for answers. Do not invent them, and do not start requirements collection.
---

# Gap analysis

Read the confirmed requirements and list what is still open. The human answers. You do not fill the gaps yourself.

## When to use

- `requirements.md` for the feature is confirmed.
- `questions.md` is missing answers you need before planning.
- The human has just answered, and you need to check whether anything is still open.

## Steps

1. Read `<workspace>/<feature>/requirements.md` and `questions.md`. If the requirements file is missing, stop and tell the human to invoke `/collect-requirements`. Do not follow that skill yourself.

2. Follow `skills/build-context/SKILL.md` for the action `gap-analysis`.

3. Add one section per open question to `questions.md`. A question is open when a wrong guess would change the spec, the acceptance criteria, or the scope. Set the file status to `open` while any Answer line is empty.

4. Follow `skills/advisors/SKILL.md` for `planner_review` on the question list. Fold in a critique that names a real missing question. Record the call. The advisor does not edit files itself.

5. Follow `skills/tldr/SKILL.md` and send the question card to the human in this conversation. Then wait. Do not split the work, and do not launch a coding agent, while a question is unanswered.

6. When the human answers, write each answer under its question. When every answer is filled, set the status to `answered`, append a `decisions.md` row, and continue.

## Writes

- `questions.md`
- `prompts/gap-analysis.md`
- `advisors.md` when the advisor ran
- `decisions.md` when the questions are answered

## Next

Follow `skills/split-into-chunks/SKILL.md` only after the status is `answered`.
