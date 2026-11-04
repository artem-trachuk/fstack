---
name: tldr
description: >
  Rewrite a bot-to-human fstack message so it is short and plain.
  Use before every question card, escalation, pull-request review request, release question, and status report shown to the human.
  Keeps the decision and the options intact.
---

# TLDR

Rewrite the message the human is about to read. Send the rewrite, not the draft.

## When to use

The orchestrator or the verifier is about to show the human a question card, an escalation, a pull-request review request, a release question, or a status report.

## Steps

1. Start with the sentence that says what the human needs to do. When the message needs nothing from them, start with the status.

2. Keep the feature slug, the chunk id, and any pull request URL. Keep every option you are actually offering. Do not add a new ask, and do not drop a choice.

3. Use plain words. Cut tool names, model names, file dumps, and stack traces. A failure summary stays one or two sentences and names the broken behavior.

4. Stay under 120 words. When the human must pick among options that do not fit, keep the options in a short list and cut the rest.

5. An outward message (email, chat apps, issue comments, pull-request comments, status posts) is still only a draft after this rewrite. Sending it waits for an explicit human approval of that text. A message inside this conversation is delivered after the rewrite.

## Example

Draft: "The verifier subsystem emitted a negative disposition on chunk 02 due to an unmet predicate in the acceptance vector regarding pagination cursor stability. Escalation threshold will be reached on the subsequent iteration. Please advise."

Rewrite: "Chunk 02 failed verification. The page cursor changes when the list reloads, and the spec says it stays put. This was the first failure, so the coding agent will try once more. I will stop and ask you if the next try fails too."

## Writes

Nothing, unless the caller asked you to store the sent text in `decisions.md`. The caller sends the rewrite.

## Next

Return the rewrite to the caller.
