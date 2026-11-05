---
name: fstack-status
description: >
  Read a feature's saved state and route a human reply, or report what the feature is waiting on.
  Use when a new session resumes a feature, the human asks for status, or the human answers a question card.
---

# Status

A new chat does not remember the last turn. Notion does. Feature pages are not in the git repository.

## When to use

The human names a feature, answers a question card, or asks where the work stands. On Grok Bot that is a message in the Orchestrator chat. With no slug, list Features pages and their Status. If Notion is unreachable, stop and say so. Do not look for a local feature folder.

## Steps

1. Read the feature page from Notion, including Status, Waiting on, and the linked chunks, and read `state/transitions.yaml`. If `state_version` is not 1, stop and say it must be migrated. If the page is missing, stop. Nothing was committed.

2. If the lease belongs to someone else and has not expired, report it and stop. `take_lease` requires a human quote and the new owner. The lease lasts 30 minutes. Two writers can still race. See `stubs/enforcement.md`.

3. If `waiting_on` is set and the human is replying to that question id, record the event the table allows and no other.

   A coverage question (`coverage_questions`) uses `answer_coverage_questions`. The options are `implement`, `add_to_linear`, `skip`, and `defer`. Partial answers leave the rest open. `implement` makes that row requirement-backed: set its classification to `missing` if it was not already. `skip` and `defer` never become chunks. `add_to_linear`, and `implement` when the human also wants it tracked, records `linear_draft_proposed` with the draft text on the row. Do not create the Linear issue in that turn. When every row is answered and no Linear draft is waiting, set Status to `awaiting_coverage_approval` and send the coverage gate.

   A Linear draft question (`linear_draft`) uses `linear_issue_created` only after a direct yes. That creates the issue through the Linear connector, as a draft when the connector can do that. No, or a missing connector, leaves the draft text in Notion and creates nothing. Then set Status to `awaiting_coverage_approval` and send the coverage gate.

   The coverage gate (`coverage_approval`) uses `approve_coverage` only for a direct yes or approve. That sets Approved on each listed `partial` or `missing` row and sets Status to `ready_to_plan`. Stop uses `human_decision` and sets Status to `stopped`. Do not plan a row the human did not approve.

   A plan question uses `approve_plan` only for a direct yes or approve.

   Stack review uses `answer_review` on the `review-stack` skill.

   Release uses `approve_release` on the `release` skill.

   An escalation uses `human_decision` with `retry`, `accept`, `change_spec`, or `stop`. An empty plan uses `human_decision` with `stop`, which sets Status to `stopped`.

   A chunk in `awaiting_verification_decision` uses `human_decision` with `accept_unverified` or `stop` only. `accept_unverified` sets the chunk to `accepted_by_human`, sets `accepted_sha` to `head_sha`, stores the quote, and sets Accepted unverified. It is not a pass and it does not set Verified SHA. Release may merge `accepted_sha`. `stop` sets the feature Status to `stopped`. Write the decision on the feature page before changing any later chunk. Pull requests stay open when the feature stops.

   A contest of a failed chunk uses `contest` and includes the implementer's reason. That moves the chunk to `disputed` without adding another failure.

4. If nobody is replying, report the status through `tldr`: feature, status, waiting question, chunk, pull requests, and shas. Then follow `pick-next-task` when the table says the work can move. End the turn when it says to wait.

## Events

- `answer_coverage_questions`
- `linear_draft_proposed`
- `linear_issue_created`
- `approve_coverage`
- `approve_plan`
- `human_decision`
- `contest`
- `take_lease`

`answer_review` and `approve_release` are recorded through the `review-stack` and `release` skills.

## Next

`pick-next-task`, or end the turn when the feature is waiting.
