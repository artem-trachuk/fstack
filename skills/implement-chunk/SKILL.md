---
name: implement-chunk
contract: implement
description: >
  Hand one chunk to a coding agent and record the agent id before waiting.
  The agent is a Cursor cloud agent on Grok Bot and Cursor, or the fstack:implementer subagent on Claude Code.
  Use when the next rule is launch_implementer for a planned, failed, or changes_requested chunk.
  The orchestrator does not edit product code.
---

# Implement a chunk

Follow the debug-log contract.

Follow the decision-policy contract.

## Contract

Inputs: one chunk spec, the base branch, and any slot parameters.
Outputs: a branch, a pull request, and the recorded head. No merge.

Hand the chunk off. Do not edit product code in the orchestrator session.

## When to use

The next rule is `launch_implementer`, or an implementer was launched and this session is resuming it.

## Steps

1. Follow `build-context` for `implement-chunk`. The prompt includes the spec, acceptance criteria, out of scope, allowed files, branch, base, existing pull request, and the previous failure summary.

2. Launch one coding agent for this chunk. It works on the chunk branch, stacked on the base, and opens one pull request. Do not merge. Do not start a second agent for the same chunk.

   On Grok Bot, that agent is a Cursor cloud agent on the chunk's code location. Do not write product code on the bot computer and do not clone that location. Read files, diffs, pull requests, and checks through the GitHub connector. When the run finishes you are revived with the branch, the pull request, and the final report. To change a running agent, send a follow-up.

   On the Cursor plugin, start a cloud agent with the same prompt when the session can. `local_worktree` in the resolved models means it cannot, so the implementer still works on the chunk branch and still receives the spec in the prompt. Do not create a fstack worktree. Tell the human when setup downgraded the runtime. The model is `roles.implementer` in the resolved models. You pass that model when you launch. The agent does not switch itself.

   On Claude Code, that agent is the `fstack:implementer` subagent. Launch it with the Agent tool in the background. The prompt is the `fstack-handoff` text from `bots/orchestrator.yaml` with `role: implementer`, and the `implement-chunk` prompt under `prompt:`. Name the chunk's code location and the checkout of that location on this computer. When that checkout is this session's own repository, launch with worktree isolation. When it is another checkout on this computer, the implementer works there on the chunk branch. When this computer has no checkout of that location, do not clone it. Tell the human through `tldr` which location needs a checkout and end the turn. The model is `roles.implementer` in `.fstack/resolved.yaml`. The subagent has no Notion tool. Its final message starts with `fstack-reply` and is its report.

   The launch prompt is the only copy of the spec the coding agent gets. Do not tell it to open Notion or `.fstack`.

3. Record `agent_launched` with `agent_id` and `launched_at` before you wait. On Claude Code, `agent_id` is the id the Agent tool returned for the background subagent. This increments `attempt`. If you stop before that write, the next session can launch a second agent.

4. On resume, check that agent id and search the forge by the head branch. On Claude Code, a subagent from an earlier session is gone. The pull request on the head branch is what remains. If the pull request exists, the prompt tells the agent to update it. If the agent is gone and there is no pull request, record `handoff_failed`. The second handoff failure escalates. Neither case increments `attempts_since_decision`.

5. When the agent returns, record `agent_reported` on the chunk page. A final line `FSTACK_BLOCKED: <reason>`, or a change outside `allowed_files`, sets `blocked` and decrements `attempt`. Do not send a blocked chunk to verify. Follow `escalate`.

   Otherwise store `pr`, `base_sha`, and `head_sha`, and set the chunk to `needs_verify`.

6. Do not judge the chunk. The next rule builds the verify prompt and launches the verifier.

## Events

- `agent_launched`
- `handoff_failed`
- `agent_reported`

## Next

Return to `pick-next-task`.
