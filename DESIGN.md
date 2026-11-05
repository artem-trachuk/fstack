# fstack design

Grok Bot is the primary host. The human chats with the Orchestrator. It asks with question cards, keeps state in Notion, launches Cursor cloud agents for code, and messages the Verifier and Advisor. The Cursor plugin is a secondary host for the same skills.

Skills live only in the git repository `artem-trachuk/fstack`. Bots copy them from that repo. They are not published to Notion Skills.

Feature state and cross-feature memory live in the user's Notion workspace. The Orchestrator is the only role that reads or writes Notion. Coding agents, the verifier, and advisors receive excerpts in the prompts the Orchestrator writes. If Notion is unreachable, the Orchestrator stops, shows the unsaved content, and does not store it anywhere else.

On Grok Bot, resolved model slugs, the advisor CLI check, and Notion page ids live in the bot's persistent state. On the Cursor plugin they stay in gitignored `.fstack/resolved.yaml`. The repository URL and the last applied skill commit also live in that persistent state, never in the product repository. None of this is a second copy of the feature.

## Notion schema

Setup searches for an existing project page and these databases before creating anything. The human approves once, in private, before any schema is created. A shared or team space needs its own approval.

Version of the Agent Operating Guide: `0.0.6`, published `2026-10-30`, from [Notion's agent setup guide](https://developers.notion.com/prompts/setup).

### Project page

One private page named for the project. A project is the boundary that owns features, workflow config, memory, and sources. It lists zero or more code locations. Each location has a name, a role, an optional subpath, and a default branch. A location may be a repo or a subpath inside a monorepo. The project does not have one base commit or one pull request.

- Child page: Agent Operating Guide. It records the workspace, the database links, preferences, exclusions, and the setup version. Unconfirmed fields stay "Not set up yet".
- Linked databases: Features, Chunks, Memories, Coverage, Codebase maps, and Workflow config.

### Features

Each feature is a page in the Features database.

Property names and types come from `notion_schema.features` and `notion_schema.feature_extra` in `state/transitions.yaml`. Every `feature_fields` entry has one property. The validator checks this table against that map.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Human title. Extra, not a state field |
| Slug | text | `slug` |
| Status | select | `feature_status` |
| Summary | text | Extra |
| Code locations | text | `repos`. Names of the locations this feature spans |
| Base SHAs | text | `base_shas`. Map of location name to pinned commit |
| Release mode | select | `release_mode`. `all_or_none` or `per_repo` |
| Release order | text | `release_order`. Location names. Empty uses the project list |
| Waiting on | text | `waiting_on` |
| Release state | select | `release_state` |
| Release approval | text | `release_approval` |
| Review approval | text | `review_approval` |
| State version | text | `state_version` |
| Lease | text | `lease` |
| Handoff failures | number | `handoff_failures` |
| Requirements status | select | `requirements_status` |
| Config version | text | `config_version`. The workflow config version this feature used |
| Step bindings | text | `step_bindings`. Slot, skill, and whether the binding came from the feature, the project, or the repo |
| Confirmed | date | Extra. When the human confirmed the requirements page |
| Chunks | relation | Extra |
| Memories | relation | Extra |
| Existing functionality | relation | Extra. The Codebase maps page for this feature's base SHA |

The page body has four sections: Requirements, Questions, Plan, Decisions. Child pages, not extra databases, hold prompts, diffs, verification results, advisor inputs, and advisor outputs. Title them `prompt <action> a<attempt>`, `diff <chunk-id> a<attempt>`, `verification <chunk-id> a<attempt>`, `advisor input <n>`, and `advisor output <n>`.

### Chunks

Each chunk is a page in the Chunks database.

Property names and types come from `notion_schema.chunks` and `notion_schema.chunk_extra`. Every `chunk_fields` entry has one property.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | `id`, the chunk id `NN-slug` |
| Title | text | `title` |
| Code location | text | `repo`. Exactly one. The chunk's branch and pull request are in this location |
| Feature | relation | Extra. Parent feature |
| Depends on | relation | `depends_on` |
| Status | select | `status` |
| Allowed files | text | `allowed_files` |
| Branch | text | `branch` |
| Base | text | `base` |
| Base SHA | text | `base_sha` |
| Head SHA | text | `head_sha` |
| Verified SHA | text | `verified_sha`. Empty unless the chunk is verified |
| Accepted SHA | text | `accepted_sha`. Set only by `accept_unverified`. This is the sha release may merge |
| Pull request | url | `pr` |
| Attempt | number | `attempt` |
| Attempts since decision | number | `attempts_since_decision` |
| Agent | text | `agent_id` |
| Launched at | text | `launched_at` |
| Verifier | text | `verifier_agent_id` |
| Needs restack | checkbox | `needs_restack` |
| Needs reverify | checkbox | `needs_reverify` |
| Marked for review | checkbox | `marked_for_review` |
| Tie-break attempt | number | `tiebreak_for_attempt` |
| Blocked reason | text | `blocked_reason` |
| Bound skill | text | `bound_skill`. The skill this chunk step actually ran |
| Accepted unverified | checkbox | Extra. Human accepted a `not_implemented` verdict |

The page body has Spec, Acceptance criteria, and Out of scope. The coding agent never opens this page. The Orchestrator copies those sections into the launch prompt.

### Codebase maps

One page per code location and commit, shared by later calls. The title starts with `Existing functionality` and the location name. The page records the location name and the commit. The body is the survey: features and screens, routes and APIs, the data model, and flags, each with a file and a line. The read is read-only. The survey skill does not prescribe how the read runs. Only the caller that owns the page writes it.

### Coverage

One page per item, in the Coverage database. Property names come from `notion_schema.coverage` and `notion_schema.coverage_extra`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | `item` |
| Feature | relation | Extra. The feature this row belongs to |
| Code location | text | `repo`. The location this evidence came from. Empty only when the row is not about code |
| Commit | text | `commit`. The pinned commit for that location, or empty when that location was not surveyed |
| Presences | text | `presences`. One entry per source kind that was compared: present, partial, or absent, plus evidence |
| Classification | select | `classification`. done, partial, missing, needs_decision, conflict, undocumented |
| Next action | select | `next_action`. plan, question, or none |
| Decision | select | `decision`. pending, implement, write_back, skip, defer, approved, or dropped |
| Write-back | text | `write_back`. Proposed text for a source writer. Empty until a human asks for one |
| Approved | checkbox | `approved`. Set only by the coverage gate |

A chunk is planned only from an approved buildable row, `partial` or `missing`. `needs_decision`, `conflict`, and `undocumented` are not planned unless the human chose implement and the gate then approved that row. Writing the decision back to a source uses that source's writer, and only after approval.

### Workflow config

One database per project. setup-project creates it and seeds it from `workflow`, `sources`, and `authoritative_kinds` in `fstack.yaml`. Human gates and the rule that only the Orchestrator writes Notion are not fields on this database. They stay in the repo.

Property names come from `notion_schema.workflow` and `notion_schema.workflow_extra`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra. Project page, slot name, or change entry |
| Scope | select | `scope`. `project`, `feature`, or `change` |
| Feature | relation | Extra. Set on a feature override or a feature change. Empty for the project |
| Config version | text | `config_version`. Increases by one on each accepted change |
| Slot | text | `slot`. Empty on the project page and on a change row |
| Skill | text | `skill`. The skill name bound to that slot |
| Params | text | `params`. Optional parameters, such as `{env: staging}` |
| Notes | text | `notes` |
| Skip | checkbox | `skip`. A feature override may set this only when the repo slot is skippable |
| Who | text | `who`. The human who asked for the change |
| When | date | `when` |
| Old | text | `old` |
| New | text | `new` |

The project page body holds code locations, sources, authoritative kinds, release policy, and standing preferences. A preference may override `plan_review` or `notify`. It must not override human gates or who writes Notion.

A feature override is a page with Scope `feature` and only the slots that differ. Precedence is feature override, then the project page, then `fstack.yaml`.

A change row records who, when, old, and new. The Orchestrator writes it in the same turn as the binding change.

The shipped verify slot binds the skill `verify`.

### Memories

One topic per page in the project Memories database. These are project records, not the user's personal Notion memory.

Notion's built-in memory is a different database. Its types are Profile, Preference, Work, People, and Notes, and it follows the user across every agent. fstack memories are scoped to one project, point at a feature, and use Decision, Correction, Preference, Convention, and Lesson. Do not call `notion-memory-search` for fstack. Do not create fstack pages with parent `memory`.

Fetch the project database, read its `collection://` URL, and query it with `notion-query-data-sources`. Update a near-duplicate instead of adding another.

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

## Notion MCP

These names were checked against the live Notion MCP. Docs and skills use them with no prefix.

- `notion-fetch`, including `notion://docs/memory` and `notion://docs/notion-flavored-markdown-spec`. Read the markdown spec before `notion-create-pages` or `notion-update-page`. The docs URI without `-spec` returns 400.
- `notion-search` to find existing pages and databases.
- `notion-query-data-sources` to read the project Memories database.
- `notion-create-pages` and `notion-update-page` to write pages.
- `notion-create-database` to create a database from SQL `CREATE TABLE` or a typed database definition.
- `notion-get-setup-guide` during setup.
- `instructions_version` (`0.0.6`) is a parameter on every Notion tool fstack calls.

`notion-complete-mcp-setup` exists and is for Notion's own skill setup. fstack does not call it. Skill files stay in git.

Do not call `notion-memory-search` for project memories. If a Notion call fails, stop and show the unsaved content. Do not guess a different tool name.

## Bots

Grok Bot is the primary host. `bots/<role>.yaml` is the config. Version `0.1`. The repository stays the source of the skill files. A bot runs `sync-bot-config` on demand and on the cron in its config. It compares the default-branch commit with the repository URL and applied commit in its own persistent state, then copies skills into its library as `<slug>/SKILL.md` folders, updates its profile, and adds, updates, or removes routines. That pair is not written into the product repository. It asks before adding a connector.

The Orchestrator reads sources through whatever reader the project config names. It messages teammates by the profile `name` in their config. The handoff text starts with `fstack-handoff`. The reply starts with `fstack-reply`. The Verifier answers `ask: verdict`. The Advisor answers `ask: critique`. Neither has Notion or GitHub connectors.

A pull-request routine on the Orchestrator listens for opened, pushed, merged, and commented events on `fstack/` branches. The yaml key is quoted `"on"` because an unquoted `on` is a YAML boolean. The public routine docs confirm GitHub events and that the schedule uses Settings, Bot, Timezone. They do not publish the event payload fields, so the bot maps those four words onto the host trigger.

Bootstrap is the Install section of the README: create the bot, paste the persona and instructions, then send one message that names `sync-bot-config` and the yaml file.
