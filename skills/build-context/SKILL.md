---
name: build-context
description: >
  Write the prompt for one fstack action onto the Notion feature or chunk page.
  Use when an action is about to start, including verification and tie-break.
  The orchestrator builds the verify prompt. The verify and tie-break prompts inline the patch and omit fstack notes.
---

# Build context

Follow the debug-log contract.

Write a fresh prompt before the action. The prompt carries the graph neighborhood the step needs, plus relevant memory. It does not carry the whole product. The skill carries the procedure. The transition table carries the legal status change. Durable facts stay on graph nodes. The feature page keeps links to Decision pages, the plan, and status.

## When to use

The action is `collect-requirements`, `survey-product`, `gap-analysis`, `split-into-chunks`, `pick-next-task`, `implement-chunk`, `verify`, `verify-tiebreak`, `advisors`, `escalate`, `review-stack`, `release`, `update-graph`, or `fstack-status`.

## Steps

1. Read the template from the plugin `templates/prompts/<action>.md`.

2. Create or update the Notion child page named `prompt <action> a<attempt>` under the chunk, or under the feature when there is no chunk. Replace a missing token with `(none)`. If Notion is unreachable, show the unsaved prompt through `tldr`, verbatim, and stop.

3. Tokens you may fill: `feature`, `chunk_id`, `chunk_title`, `attempt`, `spec`, `acceptance_criteria`, `out_of_scope`, `allowed_files`, `branch`, `stack_base`, `pr`, `diff`, `command_results`, `failure_summary`, `requirements`, `open_questions`, `plan`, `release_plan`, `pull_requests`, `shas`, `base_sha`, `head_sha`, `release_command`, `question_id`, `advisor_name`, `artifact`, `dispute_reason`, `sources`, `graph`, `code_location`. `shas` on a survey prompt is the pinned commit for that location. `base_sha` and `head_sha` are the chunk's two commits. The verify prompt must include both, and the verifier copies both into its return.

4. For `implement-chunk`, follow the chunk's Touched nodes relation and the edges one step away. Follow `memory`: fetch with id `"memory"`, then search for memories that name this product or feature. Add those short excerpts and their links. Do not attach every node or every memory. The prompt is that neighborhood, the chunk spec, and the slot parameters. A prompt or diff page is a child of the chunk, so the chunk page links back to it.

5. For `verify` and `verify-tiebreak`, build the prompt in the orchestrator session before the other agent starts.

   On Grok Bot, read the patch through the GitHub connector for `base_sha...head_sha`. Do not clone the repository and do not run `git diff` on the bot computer. On the Cursor plugin, take the patch with `git diff <base_sha>...<head_sha>` when a checkout of that head exists. Store the patch as the Notion child page `diff <chunk-id> a<attempt>`. Put that patch in `{{diff}}`. Do not put a pull request URL in the prompt. Do not put a Notion link or a workspace path in the prompt. Drop every section titled `Implementer notes`, including a pull request section with that heading. If `verify.commands` is empty, `command_results` is `(none)`. Do not clone a repository to run those commands.

   Record `attach_diff` when the patch page is saved.

5. Return the page text. The caller passes that text to the next agent. The next agent does not open Notion.

## Events

- `attach_diff`

## Next

Return to the caller.
