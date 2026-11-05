---
name: survey-product
contract: survey
description: >
  Refresh stale product-graph nodes for one code location at one pinned commit.
  Use when a code location should be surveyed, on its own or once per location before comparing sources.
  Read-only. The skill does not prescribe which mechanism performs the read.
---

# Survey the product

This skill stands alone. A feature workflow can call it. Another workflow can call it and ignore the rest of fstack.

## Inputs

- One code location: a name, a role, an optional subpath, and a default branch. If the caller has no location, return "no product source" and stop. Do not invent a map. A feature with several locations calls this skill once per location.
- A pinned commit on that location. Do not survey a moving branch tip.

## Outputs

- Graph nodes for what this location does. Kinds come from `graph.node_kinds`. Each node has evidence (location, path, commit), provenance `survey`, and last-verified commits.
- Every claim has a file and a line. A claim without both is left out.
- A node whose last-verified commit for this location equals the pinned commit is fresh. Reuse it. Do not read that path again.

## Read-only

The read does not modify the product and does not open a pull request. This skill does not prescribe a runtime, a connector, or a product. The host decides how the read happens. Only the caller that owns Notion writes the page.

## Steps

1. If the effective workflow binding skips this slot, record `survey_skipped` and stop. If this call has no code location, return "no product source".

2. Resolve the pinned commit for this location. Record it under `base_shas` for that name when a feature is in progress. Read the product graph. A node is fresh when its last-verified commit for this location equals that pin. Reuse every fresh node. Re-read only a stale node's evidence path, or an area the graph does not cover. The first survey, when the graph has no nodes for this location, seeds the graph.

3. When a feature is in progress and some nodes are stale or missing, record `survey_launched` and the location and commit, set Status to `surveying`, and hand that limited read to the host. End the turn. Do not start a second read for the same pair. Do not read the whole location when the graph already covers it.

4. When the read returns, create or update graph nodes. Set evidence, provenance `survey`, last-verified commits, and the Product relation. Create one survey page for this location and commit. Set its Product relation and its Nodes relation to the nodes this read created or refreshed. When a feature is in progress, also set the survey page's Feature relation. Do not write those facts on the feature page. If every location is filed, record `survey_filed` and set Status to `surveyed`. If this call had no feature, return the survey page and do not change a feature status.

5. If the read fails, do not invent a map. Show the failure and stop.

When the feature lists no code locations, record `survey_skipped`, set Status to `surveyed`, and leave current_product absent.

## Events

Record these only when a feature is in progress.

- `survey_launched`
- `survey_filed`
- `survey_skipped`

## Next

Return the stored page to the caller. Do not start gap analysis yourself.
