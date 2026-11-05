---
name: provision-team
description: >
  Create or update the Orchestrator's teammate bots from bots/*.yaml.
  Use when sync-bot-config has applied the Orchestrator config, or when the human asks to install fstack.
  Idempotent. A second run with the same configs changes nothing. Never deletes a bot.
---

# Provision the team

Follow the debug-log contract.

The human creates only the Orchestrator. This skill provisions the other roles. It uses host capabilities by name: create teammate, update teammate profile, message teammate, and this bot's persistent state. It stores no bot id in the repo and no path on a machine.

## When to use

You are the Orchestrator, and `sync-bot-config` has just applied `bots/orchestrator.yaml`, or the human asked you to install fstack. Another role does not run this skill.

## State

Persistent state holds:

- `team`: a map of role to bot id. The id is whatever the host returned. It is not a display name.
- `team_approved`: roles the human has already approved to create or rename.
- `team_retired`: roles whose config left the repo. The bot still exists.
- `team_sync`: for each role, the applied commit that teammate reported and any connectors still missing.

## Match

For each `bots/<name>.yaml` other than the Orchestrator:

1. Read its `model_role` and `role_marker`. The marker is a stable token such as `fstack-role:verifier`. It is not a display name.
2. If `team` has an id for that role, fetch that teammate. Use it only when its profile still contains the same marker. A display-name match is not enough.
3. If `team` has no id, search teammates for that marker in the description or profile. One match: record its id. Several matches: ask the human which id to keep. None: the role is missing.

## Create and rename

A missing role is created with the host's create-teammate capability. An existing teammate whose name or description differs from the file is updated with update-teammate-profile.

The first create or rename of a role needs the human's approval. Batch every such role into one question card. On yes, record the roles in `team_approved`, then create or rename, and store each new id in `team`.

Later syncs of those same roles do not ask again. The human's sync approval covers profile updates. A role that is not in `team_approved` still waits for a card.

Do not put a bot id in chat, in Notion, or in the repo. It stays in persistent state.

## Kickoff

Skills, routines, and connectors are not set by the Orchestrator on another bot. After the profile is current, message the teammate: follow `sync-bot-config` for its yaml at this commit. It copies its own skills, profile, and routines, then replies with `applied_commit` and any connectors still missing.

Record that reply in `team_sync` and record `teammate_synced`. If `team_sync` already has this commit and the profile already matches, do not message again.

## Connectors

Missing connectors, including read-only repo access for the Verifier and Advisor, need the human. Batch every missing connector for every bot into one question card. Do not authorize a connector yourself and do not ask a teammate to skip authorization. On yes, each teammate adds only the connectors named in that card.

## Retired roles

If `team` has a role whose yaml is gone, do not delete the bot. Add the role to `team_retired` and ask the human what to do with it. Do not send it another sync.

## Idempotent

When every configured role has a matching id, the profile matches, `team_sync` has the target commit, and no connector is waiting, stop. Record `team_provisioned` only when this run created, renamed, retired, or recorded a new sync reply. A second identical run writes nothing.

## Events

- `team_provisioned`
- `teammate_synced`

## Next

Return to `sync-bot-config`. Tell the human what was created, updated, retired, or waiting on a connector. If nothing changed, say so.
