---
name: advisors
description: >
  Run a short read-only Cursor advisor to critique a plan or a disputed verification.
  Use when the action is gap-analysis or split-into-chunks (planner_review on opus), or when a verdict is verifier-disputed (verify_tiebreak on argon).
  The advisor never edits the project. Calls stop at max_calls_per_feature.
---

# Advisors

A short second opinion from a stronger Cursor model. The advisor returns a critique. The caller decides what to do with it. The advisor run does not edit files, open pull requests, or message the human.

## When to use

Match the current action to `advisors` in `fstack.yaml`.

- `planner_review` during `gap-analysis` and `split-into-chunks`, on the `opus` model.
- `verify_tiebreak` when the verifier's verdict is `verifier-disputed`, on the `argon` model.

Skip the advisor when the action is not in that advisor's `when` list.

## Steps

1. Read `max_calls_per_feature` and the feature's `advisors.md`. Count rows that record a launched call. When the count is at the cap, append a row `skipped: cap`, tell the caller, and return. Do not launch.

2. Resolve the model. Read `models.resolved` for the advisor's short name. Use that Cursor slug. When the value is `inherit`, or resolution is `unresolved`, run on the parent Cursor model and record the fallback on the row.

3. Follow `skills/build-context/SKILL.md` for the action `advisors`, with `{{advisor_name}}` and `{{artifact}}` set. The artifact is the question list, the plan and chunk specs, or the disputed verification file.

4. Start a read-only Cursor agent on that model with `prompts/advisors.md`. Ask for a critique: what is missing, what is too big to verify, and what would change the verdict. Tell it to avoid editing files and to avoid running commands that write.

5. Append a row to `advisors.md`: number, advisor name, action, model, and a one-line result. Append a matching `decisions.md` row. Return the critique text to the caller.

6. The caller may edit the plan or the question list from the critique. The caller names, in `decisions.md`, which points it applied. The advisor process itself still does not write those edits.

## Writes

- `prompts/advisors.md`
- `advisors.md`
- `decisions.md`

## Next

Return to the skill that asked for the critique.
