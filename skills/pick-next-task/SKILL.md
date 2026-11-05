---
name: pick-next-task
description: >
  Choose the single next action from state/transitions.yaml.
  Use when the orchestrator is ready to implement, resume, verify, review, or release.
  Does not implement product code and does not grade a chunk.
---

# Pick the next task

Apply `next_rules` in `state/transitions.yaml` from top to bottom. The first rule whose `when` matches is the only action. Do not skip ahead to release while review is still open.

## When to use

The Notion feature page exists and the orchestrator needs the next legal action.

## Steps

1. Read the Notion feature page, every chunk page in id order, and any verification page whose applied flag is false. When a verifier reply arrives and that page does not exist yet, create it before you read it. Title it `verification <chunk-id> a<attempt>`. Set Product, Feature, and Chunk relations. Store the verdict, the message, `base_sha`, and `head_sha` from the reply. Set applied to false. The verifier does not create this page. Take the lease when it is free or already yours. A lease held by someone else until it expires means you stop.

2. Do that one action.

   A chunk that is `implementing` or `in_review` with an agent id is resumed. Check the agent and search the forge for the head branch before launching another. Record `handoff_failed` when the agent is gone and no pull request exists.

   A filed verdict for the current attempt and `head_sha` is applied with `apply_verdict`. Do not launch another verifier.

   When that verdict is `not_implemented`, set the chunk to `awaiting_verification_decision`. Do not set `verified`, `verified_sha`, or `accepted_sha`. Do not increment `attempts_since_decision`. Do not launch the next chunk, `review-stack`, or `release`. Set `waiting_on` kind `verification_unimplemented` and question id `Q-<slug>-<chunk-id>-unverified`. Relay this sentence through `tldr`, verbatim, with the chunk id and the options `accept_unverified` and `stop`:

   `Verification is not implemented yet, so these changes cannot be verified.`

   Then end the turn. The next rule `not_implemented` stays on that chunk until `human_decision` is logged.

   The orchestrator launches the verifier at `launch_verifier`. The verifier does not build its own prompt and, while the skill is a stub, does not judge the patch. Follow `build-context` for `verify` first, then record `verifier_launched` before you wait.

   On Grok Bot, launching the verifier means sending the handoff in `bots/orchestrator.yaml` to the teammate whose profile name is `fstack-verifier`. End the turn. The reply arrives later and starts with `fstack-reply`. On the Cursor plugin, launch the verifier agent with the same prompt.

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
