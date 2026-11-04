# Prompt: implement-chunk

Feature: {{feature}}
Workspace: {{feature_dir}}
Chunk: {{chunk_id}} {{chunk_title}}
Attempt: {{attempt}}

You are the Cursor coding agent for this chunk. Implement it. Open a stacked pull request. Stop.

## Spec

{{spec}}

## Acceptance criteria

{{acceptance_criteria}}

## Allowed files

{{allowed_files}}

Change only those paths. When the spec needs another path, stop and say so in the pull request body. Do not widen the chunk yourself.

## Stack

- Base branch: {{stack_base}}
- Branch to push: {{branch}}
- Previous failure, when this is a retry: {{failure_summary}}

Commit on `{{branch}}`, based on `{{stack_base}}`. Open a pull request into `{{stack_base}}`. The pull request body states the chunk id, the acceptance criteria, and the stack parent.

Do not merge the pull request. Do not release. Do not commit the feature workspace, and do not edit files under `verification/`.

The orchestrator owns the chunk file. If you need working notes, put them in the pull request body under a heading named `Implementer notes`. The verify prompt does not include that heading.
