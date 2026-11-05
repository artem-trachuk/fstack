---
name: fstack-status
description: >
  Read a feature's saved state and route a human reply, or report what the feature is waiting on.
  Use when a new session resumes a feature, the human asks for status, the human asks which pages are unlinked, or the human answers a question card.
---

# Status

A new chat does not remember the last turn. Notion does. Feature pages are not in the git repository.

## When to use

The human names a feature, answers a question card, or asks where the work stands. On Grok Bot that is a message in the Orchestrator chat. With no slug, list Features pages and their Status. If Notion is unreachable, stop and say so. Do not look for a local feature folder.

## Steps

1. Read the feature page from Notion, including Status, Waiting on, and the linked chunks, and read `state/transitions.yaml`. If this session has not loaded the workflow, follow `configure-workflow` first. If `state_version` is not 1, stop and say it must be migrated. If the page is missing, stop. Nothing was committed.

2. If the lease belongs to someone else and has not expired, report it and stop. `take_lease` requires a human quote and the new owner. The lease lasts 30 minutes. Two writers can still race. See `stubs/enforcement.md`.

3. If `waiting_on` is set and the human is replying to that question id, record the event the table allows and no other.

   A coverage question (`coverage_questions`) uses `answer_coverage_questions`. The options are `implement`, `write_back`, `skip`, and `defer`. Partial answers leave the rest open. `implement` makes that row buildable: set its classification to `missing` or `partial`. `skip` and `defer` never become chunks. `write_back` records `source_write_proposed` with the proposed text on the row. Do not call the source writer in that turn. When every row is answered and no write is waiting, set Status to `awaiting_coverage_approval` and send the coverage gate.

   A source-write question (`source_write`) uses `source_write_applied` only after a direct yes, and only through the writer configured on that source. No, or a source with no writer, leaves the text on the row and writes nothing. Then set Status to `awaiting_coverage_approval` and send the coverage gate.

   The coverage gate (`coverage_approval`) uses `approve_coverage` only for a direct yes or approve. That sets Approved on each listed `partial` or `missing` row and sets Status to `ready_to_plan`. Stop uses `human_decision` and sets Status to `stopped`. Do not plan a row the human did not approve.

   Graph promotion (`graph_promotion`) uses `graph_promoted` only for a direct yes or approve. Stop uses `human_decision`, sets Status to `stopped`, and does not promote. A contradicted node stays unpromoted until the human chooses.

   A plan question uses `approve_plan` only for a direct yes or approve.

   Stack review uses `answer_review` on the `review-stack` skill.

   Release uses `approve_release` on the `release` skill.

   An escalation uses `human_decision` with `retry`, `accept`, `change_spec`, or `stop`. An empty plan uses `human_decision` with `stop`, which sets Status to `stopped`.

   A chunk in `awaiting_verification_decision` uses `human_decision` with `accept_unverified` or `stop` only. `accept_unverified` sets the chunk to `accepted_by_human`, sets `accepted_sha` to `head_sha`, stores the quote, and sets Accepted unverified. It is not a pass and it does not set Verified SHA. Release may merge `accepted_sha`. `stop` sets the feature Status to `stopped`. Write the decision on the feature page before changing any later chunk. Pull requests stay open when the feature stops.

   A contest of a failed chunk uses `contest` and includes the implementer's reason. That moves the chunk to `disputed` without adding another failure.

4. If the human asks for orphans, unlinked pages, or whether the graph is connected, walk the relations in `required_relations` starting at the product page. Report two lists through `tldr`. An unlinked page is one whose required relation is empty. An orphan is a page no path from the product page reaches. Name the page and the missing link. Do not delete or rewrite those pages in this turn.

5. If nobody is replying, report the status through `tldr`: feature, status, waiting question, chunk, pull requests, and shas. Then follow `pick-next-task` when the table says the work can move. End the turn when it says to wait.

## Events

- `answer_coverage_questions`
- `source_write_proposed`
- `source_write_applied`
- `approve_coverage`
- `approve_plan`
- `human_decision`
- `contest`
- `take_lease`

`answer_review` and `approve_release` are recorded through the `review-stack` and `release` skills.

## Next

`pick-next-task`, or end the turn when the feature is waiting.
