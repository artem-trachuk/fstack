---
name: memory
description: >
  Read and write fstack's durable project memory in Notion.
  Use when setup creates the workspace, when collect-requirements, gap-analysis, or split-into-chunks starts, and when a feature ends and lessons might be saved.
  Only the Orchestrator uses this skill. Notion is required. There is no local copy of memory or feature state.
---

# Memory

Notion holds two kinds of durable material: the feature record (requirements, plan, chunks, prompts, diffs, verification, advisor inputs and outputs, decisions, logs, status) and cross-feature memory (decisions and why, corrections, preferences, conventions, lessons).

The git repository at `artem-trachuk/fstack` is the only source of skill files. Do not upload, download, or sync skills through Notion Skills.

## When to use

- `setup-project` is connecting Notion.
- `collect-requirements`, `gap-analysis`, or `split-into-chunks` is about to start.
- `release` has finished a feature, or the human asks to remember something.
- The human asks to forget a memory.

## Notion calls

On every Notion MCP tool call, pass `instructions_version` with the value from `memory.instructions_version` in `fstack.yaml` (shipped as `0.0.6`).

Before the first memory write in a session, call `notion-fetch` with `notion://docs/memory` and follow that guide. If its property names differ from `DESIGN.md`, use the guide's names.

Search with `notion-memory-search` before creating a memory. One topic per memory. Update an existing memory instead of adding a near-duplicate. Keep the source link, the date the fact was confirmed, and any uncertainty. The day you save it is not the confirmation date.

Do not save secrets, credentials, transcripts, copied code, or anything that can be recovered from the repository. Honor a forget request: mark the memory forgotten, do not recreate it, and say if Notion will not let you reach a copy.

Ask before creating a database or writing into a shared or team space. Private pages are the default.

## If Notion is unreachable

Stop. Do not write the feature record or the memory to disk, to `~/.fstack`, or to `.fstack`. Show the unsaved content in the chat through `tldr` and say that it has not been saved. Wait for the human. That is a human gate, not a fallback store.

## Read

Search memories for the project and the feature topic. Pass the short excerpts to the next skill. The coding agent, the verifier, and the advisors do not call Notion. The Orchestrator puts the excerpts in their prompts.

## Save a lesson

At the end of a feature, propose the lessons in a question card. Write them only after the human says yes, approve, or approved for that question id. A refusal leaves Notion unchanged.

## Events

This skill does not change chunk status. Feature writes still use the events in `state/transitions.yaml`, stored as Notion pages rather than local files.
