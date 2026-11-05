---
name: collect-requirements
description: >
  Write one feature's requirements on a Notion page and ask the human to confirm that page.
  Use only when the human explicitly asks in chat to start a feature or collect requirements.
  Never start this skill from another skill, a schedule, or a guess that a feature needs requirements.
disable-model-invocation: true
---

# Collect requirements

This skill runs only when the human asks in chat to start a feature or to collect requirements. On Grok Bot that is a normal message to the Orchestrator. On Cursor, a slash command is one way to ask, not the only way. Another skill must not start this one.

## When to use

The human asked in chat to start a feature.

## Steps

1. Read `fstack.yaml`. If it is missing, or the Notion database ids are missing from this bot's persistent state (Grok Bot) or from `.fstack/resolved.yaml` (Cursor plugin), follow `setup-product`, then continue.

2. Follow `memory` and search for memories about this product and the feature the human described. Pass the excerpts into the requirements. If Notion is unreachable, stop and show the unsaved requirements through `tldr`.

3. Agree a feature slug: lowercase letters, digits, and hyphens. Create a Features page in Notion from `DESIGN.md`. Do not create a local feature folder. Replace the template tokens in the page body. Do not invent a blank question.

   Do not commit the feature record. If the slug already has a confirmed requirements page, ask whether to continue it or pick another slug.

4. Fill the Requirements section of the Notion feature page from the human: problem, people, outcome, constraints, out of scope, and feature acceptance. Leave Status `requirements_draft`. Record `save_requirements` as its own decision page. Set that page's Product and Feature relations. Do not leave the decision only as a heading with no page.

5. Ask the human to confirm the Notion page. The message names the page link and uses the question card `Q-<slug>-requirements`. A 120-word summary is not the thing they confirm. Follow the `tldr` skill, and keep the link and the question id verbatim. End the turn if you are waiting.

6. On a correction, edit the page and ask again. On yes, approve, or approved, set Status to `requirements_confirmed`, quote them on the page, and record `confirm_requirements`. If Notion is unreachable, show the unsaved page text and stop.

## Events

- `save_requirements`
- `confirm_requirements`

## Next

Hand the feature slug to a new orchestrator agent and stop. Do not implement product code in this chat. Tell that agent to read `state/transitions.yaml` and run gap analysis. Do not start a second feature.
