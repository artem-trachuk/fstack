---
name: review-stack
description: >
  Ask the human to review a fully verified stack, then wait.
  Use when every chunk is verified or accepted_by_human and review_approval is empty.
  Does not ask the release question in the same turn.
---

# Review the stack

One review covers the whole stack. There is no per-chunk approval gate.

## When to use

The next rule is `stack_review`.

## Steps

1. Follow `build-context` for `review-stack`. The prompt lists every pull request and its release sha: `verified_sha`, or `accepted_sha` when the chunk is `accepted_by_human`.

2. Record `open_review`. Set `feature_status: awaiting_review` and `waiting_on` kind `stack_review`, question id `Q-<slug>-review`.

3. Send the question card through `tldr`. The options are approve, or request changes on one named chunk. End the turn.

4. When the human answers, record `answer_review`.

   A direct yes or approve sets `review_approval` and `feature_status: awaiting_release`. The next session asks the release question. Do not ask it now.

   A change request names one chunk and quotes the human. That chunk becomes `changes_requested`, its `attempts_since_decision` resets, and its `verified_sha` clears. Later chunks that have a branch get `needs_restack`. Their `verified_sha` clears until a clean range-diff or a new verify. `feature_status` returns to `building`. Any release approval is cleared.

## Events

- `open_review`
- `answer_review`

## Next

End the turn after `open_review`. After `answer_review`, return to `pick-next-task`.
