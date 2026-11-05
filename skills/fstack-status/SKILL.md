---
name: fstack-status
description: >
  Read a feature's saved state and route a human reply, or report what the feature is waiting on.
  Use when a new session resumes a feature, the human asks for status, or the human answers a question card.
---

# Status

A new chat does not remember the last turn. Notion does. Feature pages are not in the git repository.

## When to use

The human names a feature, answers a question id, or asks where the work stands. With no slug, list Features pages and their Status. If Notion is unreachable, stop and say so. Do not look for a local feature folder.

## Steps

1. Read the feature page from Notion, including Status, Waiting on, and the linked chunks, and read `state/transitions.yaml`. If `state_version` is not 1, stop and say it must be migrated. If the page is missing, stop. Nothing was committed.

2. If the lease belongs to someone else and has not expired, report it and stop. `take_lease` requires a human quote and the new owner. The lease lasts 30 minutes. Two writers can still race. See `stubs/enforcement.md`.

3. If `waiting_on` is set and the human is replying to that question id, record the event the table allows and no other.

   Questions use `answer_questions`. Partial answers leave the rest open.

   A plan question uses `approve_plan` only for a direct yes or approve.

   Stack review uses `answer_review` on the `review-stack` skill.

   Release uses `approve_release` on the `release` skill.

   An escalation uses `human_decision` with `retry`, `accept`, `change_spec`, or `stop`.

   A chunk in `awaiting_verification_decision` uses `human_decision` with `accept_unverified` or `stop` only. `accept_unverified` sets the chunk to `accepted_by_human`, stores the quote and the sha, and sets Accepted unverified. It is not a pass and it does not set Verified SHA. `stop` sets the feature Status to `stopped`. Write the decision on the feature page before changing any later chunk. Pull requests stay open when the feature stops.

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
