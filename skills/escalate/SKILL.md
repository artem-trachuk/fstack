---
name: escalate
description: >
  Stop a blocked chunk and ask the human to unblock it or decide.
  Use when verification fails repeatedly, a dispute cannot be settled, or the stack cannot move.
  Waits for the human. Does not merge, release, or widen the spec on its own.
---

# Escalate

The chunk stops. The human unblocks it or makes the decision. You do not pick the outcome for them.

## When to use

- The chunk's verify attempts have reached `verify.max_failures_before_escalation`.
- A verdict stayed `disputed` after the tie-break, or the advisor cap blocked a tie-break.
- `pick-next-task` found a stack that cannot move.
- An implement handoff failed twice on the same chunk.

## Steps

1. Set the chunk status to `escalated` when a chunk is involved. Follow `skills/build-context/SKILL.md` for `escalate`.

2. Append a `decisions.md` row with the blocker, the attempt count, and the options. Options are concrete. Typical pairs are: change the spec to match the behavior you observed, or keep the spec and name what the next attempt must do differently. Include "stop this feature" when that is a real option.

3. Follow `skills/tldr/SKILL.md`. The message starts with the chunk and the blocker, then asks the human to unblock or decide, then lists the options. Send it in this conversation.

4. Stop the feature flow. Do not launch another coding agent, do not start the next chunk, and do not change acceptance criteria while you wait.

5. When the human answers, quote the answer in `decisions.md`. Apply only the option they chose. A decision to retry sets the chunk back to `failed` and returns to `skills/pick-next-task/SKILL.md`. A decision to change the spec edits the chunk's spec or acceptance criteria in place, resets `attempt` to `0`, sets status to `planned`, and returns to `pick-next-task`. A decision to stop leaves the chunk `escalated`.

## Writes

- `prompts/escalate.md`
- chunk status
- `decisions.md`

## Next

Wait for the human. After a decision, `pick-next-task`.
