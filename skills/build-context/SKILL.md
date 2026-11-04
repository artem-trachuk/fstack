---
name: build-context
description: >
  Write the prompt for one fstack action under prompts/<chunk-id>/a<attempt>/.
  Use when an action is about to start, including verification and tie-break.
  The orchestrator builds the verify prompt. The verify and tie-break prompts inline the patch and omit the feature directory.
---

# Build context

Write a fresh prompt before the action. The prompt carries this feature's facts. The skill carries the procedure. The transition table carries the legal status change.

## When to use

The action is `collect-requirements`, `gap-analysis`, `split-into-chunks`, `pick-next-task`, `implement-chunk`, `verify`, `verify-tiebreak`, `advisors`, `escalate`, `review-stack`, `release`, or `fstack-status`.

## Steps

1. Read the template from `.fstack/templates/prompts/<action>.md`. The plugin copy is the fallback before setup has copied templates.

2. Write `prompts/<chunk-id>/a<attempt>/<action>.md`. When the action has no chunk, use `prompts/feature/a0/<action>.md`. Replace a missing value with `(none)`.

3. Tokens you may fill: `feature`, `chunk_id`, `chunk_title`, `attempt`, `spec`, `acceptance_criteria`, `out_of_scope`, `allowed_files`, `branch`, `stack_base`, `pr`, `diff`, `command_results`, `failure_summary`, `requirements`, `open_questions`, `plan`, `release_plan`, `pull_requests`, `shas`, `release_command`, `question_id`, `advisor_name`, `artifact`, `dispute_reason`.

4. For `verify` and `verify-tiebreak`, build the prompt in the orchestrator session before the other agent starts.

   Take the patch with `git diff <base_sha>...<head_sha>` and store it at `diffs/<chunk-id>/a<attempt>.diff`. Put that patch in `{{diff}}`. Do not put a pull request URL in the prompt. Do not put a feature directory or a workspace path in the prompt. Drop every section titled `Implementer notes`, including a pull request section with that heading. Run `verify.commands` in a clean checkout of `head_sha` and put the command and exit code in `{{command_results}}`.

   Record `attach_diff` when the patch is stored.

5. Return the path. The caller follows its skill with this file.

## Events

- `attach_diff`

## Next

Return to the caller.
