---
name: memory
description: >
  Read and write fstack's durable product memory in Notion.
  Use when setup creates the workspace, when collect-requirements, gap-analysis, or split-into-chunks starts, and when a feature ends and lessons might be saved.
  Only the Orchestrator uses this skill. Notion is required. There is no local copy of memory or feature state.
---

# Memory

Notion holds three different things. The product graph holds durable product facts. Memory holds preferences and lessons. A feature page holds only what is transient: the decision log, the plan, and status. Do not copy a graph fact into a memory, and do not copy a memory into a graph node.

The git repository at `artem-trachuk/fstack` is the only source of skill files. Do not upload, download, or sync skills through Notion Skills.

## When to use

- `setup-product` is connecting Notion.
- `collect-requirements`, `gap-analysis`, or `split-into-chunks` is about to start.
- `release` has finished a feature, or the human asks to remember something.
- The human asks to forget a memory.

## Notion calls

`instructions_version` is a parameter on every Notion tool this skill calls. Pass the value from `memory.instructions_version` in `fstack.yaml` (shipped as `0.0.6`).

Before the first memory write in a session, call `notion-fetch` with `notion://docs/memory` so you do not mix that store up with the product database. Do not copy its property names onto the product database.

Before creating or editing page content, call `notion-fetch` with `notion://docs/notion-flavored-markdown-spec` and write in that format.

Product memories live in the Memories database on the product page. Fetch that database, then query its `collection://` data source with `notion-query-data-sources` before creating a page. Do not call `notion-memory-search`. Do not create pages with parent `memory`. Search other product pages with `notion-search`. Create pages with `notion-create-pages` under the product Memories database. Set the Product relation. Set the Feature relation when the memory belongs to one feature. A memory with no Product relation is an orphan. Edit them with `notion-update-page`. Create a database with `notion-create-database`, using SQL `CREATE TABLE` or the typed database form that tool accepts. One topic per memory. Update an existing memory instead of adding a near-duplicate. Keep the source link, the date the fact was confirmed, and any uncertainty. The day you save it is not the confirmation date.

Do not save secrets, credentials, transcripts, copied code, or anything that can be recovered from the repository. Honor a forget request: mark the memory forgotten, do not recreate it, and say if Notion will not let you reach a copy.

Ask before creating a database or writing into a shared or team space. Private pages are the default.

Do not call `notion-complete-mcp-setup`. fstack does not publish skills to Notion.

## If Notion is unreachable

Stop. Do not write the feature record or the memory onto the local disk. `.fstack/resolved.yaml` may keep ids and model slugs only. Show the unsaved content in the chat through `tldr` and say that it has not been saved. Wait for the human. That is a human gate, not a fallback store.

## Read

Query the product Memories database for the product and the feature topic. Pass the short excerpts to the next skill. The coding agent, the verifier, and the advisors do not call Notion. The Orchestrator puts the excerpts in their prompts.

## Save a lesson

At the end of a feature, propose the lessons in a question card. Write them only after the human says yes, approve, or approved for that question id. A refusal leaves Notion unchanged.

## Events

This skill does not change chunk status. Feature writes still use the events in `state/transitions.yaml`, stored on Notion pages.
