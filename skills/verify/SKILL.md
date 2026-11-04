---
name: verify
description: >
  Judge one chunk from its spec, its acceptance criteria, and the diff.
  Use when a chunk is in_review and has a pull request, and the judge is the verifier, not the coding agent.
  Leaves implementer notes out of the review. A repeated failure escalates to the human.
---

# Verify

Judge the chunk as the verifier. The coding agent does not run this skill on its own output.

## When to use

A chunk is `in_review`, its pull request or branch is known, and this attempt does not yet have a verification result. A disputed verdict also re-enters this skill after the tie-break advisor returns.

## Inputs you use

Follow `skills/build-context/SKILL.md` for `verify` first. The written prompt is the allow-list for prose context.

- Requirements for the feature.
- The chunk's spec, acceptance criteria, and out of scope.
- The diff of the chunk branch against its base. Prefer the three-dot diff, `base...branch`, or the pull request diff when that is the same change.
- The result template `templates/feature/verification/result.md`.

## Inputs you exclude

- Any section titled Implementer notes.
- `prompts/implement-chunk.md`.
- The coding agent's explanation of why the change is correct.
- Your own earlier draft of the verdict. The diff and the spec are the evidence.

When excluded material is present anyway, ignore it and write one line in the result: `Ignored implementer notes that were attached.`

## Steps

1. Write `verification/<chunk-id>.md` from the result template. Fill the checks by walking every acceptance criterion. Each check cites the diff, a test you ran, or a command output. A criterion with no evidence is a failure.

2. Set the verdict:

   - `pass` when every criterion has evidence and the diff stays inside the allowed files and the stated scope.
   - `fail` when a criterion is missed, the diff leaves the allowed files, or a check you ran does not match the spec.
   - `disputed` when the diff and the spec disagree with each other in a way you cannot settle, or when a later reading contradicts an earlier pass. Before publishing `disputed`, follow `skills/advisors/SKILL.md` for `verify_tiebreak` and include the critique. If the advisor cap is already spent, keep `disputed` and follow `skills/escalate/SKILL.md`.

3. On `pass`, set the chunk status to `verified` and tell the orchestrator to follow `skills/pick-next-task/SKILL.md`.

4. On `fail`, write the failure summary into the result file. Read `verify.max_failures_before_escalation` from `fstack.yaml` (the shipped value is `2`). Compare it to the chunk's `attempt`.

   - Below the cap: set the chunk status to `failed` and tell the orchestrator to follow `skills/implement-chunk/SKILL.md`. The next implement prompt may include this failure summary. It still must not include implementer notes.
   - At the cap: set the chunk status to `escalated` and follow `skills/escalate/SKILL.md`.

5. Show the human a verdict only when you need a decision or the stack is done. Rewrite that message with `skills/tldr/SKILL.md`. A routine pass is reported to the orchestrator and recorded in `decisions.md`.

## Writes

- `prompts/verify.md`
- `verification/<chunk-id>.md`
- the chunk status
- `decisions.md`

## Next

`pick-next-task` on pass, `implement-chunk` on a retryable fail, `escalate` on a repeated fail or an unresolved dispute.
