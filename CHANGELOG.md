# Changelog

## 0.4.0

- Add `scripts/next_action.py`. It reads `state/transitions.yaml` and a JSON snapshot of the feature, returns the next rule, and checks an event's statuses before the orchestrator writes it. It never touches Notion.
- `pick-next-task` and the orchestrators use it when the host can run Python. Grok Bot applies the table by hand, as before.
- Add `tests/test_next_action.py`, which reaches every rule, and run it in CI. Three `test_gap_*` tests record table gaps: a tie-break in flight falls to `stuck`, `dispute_budget` repeats and hides `dispute_decide`, and `merge_restack` is shadowed by `restack` and `range_diff`.

## 0.3.0

- Add Claude Code as a host. Install from this repository's marketplace with `claude plugin install fstack@fstack`, then run `claude --agent fstack:orchestrator`.
- On Claude Code the bots are subagents: `fstack:verifier`, `fstack:advisor`, and `fstack:implementer`, in `claude/agents/`. They use the same `fstack-handoff` and `fstack-reply` messages. None of them has a Notion tool.
- The implementer subagent replaces the Cursor cloud agent on Claude Code. Question cards are AskUserQuestion calls. The plugin update replaces `sync-bot-config`.

## 0.2.0

- Add `upgrade-fstack`. "update fstack", "upgrade fstack", and "sync fstack" bring the installed commit up to main, migrate workflow defaults, and record the fstack version apart from Notion's `0.0.6` setup guide.

## 0.1.0

### Pull request 3

- A bug is a Fix page on the existing feature. The Orchestrator decides the approach and continues.
- Any work item defaults to one chunk per repo unless a split clearly helps.

### Pull request 2

- Preferences and lessons use Notion Memory. fstack does not create a Memories database.
- Skills stay in the git repository named by `plugin.json`.

### Pull request 1

- fstack 0.1 on Grok Bot, with Notion as the state store, a product graph, workflow config, and teammate provisioning.
- Debug logging is off until asked. The Orchestrator is the only writer.
