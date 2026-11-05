# Changelog

## 0.3.0

- An advisor is a read-only Cursor cloud agent. Opus runs first. Argon runs only when the decision is still unclear. A critique needs an agent id or a CLI run record, and file citations.
- The fstack-advisor teammate is retired, not deleted. The Orchestrator reads repositories through the GitHub connector and does not clone.

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
