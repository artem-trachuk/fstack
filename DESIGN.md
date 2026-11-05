# fstack design

Grok Bot is the primary host. The human chats with the Orchestrator. It asks with question cards, keeps state in Notion, launches Cursor cloud agents for code, and messages the Verifier. An advisor is a separate read-only Cursor cloud agent, not a teammate. The Cursor plugin is a secondary host for the same skills.

This is the one deviation from Notion's official agent setup. The git repository named by the `repository` field in `plugin.json` is the single source of skill files, and bots copy them from that repo. Skills are not saved as Notion Skills, even when the human picks the Shared context layer, which covers memory and artifacts only. The Agent Operating Guide lists that repository, with its link, under Skills, and adds this line under User preferences and exclusions: Skills are kept in GitHub only. Do not save them to Notion Skills.

Feature state and cross-feature memory live in the user's Notion workspace. The Orchestrator is the only role that reads or writes Notion. Coding agents, the verifier, and advisors receive excerpts in the prompts the Orchestrator writes. If Notion is unreachable, the Orchestrator stops, shows the unsaved content, and does not store it anywhere else.

On Grok Bot, resolved model slugs, the advisor CLI check, and Notion page ids live in the bot's persistent state. On the Cursor plugin they stay in gitignored `.fstack/resolved.yaml`. The repository URL and the last applied skill commit also live in that persistent state, never in the product repository. None of this is a second copy of the feature.

## Notion schema

Setup searches for an existing product page and these databases before creating anything. The human approves once, in private, before any schema is created. A shared or team space needs its own approval.

Version of the Agent Operating Guide: `0.0.6`, published `2026-10-30`, from [Notion's agent setup guide](https://developers.notion.com/prompts/setup).

### Product page

One private page named for the product. A product owns features, the workflow config, sources, and zero or more repos. Preferences and lessons live in Notion Memory, not in a database this product creates. Each repo is a code location with a name, a role, an optional subpath, and a default branch. The product does not have one base commit or one pull request. Features, chunks, coverage rows, and workflow pages point back with a Product relation.

- The Agent Operating Guide is the user's private page in a Documents database. Setup keeps an existing guide and suggests additions. A new guide uses version `0.0.6`, published `2026-10-30`, and the official sections. That `0.0.6` is Notion's setup guide, not the fstack version. `upgrade-fstack` appends the fstack version and commit to Version history and does not change `0.0.6`. fstack records its product home and databases under destinations only after the human approves those additions. Skills records the repository from `plugin.json`. Other unconfirmed fields stay "Not set up yet".
- Linked databases: Features, Chunks, Coverage, Graph nodes, Graph edges, Workflow config, Survey, Decision, Verification, Debug log, and Fixes. Do not create a Memories database.

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
| Release order | text | `release_order`. Location names. Empty uses the product list |
| Waiting on | text | `waiting_on` |
| Release state | select | `release_state` |
| Release approval | text | `release_approval` |
| Review approval | text | `review_approval` |
| State version | text | `state_version` |
| Lease | text | `lease` |
| Handoff failures | number | `handoff_failures` |
| Requirements status | select | `requirements_status` |
| Config version | text | `config_version`. The workflow config version this feature used |
| Step bindings | text | `step_bindings`. Slot, skill, and whether the binding came from the feature, the product, or the repo |
| Nodes read | relation | `nodes_read`. Graph nodes this feature read |
| Nodes added | relation | `nodes_added`. Graph nodes this feature proposes to add |
| Nodes changed | relation | `nodes_changed`. Graph nodes this feature proposes to change |
| Nodes removed | relation | `nodes_removed`. Graph nodes this feature proposes to remove |
| Confirmed | date | Extra. When the human confirmed the requirements page |
| Chunks | relation | Extra |
| Product | relation | Extra. The product this feature belongs to |

The page title and description stay about the feature. A bug is not a new feature and does not rename this page. The page body has three transient sections: Requirements, Questions, and Plan. Decisions are their own pages, related to the feature and the product. The feature page links to those pages and does not copy the entries into its body. Durable product facts are graph nodes, not sections of this page. The feature stores node relations only. Child pages hold prompts and diffs. Verification is its own page, related to the chunk. Title prompt and diff pages `prompt <action> a<attempt>` and `diff <chunk-id> a<attempt>`. Title a verification page `verification <chunk-id> a<attempt>`. The Orchestrator creates that verification page when the verifier reply arrives.

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
| Touched nodes | relation | `nodes`. Graph nodes this chunk touches |
| Accepted unverified | checkbox | Extra. Human accepted a `not_implemented` verdict |
| Product | relation | Extra. The product this chunk belongs to |

The page body has Spec, Acceptance criteria, and Out of scope. The coding agent never opens this page. The Orchestrator copies those sections into the launch prompt.

### Graph nodes

The product graph is the accumulating record of how the product works. One page per durable fact. Kinds are configured on the product workflow page. The shipped kinds are capability, component, entity, interface, requirement, decision, and constraint. A product may add kinds. Property names come from `notion_schema.graph_nodes`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra. One topic |
| Kind | text | `kind` |
| Status | select | `status`. `active`, `stale`, `superseded`, or `contradicted` |
| Evidence | text | `evidence`. Location, path, and commit |
| Provenance | text | `provenance`. The survey or the feature that last wrote the node |
| Last verified | text | `last_verified`. Map of location name to commit |
| Product | relation | Extra |

### Graph edges

One page per typed link. Shipped kinds are depends_on, implements, part_of, touches, constrains, supersedes, and conflicts_with. Property names come from `notion_schema.graph_edges`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra |
| Kind | text | `kind` |
| From | relation | `from_node` |
| To | relation | `to_node` |
| Product | relation | Extra |

Survey creates and refreshes nodes. A feature does not copy those facts onto its own page. `update-graph` promotes a merged feature's delta after approval when `graph.promote` is `require_approval`.

### Survey

One page per survey of one code location. It is the record of the read, not a copy of the facts. Facts stay on the graph nodes.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra |
| Commit | text | `commit` |
| Product | relation | Extra. Required |
| Feature | relation | Extra. Set when a feature asked for the survey |
| Nodes | relation | Extra. Required. Nodes this survey created or refreshed |

### Decision

One page per decision. The feature page links to it. The page is not only a heading in the feature body.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra |
| Summary | text | `summary` |
| Product | relation | Extra. Required |
| Feature | relation | Extra. Required |

### Verification

One page per verification result.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra |
| Verdict | text | `verdict` |
| Product | relation | Extra. Required |
| Feature | relation | Extra |
| Chunk | relation | Extra. Required |

### Coverage

One page per item, in the Coverage database. Property names come from `notion_schema.coverage` and `notion_schema.coverage_extra`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | `item` |
| Feature | relation | Extra. The feature this row belongs to |
| Product | relation | Extra. The product this row belongs to |
| Code location | text | `repo`. The location this evidence came from. Empty only when the row is not about code |
| Commit | text | `commit`. The node's last-verified commit for that location |
| Node | relation | `node`. The graph node this row is about |
| Presences | text | `presences`. One entry per source kind that was compared: present, partial, or absent, plus evidence |
| Classification | select | `classification`. done, partial, missing, needs_decision, conflict, undocumented |
| Next action | select | `next_action`. plan, question, or none |
| Decision | select | `decision`. pending, implement, write_back, skip, defer, approved, or dropped |
| Write-back | text | `write_back`. Proposed text for a source writer. Empty until a human asks for one |
| Approved | checkbox | `approved`. Set only by the coverage gate |

A chunk is planned only from an approved buildable row, `partial` or `missing`. `needs_decision`, `conflict`, and `undocumented` are not planned unless the human chose implement and the gate then approved that row. Writing the decision back to a source uses that source's writer, and only after approval.

### Fixes

A bug or a regression is a page in the Fixes database, related to the existing feature. Property names come from `notion_schema.fix` and `notion_schema.fix_extra`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | The broken behaviour. Extra |
| Expected | text | `expected`. What the feature should do |
| Actual | text | `actual`. What it does instead |
| Reproduce | text | `reproduce`. How to see the failure |
| Severity | text | `severity` |
| Product | relation | Extra. Required |
| Feature | relation | Extra. Required. Every feature this fix belongs to |
| Nodes | relation | Extra. Empty until the graph match is known |
| Chunks | relation | Extra. Empty until the plan exists |
| Verification | relation | Extra. Empty until a verification page exists |

A fix may span features and repos. Each chunk still names one repo. `fstack-status` treats a Fix page with an empty Product or Feature relation as unlinked.

### Workflow config

One database per product. setup-product creates it and seeds it from `workflow`, `sources`, and `authoritative_kinds` in `fstack.yaml`. Human gates and the rule that only the Orchestrator writes Notion are not fields on this database. They stay in the repo.

Property names come from `notion_schema.workflow` and `notion_schema.workflow_extra`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra. Product page, slot name, or change entry |
| Scope | select | `scope`. `product`, `feature`, or `change` |
| Feature | relation | Extra. Set on a feature override or a feature change. Empty for the product |
| Product | relation | Extra. The product this workflow page belongs to |
| Config version | text | `config_version`. Increases by one on each accepted change |
| Slot | text | `slot`. Empty on the product page and on a change row |
| Skill | text | `skill`. The skill name bound to that slot |
| Params | text | `params`. Optional parameters, such as `{env: staging}` |
| Notes | text | `notes` |
| Skip | checkbox | `skip`. A feature override may set this only when the repo slot is skippable |
| Who | text | `who`. The human who asked for the change |
| When | date | `when` |
| Old | text | `old` |
| New | text | `new` |

The product page body holds code locations, sources, authoritative kinds, release policy, graph kind lists, `graph.promote`, `debug`, `autonomy`, and standing preferences. A preference may override `plan_review`, `notify`, `graph.promote`, `debug`, or `autonomy`. It must not override human gates or who writes Notion. `autonomy` ships as `auto`. The Orchestrator decides a fix approach, a design, and a chunk split, after the configured advisors rank a non-trivial choice. Any work item, `new_feature` or `fix`, defaults to one chunk per repo. A split happens only when size, independent risk, multiple repos, or a staged rollout clearly helps. Notion Memory holds preferences and lessons. The graph holds product facts. Do not store the same fact in both.

### Debug log

One log per product. The first page is titled Debug log. Entries are appended in order under a heading for each session. When the page is too large, add a continuation page and set its Previous relation to the page it continues. Property names come from `notion_schema.debug_log`.

| Property | Type | Field |
| --- | --- | --- |
| Name | title | Extra |
| Opened | date | `opened` |
| Product | relation | Extra. Required |
| Previous | relation | Extra. Empty on the first page |

Only the Orchestrator appends. Teammates and implementers return trace entries in their replies. When `debug` is off, the page is not written. A secret, token, or credential value is stored as the word redacted. The log holds references and short summaries, not file bodies or full prompts.

A feature override is a page with Scope `feature` and only the slots that differ. Precedence is feature override, then the product page, then `fstack.yaml`.

A change row records who, when, old, and new. The Orchestrator writes it in the same turn as the binding change.

The shipped verify slot binds the skill `verify`.

### Notion Memory

Preferences and lessons use Notion Memory. Fetch with id `"memory"` returns the About page and the built-in Memories database. Do not create a Memories database. Do not add Product, Source, Uncertainty, Forgotten, or Confirmed to it.

Recall fetches id `"memory"` first, then calls `notion-memory-search`. When the About page and a memory disagree, trust the more recent, more specific one. Link a memory inline when it informs an answer.

A save uses `notion-create-pages` with `parent: "memory"`, no creation_mode, and Type set to exactly one of Profile, Preference, Work, People, or Notes. Search first and update the existing topic. A product decision or lesson is Type Work. The body names the product and links the product or feature page. Working style is Type Preference. Title the topic, not the fact. The body is short standalone sentences, refers to the human by name, says why and when it applies, and marks an untested idea as untested. A full date is a Notion date mention.

The About page stays under about 300 words, with the sections Role, Current work, and Working preferences. Edit it when the overall picture changes, and keep what the human wrote.

To list or audit, fetch id `"memory"` for the data source URL, then run `notion-query-data-sources` in SQL mode and page through the results. To forget, delete a page that is entirely about the topic with `notion-delete-pages`, or remove only that information. Remove it from the About page too. Leave no note that restates it.

A feature page mentions the memory in its body. Memory pages are not in `required_relations`.

Do not save temporary progress, copied code, a repository fact, a guess, generic advice, a secret, a transcript, or instructions for agents. A reusable procedure belongs in a skill. Product facts belong in the product graph.

## Links

Pages are separate. They stay connected. `required_relations` in `state/transitions.yaml` names the relation each page type must set. The product page is the root. Every other fstack page is reachable from it by those relations. A feature page relates to its chunks and to the graph nodes it read, added, changed, or removed. A chunk relates to that feature and to the nodes it touches. A survey page relates to the product and to the nodes it refreshed. Coverage relates to its feature and its node. A decision relates to its feature. A verification relates to its chunk. A fix relates to its product and its feature. Notion Memory is linked from a feature page by a mention in the body, not by a required relation. An empty required relation is an unlinked page. A page that no path from the product page reaches is an orphan. `fstack-status` reports both when asked. It does not delete them, and it does not report a memory as unlinked.

## Notion MCP

These names were checked against the live Notion MCP. Docs and skills use them with no prefix.

- `notion-fetch`, including id `"memory"`, `notion://docs/memory`, and `notion://docs/notion-flavored-markdown-spec`. Read the markdown spec before `notion-create-pages` or `notion-update-page`. The docs URI without `-spec` returns 400.
- `notion-memory-search` after that fetch, for a specific memory.
- `notion-search` to find existing pages and databases.
- `notion-query-data-sources` in SQL mode to list Notion Memory. Page through the results.
- `notion-create-pages` with `parent: "memory"` and no creation_mode for a memory. Type is exactly one of Profile, Preference, Work, People, or Notes. Other fstack pages are not created with that parent.
- `notion-update-page` to edit a page and keep unrelated content.
- `notion-delete-pages` when a memory is entirely about a forgotten topic.
- `notion-create-database` to create a database from SQL `CREATE TABLE` or a typed database definition.
- `notion-get-setup-guide` during setup.
- `instructions_version` (`0.0.6`) is a parameter on every Notion tool fstack calls.

If a Notion call fails, stop and show the unsaved content. Do not guess a different tool name.

## Bots

Grok Bot is the primary host. `bots/<role>.yaml` is the config. Version `0.1`. The repository stays the source of the skill files. A bot runs `sync-bot-config` on demand and on the cron in its config. It compares the default-branch commit with the repository URL and applied commit in its own persistent state, then copies skills into its library as `<slug>/SKILL.md` folders, updates its profile, and adds, updates, or removes routines. That pair is not written into the product repository. It asks before adding a connector.

The Orchestrator reads repositories through the GitHub connector and does not clone. It messages the Verifier by the profile `name` in its config. The handoff text starts with `fstack-handoff`. The reply starts with `fstack-reply`. The Verifier answers `ask: verdict`. An advisor is a Cursor cloud agent launched with the model id from `fstack.yaml`. Opus runs first. Argon runs only when that critique leaves the decision unclear. The Advisor calls page stores the agent id, the `cursor.com` URL, the model id, and the raw critique. A critique the Orchestrator wrote itself is invalid. The Verifier has one read-only repo reader so sync can copy skills, or sync fetches the public default branch when that reader is absent. It does not write Notion and it does not open pull requests.

A pull-request routine on the Orchestrator listens for opened, pushed, merged, and commented events on `fstack/` branches. The yaml key is quoted `"on"` because an unquoted `on` is a YAML boolean. The public routine docs confirm GitHub events and that the schedule uses Settings, Bot, Timezone. They do not publish the event payload fields, so the bot maps those four words onto the host trigger.

Bootstrap is the Install section of the README: create the bot, paste the persona and instructions, then send one message that names `sync-bot-config` and the yaml file.
