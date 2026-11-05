# fstack

fstack is a way to deliver one software feature with a small team of bots. You chat with the Orchestrator. It keeps the feature in Notion, asks you with question cards, and launches a Cursor cloud agent for each chunk. The Verifier is a teammate it messages. An advisor is a separate read-only Cursor cloud agent. You review the stacked pull requests once, then approve release.

The name is short for feature stack. Statuses and transitions live in [`state/transitions.yaml`](state/transitions.yaml). Skills follow that table. There is no command-line runner. Grok Bot is the host these skills are written for. A Cursor plugin install is a secondary option at the end of this file.

## Install

Create three bots from the configs in [`bots/`](bots/) and connect Notion and GitHub on the account that will run them.

1. In Grok Bot, choose New Bot. Name it **Fstack Orchestrator**. In the first message, paste the persona and instructions from [`bots/orchestrator.yaml`](bots/orchestrator.yaml) and ask it to remember them.
2. Tell that bot: "Follow the sync-bot-config skill. The config file is bots/orchestrator.yaml." It copies the skills from this repository, sets its profile, and saves its routines. The first run is the bootstrap. The weekly routine keeps it current.
3. Do not create the Verifier yourself. The Orchestrator provisions it. An advisor is not a bot.
4. Connect Notion and the repo reader when the Orchestrator shows a connect card. Other inputs are sources in the product config: a kind plus a reader. Ask the Orchestrator to install fstack. It provisions the other bots. Their feature inputs still arrive as messages. Each teammate syncs through a read-only repo reader, or by a public fetch of the skill repository when that reader is absent.
5. Schedules use the timezone in Grok Bot settings under Bot. The five cron fields do not name a zone.

## Quick start

Chat with the Orchestrator. Do not start a feature from another bot.

1. Ask it to set up a product. A product is a Notion boundary, not one code location. Name zero or more locations, each with a role and a default branch. `fstack.yaml` can live in any one of them, or only in Notion. You approve the product page and databases before any schema is created.
2. Ask it to start a feature and describe what you want. That request is the only way requirements collection starts. A bug is a fix on an existing feature, not a new feature page. Confirm the requirements page when the question card asks.
3. When the feature lists code locations, `survey-product` reads the product graph first. It re-surveys only nodes whose evidence is stale for that location's current commit, and areas the graph does not cover. The first survey seeds the graph. The read is read-only. With no locations, this step is skipped.
4. Gap analysis compares the sources that are present against the graph, not against a fresh read of the code. Coverage rows point at node ids. A source is a kind, such as requirements, design, or the current product, plus whatever reader the host has. You answer one card for conflicts, items that are not backed by an authoritative source, and behaviour a location has with no requirement. The choices are implement, write back to a source, skip, or defer. A write happens only after you approve it, and only if that source has a writer.
5. Clear partial and missing rows become chunks, one per location. A simple feature, update, or fix is one chunk per repo and goes straight to implementation. A split happens only when size, independent risk, multiple repos, or a staged rollout clearly helps. Stacks do not cross locations. A plan question is only for that multi-chunk case when `autonomy` is `ask_more`. Release is per location, then the feature follows `release_policy`: `all_or_none` or `per_repo`.
6. For each chunk it launches one Cursor cloud agent, stacked on the previous branch. When the run finishes, the Orchestrator is revived with the branch, the pull request, and the report. It messages the Verifier. Verification is a stub, so you get a card: accept the chunk unverified, or stop. That choice is saved in Notion. The stack does not continue until you answer.
7. Review the stacked pull requests when the card asks. That card does not approve release.
8. Answer the later release card. The stack is merged only after you approve the effect and the shas that card names.
9. After the merge, `update-graph` proposes the feature's confirmed changes as graph updates. You approve that promotion when `graph.promote` is `require_approval`. A stopped feature is not promoted. Lessons go to memory, not into the graph. Then it can start the next feature, and only when you ask.

A later chat with the same Orchestrator resumes from Notion. Ask where the feature stands.

## Cursor plugin

Grok Bot does not read the Cursor rule files. The skills are the instructions on the primary path. The files under `rules/` are a secondary Cursor install only, and `alwaysApply` is false so they do not attach to unrelated chats.

The Cursor manifest is `.cursor-plugin/plugin.json`. The root `plugin.json` is the Agent Plugins manifest. To try the same skills inside Cursor, copy this repository to `~/.cursor/plugins/local/fstack`, reload the window, and confirm the skills in Customize. A team marketplace install is a separate step. Cursor skips a symlink that points outside that folder, so copy the files.

In Cursor, asking in chat is still how a feature starts. A slash command is only one way to ask.

## Flow

```mermaid
flowchart TD
  human([Human])
  collect[collect-requirements]
  survey[survey-product]
  gap[gap-analysis]
  questions[Coverage card]
  split[split-into-chunks]
  pick[pick-next-task]
  implement[implement-chunk]
  coding[Cursor coding agent]
  verify[verify]
  review[review-stack]
  release[release]
  graph[update-graph]
  done([Next feature])

  human -->|asks in chat| collect
  collect --> survey
  survey --> gap
  gap --> questions
  questions --> human
  human -->|approves rows| split
  split --> pick
  pick --> implement
  implement --> coding
  coding -->|stacked pull request| verify
  verify -->|not_implemented| human
  human -->|accept unverified or stop| pick
  pick -->|every chunk accepted or verified| review
  review -->|changes on one chunk| pick
  review -->|review done, next turn| release
  release -->|Approve release?| human
  human -->|explicit approval| graph
  graph -->|promote the delta| done
```

`build-context` writes a Notion child page named `prompt verify a<attempt>` on the chunk before `verify` is called. The skill does not use that page to judge the chunk. It returns `verdict: not_implemented` and the message `Verification is not implemented yet, so these changes cannot be verified.` The orchestrator sends that sentence through `tldr` and leaves the chunk in `awaiting_verification_decision`. `accept_unverified` is logged and is not a pass. `stop` ends the feature and leaves pull requests open.

The prompt shape the stub will someday use is unchanged: the orchestrator builds it from `git diff <base_sha>...<head_sha>`, with the spec, the acceptance criteria, the out-of-scope section, and the patch. It does not include a Notion workspace link, a pull request URL, or implementer notes. The intended verifier runs in a clean checkout of that head. That design is the TODO in the `verify` skill and in [stubs/enforcement.md](stubs/enforcement.md).

`tldr` rewrites messages to the human. Question ids, options, the release command, shas, and pull request URLs stay verbatim.

`planner_review` critiques gap analysis and the chunk split. `verify_tiebreak` is reserved for a future disputed verdict. The stub never asks for it, because it does not judge the chunk. Both are read-only Cursor cloud agents. Opus runs first. Argon runs only when the decision is still unclear. A feature allows six advisor calls, and two of those are reserved for the tie-break. The tie-break is advice. The orchestrator decides or escalates. A critique needs an agent id or a CLI run record, and file citations.

## Configuration

`fstack.yaml` is the repo default for one product. It may sit in any one code location, or the product may keep that default only in Notion. Paths inside it are relative to the location that holds the file. Resolved model slugs are written to `.fstack/resolved.yaml` in a checkout that has the file, and that folder is gitignored.

| Key | Shipped value | Meaning |
| --- | --- | --- |
| `state.backend` | `notion` | Feature records live in the user's Notion workspace |
| `memory.backend` | `notion` | Notion Memory. Lessons are Type Work. Working style is Type Preference |
| `memory.instructions_version` | `0.0.6` | Sent on every Notion MCP call |
| `plan_review` | `notify` | Show a multi-chunk plan and continue. `approve` waits only when `autonomy` is `ask_more` |
| `autonomy` | `auto` | Decide and continue. `ask_more` adds check-ins. Human gates stay on |
| `workflow.slots.advise` | `advisors` | On for a non-trivial choice. The configured advisors rank the options |
| `review.mode` | `end_of_stack` | One human review for the stack, then one release question |
| `verify.max_failures_before_escalation` | `2` | Counted with `attempts_since_decision`, using `>=` |
| `release.command` | empty | An approved release merges the stack and stops |
| `authoritative_kinds` | `requirements` | Source kinds that can make an item buildable |
| `sources` | kind, ref, reader | Inputs. `ref` and `reader` are how this host reads that kind. `writer` is optional |
| `workflow.slots` | skill per slot | Repo default. A Notion product page overrides it, and a feature page overrides the product |
| `workflow.slots.fix` | `file-fix` | A bug stays on the existing feature. Same override order as the other slots |
| `debug` | `false` | Trace in the product Debug log. A product page or a feature override may turn it on |

`setup-product` creates a Workflow config database and seeds it from those repo defaults. At session start the Orchestrator reads the feature override, then the product page, then `fstack.yaml`, and records the binding and config version it used. You can say "use skill X for verification" or "for this feature only, skip survey". It checks that the skill is in the library and that its contract matches the slot, confirms in one line, and writes a change log entry. Human gates stay in the repo. The verify slot ships bound to `verify`.

`models.opus` and `models.argon` are match prefixes and an effort list, in preference order. setup walks that list against the slugs this Cursor session can use. A missing family becomes `inherit`, the parent Cursor model.

The advisor block keeps the original fields and adds a fallback:

```yaml
advisors:
  planner_review:
    model: opus        # e.g. Claude Opus 5.5 in Cursor
    when: [gap-analysis, split-into-chunks]
  verify_tiebreak:
    model: argon       # Gemini 4 Argon in Cursor
    when: [verifier-disputed]
    fallback: [opus]
    must_differ_from: verifier
  max_calls_per_feature: 6
  reserve:
    verify_tiebreak: 2
  fallback:
    - runtime: claude-cli
      command: claude
      model: opus
      enabled: true
```

`verify_tiebreak.fallback` is another Cursor model to try inside Cursor. `advisors.fallback` is a local CLI used only when Cursor cannot start Opus, for example when the account has no credits for that model. The shipped entry is the Claude Code CLI. There is no Argon CLI. setup checks that `claude` is on `PATH` and signed in, and it does not read or print tokens. A local CLI runs under the user's own subscription terms. A teammate bot is never the advisor.

If the tie-break would use the same model as the verifier, including when both are `inherit`, the orchestrator skips it and asks the human. That independence rule is not a credit failure, so it does not switch to the local CLI.

Human gates stay fixed: merge, release, and outward messages `require_approval`, and `collect_requirements` `manual_only`. setup stops when a config weakens them. Only a human quote of yes, approve, or approved counts, and only for the question id that was asked.

Roles name an agent and a model. They do not list skills. The agent file is the skill list. Whoever launches a coding agent, verifier, or advisor passes the model from `.fstack/resolved.yaml`.

`implementer.runtime` ships as `cloud`. setup sets `local_worktree` in the resolved file when this session cannot start a cloud agent that opens a pull request onto a non-default base. The implementer still gets the chunk spec in the launch prompt.

## Where state lives

`state.backend` and `memory.backend` are `notion`. The schema is in [DESIGN.md](DESIGN.md): a private product page, the user's Agent Operating Guide at version `0.0.6`, and Features, Chunks, Coverage, Graph nodes, Graph edges, and Workflow config. The graph holds durable product facts. Preferences and lessons use Notion Memory, fetched with id `"memory"`. fstack does not create a Memories database. A feature page holds links to Decision pages, the plan, and status, and mentions related memories. Coverage rows point at graph nodes. Skills stay in the git repository named by `plugin.json`. They are not saved as Notion Skills.

The Orchestrator is the only role that calls Notion. It copies the chunk spec into the coding agent's launch prompt, passes the verifier its prompt and patch, and passes advisors their input pages' text. Asking the Orchestrator where the feature stands reads the Features database.

On the Cursor plugin, gitignored `.fstack/resolved.yaml` holds resolved model slugs and Notion ids. On Grok Bot those same notes live in the bot's persistent state, because the bot does not clone the product repository. Neither place holds the sync commit, and neither is a copy of the feature. If Notion is unreachable, the Orchestrator stops and shows the unsaved content. It does not write that content to disk.

The skill files stay in this git repository. They are not uploaded to Notion Skills.

Pull requests are still the code handoff: a branch and a short description of the change. They do not carry fstack's notes, prompts, or critiques.

## Workspace

The Notion databases above hold the feature. They are not a git branch.

A chunk id is `NN-slug`. Status values and the events that change them are only those in [`state/transitions.yaml`](state/transitions.yaml).

## Skills

| Skill | Who invokes it | What it does |
| --- | --- | --- |
| `setup-product` | Human, or the orchestrator when config is missing | Copies templates, resolves models, creates Workflow config |
| `upgrade-fstack` | Human says update, upgrade, or sync fstack | Brings the install up to main and records the fstack version |
| `configure-workflow` | Session start, or the human in chat | Shows the effective bindings and writes an approved change |
| `collect-requirements` | Human, only after an explicit chat request | Classifies `new_feature` or `fix`. A fix does not create a feature page |
| `file-fix` | The `fix` slot, after that classification | Files a Fix page under the existing feature |
| `survey-product` | On its own, or once per code location | Read-only description of that location at a pinned commit |
| `gap-analysis` | On its own, or after the survey | Compares the sources that are present and classifies each item |
| `split-into-chunks` | On its own with approved rows, or after the coverage gate | Plans only approved partial and missing rows |
| `pick-next-task` | Orchestrator | Applies the next-rule list once |
| `implement-chunk` | Orchestrator | Hands off one chunk and records the agent id first |
| `verify` | Verifier, at the same point in the flow | Returns `not_implemented` and does not judge the chunk |
| `build-context` | Orchestrator, before an action | Writes the prompt onto a Notion page |
| `tldr` | Before a human-facing message | Short prose, verbatim decisions |
| `advisors` | Gap analysis, split, one dispute per attempt | Read-only Cursor cloud agent. Opus first, Argon only if still unclear |
| `escalate` | Orchestrator | Stops for retry, accept, a spec change, or stop |
| `review-stack` | Orchestrator, after every chunk is verified | Asks for review and waits |
| `release` | Orchestrator, after review | Asks, then merges only the approved shas, then proposes memories |
| `update-graph` | After merge, unless the feature stopped | Promotes confirmed changes into the product graph |
| `fstack-status` | Human or a fresh session | Reads Notion, routes a reply, and reports orphaned or unlinked pages when asked |
| `memory` | Orchestrator | Reads and writes Notion Memory. Does not publish skills |

## What is not enforced yet

[stubs/enforcement.md](stubs/enforcement.md) describes verification, the approval record, the merge and release steps, and a shell hook that should refuse a merge without a matching approval. None of that runs. `verify` returns `not_implemented`. The release skill is the procedure the orchestrator follows by hand. `hooks.json` is absent so a stub is not loaded as if it enforced the gate.

## Adding a bot or a skill

Add a skill by creating `skills/<name>/SKILL.md`. The frontmatter `name` matches the folder. `description` says what it does and when to use it. On the Cursor plugin, `collect-requirements` sets `disable-model-invocation: true` so Cursor does not start it. The rule on every host is the skill text: only an explicit human request in chat.

Add a Cursor agent by creating `agents/<name>.md` with `name` and `description`, then a `roles` entry in `fstack.yaml` with `agent` and `model`. Put the skills it follows in the agent file. A read-only plugin agent sets `permissionMode: readonly`. When the bot needs a prompt, add `templates/prompts/<action>.md` and name the action in `build-context`. New statuses and events go in `state/transitions.yaml` first.

Add a hosted bot by creating `bots/<role>.yaml` as described under Bots. Include `sync-bot-config` in its skill list.

Run `python3 scripts/validate_plugin.py` after the edit. It checks the manifest, the transition table, the config, the template tokens, the bot configs, and that each event is named by its skill.

## Bots

Grok Bot is the primary host. Configs in `bots/` are version `0.1`. Each file has a profile (`name`, `title`, `description`, `persona`, `instructions`), skills copied from this repo, a `model_role` from `fstack.yaml`, connectors, teammates, a handoff message, and routines. A routine has a name, a prompt, and either a five-field cron schedule or a GitHub pull-request event. Cron uses the timezone in Grok Bot settings under Bot. The files name no host, user, or bot id. Address a teammate by the `name` in its config, which is the profile name you give it at creation.

The Orchestrator connects to Notion and GitHub. It reads repositories through the GitHub connector and does not clone. It messages the Verifier. The message starts with `fstack-handoff` and includes the role, feature, chunk, ask (`verdict`), and the prompt. The reply starts with `fstack-reply`. The Verifier has one read-only reader for the skill repository, used only by sync. An advisor is a Cursor cloud agent. Opus uses `claude-opus-5-5`. Argon uses `gemini-4-argon` only when the first critique leaves the choice unclear. See `advisors.fallback` in `fstack.yaml`.

The Orchestrator also has a routine for pull requests on chunk branches: opened, pushed, merged, and commented. Public docs confirm that a routine can start from a GitHub event. They do not publish the exact event-field names, so the bot maps those four words onto the host's GitHub trigger and narrows it to branches named `fstack/`.

### Bootstrap

The human creates only the Orchestrator. It provisions the other roles.

1. In the host, create one bot. Name it with the `title` from [`bots/orchestrator.yaml`](bots/orchestrator.yaml).
2. Paste that file's persona and instructions into the first message and ask the bot to remember them.
3. Connect the repo reader and Notion when it asks.
4. Ask it to install fstack. It syncs itself, then provisions each other role in `bots/`. The first create or rename waits for one question card. After that, sync updates those same roles without asking again.
5. Approve the one card that lists any connector those teammates still need, including read-only repo access. The Orchestrator does not authorize a connector itself.
6. Tell the Orchestrator the product's code locations. Ask it to set up the product. That is the first feature task.

The sync records the repository URL and the applied commit in the bot's persistent state, not in a product code location. The weekly routine in each config runs the same skill later. A removed role is marked retired. The bot is not deleted.

## License

MIT. See [LICENSE](LICENSE).
