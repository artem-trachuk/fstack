---
name: survey-product
description: >
  Map how the product works today and save that map on a Notion page stamped with the base SHA.
  Use when feature_status is requirements_confirmed or surveying.
  Read-only. The cloud agent does not write Notion, edit the product, or open a pull request.
---

# Survey the product

Look at the product before gap analysis. Requirements alone are not enough.

## When to use

The next rule is `survey_product` or `resume_survey`. Do not start this from gap analysis. Do not start it before the human has confirmed requirements.

## What the map contains

Features and screens, routes and APIs, the data model, and flags. Every claim has a file and a line. A claim without a file and a line is not written down.

## Steps

1. Read the default branch SHA. That is the pinned base commit. Record it as `default_branch_sha` on the feature if it is empty. Do not survey a moving branch tip.

2. Search the Codebase maps database for a page whose Base SHA is that commit. If one exists, link it to this feature as Existing functionality, record `survey_filed` with reused set, set Status to `surveyed`, and stop. Do not launch another agent. Later features reuse the same page.

3. If no page exists, follow `build-context` for `survey-product`. Record `survey_launched` with the agent id before you wait. Set Status to `surveying`. Launch one read-only Cursor cloud agent on the product repository at that pinned commit.

   On Grok Bot, launch the cloud agent. Do not clone the repository. Do not write product code on the bot computer. The agent reads files through the GitHub connector. It does not open a pull request and it does not push. When the run finishes you are revived with its report. To change a running survey, send a follow-up. Do not start a second agent.

   On the Cursor plugin, start a read-only cloud agent at the same commit when the session can. It must not edit files.

   The agent does not open Notion. You are the only writer.

4. On resume, if the agent is still running, end the turn. If it failed and there is no report, record that and stop. Show the human the failure through `tldr`. Do not invent a map.

5. Write one Codebase maps page titled `Existing functionality` plus the short SHA. Set Base SHA to the pinned commit. The body is the report: features and screens, routes and APIs, data model, and flags, each with file and line. Link that page to the feature. Record `survey_filed`. Set Status to `surveyed`.

## Events

- `survey_launched`
- `survey_filed`

## Next

Return to `pick-next-task`. Gap analysis runs only after Status is `surveyed`.
