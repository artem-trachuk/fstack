---
name: survey-product
contract: survey
description: >
  Describe how a product behaves at one pinned commit and store that description with the commit.
  Use when a repository should be surveyed, on its own or before comparing sources.
  Read-only. The skill does not prescribe which mechanism performs the read.
---

# Survey the product

This skill stands alone. A feature workflow can call it. Another workflow can call it and ignore the rest of fstack.

## Inputs

- A repository ref. If there is no repository, return "no product source" and stop. Do not invent a map.
- A pinned commit. Do not survey a moving branch tip.

## Outputs

- A stored description of current behaviour: features and screens, routes and APIs, the data model, and flags.
- Every claim has a file and a line. A claim without both is left out.
- The store is keyed by the commit. A later call for the same commit returns the stored page and does not read the repository again.

## Read-only

The read does not modify the product and does not open a pull request. This skill does not prescribe a runtime, a connector, or a product. The host decides how the read happens. Only the caller that owns Notion writes the page.

## Steps

1. If the effective workflow binding skips this slot, record `survey_skipped` and stop. If this call has no repository, return "no product source".

2. Resolve the pinned commit. Search the stored maps for that commit. If one exists, reuse it and return it. When a feature is in progress, link that page to the feature, record `survey_filed` with reused set, set Status to `surveyed`, and stop.

3. When a feature is in progress and no stored map exists, record `survey_launched` and the pinned commit, set Status to `surveying`, and hand the read to the host. End the turn. Do not start a second read for the same commit.

4. When the read returns, write one Codebase maps page titled `Existing functionality` plus the short commit. Set Base SHA to that commit. The body is the description. If a feature is in progress, link the page and record `survey_filed`, then set Status to `surveyed`. If this call had no feature, return the page and do not change a feature status.

5. If the read fails, do not invent a map. Show the failure and stop.

When the feature flow has no repository, record `survey_skipped`, set Status to `surveyed`, and leave current_product absent.

## Events

Record these only when a feature is in progress.

- `survey_launched`
- `survey_filed`
- `survey_skipped`

## Next

Return the stored page to the caller. Do not start gap analysis yourself.
