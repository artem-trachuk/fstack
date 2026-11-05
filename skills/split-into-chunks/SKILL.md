---
name: split-into-chunks
contract: split
description: >
  Turn approved coverage rows into stacked chunks.
  Use when feature_status is ready_to_plan and the plan has no chunks, or when the human changes scope before implementation starts.
  Plans only rows the human approved whose classification is partial or missing.
  Follows plan_review from fstack.yaml. The default notify does not wait for plan approval.
---

# Split into chunks

## Contract

Inputs: approved buildable coverage rows, the base commit, and any slot parameters.
Outputs: ordered chunk pages, or a report that nothing is buildable.

Write the stack. Chunk ids look like `01-slug`, in order. Each chunk names exactly one code location. Within one location, the first chunk's base is that location's default branch. Each later chunk in that location uses the previous chunk's branch `fstack/<feature>/<chunk-id>`. A dependency in another location is `depends_on` only. It does not change the git base. Stacking, restack, and review are per location.

## When to use

Status is `ready_to_plan` after `approve_coverage`, and no chunk has left `planned`.

## Chunk file

Copy `templates/feature/chunks/chunk.md` from the plugin into the chunk page body. The Notion properties are the only place for status, branch, base, shas, allowed files, and attempt counts. The page body has spec, acceptance criteria, and out of scope. Do not add an implementer-notes section.

Allowed files are concrete paths or globs. They must not include `.fstack/`. One chunk at a time is the v0.1 rule.

## Steps

1. Follow `memory` and search for memories that bear on the plan. Then follow `build-context` for `split-into-chunks`. If Notion is unreachable, show the unsaved plan and stop.

2. Read the approved buildable rows you were given. Inside a feature, that is Coverage rows whose Approved flag is set and whose classification is `partial` or `missing`. Skip `done`, `conflict`, `needs_decision`, `undocumented`, `skip`, and `defer`. A decision row becomes buildable only after the human chose `implement` and the coverage gate approved it. If no row qualifies, tell the human there is nothing to build. Set `waiting_on` kind `plan`, question id `Q-<slug>-empty-plan`, options stop or describe a change. Do not record `save_plan` and do not set `building`. Do not launch an implementer. When this skill is called alone, split the rows you were given and return the plan. Do not look for a feature status.

   Write the Plan section and one Chunks page per planned row, as in `DESIGN.md`. Set each chunk's `repo` to one location. Set Product, Feature, and Touched nodes relations on the chunk. Set the feature's Chunks relation, and its Nodes read, Nodes added, Nodes changed, and Nodes removed relations. Those are relations, not copied ids. Do not copy node bodies onto the feature page. A chunk with no single location is not a chunk. A chunk or feature missing one of those relations is unlinked.

3. Record `save_plan`.

   When `plan_review` is `notify`, set `feature_status: building`. Tell the human the chunk list through `tldr`, then continue.

   When `plan_review` is `approve`, set `feature_status: awaiting_plan_approval` and `waiting_on` to `Q-<slug>-plan`. Send the question card and end the turn. `approve_plan` is recorded later by `fstack-status` after a direct yes or approve.

4. Follow `advisors` for `planner_review` once for this plan text, before you treat the plan as saved. Apply a critique that makes a chunk smaller, testable, or correctly ordered. A failed call does not block the plan.

## Events

- `save_plan`

## Next

`pick-next-task` when the status is `building`.
