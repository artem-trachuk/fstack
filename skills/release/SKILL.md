---
name: release
description: >
  Ask the human to approve release of a fully verified fstack feature, then merge and release only after that approval.
  Use when every chunk is verified and the human has the stacked pull requests.
  Never merges or releases on its own.
---

# Release

Ask the release question. Act only after the human answers it with an explicit approval.

## When to use

`pick-next-task` found every chunk `verified`. The pull request URLs are recorded on the chunk files.

## Steps

1. Read the plan's Release section and `release.command` in `fstack.yaml`. Follow `skills/build-context/SKILL.md` for `release`.

2. List the pull requests in stack order, bottom of the stack first. State the production effect in one sentence. When the Release section and `release.command` are empty, the effect is merging the stack and nothing further. When a command is named, include that command in the sentence so the approval covers it.

3. Follow `skills/tldr/SKILL.md` and ask, in this conversation:

   `Approve release? I will <effect>.`

   The effect is the sentence from step 2.

4. Wait. An explicit approval names this release and agrees to the effect you stated. Silence, a comment on one pull request, or approval of a different feature does not count. On anything else, stop and leave the stack unmerged.

5. On approval, quote it in `decisions.md` before you change anything. Then merge the pull requests from the bottom of the stack upward, using the forge that opened them. After the merges, run `release.command` when it is non-empty. Record the merge commits and the command result in `decisions.md`.

6. Tell the human the release is done, through `tldr`. The feature has no next chunk. Stop.

## Writes

- `prompts/release.md`
- `decisions.md` with the quoted approval, and later the result

## Gates

Do not merge, do not run the release command, and do not announce the release outside this conversation before step 5's quote is in the decision log. A review request is not an approval.
