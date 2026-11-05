---
name: survey-product
contract: survey
description: >
  Describe one code location at one pinned commit and store that description.
  Use when a code location should be surveyed, on its own or once per location before comparing sources.
  Read-only. The skill does not prescribe which mechanism performs the read.
---

# Survey the product

This skill stands alone. A feature workflow can call it. Another workflow can call it and ignore the rest of fstack.

## Inputs

- One code location: a name, a role, an optional subpath, and a default branch. If the caller has no location, return "no product source" and stop. Do not invent a map. A feature with several locations calls this skill once per location.
- A pinned commit on that location. Do not survey a moving branch tip.

## Outputs

- A stored description of current behaviour: features and screens, routes and APIs, the data model, and flags.
- Every claim has a file and a line. A claim without both is left out.
- The store is keyed by the location name and the commit. A later call for the same pair returns the stored page and does not read that location again.

## Read-only

The read does not modify the product and does not open a pull request. This skill does not prescribe a runtime, a connector, or a product. The host decides how the read happens. Only the caller that owns Notion writes the page.

## Steps

1. If the effective workflow binding skips this slot, record `survey_skipped` and stop. If this call has no code location, return "no product source".

2. Resolve the pinned commit for this location. Record it under `base_shas` for that name when a feature is in progress. Search the stored maps for that location and commit. If one exists, reuse it and return it. When every location on the feature has a map, link the pages, record `survey_filed` with reused set, set Status to `surveyed`, and stop. If another location still needs a map, survey that one next.

3. When a feature is in progress and no stored map exists for this pair, record `survey_launched` and the location and commit, set Status to `surveying`, and hand the read to the host. End the turn. Do not start a second read for the same pair.

4. When the read returns, write one Codebase maps page titled `Existing functionality`, the location name, and the short commit. The page records that name and commit. The body is the description. If a feature is in progress and every location is filed, link the pages and record `survey_filed`, then set Status to `surveyed`. If this call had no feature, return the page and do not change a feature status.

5. If the read fails, do not invent a map. Show the failure and stop.

When the feature lists no code locations, record `survey_skipped`, set Status to `surveyed`, and leave current_product absent.

## Events

Record these only when a feature is in progress.

- `survey_launched`
- `survey_filed`
- `survey_skipped`

## Next

Return the stored page to the caller. Do not start gap analysis yourself.
