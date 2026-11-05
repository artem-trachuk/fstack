---
name: build-context
description: >
  Write the prompt for one fstack action onto the Notion feature or chunk page.
  Use when an action is about to start, including verification and tie-break.
  The orchestrator builds the verify prompt. The verify and tie-break prompts inline the patch and omit fstack notes.
---

# Build context

Write a fresh prompt before the action. The prompt carries this feature's facts. The skill carries the procedure. The transition table carries the legal status change.

## When to use

The action is `collect-requirements`, `gap-analysis`, `split-into-chunks`, `pick-next-task`, `implement-chunk`, `verify`, `verify-tiebreak`, `advisors`, `escalate`, `review-stack`, `release`, or `fstack-status`.

## Steps

1. Read the template from the plugin `templates/prompts/<action>.md`.

2. Create or update the Notion child page named `prompt <action> a<attempt>` under the chunk, or under the feature when there is no chunk. Replace a missing token with `(none)`. If Notion is unreachable, show the unsaved prompt through `tldr` and stop.

3. Tokens you may fill: `feature`, `chunk_id`, `chunk_title`, `attempt`, `spec`, `acceptance_criteria`, `out_of_scope`, `allowed_files`, `branch`, `stack_base`, `pr`, `diff`, `command_results`, `failure_summary`, `requirements`, `open_questions`, `plan`, `release_plan`, `pull_requests`, `shas`, `release_command`, `question_id`, `advisor_name`, `artifact`, `dispute_reason`.

4. For `verify` and `verify-tiebreak`, build the prompt in the orchestrator session before the other agent starts.

   Take the patch with `git diff <base_sha>...<head_sha>` and store it as the Notion child page `diff <chunk-id> a<attempt>`. Put that patch in `{{diff}}`. Do not put a pull request URL in the prompt. Do not put a Notion link or a workspace path in the prompt. Drop every section titled `Implementer notes`, including a pull request section with that heading. Run `verify.commands` in a clean checkout of `head_sha` and put the command and exit code in `{{command_results}}`.

   Record `attach_diff` when the patch page is saved.

5. Return the page text. The caller passes that text to the next agent. The next agent does not open Notion.

## Events

- `attach_diff`

## Next

Return to the caller.
