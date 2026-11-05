---
name: tldr
description: >
  Rewrite a bot-to-human fstack message so it is short and plain, without dropping question ids, options, commands, shas, or pull request URLs.
  Use when sending a question card, escalation, review request, release question, or status report.
---

# TLDR

The message rules live in `rules/human-facing.mdc`. This skill is how you apply them.

## When to use

You are about to show the human a question card, an escalation, a review request, a release question, or a status report.

## Steps

1. Start with what the human needs to do. When you need nothing, start with the status.

2. Use the question card in `templates/question-card.md` for a decision. Keep the question id, each option id, the default, and the impact line verbatim. A partial answer names the ids it covers. The rest stay open.

   On Grok Bot, send the short prose, then a question card whose clickable options are those option ids. Gap analysis, the unverified-chunk decision, escalation, stack review, plan approval, and release approval all use a card. The card ends the turn. On the Cursor plugin, ask the same options in chat. A click on an option is the reply. A typed reply still has to match the approval rule for that question.

3. Keep `release.command`, verified shas, and pull request URLs verbatim. Do not shorten them to fit a word count.

4. Use plain words for the rest. Cut tool names, model names, and file dumps. Stay under 120 words only for the prose around those verbatim lines.

5. An outward message stays a draft until the human approves that exact text. `notify: conversation` is sent in this chat after the rewrite.

## Events

This skill does not record a feature event.

## Next

Return the rewrite to the caller.
