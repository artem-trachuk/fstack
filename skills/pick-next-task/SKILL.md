---
name: pick-next-task
description: >
  Choose the single next action from state/transitions.yaml.
  Use when the orchestrator is ready to implement, resume, verify, review, or release.
  Does not implement product code and does not grade a chunk.
---

# Pick the next task

Apply `next_rules` in `state/transitions.yaml` from top to bottom. The first rule whose `when` matches is the only action. Do not skip ahead to release while review is still open.

## When to use

The feature folder exists and the orchestrator needs the next legal action.

## Steps

1. Read `feature.yaml`, every chunk frontmatter in id order, and any verdict file whose `applied` flag is false. Take the lease when it is free or already yours. A lease held by someone else until `expires_at` means you stop.

2. Do that one action.

   A chunk that is `implementing` or `in_review` with an agent id is resumed. Check the agent and search the forge for the head branch before launching another. Record `handoff_failed` when the agent is gone and no pull request exists.

   A filed verdict for the current attempt and `head_sha` is applied with `apply_verdict`. Do not launch another verifier.

   The orchestrator launches the verifier. The verifier does not build its own prompt. Follow `build-context` for `verify` first, then record `verifier_launched` before you wait.

   `decide_dispute` is yours. The tie-break critique is not the verdict.

   When the cap rule matches, follow `escalate`. The comparison is `attempts_since_decision` greater than or equal to `verify.max_failures_before_escalation`.

   When the stack-review rule matches, follow `review-stack` and end the turn. Do not open the release question in that turn.

3. If the default branch sha moved, record `base_moved` before launching more work. Open chunks get `needs_restack`. Verified chunks get a range-diff before they stay verified.

4. Append the event file and update the status the event names in the same turn. You are the only writer.

## Events

- `apply_verdict`
- `decide_dispute`
- `verifier_launched`
- `base_moved`

## Next

The skill named by the matching rule. End the turn when the rule says to wait.
