---
name: collect-requirements
description: >
  Turn a human request into a new feature or a fix on an existing feature.
  Use only when the human explicitly asks in chat to start a feature, collect requirements, or fix a bug.
  Never start this skill from another skill, a schedule, or a guess that a feature needs requirements.
disable-model-invocation: true
---

# Collect requirements

Follow the debug-log contract.

This skill runs only when the human asks in chat to start a feature, to collect requirements, or to fix a bug. On Grok Bot that is a normal message to the Orchestrator. On Cursor, a slash command is one way to ask, not the only way. Another skill must not start this one.

## When to use

The human asked in chat to start a feature, or to fix a bug or a regression.

## Steps

1. Read `fstack.yaml`. If it is missing, or the Notion database ids are missing from this bot's persistent state (Grok Bot) or from `.fstack/resolved.yaml` (Cursor plugin), follow `setup-product`, then continue.

2. Follow `memory` and search for memories about this product and the request the human described. Pass the excerpts into the requirements or the fix. If Notion is unreachable, stop and show the unsaved text through `tldr`.

3. Classify the request before any page is created. `new_feature` is new behaviour. `fix` is a bug or a regression in existing behaviour. Use the source kinds already in config, such as `requirements`, `design`, and `current_product`. Do not name a vendor.

   When the class is `new_feature`, agree a feature slug: lowercase letters, digits, and hyphens. Create a Features page in Notion from `DESIGN.md`. Do not create a local feature folder. Replace the template tokens in the page body. Do not invent a blank question. Do not commit the feature record. If the slug already has a confirmed requirements page, ask whether to continue it or pick another slug.

   When the class is `fix`, follow the skill bound to the `fix` slot. The repo default is `file-fix`. Never create a Features page for a fix. Stop this skill after that handoff.

The remaining steps apply only when the class is `new_feature`.

4. Fill the Requirements section of the Notion feature page from the human: problem, people, outcome, constraints, out of scope, and feature acceptance. Leave Status `requirements_draft`. Record `save_requirements` as its own decision page. Set that page's Product and Feature relations. Do not leave the decision only as a heading with no page.

5. Ask the human to confirm the Notion page. The message names the page link and uses the question card `Q-<slug>-requirements`. A 120-word summary is not the thing they confirm. Follow the `tldr` skill, and keep the link and the question id verbatim. End the turn if you are waiting.

6. On a correction, edit the page and ask again. On yes, approve, or approved, set Status to `requirements_confirmed`, quote them on the page, and record `confirm_requirements`. If Notion is unreachable, show the unsaved page text and stop.

## Events

- `save_requirements`
- `confirm_requirements`

## Next

Stop this skill. Do not implement product code in this chat. The next rule is survey when the feature lists code locations, then gap analysis. Do not jump to gap analysis and do not start a second feature.
