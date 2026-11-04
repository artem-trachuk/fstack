---
name: implement-chunk
description: >
  Hand one chunk to a Cursor coding agent with its spec, stack rules, and allowed files.
  Use when pick-next-task has selected a planned or failed chunk.
  The orchestrator records the branch and pull request and does not implement the chunk itself.
---

# Implement a chunk

Hand the chunk to a Cursor coding agent. The orchestrator session does not edit product code for the chunk.

## When to use

`pick-next-task` selected a chunk whose status is `planned` or `failed`. Also use it when a chunk is `implementing` and the pull request was never recorded.

## Steps

1. Read the chunk file. Follow `skills/build-context/SKILL.md` for `implement-chunk`. The prompt at `prompts/implement-chunk.md` is what the coding agent receives. It carries the spec, the acceptance criteria, the allowed files, the base branch, and the branch name.

2. Branch name is `fstack/<feature>/<chunk-id>`, lowercase. The base is the default branch for the first chunk, and the previous chunk's branch for every later chunk. Record both on the chunk file before the handoff.

3. Set status to `implementing` and increment `attempt` when the previous attempt finished a verify cycle. The first handoff sets `attempt` to `1`.

4. Start a Cursor coding agent.

   - Use `roles.implementer.model`. `inherit` means no model override. `opus` or `argon` means the slug in `models.resolved`. When the resolution is missing, use the parent Cursor model and write that fallback on the chunk.
   - When this session can start a Cursor cloud agent, start one with `prompts/implement-chunk.md` as its task so it can open a stacked pull request.
   - When it cannot, start a Cursor subagent with the same prompt and the same model rule.
   - Give the agent that prompt only. Do not attach the verify prompt, prior verifier grievances beyond the failure summary already in the prompt, or a request to merge.

5. The coding agent's job is in the prompt: change only allowed files, commit on the chunk branch, open a pull request into the stack base, and stop. It does not merge and it does not release.

6. When the agent returns, record the branch, the pull request URL, and the agent id on the chunk file. Set status to `in_review`. If the agent failed before opening a pull request, leave status at `implementing`, record the blocker, and follow `skills/escalate/SKILL.md` when you cannot repair the handoff by restating the same prompt once.

7. Append a `decisions.md` row with the branch and the pull request URL.

## Writes

- `prompts/implement-chunk.md`
- the chunk file's status, branch, base, pull request, and attempt
- `decisions.md`

## Next

Start a new verifier agent with `agents/verifier.md`. Give it `prompts/verify.md` and the diff. Do not pass `prompts/implement-chunk.md`, and do not judge the chunk in the orchestrator session. The verifier follows `skills/verify/SKILL.md`. When this session cannot start that agent, stop and tell the human the chunk is waiting for the verifier, with the path to `prompts/verify.md`.
