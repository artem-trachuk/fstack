---
name: configure-workflow
description: >
  Show or change the effective workflow config stored in Notion.
  Use when a session starts, when the human asks which skill a step uses, or when the human wants to bind or skip a slot.
  Does not change human gates or who is allowed to write Notion.
---

# Configure workflow

Slots choose skills. They do not choose policy.

## Inputs

- The repo defaults in `fstack.yaml` wherever that file lives, or the Notion copy when the product has no file: `workflow.slots`, `code_locations`, `release_policy`, `sources`, and `authoritative_kinds`.
- The product Workflow config page in Notion.
- The feature override page, when a feature is in progress.
- The human's request, when they are changing a binding.

## Outputs

- The effective config: one binding per slot, the sources, the authoritative kinds, and the standing preferences.
- On a session start, `workflow_loaded` recorded on the feature: the skill used for each slot, where that binding came from, and the config version.
- On a change, the Notion page updated and one change row with Who, When, Old, and New.

## Precedence

A feature override beats the product page. The product page beats `fstack.yaml`. Missing Notion pages mean the repo defaults.

Read this at session start, with the Agent Operating Guide, before any other feature step. Record `workflow_loaded` when a feature is open. Copy the skill name for a chunk step onto that chunk's Bound skill when the step starts.

## Fixed

Refuse a request to change human gates, merge, release, outward messages, coverage approval, source writes, who may write Notion, or `collect_requirements`. Say those stay in the repo. Do not write them on the Workflow config page.

## Show

When the human asks what is configured, list each slot, the effective skill, the parameters, whether it is skipped, and whether the binding came from the feature, the product, or the repo. Include sources, authoritative kinds, and preferences. One short list. Do not dump the page.

## Change

1. Resolve the slot. "Verification" is the `verify` slot. "For this feature only" means a feature override. Anything else is the product page.

2. Resolve the skill name. It must be a folder in the synced skill library. If it is not, say it is missing and name the closest library names that share a prefix or a word with the request. Do not bind a guess.

3. Read that skill's `contract`. The slot's `contract` is in `fstack.yaml`. If the skill does not declare a contract, or the two differ, refuse the binding and say what the slot requires. Do not write.

4. A skip is allowed only when that slot's `skippable` is true. The shipped skippable slot is `survey`. Refuse any other skip.

5. Confirm in one line, naming the slot, the skill, the parameters, and whether the change is for this feature or the product. Then write.

6. Bump Config version by one. Record `workflow_changed` with who (the human in this chat), when (today's date), the old binding, and the new binding. That row is the change log entry. A feature change is a feature-scoped page. A product change is the product page.

Parameters are an optional map the skill reads, such as `{env: staging}`. Notes are optional text. Neither can carry a human gate.

Standing preferences may set `plan_review` or `notify` on the product page. The same precedence applies. They are not gates.

## Events

- `workflow_loaded`
- `workflow_changed`

## Next

Return the effective config to the caller. The caller runs the bound skill for the slot, not a hard-coded name, after the contract check.
