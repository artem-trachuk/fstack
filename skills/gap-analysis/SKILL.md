---
name: gap-analysis
contract: gap_analysis
description: >
  Compare whatever sources are present and classify each item from those roles.
  Use when two or more sources should be compared, or when a feature status is surveyed.
  Only buildable items can become chunks, and only after the human approves them.
  Do not start requirements collection. Do not write to a source without approval.
---

# Gap analysis

Follow the debug-log contract.

Follow the decision-policy contract.

This skill stands alone. Give it the sources that are present. It returns a coverage table. It does not read a repository and it does not start `survey-product`.

## Inputs

- `sources` from config. Each entry has `kind`, `ref`, and `reader`. `writer` is optional. A source is present when its reader returns content. Empty `ref` and `reader` mean the host may still pass pasted content. If nothing was read, the source is absent.
- `authoritative_kinds` from config. The shipped default is `requirements`. A kind not in that list is not authoritative.
- Kinds are names such as `requirements`, `design`, and `current_product`. Others are allowed. The kind is not a product name, and this skill does not care which connector, link, or paste produced the text.

`current_product` is the product graph, which is the current product truth. Compare sources against those nodes. Do not re-read raw code when the graph already covers it. A feature with several locations uses the nodes whose evidence names each location, then one coverage view. Every row sets the Node relation to the graph node, `repo` to the location, and `commit` to that node's last-verified commit. Also set the Product and Feature relations. A coverage row with an empty Node, Feature, or Product relation is unlinked. If the graph has no nodes for a location, stop and tell the caller to run `survey-product`. Do not describe the location from memory. If the feature has no code locations, `current_product` is absent and the comparison uses the other sources. Those rows leave `node` and `repo` empty.

## Outputs

One coverage row per item. The same item from two sources in one location is one row. `node` is the graph node id. `repo` names the location. `commit` is that node's last-verified commit, or empty when the graph has no node yet.

Each row has one presence entry per source that was compared: the kind, whether the item is present, partial, or absent, and the evidence. Presence entries live in the row body. They are not fixed columns.

Then a classification, from the rules below, and a next action: `plan`, `question`, or `none`.

## Rules

Apply these in order. Do not special-case a source name.

1. Present in `current_product` and matching an authoritative source: `done`. Next action `none`.
2. Backed by an authoritative source and absent from `current_product`: `missing`. Partly present in `current_product`: `partial`. Both are buildable. Next action `plan`.
3. Two present sources contradict each other: `conflict`. Next action `question`.
4. Present only in a non-authoritative source, with no authoritative backing: `needs_decision`. Next action `question`.
5. Present in `current_product` and in no authoritative source: `undocumented`. Next action `question`.

If `current_product` is absent, do not use rules 1, 2, or 5. An authoritative item is then not buildable, because the product was not surveyed. Say that on the row.

`done` is not a chunk. `needs_decision`, `conflict`, and `undocumented` are not chunks until the human accepts one as a requirement and the coverage gate approves it. A conflict is never implemented from the table alone.

When a Fix page is related to the feature, compare its Expected and Actual text with the linked graph node's recorded behaviour and with the authoritative requirements. Cite the node's evidence. Where the requirement agrees with Expected and the node or the product disagrees, the row is `partial` or `missing` and buildable. If the requirement itself is ambiguous, the row is a question for the human, not a fix. Classify it `needs_decision` and set the next action to `question`. Do not plan that row.

## Steps

1. Follow `memory` when a feature is in progress. Follow `build-context` for `gap-analysis` when a feature page exists. If this call has no feature, compare the inputs and return the table. Do not write a feature status.

2. Read every present source. Write one Coverage row per item. Record `record_coverage` when a feature is in progress.

3. Follow the decision-policy contract for a non-trivial classification. That asks each advisor named in `advisors.decision`, including `planner_review`, to critique and rank the options. A failed call does not stop you. Skip the advisors when this call has no feature or the `advise` slot is skipped.

4. Decide rows that are not human-only. Do not ask the human to choose an implementation. A conflict between authoritative sources, or a user-visible requirement that no authoritative source settles, is human-only. Batch those questions into one card. Options for each such row: `implement`, `write_back`, `skip`, and `defer`. `implement` makes the row buildable. `skip` and `defer` are not chunks. `write_back` stores proposed text and does not send it. Keep working on rows the card does not block.

5. Under `autonomy` `auto`, record the buildable `partial` and `missing` rows as approved and continue. Under `ask_more`, the coverage gate is one card with approve and stop, batched with any other human-only question. `approve_coverage` is recorded by the caller. When this skill is used alone, return the table. Do not approve it yourself.

A `write_back` is sent only by the source's `writer`, and only after the human approves that text. If the source has no writer, keep the text on the row and do not invent a destination. Do not write to a source unless the human approves that write.

## Events

Record these only when a feature is in progress.

- `record_coverage`

## Next

Return the table to the caller. Stop while a feature question is open. `split-into-chunks` is a separate skill. Call it only with approved buildable rows.
