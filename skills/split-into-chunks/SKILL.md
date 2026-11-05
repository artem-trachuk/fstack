---
name: split-into-chunks
description: >
  Turn a feature with settled questions into stacked chunks.
  Use when feature_status is ready_to_plan and the plan has no chunks, or when the human changes scope before implementation starts.
  Follows plan_review from fstack.yaml. The default notify does not wait for plan approval.
---

# Split into chunks

Write the stack. Chunk ids look like `01-slug`, in order. The first chunk's base is the default branch. Each later chunk's base is the previous chunk's branch `fstack/<feature>/<chunk-id>`.

## When to use

`questions_status` is `answered` or `none`, and no chunk has left `planned`.

## Chunk file

Copy `templates/feature/chunks/chunk.md` from the plugin into the chunk page body. The Notion properties are the only place for status, branch, base, shas, allowed files, and attempt counts. The page body has spec, acceptance criteria, and out of scope. Do not add an implementer-notes section.

Allowed files are concrete paths or globs. They must not include `.fstack/` or the Orchestrator's state path. One chunk at a time is the v0.1 rule.

## Steps

1. Follow `memory` and search for memories that bear on the plan. Then follow `build-context` for `split-into-chunks`. If Notion is unreachable, show the unsaved plan and stop.

2. Write the Plan section and one Chunks page per chunk, as in `DESIGN.md`. Record `default_branch` and `default_branch_sha` on the feature.

3. Record `save_plan`.

   When `plan_review` is `notify`, set `feature_status: building`. Tell the human the chunk list through `tldr`, then continue.

   When `plan_review` is `approve`, set `feature_status: awaiting_plan_approval` and `waiting_on` to `Q-<slug>-plan`. Send the question card and end the turn. `approve_plan` is recorded later by `fstack-status` after a direct yes or approve.

4. Follow `advisors` for `planner_review` once for this plan text, before you treat the plan as saved. Apply a critique that makes a chunk smaller, testable, or correctly ordered. A failed call does not block the plan.

## Events

- `save_plan`

## Next

`pick-next-task` when the status is `building`.
