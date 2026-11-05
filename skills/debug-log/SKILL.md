---
name: debug-log
description: >
  Append a redacted trace entry to the product Debug log when debug is on.
  Use when any skill finishes an action, transition, decision, outside call, handoff, or config change.
  When debug is off, write nothing. Never block the workflow.
---

# Debug log

Follow the debug-log contract.

## Contract

Only the Orchestrator writes the Debug log. A teammate or an implementer returns its own trace entries in the reply payload. The Orchestrator appends those entries. Do not write the log from any other role.

Read the effective `debug` flag with the usual precedence: feature override, then the product workflow page, then `fstack.yaml`. The shipped default is false.

When debug is off, return immediately. Write nothing and add nothing to a reply.

When debug is on, append one entry per action. An entry records:

- timestamp
- bot role
- correlation id for this session, so one session reads as one trace
- product, feature, chunk, repo, and commit where they exist
- one of: a transition (event name, from, to), a skill invocation (skill, slot, binding source: feature, product, or repo), a decision (what, the options, why, and who: agent, advisor, or human via a question card), an outside call (connector or tool category, target, outcome, including failure and retry), a handoff and its reply, or a config or sync event

Group entries under a heading for the session. Append in order. The log is one Debug log page per product, related to the product. When the page is too large, add a continuation page, set its Previous relation to the page it continues, and append there. It still reads as one log.

Log references and short summaries. Do not log full file contents or full prompts. Never log a secret, a token, or a credential value. If a value looks like one, replace it with the word redacted and do not keep the original.

If Notion is unavailable, buffer the entries and show them with the unsaved content. Do not drop them. Do not stop the workflow because a debug write failed.

## Events

- `debug_entry`

## Next

Return to the caller. The caller continues whether or not the entry was saved.
