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

Change only those paths. Do not commit `features/`, `.fstack/`, or `.fstack-worktrees/`.

## Stack

- Base: {{stack_base}}
- Branch: {{branch}}
- Existing pull request: {{pr}}
- Previous failure summary: {{failure_summary}}

If `{{pr}}` is not `(none)`, push to `{{branch}}` and update that pull request. Otherwise open one into `{{stack_base}}`. The pull request body states the chunk id, the acceptance criteria, and the stack parent.

Do not merge. Do not release.

If you cannot do the chunk, make no commit and end with this line:

`FSTACK_BLOCKED: <reason>`

Working notes, if you need them, go in the pull request body under a heading named `Implementer notes`. The verify prompt does not include that heading.
