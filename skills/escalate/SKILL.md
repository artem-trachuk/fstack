---
name: escalate
description: >
  Stop a blocked or capped chunk and ask the human to retry, accept, change the spec, or stop.
  Use when the next rule is escalate_chunk, a block, a repeated handoff failure, or a same-model tie-break.
  Waits for the human. Does not merge, release, or change the spec on its own.
---

# Escalate

Follow the debug-log contract.

Follow the decision-policy contract.

The chunk stops. The human chooses. Record `waiting_on` before you end the turn.

## When to use

- `attempts_since_decision` is greater than or equal to `verify.max_failures_before_escalation`.
- The chunk is `blocked`. That does not use an attempt.
- `handoff_failures` reached 2.
- A dispute was skipped because the tie-break model matches the verifier.
- No next rule matched.

## Steps

1. Set the chunk to `escalated` and `feature_status` to `escalated`. Record `escalate_chunk` with the reason, the attempt, and `handoff_failures`. Set `waiting_on` kind `escalation` and question id `Q-<slug>-<chunk-id>-unblock`. Send that decision as a question card through `tldr`, with options `retry`, `accept`, `change_spec`, and `stop`.

2. The options are `retry`, `accept`, `change_spec`, and `stop`. `accept` means ship this sha anyway. Send them through `tldr` and end the turn.

3. The reply is recorded by `fstack-status` as `human_decision`.

   `retry` sets `attempts_since_decision` back to 0 and returns the chunk to `failed`, or to `planned` when `attempt` is 0. It also clears `handoff_failures`.

   `accept` sets `accepted_by_human`, sets `accepted_sha` to `head_sha`, stores the quote, and does not set `verified_sha`. It sets `marked_for_review` on later chunks. Later chunks that were verified lose `verified_sha`. Later chunks that were `accepted_by_human` lose `accepted_sha` until a clean restack or a new decision.

   `change_spec` edits the spec or acceptance criteria, resets `attempts_since_decision`, sets the chunk to `planned`, and marks later chunks the same way.

   `stop` sets `feature_status: stopped`. Pull requests stay open.

## Events

- `escalate_chunk`

## Next

End the turn. `fstack-status` records the decision.
