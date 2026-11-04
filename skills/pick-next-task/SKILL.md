---
name: pick-next-task
description: >
  Choose the single next chunk in a feature stack.
  Use when the plan exists and the orchestrator is ready to implement, resume, or stop for release.
  Returns one chunk, or release, or a block. Does not implement and does not merge.
---

# Pick the next task

Choose one next action from the chunk files. v0.1 works one chunk at a time, in stack order.

## When to use

The plan and chunk files exist, and the flow needs to know what to do next: after a split, after a verify verdict, or after the human unblocks an escalation.

## Status

Use only these values on a chunk: `planned`, `implementing`, `in_review`, `verified`, `failed`, `escalated`.

## Steps

1. Read every file in `<workspace>/<feature>/chunks/` in id order. Follow `skills/build-context/SKILL.md` for `pick-next-task`.

2. Apply the first matching rule:

   - A chunk is `escalated`: stop. The human's decision is the next input. Point at `decisions.md` and the escalation. Do not start a later chunk.
   - A chunk is `failed`: that chunk is next. Follow `skills/implement-chunk/SKILL.md`.
   - A chunk is `implementing` or `in_review`: that chunk is current. If it has a pull request and no verification result for this attempt, start a new verifier agent with `agents/verifier.md`, and give it `prompts/verify.md` plus the diff. Do not pass `prompts/implement-chunk.md`, and do not judge the chunk in the orchestrator session. If the pull request is missing, follow `skills/implement-chunk/SKILL.md` to finish the handoff record.
   - A chunk is `planned`, and every chunk it depends on is `verified` (or it depends on nothing): that chunk is next. Follow `skills/implement-chunk/SKILL.md`.
   - Every chunk is `verified`: the stack is ready for review. Follow `skills/tldr/SKILL.md` with a review request that lists the pull requests in stack order, then follow `skills/release/SKILL.md`.
   - Anything else: the stack is blocked. Follow `skills/escalate/SKILL.md`.

3. Append a short `decisions.md` row naming the chunk or the release handoff.

## Writes

- `prompts/pick-next-task.md`
- one `decisions.md` row

## Next

The skill named by the matching rule. Do not implement the chunk in the orchestrator session.
