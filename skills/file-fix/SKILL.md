---
name: file-fix
contract: fix
description: >
  File a bug or regression as a Fix page under an existing feature.
  Use when collect-requirements or pick-next-task classifies a request as fix.
  Never create a feature page for a bug. Only the Orchestrator writes Notion.
---

# File a fix

Follow the debug-log contract.

Follow the decision-policy contract.

A fix is a correction to existing behaviour. The feature page keeps its title and its description. The bug is a Fix page related to that feature.

## Inputs

- The human's request, already classified as `fix`.
- The product graph: nodes, their evidence, and the features that read or changed them.
- The effective `fix` slot. The repo default is this skill. A product page or a feature override may bind another skill with the same contract.

## Outputs

- One Fix page in the Fixes database. It records Expected, Actual, Reproduce, and Severity.
- Relations: Product and Feature are required. Nodes, Chunks, and Verification may be empty until they exist.
- No new Features page. No new graph node for the bug.

## Steps

1. Read the product graph. Match the broken behaviour to existing nodes. Cite each candidate with the node's evidence: location, path, and commit. A confident match is exactly one feature whose nodes describe that behaviour, with no second feature in contention.

2. Score the candidates on the evidence you cited. Use the best-evidenced feature when it is clearly ahead. Follow the decision-policy contract, and ask the configured advisors when more than one feature is plausible. Ask only when the top candidates are genuinely tied after checking evidence. Do not ask the human to choose a fix approach. If no feature has evidence, ask which existing feature it belongs to, in the same batched card as any other human-only question. Never create a Features page for a fix.

3. Never create a Features page for a fix. Do not rename the feature page, and do not rewrite its description to the bug. A fix may list more than one feature and more than one repo. Set Feature to the chosen features. Each later chunk still names one repo.

4. Create the Fix page. Title it with the broken behaviour, not with a new feature name. Fill Expected, Actual, Reproduce, and Severity from the human's message. Leave a missing field blank. Do not invent a behaviour, and do not ask which approach to take. If the desired behaviour is ambiguous in a way users would notice and no authoritative source settles it, batch that question. Link the matched nodes. Leave Chunks and Verification empty until they exist.

5. A feature whose status is `done` returns to `requirements_confirmed`, so survey and gap analysis run on the fix. A feature already in progress keeps its status. A stopped feature is reopened when the human asked for the fix. Record that decision. Record `fix_filed`. If Notion is unreachable, show the unsaved Fix page and stop.

## Events

- `fix_filed`

## Next

Return to `pick-next-task`. Gap analysis compares the Fix page with the graph. Do not start a second feature.
