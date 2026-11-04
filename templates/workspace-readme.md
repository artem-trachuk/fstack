# Feature workspace

fstack keeps one folder per feature under this directory. `setup-project` creates the directory. `collect-requirements` creates a feature folder when the human invokes `/collect-requirements`.

```
features/<name>/
  requirements.md    what the human confirmed
  questions.md       open questions and the human's answers
  plan.md            stack summary and the release note
  decisions.md       decisions and quoted approvals
  advisors.md        read-only advisor calls, counted against the cap
  chunks/            one file per stacked chunk
  prompts/           the latest prompt for each action
  verification/      one result per chunk attempt
```

Paths stay relative to the project. The verifier's prompt is `prompts/verify.md`. That file is built without implementer notes.
