---
name: sync-bot-config
description: >
  Update this bot from the fstack repository's bot config.
  Use when a scheduled routine runs, or when the human asks to sync the bot.
  Copies skills from the repo, updates the profile and routines, and asks before widening connectors.
---

# Sync bot config

The git repository is the only source of skill files and bot config. This bot applies the config with its own tools. There is no public API to call, and this skill names no bot id, home directory, or person.

## When to use

A routine named in `bots/<name>.yaml` fires, or the human asks to sync. The routine prompt says which config file you are.

## Steps

1. Read the `repository` field in `plugin.json`. That is the fstack repo. Read the latest commit on its default branch. Do not hardcode a user or a machine.

2. Read the last applied commit from this bot's persistent state. The record is the fstack repository URL and `applied_commit`. If it is missing, this bot has not applied a config yet. Do not read it from the product repository or from `.fstack/resolved.yaml`.

3. Read `bots/<name>.yaml` at that remote commit. If the commit matches the last applied commit, report that nothing changed and stop.

4. Copy each listed skill from the repo as a `<slug>/SKILL.md` folder this bot can run. Add skills that are new, replace skills whose files changed, and remove skills that left the list. Do not copy skills from Notion.

5. If `name`, `title`, `description`, `persona`, or `instructions` changed, update this bot's profile to match the file.

6. Compare `routines` by name. Add a routine that is new, update its prompt and its schedule or GitHub events when they changed, and remove a routine that is no longer in the file. Do not leave a copy of a removed routine running. The event key in the yaml is quoted `"on"` because an unquoted `on` is a YAML boolean.

7. Compare `connectors`. If a connector was added, or a purpose would widen what the bot can reach, stop and ask the human before changing it. On Grok Bot, that ask is a question card. Do not add the connector in that same turn. Removing a connector does not need approval. Report the request through `tldr`.

   A routine may be a five-field cron, which runs in the timezone under Grok Bot settings, Bot. Or it may be a GitHub pull-request event: opened, pushed, merged, or commented. Map those four words onto the host's GitHub trigger and narrow it to branches named `fstack/`. Do not invent extra event types.

8. When the human approves a connector change, apply it, then continue. Record the repository URL and `applied_commit` in this bot's persistent state. On Grok Bot that is the memory that survives between chats. Do not write that pair into the product repository, into `.fstack/resolved.yaml`, or onto a Notion feature or memory page. If the host has no persistent state, say the commit was not saved and do not invent a file in the product repo.

9. Tell the human what changed: skills copied, profile fields, routines, and any connector still waiting.

## Events

This skill does not change a feature's status.
