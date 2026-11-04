---
name: fstack-status
description: >
  Read a feature's saved state and route a human reply, or report what the feature is waiting on.
  Use when a new session resumes a feature, the human asks for status, or the human answers a question card.
---

# Status

A new chat does not remember the last turn. The feature files do. They are not in the git repository.

## When to use

The human names a feature, answers a question id, or asks where the work stands. With no slug, list every feature directory under the state root and its `feature_status`.

The state root is `/cursor/stores/self/fstack/features/` when that store is mounted. Otherwise it is `.fstack/features/`. If you were given a store id and `/cursor/stores/<id>/fstack/features/` exists, use that. If the mount is missing, do not wait for it and do not look in GitHub. Say that the state stayed on the machine or agent store where the feature was started.

## Steps

1. Read `feature.yaml` from that local or store folder, plus `waiting_on`, the lease, and `state/transitions.yaml`. If `state_version` is not 1, stop and say it must be migrated. If the folder is missing, stop. Nothing was committed.

2. If the lease belongs to someone else and has not expired, report it and stop. `take_lease` requires a human quote and the new owner. The lease lasts 30 minutes. Two writers can still race. See `stubs/enforcement.md`.

3. If `waiting_on` is set and the human is replying to that question id, record the event the table allows and no other.

   Questions use `answer_questions`. Partial answers leave the rest open.

   A plan question uses `approve_plan` only for a direct yes or approve.

   Stack review uses `answer_review` on the `review-stack` skill.

   Release uses `approve_release` on the `release` skill.

   An escalation uses `human_decision` with `retry`, `accept`, `change_spec`, or `stop`.

   A chunk in `awaiting_verification_decision` uses `human_decision` with `accept_unverified` or `stop` only. `accept_unverified` sets `accepted_by_human`, stores the quote and the sha, and sets `accepted_unverified: true` on the chunk. It is not a pass and it does not set `verified`. `stop` sets `feature_status: stopped`. Write the event file before changing any later chunk. Pull requests stay open when the feature stops.

   A contest of a failed chunk uses `contest` and includes the implementer's reason. That moves the chunk to `disputed` without adding another failure.

4. If nobody is replying, report the status through `tldr`: feature, status, waiting question, chunk, pull requests, and shas. Then follow `pick-next-task` when the table says the work can move. End the turn when it says to wait.

## Events

- `answer_questions`
- `approve_plan`
- `human_decision`
- `contest`
- `take_lease`

`answer_review` and `approve_release` are recorded through the `review-stack` and `release` skills.

## Next

`pick-next-task`, or end the turn when the feature is waiting.
