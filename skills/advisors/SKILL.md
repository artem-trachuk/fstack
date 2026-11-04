---
name: advisors
description: >
  Run a short read-only Cursor advisor and record the call before it returns.
  Use when the action is planner_review during gap-analysis or split-into-chunks, or one verify_tiebreak on a disputed attempt.
  The advisor never edits the project and never owns the verdict.
---

# Advisors

A second opinion. The caller decides what to do with it.

## When to use

`planner_review` during `gap-analysis` and `split-into-chunks`. `verify_tiebreak` when a chunk is `disputed`. Skip the advisor when the action is not in its `when` list.

## Budget

`max_calls_per_feature` is 6. `reserve.verify_tiebreak` is 2. Planner calls may use the other 4. A launched, finished, or failed row counts. A skipped row does not. Write the row as `launched` before you wait, then update it to `finished` or `failed`. A crash still counts.

Review one artifact hash once. A duplicate returns `skipped: duplicate` and does not count.

If the tie-break slug in `.fstack/resolved.yaml` equals the verifier model, including when both are `inherit`, do not launch it. Record `tiebreak_skipped` with reason `same_model` and escalate. On a launch error, try `fallback` in order. If every fallback fails, record `launch_failed` and let the orchestrator decide or escalate.

## Steps

1. Resolve the model from `.fstack/resolved.yaml`. You pass that model when you launch the `advisor` agent. The advisor does not switch itself.

2. Follow `build-context`. A tie-break uses `verify-tiebreak`, with the same patch as verify and no feature directory.

3. Launch the advisor. Record `advisor_launched` or `tiebreak_launched` first. The advisor is the `advisor` agent, which is read-only.

4. Record `advisor_finished` or `tiebreak_finished`. A planner failure does not stop the feature. A tie-break failure does not become the verdict. The orchestrator records `decide_dispute`.

## Events

- `advisor_launched`
- `advisor_finished`
- `tiebreak_launched`
- `tiebreak_finished`
- `tiebreak_skipped`

## Next

Return the critique to the caller.
