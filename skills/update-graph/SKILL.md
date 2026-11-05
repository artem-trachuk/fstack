---
name: update-graph
contract: update_graph
description: >
  Promote a finished feature's confirmed changes into the product graph.
  Use when feature_status is awaiting_graph_update, after merge or release.
  Does not promote a stopped or abandoned feature. Does not store durable facts on the feature page.
---

# Update the graph

Follow the debug-log contract.

Follow the decision-policy contract.

The graph is the product's accumulating knowledge. This skill writes that knowledge. A feature page keeps only links to Decision pages, the plan, and status.

## Contract

Inputs: the feature delta (nodes read, added, changed, removed), the merged commits per code location, and `graph.promote`.
Outputs: updated graph nodes and edges, or a contradiction waiting for the human. A stopped feature writes nothing to the graph.

## When to use

Status is `awaiting_graph_update`. If the feature is `stopped`, or it never merged, stop. Do not promote. Decisions and memory may already exist. That is the only residue.

## Steps

1. Read the delta lists and the chunk nodes. Read the current graph nodes those ids name, and the edges among them. If Notion is unreachable, show the unsaved promotion and stop.

2. Build the promotion: new nodes, changed evidence, removed nodes, and `supersedes` edges from the new node to the one it replaces. Set last-verified commits from the merged commits. Set provenance to this feature.

   When a Fix page is related to the feature, update the nodes that page links. Write the corrected behaviour, a regression check or the verification link, and provenance to that Fix page. Do not add a feature node. Do not add a node that stands for the bug.

3. If a proposed node contradicts an active node, record `graph_flagged`. Do not promote the contradicted node yet. Follow the decision-policy contract. An authoritative conflict is one batched question: keep the graph, replace it, or stop. Any other contradiction is decided and logged, including when the advisors disagree. End the turn only when that question is the thing blocking promotion.

4. Read `graph.promote` from the effective workflow config. The repo default is `require_approval`.

   When `autonomy` is `auto`, or `graph.promote` is `notify`, show the delta, log the decision, and promote in the same turn.

   When `autonomy` is `ask_more` and `graph.promote` is `require_approval`, set `waiting_on` kind `graph_promotion`, question id `Q-<slug>-graph`. Show the delta in one card, batched with any other human-only question. Options are approve and stop. End the turn. Do not write nodes in that turn.

5. On approval, or when `auto` or `notify` applies, write the nodes and edges. Set each node's Product relation. Set each edge's Product, From, and To relations. Point the feature's node relations at the promoted nodes. Record `graph_promoted`. Set Status to `done`. Do not copy the node bodies onto the feature page.

Stop does not promote. Set Status to `stopped` with `human_decision`.

## Events

- `graph_promoted`
- `graph_flagged`

## Next

After `done`, return to `pick-next-task`. While a contradiction or an approval is open, stop.
