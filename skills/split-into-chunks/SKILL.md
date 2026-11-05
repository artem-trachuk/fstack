---
name: split-into-chunks
contract: split
description: >
  Turn approved coverage rows into one or more chunks.
  Use when the plan has no chunks yet, including straight after gap analysis when the work is one chunk per repo.
  Any work item, new_feature or fix, defaults to one chunk per repo. Split only when that clearly helps. No separate planning pass and no plan question for the single chunk.
  Plans only approved rows whose classification is partial or missing.
---

# Split into chunks

Follow the debug-log contract.

Follow the decision-policy contract.

## Contract

Inputs: approved buildable coverage rows, the base commit, and any slot parameters.
Outputs: ordered chunk pages, or a report that nothing is buildable.

Write the stack. Chunk ids look like `01-slug`, in order. Each chunk names exactly one code location. Within one location, the first chunk's base is that location's default branch. Each later chunk in that location uses the previous chunk's branch `fstack/<feature>/<chunk-id>`. A dependency in another location is `depends_on` only. It does not change the git base. Stacking, restack, and review are per location.

## When to use

Status is `ready_to_plan`, or gap analysis has just approved a one-chunk plan. No chunk has left `planned`.

## Chunk page

Copy the body of `templates/feature/chunks/chunk.md` onto the chunk page. The Notion properties are the only place for status, branch, base, shas, allowed files, and attempt counts. The page body has spec, acceptance criteria, and out of scope. Do not add an implementer-notes section.

Allowed files are concrete paths or globs. They must not include `.fstack/`. One chunk at a time is the v0.1 rule.

## Steps

1. Follow `memory` and search for memories that bear on the plan. Then follow `build-context` for `split-into-chunks`. If Notion is unreachable, show the unsaved plan and stop.

2. Read the approved buildable rows you were given. Inside a feature, that is Coverage rows whose Approved flag is set and whose classification is `partial` or `missing`. Skip `done`, `conflict`, `needs_decision`, `undocumented`, `skip`, and `defer`. If no row qualifies, say there is nothing to build and stop. Do not open a plan question. Do not record `save_plan` and do not set `building`. When this skill is called alone, split the rows you were given and return the plan.

   Decide whether splitting helps. Follow the decision-policy contract. The default for any work item, `new_feature` or `fix`, is one chunk for each repo the change touches. Split only when that clearly helps: size, independent risk, multiple repos, or a staged rollout. Record `single_chunk_filed`, write that chunk, and set `feature_status: building`. Do not run a separate planning pass and do not send a plan question.

3. When splitting does help, draft the chunks in the session. Follow `advisors` for `planner_review` on that draft before `save_plan`. Apply a critique that makes a chunk smaller, testable, or correctly ordered. A failed or skipped call does not block the plan. If the advisor was only launched and the critique is not back yet, end the turn without `save_plan` and without setting `building`. When the critique is in hand, continue in that same turn. Do not end the turn between the critique and `save_plan`.

4. Record `save_plan` only after that review step, and only for a plan with more than one chunk in a repo. Write the Plan section and one Chunks page per planned row, as in `DESIGN.md`. Set each chunk's `repo` to one location. Set Product, Feature, and Touched nodes relations on the chunk. Set the feature's Chunks relation, and its Nodes read, Nodes added, Nodes changed, and Nodes removed relations. Those are relations, not copied ids. Do not copy node bodies onto the feature page. A chunk with no single location is not a chunk. A chunk or feature missing one of those relations is unlinked. When the rows come from a Fix page, set that page's Chunks relation to these chunks. A fix may span features and repos. Each chunk still names one repo. One chunk is a valid plan.

   When `plan_review` is `notify`, or `autonomy` is `auto`, set `feature_status: building`. Tell the human the chunk list through `tldr`, then continue.

   When `plan_review` is `approve` and `autonomy` is `ask_more` and the plan has more than one chunk in a repo, set `feature_status: awaiting_plan_approval` and `waiting_on` to `Q-<slug>-plan`. Send the question card and end the turn. `approve_plan` is recorded later by `fstack-status` after a direct yes or approve. A single chunk does not send that card.

## Events

- `single_chunk_filed`
- `save_plan`

## Next

`pick-next-task` when the status is `building`.
