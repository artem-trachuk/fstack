# Feature state

Feature state lives in Notion, in the shape described in `DESIGN.md`. This file is not a copy of that state.

Only the Orchestrator reads and writes Notion. Coding agents, the verifier, and advisors receive excerpts in their prompts. If Notion is unreachable, the unsaved content is shown in chat and is not stored on disk.

A coding agent receives the chunk spec in its launch prompt. The verifier receives its prompt and patch from the Orchestrator. Advisor inputs are written to Notion by the Orchestrator. Pull request text is a summary of the code change. It does not include implementer notes, advisor critiques, or verify prompts.
