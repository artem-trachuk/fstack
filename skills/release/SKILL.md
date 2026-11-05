---
name: release
contract: release
description: >
  Ask the human to approve release of a reviewed stack, then merge only that approved sha.
  Use when feature_status is awaiting_release or merging.
  Never merges or runs a release command without a recorded human approval.
---

# Release

Follow the debug-log contract.

## Contract

Inputs: the approved review, the release command, and the release shas, plus any slot parameters.
Outputs: merged pull requests, or a stop. No merge without a human approval.

Ask the question. Act only after a direct yes or approve for that question id. There is no release script. Follow the steps and record each event. The checks in `stubs/enforcement.md` are not automated.

## When to use

The next rule is `release_question` or a merging rule. Stack review is already recorded. Do not enter this skill from `building`.

## Steps

1. Follow `build-context` for `release`. The release sha for a chunk is `verified_sha` when the chunk is verified, and `accepted_sha` when the chunk is `accepted_by_human`. A chunk with neither sha cannot be released. Record `open_release` with the exact `release.command` and the map of chunk id to release sha. Set `waiting_on` kind `release`, question id `Q-<slug>-release`. Send a question card through `tldr`, keeping the command and the shas verbatim. The options are approve and stop. End the turn.

2. Accept only a direct reply of yes, approve, or approved to that question id. Vague praise is asked again. A hedge is asked again. If `release.command` or any release sha changed since the question, do not accept the old reply. Ask again.

3. Record `approve_release`. Set the feature Status to `merging` and Release state to `merging` on the Notion feature page. Record the approval there, as described in `stubs/enforcement.md`. Do not commit it.

4. Release one code location at a time. The order is `release_order`, or the product list when that is empty. Inside a location, take chunks in stack order. `all_or_none` does not start the next location until this one is merged. `per_repo` may finish locations independently. A failure stops `all_or_none` before the next location and does not roll back a location already merged. The feature is done only when every location in the feature is merged, or the human stops.

   For each chunk in that location, by hand:

   - If the forge already merged it, record `merge_recorded` and continue.
   - If the pull request head differs from the release sha, record `void_release` and stop. Do not merge that sha.
   - If its parent merged, rebase and retarget, then record `restack_recorded`. A clean restack of an `accepted_by_human` chunk updates `accepted_sha` to the new head and leaves the chunk `accepted_by_human`. A real difference clears `accepted_sha` and sets `awaiting_verification_decision`. Do not copy `accepted_sha` into `verified_sha`. Then record `range_diff_recorded` for a chunk that was verified. A clean diff updates `verified_sha` and the approval sha. A real difference on a verified chunk sets `needs_verify`. Leave this skill when the restack is not clean.
   - Record `ci_recorded`. `pending` waits. `failing` escalates and leaves already merged chunks merged. `none` means there is no CI. Do not roll back.
   - Merge that one pull request. Record `merge_recorded` with the head sha. Mark later chunks in the same location `needs_restack`. Do not restack another location unless a cross-location dependency says so.

5. When every chunk is `merged`, run `release.command` only if it is non-empty and still equals the approved string. Record `release_command_recorded`. Exit 0 sets `feature_status: awaiting_graph_update`. Any other exit sets `release_state: command_failed`, escalates, and does not roll back. An empty command finishes the same way with exit 0 and no command. Do not promote the graph in this skill.

6. Follow `memory` and propose lessons. A lesson is Type Work: name the product in the body and link the product or feature page. Working style is Type Preference. These are memory, not product facts. Do not add custom properties. On Grok Bot, send that proposal as a question card. Write the lessons to Notion only after the human chooses yes, then mention each new memory from the feature page. If Notion is unreachable, show the unsaved lessons and stop. Then follow `update-graph`. A stopped feature is not promoted.

A human can record `retry_release` with a quote after a CI or command failure. Merged chunks stay merged.

## Events

- `open_release`
- `approve_release`
- `void_release`
- `merge_recorded`
- `restack_recorded`
- `range_diff_recorded`
- `ci_recorded`
- `release_command_recorded`
- `retry_release`

## Next

End the turn while waiting for the approval. After `done`, `pick-next-task` moves to the next feature.
