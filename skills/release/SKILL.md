---
name: release
description: >
  Ask the human to approve release of a reviewed stack, then merge only that approved sha.
  Use when feature_status is awaiting_release or merging.
  Never merges or runs a release command without a recorded human approval.
---

# Release

Ask the question. Act only after a direct yes or approve for that question id. There is no release script. Follow the steps and record each event. The checks in `stubs/enforcement.md` are not automated.

## When to use

The next rule is `release_question` or a merging rule. Stack review is already recorded. Do not enter this skill from `building`.

## Steps

1. Follow `build-context` for `release`. The release sha for a chunk is `verified_sha` when the chunk is verified, and `accepted_sha` when the chunk is `accepted_by_human`. A chunk with neither sha cannot be released. Record `open_release` with the exact `release.command` and the map of chunk id to release sha. Set `waiting_on` kind `release`, question id `Q-<slug>-release`. Send a question card through `tldr`, keeping the command and the shas verbatim. The options are approve and stop. End the turn.

2. Accept only a direct reply of yes, approve, or approved to that question id. Vague praise is asked again. A hedge is asked again. If `release.command` or any release sha changed since the question, do not accept the old reply. Ask again.

3. Record `approve_release`. Set the feature Status to `merging` and Release state to `merging` on the Notion feature page. Record the approval there, as described in `stubs/enforcement.md`. Do not commit it.

4. For each chunk in order, by hand:

   - If the forge already merged it, record `merge_recorded` and continue.
   - If the pull request head differs from the release sha, record `void_release` and stop. Do not merge that sha.
   - If its parent merged, rebase and retarget, record `restack_recorded`, then record `range_diff_recorded`. A clean diff updates the release sha and the approval sha. A real difference on a verified chunk sets `needs_verify`. A real difference on an `accepted_by_human` chunk clears `accepted_sha` and sets `awaiting_verification_decision`. Leave this skill.
   - Record `ci_recorded`. `pending` waits. `failing` escalates and leaves already merged chunks merged. `none` means there is no CI. Do not roll back.
   - Merge that one pull request. Record `merge_recorded` with the head sha. Mark later chunks `needs_restack`.

5. When every chunk is `merged`, run `release.command` only if it is non-empty and still equals the approved string. Record `release_command_recorded`. Exit 0 sets `feature_status: done` and `release_state: done`. Any other exit sets `release_state: command_failed`, escalates, and does not roll back. An empty command finishes the same way with exit 0 and no command.

6. Tell the human the release is done, through `tldr`. Then follow `memory` and propose the durable lessons from this feature: decisions, corrections, preferences, conventions. On Grok Bot, send that proposal as a question card. Write the lessons to Notion only after the human chooses yes. If Notion is unreachable, show the unsaved lessons and stop. Do not start a new feature unless the human asks.

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
