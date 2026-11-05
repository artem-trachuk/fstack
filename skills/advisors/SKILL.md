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

- A critique and a ranking that cite files and lines, plus a confidence. This skill does not pick the option and does not escalate a disagreement.
- Proof: the cloud agent id (`bc-...`), its `cursor.com` URL, the model id actually used, and the raw critique.

## When to use

`planner_review` during `gap-analysis` and `split-into-chunks`. `verify_tiebreak` when a chunk is `disputed`. A non-trivial decision launches the first role in `advisors.decision` first. That role maps to the Opus model id. Launch the next role, which maps to the Argon model id, only when the first critique is low confidence, says the options are close, or conflicts with the score. The fallback below is unchanged. Skip an advisor when the `advise` slot is skipped.

Never write an advisor critique or ranking from your own reasoning, and never label your own reasoning as an advisor's. A critique without an agent id or a CLI run record, or without a file citation, is invalid.

## Budget

`max_calls_per_feature` is 6. `reserve.verify_tiebreak` is 2. Planner calls may use the other 4. A launched, finished, or failed row counts. A skipped row does not. The ledger is the Advisor calls page related to the feature and the product. Write the row there as `launched` before you wait, then update it to `finished` or `failed`. A crash still counts. A local CLI fallback is its own call and counts too. Do not keep the ledger in a file.

Review one artifact hash once. A duplicate returns `skipped: duplicate` and does not count.

If the resolved tie-break slug equals the verifier model, including when both are `inherit`, do not launch it and do not use a local CLI. On Grok Bot that slug is in the bot's persistent state. On the Cursor plugin it is in `.fstack/resolved.yaml`. Record `tiebreak_skipped` with reason `same_model` and escalate. That rule is about independence, not about credits.

`verify_tiebreak.fallback` is a list of other Cursor short names to try in Cursor. `advisors.fallback` is the local CLI list.

## When Cursor cannot start

Use a local CLI only when the Cursor cloud agent cannot start because the account has no credits for that model, or the model is unavailable. A message such as "Buy credits or switch to a Grok model" is this case. A critique that started and then failed is a failed call, not a reason to start the CLI. The CLI path is Opus only. There is no Argon CLI. If Argon cannot start, record `skipped: no_runtime`. The teammate bot is never a fallback.

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

3. Record `advisor_launched` or `tiebreak_launched` before the session starts. Launch a separate read-only Cursor cloud agent on the product repo at the pinned commit. On Grok Bot use the host's cloud-agent launch. On the Cursor plugin launch the advisor agent. Pass the model id explicitly. The Opus default is `claude-opus-5-5` with effort `xhigh` or `high`. The Argon default is `gemini-4-argon` with reasoning effort `high`. Resolve those ids from `models` in `fstack.yaml`. Do not leave the model as inherit and do not use the Orchestrator's own model.

   The prompt says read-only. Do not edit files, push, open a pull request, or create a branch. Read the code. Return a structured critique: a ranking, a confidence, and citations of files and lines. Include the options, the Fix or feature page, and the relevant graph nodes. An Argon session also receives the Opus critique.

   If the cloud agent makes commits anyway, ignore those commits and archive the agent. Archive each advisor agent after its critique is saved.

   On a credit or unavailable-model failure, mark that row `failed` and try the local CLI only for Opus. Record a new launched row before the CLI runs, and store that the proof is a CLI run. Same-model tie-break still skips and does not use the CLI. Never message a teammate for a critique.

4. Record `advisor_finished` or `tiebreak_finished` on the Advisor calls page. Store the cloud agent id (`bc-...`), its `cursor.com` URL, the model id actually used, and the raw critique on the Notion page `advisor output <n>` under the feature. A planner failure does not stop the feature. A tie-break failure does not become the verdict. The orchestrator records `decide_dispute`. If no runtime can start, record `skipped: no_runtime` and say so plainly through `tldr`.

## Events

- `advisor_launched`
- `advisor_finished`
- `tiebreak_launched`
- `tiebreak_finished`
- `tiebreak_skipped`

## Next

Return the critique to the caller, or the skip, when no runtime ran.
