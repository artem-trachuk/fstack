---
name: split-into-chunks
description: >
  Turn a feature with answered questions into small stacked chunks a verifier can check.
  Use when questions.md is answered and plan.md does not yet list the chunks.
  Runs the planner_review advisor on the draft plan, then hands off to pick-next-task.
---

# Split into chunks

Turn the feature into a stack of small chunks. Each chunk is one branch, one pull request, and one verification.

## When to use

`questions.md` has status `answered`, and the plan does not yet name the chunks. Use it again when the human changes scope and the chunk list has to be rewritten before the next implementation.

## Chunk shape

Each chunk file is copied from `templates/feature/chunks/chunk.md` into `chunks/NN-slug.md`.

- `NN` starts at `01` and matches stack order.
- The first chunk depends on nothing and is based on the repository default branch.
- Each later chunk depends on the previous chunk and is based on that chunk's branch.
- Spec and acceptance criteria are specific enough to judge from the diff alone.
- Allowed files are concrete paths or globs. A chunk that needs the whole repository is too big; split it.
- Out of scope names the neighboring work this chunk will not do.
- The Implementer notes section stays empty here. The coding agent may fill it later. Verification does not read it.

One chunk at a time is the v0.1 rule. Do not plan two chunks that would be implemented in parallel.

## Steps

1. Read `requirements.md` and the answered `questions.md`. Follow `skills/build-context/SKILL.md` for `split-into-chunks`.

2. Write `plan.md`: summary, the stack table, risks, and a Release section. The Release section says what "push to production" means in this project. Leave the command empty when merging the approved stack is the whole release, and say that in the section.

3. Write the chunk files from `templates/feature/chunks/chunk.md`. Fill the id, title, spec, acceptance criteria, out of scope, and allowed files. Set `depends_on`, `base`, and status `planned`. Leave Implementer notes empty. The orchestrator owns these files. The coding agent does not commit the feature workspace.

4. Follow `skills/advisors/SKILL.md` for `planner_review` on the plan and the chunk specs. Apply a critique that makes a chunk smaller, testable, or correctly ordered. Record the call.

5. Follow `skills/tldr/SKILL.md` and show the human the chunk list: id, title, and what each one proves. The human reviews the pull requests before release. If the human interrupts with a plan change before the handoff, revise the plan and run this skill again. Otherwise follow `pick-next-task`.

## Writes

- `plan.md`
- `chunks/NN-slug.md`
- `prompts/split-into-chunks.md`
- `advisors.md` when the advisor ran

## Next

Follow `skills/pick-next-task/SKILL.md`.
