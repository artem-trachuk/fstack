# fstack design

Skills live only in the git repository `artem-trachuk/fstack`. Bots copy them from that repo. They are not published to Notion Skills.

Feature state and cross-feature memory live in the user's Notion workspace. The Orchestrator is the only role that reads or writes Notion. Coding agents, the verifier, and advisors receive excerpts in the prompts the Orchestrator writes. If Notion is unreachable, the Orchestrator stops, shows the unsaved content, and does not store it anywhere else.

Machine-specific notes stay in gitignored `.fstack/resolved.yaml`: resolved Cursor model slugs, whether the advisor CLI is signed in, and the Notion page and database ids. That file is a cache of ids, not a second copy of the feature.

## Notion schema

Setup searches for an existing project page and these databases before creating anything. The human approves once, in private, before any schema is created. A shared or team space needs its own approval.

Version of the Agent Operating Guide: `0.0.6`, published `2026-10-30`, from [Notion's agent setup guide](https://developers.notion.com/prompts/setup).

### Project page

One private page named for the repository.

- Child page: Agent Operating Guide. It records the workspace, the three database links, preferences, exclusions, and the setup version. Unconfirmed fields stay "Not set up yet".
- Linked databases: Features, Chunks, Memories.

### Features

Each feature is a page in the Features database.

| Property | Type | Use |
| --- | --- | --- |
| Name | title | Human title |
| Slug | text | Feature slug |
| Status | select | A `feature_status` from `state/transitions.yaml` |
| Summary | text | One-line outcome |
| Default branch | text | Stack base |
| Default branch SHA | text | Sha recorded at plan time |
| Waiting on | text | Question id, or empty |
| Release state | select | `approved`, `merging`, `command_failed`, `done` |
| Handoff failures | number | Implementer handoff count |
| Confirmed | date | When the human confirmed the requirements file |
| Chunks | relation | Chunks in this feature |
| Memories | relation | Memories tied to this feature |

The page body has four sections: Requirements, Questions, Plan, Decisions. Child pages, not extra databases, hold prompts, diffs, verification results, advisor inputs, and advisor outputs. Title them `prompt <action> a<attempt>`, `diff <chunk-id> a<attempt>`, `verification <chunk-id> a<attempt>`, `advisor input <n>`, and `advisor output <n>`.

### Chunks

Each chunk is a page in the Chunks database.

| Property | Type | Use |
| --- | --- | --- |
| Name | title | Chunk id, `NN-slug` |
| Feature | relation | Parent feature |
| Depends on | relation | Earlier chunks in the stack |
| Status | select | A chunk status from `state/transitions.yaml` |
| Allowed files | text | Paths or globs |
| Branch | text | `fstack/<feature>/<chunk-id>` |
| Base | text | Parent branch or the default branch |
| Base SHA | text | |
| Head SHA | text | |
| Verified SHA | text | Empty when verification did not pass |
| Pull request | url | |
| Attempt | number | |
| Attempts since decision | number | |
| Accepted unverified | checkbox | Human accepted a `not_implemented` verdict |

The page body has Spec, Acceptance criteria, and Out of scope. The coding agent never opens this page. The Orchestrator copies those sections into the launch prompt.

### Memories

One topic per page. Before creating a Memories database, fetch `notion://docs/memory` and use that guide's property names when they differ from this table.

| Property | Type | Use |
| --- | --- | --- |
| Name | title | One topic |
| Type | select | Decision, Correction, Preference, Convention, Lesson |
| Feature | relation | Empty when the memory is for the whole project |
| Confirmed | date | When the fact was confirmed, not merely when it was saved |
| Source | url | Where it came from |
| Uncertainty | text | What is still unsure |
| Forgotten | checkbox | A forget request |

The body is a few sentences. It is not a transcript, a secret, copied code, or a restatement of the repository.

Search with `notion-memory-search` before creating a page. Update a near-duplicate instead of adding another.

## Notion MCP assumptions

These names come from Notion's setup guide, version 0.0.6. This repo does not ship a Notion MCP server, and the parameter lists were not verified against a live server.

- Every Notion MCP call takes `instructions_version` (`0.0.6`).
- `notion-fetch("notion://docs/memory")` loads the memory rules.
- `notion-memory-search` looks up memories.
- `notion-get-enabled-skills`, `notion-upload-skill`, and `notion-download-skill` exist in the guide for Notion Skills. fstack does not call the upload or download tools. Skill files stay in git.
- `notion-complete-mcp-setup` is for Notion's own skill setup. fstack does not call it.

If a tool is missing or rejects `instructions_version`, stop, show the unsaved content, and tell the human. Do not guess a different API.
