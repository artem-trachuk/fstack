---
name: advisors
contract: advise
description: >
  Run a short read-only advisor and record the call before it returns.
  Use when the action is planner_review during gap-analysis or split-into-chunks, or one verify_tiebreak on a disputed attempt.
  Falls back to a configured local CLI when Cursor cannot start the model. The advisor never edits the product and never owns the verdict.
---

# Advisors

Follow the debug-log contract.

Follow the decision-policy contract.

A second opinion. The caller decides what to do with it.

## Inputs

- The options, the artifact, and which configured advisor is being asked.
- `advisors.decision` lists the advisors used for a non-trivial choice. The names are roles, not models.

## Outputs

- A critique and a ranking. This skill does not pick the option and does not escalate a disagreement.

## When to use

`planner_review` during `gap-analysis` and `split-into-chunks`. `verify_tiebreak` when a chunk is `disputed`. A non-trivial decision asks each advisor named in `advisors.decision` to critique and rank the options. The fallback below is unchanged. Skip an advisor when the `advise` slot is skipped, or when the action is outside that advisor's `when` list and it is not a decision round.

## Budget

`max_calls_per_feature` is 6. `reserve.verify_tiebreak` is 2. Planner calls may use the other 4. A launched, finished, or failed row counts. A skipped row does not. The ledger is the Advisor calls page related to the feature and the product. Write the row there as `launched` before you wait, then update it to `finished` or `failed`. A crash still counts. A local CLI fallback is its own call and counts too. Do not keep the ledger in a file.

Review one artifact hash once. A duplicate returns `skipped: duplicate` and does not count.

If the resolved tie-break slug equals the verifier model, including when both are `inherit`, do not launch it and do not use a local CLI. On Grok Bot that slug is in the bot's persistent state. On the Cursor plugin it is in `.fstack/resolved.yaml`. Record `tiebreak_skipped` with reason `same_model` and escalate. That rule is about independence, not about credits.

`verify_tiebreak.fallback` is a list of other Cursor short names to try in Cursor. `advisors.fallback` is the local CLI list.

## When Cursor cannot start

Use a local CLI only when the Cursor advisor cannot start because the account has no credits for that model, or the model is unavailable. A message such as "Buy credits or switch to a Grok model" is this case. A critique that started and then failed is a failed call, not a reason to start the CLI.

Walk `advisors.fallback` in order. Use an entry only when `enabled` is true and the resolved `advisor_cli` says it is available and signed in. On Grok Bot that record is in the bot's persistent state. On the Cursor plugin it is in `.fstack/resolved.yaml`. The `command` is a name on `PATH`. Do not build a filesystem path, a user name, or a machine name.

For `runtime: claude-cli`, run:

`claude -p --model <model> --tools Read,Grep,Glob --allowedTools Read,Grep,Glob`

Use the configured `command` and `model` alias. `--tools` leaves only Read, Grep, and Glob available. Do not allow Edit, Write, or Bash. Do not add a flag that skips permissions. A local CLI runs under the user's own subscription terms.

Write the prompt onto the Notion page `advisor input <n>` under the feature before the command. Pass the prompt text. If a product checkout is already on this computer, use it as the working directory. Do not clone a repository to get one. Save stdout onto the Notion page `advisor output <n>`. That page is the critique. The Orchestrator writes both pages. The advisor does not. Do not paste them into a pull request. Do not put tokens, credential paths, or environment secrets in the prompt or on the command line.

If the cap would be exceeded by this call, do not start it.

## When nothing can start

If Cursor cannot start and every fallback is disabled, unavailable, or not signed in, do not invent a critique. Record `skipped: no_runtime` on the advisor row. Tell the human through `tldr` that this advisor step was skipped and why. A planner skip does not stop the feature. A tie-break skip leaves `decide_dispute` or `escalate_chunk` to the orchestrator.

## Steps

1. Resolve the Cursor model from the bot's persistent state on Grok Bot, or from `.fstack/resolved.yaml` on the Cursor plugin. You pass that model when you launch the advisor. The advisor does not switch itself.

2. Follow `build-context`. A tie-break uses `verify-tiebreak`, with the same patch as verify and no fstack notes.

3. Record `advisor_launched` or `tiebreak_launched`, then start the advisor. On Grok Bot, send the handoff in `bots/orchestrator.yaml` to the teammate whose profile name is `fstack-advisor` and end the turn. The reply starts with `fstack-reply` and the critique is the `critique` field. If that teammate is unavailable, or a Cursor advisor model cannot start because of credits or an unavailable model, use the local CLI above. On the Cursor plugin, launch the advisor agent. On a credit or unavailable-model failure, mark that row `failed` and try the local CLI list above. Record a new launched row before the CLI runs. Same-model tie-break still skips and does not use the CLI or the teammate.

4. Record `advisor_finished` or `tiebreak_finished` on the Advisor calls page, and store the critique on the Notion page `advisor output <n>` under the feature. A planner failure does not stop the feature. A tie-break failure does not become the verdict. The orchestrator records `decide_dispute`.

## Events

- `advisor_launched`
- `advisor_finished`
- `tiebreak_launched`
- `tiebreak_finished`
- `tiebreak_skipped`

## Next

Return the critique to the caller, or the skip, when no runtime ran.
