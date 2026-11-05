---
name: setup-product
description: >
  Initialize a product for fstack and resolve Cursor model names on the Orchestrator's machine.
  Use when fstack.yaml is missing, when the local resolved file is missing, or when the human asks to set up fstack or recheck models.
---

# Setup product

Prepare the product. Do not write session model slugs into `fstack.yaml`.

## When to use

- The product has no `fstack.yaml`.
- Notion database ids are missing from the bot's persistent state, or from `.fstack/resolved.yaml` on a Cursor checkout.
- The human asks to set up fstack or to recheck models.

## Plugin root

The fstack repository is the `repository` field in `plugin.json`. On Grok Bot, read templates and `state/transitions.yaml` through the GitHub connector. Do not clone the repository to do that. On the Cursor plugin, the plugin root is the directory that contains `.cursor-plugin/plugin.json` whose `name` is `fstack`. Do not hardcode a machine path or a user name.

## Steps

1. A product is not one code location. Ask for zero or more locations. Each has a name, a role, an optional subpath, and a default branch. Record that list on the Notion product. If `fstack.yaml` is missing, copy the plugin defaults. Put the file in a location only when the human names one location to hold it. With several locations, or with none, the copy of record is the Notion product. Do not invent a home location. If a file already exists, leave it. Do not rewrite it to store resolved slugs.

2. Read `fstack.yaml`. Stop if `version` is not `0.1` or `state_version` is not `1`, and say the product must be migrated. Stop if `state.backend` or `memory.backend` is not `notion`. Stop if `human_gates` differs from merge, release, outward_messages, coverage, and source_write `require_approval`, or `collect_requirements` `manual_only`. Do not silently change those keys. `sources` entries have `kind`, `ref`, and `reader`. Do not put a product name in `kind`.

3. On the Cursor plugin, ensure `.gitignore` contains a `.fstack/` line. Append that line when it is missing. That line is a guard for machine-specific config. It is the only fstack edit that belongs in the repository. Do not commit feature files. Feature state is not written under `.fstack/`. On Grok Bot, do not clone the product repository to edit that file. The same guard still belongs in the product repository when a human has a checkout.

4. Resolve models using `templates/resolved.yaml`. On Grok Bot, keep the resolved slugs and Notion ids in this bot's persistent state, not in a file in the product repository. Set each model to `inherit` and `source` to `unresolved` unless the human names a slug this account can pass to a Cursor cloud agent. On the Cursor plugin, write `.fstack/resolved.yaml` and detect the slugs this session can pass when it launches an agent. If you cannot detect any, set each model to `inherit`, set `source` to `unresolved`, and say so. Do not invent a slug. Do not put Notion page bodies in this file. It holds resolved model slugs and Notion ids only. It does not hold the fstack repository URL or the last applied skill commit.

5. Resolve the model families into that same file.

   For `opus` and `argon`, walk `models.<name>.match`, then walk `effort` in list order. A slug matches a prefix when it equals the prefix or starts with the prefix plus a hyphen. The first detected slug whose effort token matches the next effort in the list wins. If the family exists but no effort matches, use the first family slug and record that under `fallbacks`. If the family is missing, use `inherit` and record why.

6. Role models stay `inherit` unless `fstack.yaml` names `opus` or `argon` for that role. Resolve that short name the same way. Whoever launches an agent reads the resolved models from the bot's persistent state on Grok Bot, or from `.fstack/resolved.yaml` on the Cursor plugin. Agents do not switch their own model.

7. On Grok Bot, set `runtime` to `cloud`. Coding is a Cursor cloud agent on the product repository. On the Cursor plugin, set `runtime` to `cloud` when this session can start a Cursor cloud agent that opens a pull request against a non-default base. Otherwise set `local_worktree` and tell the human, through the `tldr` skill, that the implementer still receives the chunk spec in its launch prompt. Do not create a fstack worktree and do not copy state into the product checkout. Record the reason in `runtime_note`.

8. For each `advisors.fallback` entry, record availability in the resolved file under `advisor_cli`. Do not rewrite `fstack.yaml`. Skip an entry whose `enabled` is not true.

   The `command` must be a single name with no slash. Reject a path. Find it with `command -v` and keep only the exit status. Do not write the resolved path into the file or the chat.

   For `runtime: claude-cli`, run `<command> auth status` and keep only the exit status. Exit 0 means signed in. Do not print or store the command's output. Do not read token files, environment values, or a keychain. If the status subcommand is missing, mark the entry unavailable.

   Set `available` and `signed_in` from those exit statuses. A local CLI runs under the user's own subscription terms.

9. Connect Notion. This step is required. There is no local feature store.

   Ask the human to authenticate the Notion MCP. Confirm the connection by telling them their name and workspace name. Read the current setup notes with `notion-get-setup-guide`. Pass `instructions_version` from `memory.instructions_version` (`0.0.6`) on every Notion MCP call.

   Follow `memory` and `DESIGN.md`. Call `notion-fetch` on `notion://docs/memory` so the product database is not confused with the user's personal memory, and on `notion://docs/notion-flavored-markdown-spec` before writing any page body. Pass `instructions_version` on every Notion call. Search with `notion-search` for an existing product page and for Features, Chunks, Memories, Coverage, Codebase maps, and Workflow config databases. Show the human one yes-or-no question before creating any schema. On Grok Bot that question is a question card. Private is the default. Do not create pages until they approve. Ask again before anything is written to a shared or team space. Do not create fstack pages with parent `memory`.

   After approval, create or reuse a private product page with `notion-create-pages`, the six databases with `notion-create-database`, and a private Agent Operating Guide page. Use the property names in `notion_schema` in `state/transitions.yaml`. Seed Workflow config from `workflow`, `code_locations`, `release_policy`, `sources`, and `authoritative_kinds`. Do not copy human gates or the writer rule onto that page. Setup accepts any number of code locations, including zero. Set the guide version to `0.0.6` and the published date to `2026-10-30`. Fill the guide's destinations with the real links. Leave anything you did not create as "Not set up yet". Record the page and database ids in the same place as the resolved models: the bot's persistent state on Grok Bot, or `.fstack/resolved.yaml` on the Cursor plugin. Update later text with `notion-update-page`.

   Do not upload skills to Notion. Do not call `notion-complete-mcp-setup`. Do not create the daily loop unless the human asks for it in a separate yes.

   If Notion is unreachable, stop and show what you could not save. Do not write feature content under `.fstack/`.

10. Branch protection is not checked. Say that the check was not run. See `stubs/enforcement.md`.

## Events

This skill does not record a feature event.

## Next

Stop when the human asked to set up fstack, and tell them to ask you to start a feature when they are ready. When another skill sent you here, return to it. Do not start requirements collection.
