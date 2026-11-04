# Prompt: verify

Feature: {{feature}}
Workspace: {{feature_dir}}
Chunk: {{chunk_id}} {{chunk_title}}
Attempt: {{attempt}}

Follow the fstack skill `verify`. Judge this chunk from the spec, the acceptance criteria, and the diff.

Do not attach implementer notes. Do not use the implementer's rationale, the implement-chunk prompt, or any section titled Implementer notes. If those are present, ignore them.

## Requirements

{{requirements}}

## Spec

{{spec}}

## Acceptance criteria

{{acceptance_criteria}}

## Allowed files

{{allowed_files}}

## Diff

Compare `{{diff_source}}`.

## Earlier failure summary

{{failure_summary}}

That summary is the previous verdict, when this is a retry. It is not implementer notes. Re-check it against the current diff.
