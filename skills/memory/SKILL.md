---
name: memory
description: >
  Read and write durable preferences and lessons in Notion Memory.
  Use when setup connects Notion, when collect-requirements, gap-analysis, or split-into-chunks starts, and when a feature ends and lessons might be saved.
  Only the Orchestrator uses this skill. Notion is required. There is no local copy of memory or feature state.
---

# Memory

Follow the debug-log contract.

Notion holds three different things. The product graph holds durable product facts. Notion Memory holds preferences and lessons. A feature page holds only what is transient: links to Decision pages, the plan, and status. Do not copy a graph fact into a memory, and do not copy a memory into a graph node.

The git repository at `artem-trachuk/fstack` is the only source of skill files. Do not upload, download, or sync skills through Notion Skills.

TODO(skills-in-notion): the official Shared context layer would store skills as Notion Skills, then call `notion-get-enabled-skills` and `notion-complete-mcp-setup` with type skills. That is not in force. Do not call those tools for skills. Leave this rule until the owner decides.

## When to use

- `setup-product` is connecting Notion.
- `collect-requirements`, `gap-analysis`, or `split-into-chunks` is about to start.
- `release` has finished a feature, or the human asks to remember something.
- The human asks to forget a memory.

## Notion calls

`instructions_version` is a parameter on every Notion tool this skill calls. Pass the value from `memory.instructions_version` in `fstack.yaml` (shipped as `0.0.6`).

Before the first memory read or write in a session, call `notion-fetch` with `notion://docs/memory`, then fetch with id `"memory"`. That fetch returns the About page and the built-in Memories database. Do not create a second Memories database. Do not add Product, Source, Uncertainty, Forgotten, or Confirmed to it.

Before creating or editing page content, call `notion-fetch` with `notion://docs/notion-flavored-markdown-spec` and write in that format.

## Recall

Fetch with id `"memory"` first and read the About page. Then call `notion-memory-search` for the specific topic. When the About page and a memory disagree, trust the more recent, more specific one. When a memory informs an answer, link it inline with the URL the tool returned.

Pass short excerpts and those links to the next skill. The coding agent, the verifier, and the advisors do not call Notion. The Orchestrator puts the excerpts in their prompts.

## Save

Search first with `notion-memory-search`. One topic per memory. Update the existing page instead of adding a duplicate.

Create with `notion-create-pages`, `parent: "memory"`, and no creation_mode. Set Type to exactly one of Profile, Preference, Work, People, or Notes. A product decision or a lesson is Type Work. Name the product in the body and link the product page or the feature page. Working style is Type Preference. Title the topic, not the fact. A People memory is titled with the person's name alone.

The body is short sentences that stand on their own. Refer to the human by the name Notion returned, never as "the user". Say why the memory applies and when. Mark an untested idea as untested. Use a Notion date mention for a full calendar date, such as `<date start="2026-10-30" />`. Do not invent a day for a month-only or year-only date.

Edit with `notion-update-page` and keep unrelated content. Confirm with the page link. Search can lag, so verify by fetching the page. If the save fails, say so.

When the memory changes the overall picture, update the About page with a targeted edit. Keep anything the human wrote. Stay under about 300 words. Use the sections Role, Current work, and Working preferences. Link the memories behind each point. Leave product details in the memories.

After a save that names a feature, mention that memory from the feature page body. Do not add a Memories relation, and do not put memory pages in `required_relations`.

## List or audit

`notion-memory-search` returns matches, not the whole database. To list or check for duplicates, fetch with id `"memory"`, read the data source URL, and run `notion-query-data-sources` in SQL mode. Start with about 20 rows and page until the result is complete. A limited page is not the whole database. Fetch likely matches to read their bodies.

## Forget

Find every matching memory. Delete a page that is entirely about that topic with `notion-delete-pages`. Otherwise remove only that information with `notion-update-page`. Remove it from the About page too. Do not leave a note that restates what was forgotten. Verify by fetching, then confirm.

## Do not save

Do not save temporary progress, copied code, a fact that is in the repository, a guess, generic advice, a secret, a credential, or a transcript. Do not save instructions for agents. A reusable procedure belongs in a skill. Product facts belong in the product graph.

Ask before writing into a shared or team space. Private pages are the default.

## If Notion is unreachable

Stop. Do not write the feature record or the memory onto the local disk. `.fstack/resolved.yaml` may keep ids and model slugs only. Show the unsaved content through `tldr`, verbatim, and say that it has not been saved. Wait for the human. That is a human gate, not a fallback store.

## Save a lesson

At the end of a feature, propose the lessons in a question card. Write them only after the human says yes, approve, or approved for that question id. Each accepted lesson is Type Work, names the product, and links the feature page. A refusal leaves Notion unchanged.

## Events

This skill does not change chunk status. Feature writes still use the events in `state/transitions.yaml`, stored on Notion pages.
