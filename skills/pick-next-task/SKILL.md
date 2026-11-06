---
name: pick-next-task
description: >
  Choose the single next action from state/transitions.yaml, with scripts/next_action.py when the host can run it.
  Use when the orchestrator is ready to implement, resume, verify, review, or release.
  Does not implement product code and does not grade a chunk.
---

# Pick the next task

Follow the debug-log contract.

Follow the decision-policy contract.

Apply `next_rules` in `state/transitions.yaml` from top to bottom. The first rule whose `when` matches is the only action. Do not skip ahead to release while review is still open.

## The next-action script

When the host can run `python3` with PyYAML, `scripts/next_action.py` in the plugin root applies the table for you. On Claude Code the path is `${CLAUDE_PLUGIN_ROOT}/scripts/next_action.py`. It reads `state/transitions.yaml`. It does not read or write Notion.

1. Build one JSON snapshot from what step 1 below read. `feature` holds the feature page properties under their `feature_fields` names. `chunks` holds every chunk page under its `chunk_fields` names. Read them with one query on the Chunks database filtered by the feature, not one fetch per page. `verifications` lists each verification page whose applied flag is false. `observed` holds what you checked this turn: the default-branch commit for each code location, and per chunk whether the diff page for this attempt exists, the pull request head, whether it is merged, and its CI. The script's docstring lists every key. Leave out what you did not check.
2. Run `python3 scripts/next_action.py next` with the snapshot on stdin. The answer names the rule, the action, the slot or skill to follow, the chunk or location, the rule's detail, and the events that are legal now. Follow that answer. Do not apply the table again by hand.
3. Before you write a status change, run `python3 scripts/next_action.py record <event>` with the same snapshot, plus `--chunk`, `--to`, or `--chunk-to` when the event needs them. Write only the statuses it returns. Exit code 2 means the event is not legal from these statuses: do not write it, and show the reason.

The script checks statuses only. The guard text it returns is still yours to follow. A refused snapshot, such as an unknown status, is a sign the Notion page drifted: report it and stop. When the host cannot run the script, apply the table by hand as the steps below describe.

## When to use

The Notion feature page exists and the orchestrator needs the next legal action. If the human is asking to fix a bug or a regression, classify it as `fix` first and follow the skill bound to the `fix` slot. Do not create a Features page.

## Steps

1. Read the Notion feature page, every chunk page in id order, every Fix page related to the feature, and any verification page whose applied flag is false. When a verifier reply arrives and that page does not exist yet, create it before you read it. Title it `verification <chunk-id> a<attempt>`. Set Product, Feature, and Chunk relations. When the chunk is linked from a Fix page, set that Fix page's Verification relation too. Store the verdict, the message, `base_sha`, and `head_sha` from the reply. Set applied to false. The verifier does not create this page. Take the lease when it is free or already yours. A lease held by someone else until it expires means you stop.

2. Do that one action.

   A chunk that is `implementing` or `in_review` with an agent id is resumed. Check the agent and search the forge for the head branch before launching another. Record `handoff_failed` when the agent is gone and no pull request exists.

   A filed verdict for the current attempt and `head_sha` is applied with `apply_verdict`. Do not launch another verifier.

   When that verdict is `not_implemented`, set the chunk to `awaiting_verification_decision`. Do not set `verified`, `verified_sha`, or `accepted_sha`. Do not increment `attempts_since_decision`. Do not launch the next chunk, `review-stack`, or `release`. Set `waiting_on` kind `verification_unimplemented` and question id `Q-<slug>-<chunk-id>-unverified`. Relay this sentence through `tldr`, verbatim, with the chunk id and the options `accept_unverified` and `stop`:

   `Verification is not implemented yet, so these changes cannot be verified.`

   Then end the turn. The next rule `not_implemented` stays on that chunk until `human_decision` is logged.

   The orchestrator launches the verifier at `launch_verifier`. The verifier does not build its own prompt and, while the skill is a stub, does not judge the patch. Follow `build-context` for `verify` first, then record `verifier_launched` before you wait.

   On Grok Bot, launching the verifier means sending the handoff in `bots/orchestrator.yaml` to the teammate whose profile name is `fstack-verifier`. End the turn. The reply arrives later and starts with `fstack-reply`. On Claude Code, launch the `fstack:verifier` subagent with the Agent tool. Its prompt is that same handoff text, and its final message is the reply that starts with `fstack-reply`. Pass `roles.verifier` from `.fstack/resolved.yaml` as the model. On the Cursor plugin, launch the verifier agent with the same prompt.

   `decide_dispute` is yours. The tie-break critique is not the verdict.

   When the cap rule matches, follow `escalate`. The comparison is `attempts_since_decision` greater than or equal to `verify.max_failures_before_escalation`.

   When the stack-review rule matches, follow `review-stack` and end the turn. Do not open the release question in that turn.

3. If the default branch sha moved, record `base_moved` before launching more work. Open chunks get `needs_restack`. Verified chunks get a range-diff before they stay verified.

4. Write a Decision page related to the feature and the product, and update the status the event names in the same turn. You are the only writer.

## Events

- `apply_verdict`
- `decide_dispute`
- `verifier_launched`
- `base_moved`

## Next

The skill named by the matching rule. End the turn when the rule says to wait.
