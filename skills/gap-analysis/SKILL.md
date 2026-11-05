---
name: gap-analysis
description: >
  Build a coverage table from the requirements, Linear, Figma, and the product survey.
  Use when feature_status is surveyed, or when the human is answering a coverage question.
  Only requirement-backed partial and missing rows can become chunks, and only after the human approves them.
  Do not start requirements collection. Do not implement unrequested design or a conflict.
---

# Gap analysis

Compare three sources. The codebase is required. The others are optional.

## Sources

- Requirements written by `collect-requirements`. Optional. An empty page means this source has no rows.
- Linear, through the Linear connector: the project, its issues, and their acceptance criteria. Optional. If the connector is not connected, say so and continue. Do not block.
- Design from Figma, through the Figma connector: frames and components. Optional. If Figma is not connected, ask the human for a link or a short description, then continue. A missing design is an empty column, not a stop.
- The current app, from the Existing functionality page for this base SHA. Required. If that page is missing, stop and follow `survey-product`. Do not describe the app from memory.

## When to use

Status is `surveyed`. If it is still `requirements_confirmed` or `surveying`, stop. The survey has not been filed.

## Coverage row

One row per item from any source. The same item from two sources is one row.

| Column | Meaning |
| --- | --- |
| Item | The short name |
| In design | Evidence from Figma, or empty |
| In requirements | Evidence from the requirements page or from Linear, or empty |
| In app | Evidence from the survey, with file and line, or empty |
| Classification | One of the six names below |
| Next action | `plan`, `question`, or `none` |

Classifications:

- `done`. The app matches the requirement.
- `partial`. The requirement is only partly in the app.
- `missing`. It is required and designed, and it is not built.
- `conflict`. The app or the design contradicts a requirement.
- `unrequested_design`. It is in Figma and not in Linear or the requirements. A new button is this.
- `undocumented_behaviour`. It is in the app and in no requirement.

Next action:

- `done` is `none`. It does not become a chunk.
- `partial` and `missing` are `plan`. They are the only requirement-backed rows that can become chunks, and only after `approve_coverage`.
- `conflict`, `unrequested_design`, and `undocumented_behaviour` are `question`. An unrequested design and a conflict are never implemented automatically. Undocumented behaviour is not a chunk either.

## Steps

1. Follow `memory`. Then follow `build-context` for `gap-analysis`. If Notion is unreachable, show the unsaved table and stop.

2. Read the four sources. Write one Coverage row per item, with Base SHA set to the survey commit. Record `record_coverage`.

3. Follow `advisors` for `planner_review` once for this table. Fold in a critique that names a real missing row or a wrong classification. A failed call does not stop you.

4. If any row is `conflict`, `unrequested_design`, or `undocumented_behaviour`, set Status to `questions_open` and `waiting_on` kind `coverage_questions`, question id `Q-<slug>-coverage`. Send one question card through `tldr` for all of those rows. The options on every row are `implement`, `add_to_linear`, `skip`, and `defer`. End the turn. Do not plan chunks in this turn.

   If there are no such rows, set Status to `awaiting_coverage_approval` and send the coverage gate in the next step. Do not skip the gate.

5. The coverage gate lists every row whose classification is `partial` or `missing`, including a row the human marked `implement` (that answer makes it requirement-backed, so set its classification to `missing` if it was not already). Set `waiting_on` kind `coverage_approval`, question id `Q-<slug>-coverage-approve`. The options are approve and stop. End the turn. `approve_coverage` is recorded by `fstack-status`.

`skip` and `defer` do not become chunks. `add_to_linear` does not become a chunk by itself. It saves a Linear draft on the row. Creating that issue waits for a separate yes. Never create a Linear issue without that approval.

## Events

- `record_coverage`

## Next

Stop while a question is open. `split-into-chunks` runs only after Status is `ready_to_plan`.
