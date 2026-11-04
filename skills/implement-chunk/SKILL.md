---
name: implement-chunk
description: >
  Hand one chunk to a Cursor coding agent and record the agent id before waiting.
  Use when the next rule is launch_implementer for a planned, failed, or changes_requested chunk.
  The orchestrator does not edit product code.
---

# Implement a chunk

Hand the chunk off. Do not edit product code in the orchestrator session.

## When to use

The next rule is `launch_implementer`, or an implementer was launched and this session is resuming it.

## Steps

1. Follow `build-context` for `implement-chunk`. The prompt includes the spec, acceptance criteria, out of scope, allowed files, branch, base, existing pull request, and the previous failure summary.

2. Read `runtime` from the resolved file. `cloud` uses a Cursor cloud agent that can open a pull request against the chunk base. `local_worktree` means this session cannot start that cloud agent, so the implementer still works on the chunk branch and still receives the spec in the launch prompt. Do not create a fstack worktree. Tell the human when setup downgraded the runtime. The model is `roles.implementer` in the resolved file. You pass that model when you launch. The agent does not switch itself.

   The launch prompt is the only copy of the spec the coding agent gets. Do not tell it to read `.fstack` or the agent store. Do not assume the store is mounted in its VM.

3. Record `agent_launched` with `agent_id` and `launched_at` before you wait. This increments `attempt`. If you stop before that write, the next session can launch a second agent.

4. On resume, check that agent id and search the forge by the head branch. If the pull request exists, the prompt tells the agent to update it. If the agent is gone and there is no pull request, record `handoff_failed`. The second handoff failure escalates. Neither case increments `attempts_since_decision`.

5. When the agent returns, record `agent_reported`. A final line `FSTACK_BLOCKED: <reason>`, or a change outside `allowed_files` or under `.fstack` or `/cursor/stores`, sets `blocked` and decrements `attempt`. Do not send a blocked chunk to verify. Follow `escalate`.

   Otherwise store `pr`, `base_sha`, and `head_sha`, and set the chunk to `needs_verify`.

6. Do not judge the chunk. The next rule builds the verify prompt and launches the verifier.

## Events

- `agent_launched`
- `handoff_failed`
- `agent_reported`

## Next

Return to `pick-next-task`.
