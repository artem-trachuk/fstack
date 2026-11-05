---
name: update-graph
contract: update_graph
description: >
  Promote a finished feature's confirmed changes into the product graph.
  Use when feature_status is awaiting_graph_update, after merge or release.
  Does not promote a stopped or abandoned feature. Does not store durable facts on the feature page.
---

# Update the graph

The graph is the product's accumulating knowledge. This skill writes that knowledge. A feature page keeps only links to Decision pages, the plan, and status.

## Contract

Inputs: the feature delta (nodes read, added, changed, removed), the merged commits per code location, and `graph.promote`.
Outputs: updated graph nodes and edges, or a contradiction waiting for the human. A stopped feature writes nothing to the graph.

## When to use

Status is `awaiting_graph_update`. If the feature is `stopped`, or it never merged, stop. Do not promote. Decisions and memory may already exist. That is the only residue.

## Steps

1. Read the delta lists and the chunk nodes. Read the current graph nodes those ids name, and the edges among them. If Notion is unreachable, show the unsaved promotion and stop.

2. Build the promotion: new nodes, changed evidence, removed nodes, and `supersedes` edges from the new node to the one it replaces. Set last-verified commits from the merged commits. Set provenance to this feature.

3. If a proposed node contradicts an active node, record `graph_flagged`. Do not promote the contradicted node. Ask the human with one question card. Options are keep the graph, replace it, or stop. End the turn.

4. Read `graph.promote` from the effective workflow config. The repo default is `require_approval`.

   When it is `require_approval`, set `waiting_on` kind `graph_promotion`, question id `Q-<slug>-graph`. Show the delta in one card. Options are approve and stop. End the turn. Do not write nodes in this turn.

   When it is `notify`, show the delta, then promote in the same turn.

5. On approval, or when `notify` applies, write the nodes and edges. Set each node's Product relation. Set each edge's Product, From, and To relations. Point the feature's node relations at the promoted nodes. Record `graph_promoted`. Set Status to `done`. Do not copy the node bodies onto the feature page.

Stop does not promote. Set Status to `stopped` with `human_decision`.

## Events

- `graph_promoted`
- `graph_flagged`

## Next

After `done`, return to `pick-next-task`. While a contradiction or an approval is open, stop.
