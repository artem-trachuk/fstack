---
name: decision-policy
description: >
  Choose among valid options and continue.
  Use when a skill has more than one valid option, including a fix approach, a design choice, a chunk split, a feature match, or a skill choice.
  The Orchestrator decides. A human is asked only for the cases named here.
---

# Decision policy

Follow the debug-log contract.

Follow the decision-policy contract.

## Contract

The goal is to keep the workflow moving. The Orchestrator picks a valid option and proceeds. Do not ask the human to choose a fix approach or an implementation.

Read `autonomy` with the usual precedence: feature override, then the product workflow page, then `fstack.yaml`. The shipped value is `auto`. `ask_more` adds check-ins. It cannot turn off a human gate.

### How to choose

Generate the options. For a non-trivial choice, such as a fix approach or a design, follow the `advise` slot when it is not skipped. The repo default is on. The first role in `advisors.decision` runs first. The next role runs only when that critique is low confidence, says the options are close, or conflicts with the score. Those names are the configured advisors. Do not hardcode a model in the choice itself. The launch passes the model id from `fstack.yaml`. Keep the advisor fallback as the `advisors` skill defines it. Never write an advisor critique or ranking from your own reasoning, and never label your own reasoning as an advisor's. A critique with no cloud agent id or CLI run record, or with no file citation, is invalid. If the advisors disagree, and the case is not human-only, the Orchestrator still decides and records the disagreement. Do not escalate to the human for disagreement alone.

Score every option on these points: it satisfies the authoritative requirement, it is the smallest change consistent with the feature graph, it has the lowest risk and blast radius, it is reversible, and it matches existing patterns in the repo. The Orchestrator picks using that score and the advisors' views.

Record the decision on the feature page, or on the Fix page when the work is a fix: the options, the choice, why, who decided, and the confidence. Who decided is the agent. Include each advisor's view. When debug is on, follow `debug-log` with the same record. Then continue.

A feature match uses the best-evidenced candidate when it is clearly ahead. Ask only when the top candidates are genuinely tied after checking evidence.

A chunk split defaults to one chunk per repo for any work item, whether the class is `new_feature` or `fix`. Split only when that clearly helps: size, independent risk, multiple repos, or a staged rollout. A single chunk has no separate planning pass and no plan question.

### When the human is asked

Ask only for these cases:

- A requirement is ambiguous, the options would change behaviour users would notice, and no authoritative source settles it.
- Authoritative sources conflict.
- The action is irreversible or destructive: deleting or moving a Notion page, or retiring a bot.
- The action spends money or sends an outward message, including a source write.
- A fixed human gate: merge or release approval, the first create or rename of a bot, or Notion schema creation. Stack review stays with release. Shipping an unverified chunk stays with the human. These gates cannot be disabled.

`ask_more` also asks before confirming an unambiguous requirements page, before approving clear coverage rows, before a multi-chunk plan, before promoting the graph, and before saving a lesson. `auto` decides those and logs them.

Batch every pending human-only question into one card at the next checkpoint. Keep working on anything that question does not block.

## When to use

A skill is about to choose, or it is about to ask the human.

## Next

Return the choice to the caller. The caller continues.
