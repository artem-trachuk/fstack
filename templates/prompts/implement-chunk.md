# Prompt: implement-chunk

Feature: {{feature}}
Chunk: {{chunk_id}} {{chunk_title}}
Attempt: {{attempt}}

You are the Cursor coding agent for this chunk. Implement it on `{{branch}}`, based on `{{stack_base}}`. Then stop.

## Spec

{{spec}}

## Acceptance criteria

{{acceptance_criteria}}

## Out of scope

{{out_of_scope}}

## Allowed files

{{allowed_files}}

Change only those paths. Do not open Notion or `.fstack`. The spec in this prompt is the whole assignment.

## Stack

- Base: {{stack_base}}
- Branch: {{branch}}
- Existing pull request: {{pr}}
- Previous failure summary: {{failure_summary}}

If `{{pr}}` is not `(none)`, push to `{{branch}}` and update that pull request. Otherwise open one into `{{stack_base}}`. The pull request body is a short summary of the code change: what behavior changed and which acceptance criteria it covers. Do not include implementer notes, advisor critiques, verify prompts, requirements, decision logs, or diffs copied from fstack state.

Do not merge. Do not release.

If you cannot do the chunk, make no commit and end with this line:

`FSTACK_BLOCKED: <reason>`

Keep working notes in your own session. Do not put them in the pull request.
