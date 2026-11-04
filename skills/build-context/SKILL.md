---
name: build-context
description: >
  Write the prompt for one fstack action into the feature's prompts folder.
  Use at the start of every action, before gap analysis, splitting, handoff, verification, advice, escalation, or release.
  The verify prompt includes the spec, acceptance criteria, and diff source, and excludes implementer notes.
---

# Build context

Every action gets a fresh prompt file under the feature before it runs. The prompt carries this feature's facts. The skill file carries the procedure.

## When to use

You are about to run one of these actions: `collect-requirements`, `gap-analysis`, `split-into-chunks`, `pick-next-task`, `implement-chunk`, `verify`, `advisors`, `escalate`, `release`.

## Steps

1. Find the plugin root, the directory that contains `.cursor-plugin/plugin.json` with `"name": "fstack"`. Read `templates/prompts/<action>.md` from that root.

2. Fill tokens from the feature folder. Replace a missing value with `(none)`.

   | Token | Source |
   | --- | --- |
   | `{{feature}}` | feature slug |
   | `{{feature_dir}}` | `<workspace>/<feature>` |
   | `{{chunk_id}}` | chunk id, or `(none)` when the action has no chunk |
   | `{{chunk_title}}` | chunk title |
   | `{{spec}}` | the chunk Spec section |
   | `{{acceptance_criteria}}` | the chunk Acceptance criteria section |
   | `{{allowed_files}}` | the chunk allowed files |
   | `{{stack_base}}` | the chunk base branch |
   | `{{branch}}` | the chunk branch |
   | `{{requirements}}` | `requirements.md` |
   | `{{open_questions}}` | unanswered questions, or the answered file when the action is later than gap analysis |
   | `{{plan}}` | `plan.md` |
   | `{{diff_source}}` | `base...branch`, or the pull request URL when that is the diff |
   | `{{attempt}}` | chunk attempt |
   | `{{failure_summary}}` | latest verification failure summary, else `(none)` |
   | `{{advisor_name}}` | advisor id when the action is `advisors` |
   | `{{artifact}}` | path the advisor is reading |
   | `{{release_plan}}` | the plan's Release section |
   | `{{pull_requests}}` | stack pull requests in order |

3. For the `verify` action, build those token values with implementer notes removed first.

   - Drop every markdown section titled `Implementer notes`, including its body, before you fill `{{spec}}` or any other token.
   - Do not read `prompts/implement-chunk.md` while filling the verify prompt.
   - Do not paste the coding agent's rationale, a pull request section titled Implementer notes, or a previous implement prompt.
   - The verify template has no slot for those notes. Do not add one.

4. Write the filled prompt to `<workspace>/<feature>/prompts/<action>.md`, replacing the previous file for that action.

5. Return that path to the caller. The caller follows its skill with this file as the feature context.

## Writes

`<workspace>/<feature>/prompts/<action>.md`

## Next

Return to the skill that called you. This skill does not pick the next task.
