---
name: upgrade-fstack
description: >
  Bring the installed fstack up to the repository's current main.
  Use when the human says "update fstack", "upgrade fstack", or "sync fstack".
  Idempotent. Does not change Notion's setup-guide version.
---

# Upgrade fstack

Follow the debug-log contract.

Follow the decision-policy contract.

The fstack version is the `version` in `plugin.json` plus the commit on main. The Agent Operating Guide version `0.0.6` is Notion's setup guide. It is not the fstack version. Do not stop because the guide is `0.0.6`, and do not change `instructions_version`.

## When to use

The human says "update fstack", "upgrade fstack", or "sync fstack".

## Steps

1. Read the `repository` field in `plugin.json` and the `version` there. Read the current commit on that repository's main branch. Read `fstack_version` and `fstack_commit` from this bot's persistent state, and the latest fstack line in the Agent Operating Guide's Version history. If both the version and the commit already match, say so and stop. A second run with the same commit changes nothing.

2. Summarise what changed between the installed commit and main. Use `CHANGELOG.md` and the diff. Cover skills added, changed, or removed, bot config, workflow-config defaults, and the Notion model or `required_relations`. Do not paste full files.

3. Follow `sync-bot-config` for the Orchestrator. That records `applied_commit` on every successful apply.

4. Follow `provision-team` so teammates match the new config. Message each one to follow `sync-bot-config` for its own yaml at this commit. Collect each reply. A missing reply is reported, not invented.

5. For every product Workflow config, add a default that the new version introduces and that the page does not already set. Keep a value the human set. Record each added or kept difference with `workflow_changed`. Flag a setting the new version removed or renamed, and do not delete the human's value in this step.

6. Apply Notion model changes the new version needs, such as a Fix page kind or a new relation, when that does not create a schema, move a page, or delete a page. Schema creation, and any move or delete, stay human gates. Batch every one of those into one question card and wait. Do not apply them in that turn.

7. Follow `fstack-status`. Report orphans and any pending migration, including a feature page that is really a bug.

8. Record the new `fstack_version` and `fstack_commit` in persistent state, and append the same pair to the Operating Guide's Version history. Leave the guide's `0.0.6` line as it is. Then report a short summary: what changed, what was applied, and what is waiting on the human.

If Notion is unreachable, show the unsaved summary and stop. Do not invent a local copy of the version record.

## Events

This skill does not change feature status. Workflow edits use `workflow_changed`.

## Next

Stop. Do not start a feature.
