# Feature state

fstack does not commit this tree and does not push it. The only published artifacts are pull requests that contain the code change.

When `/cursor/stores/self` is mounted, the same tree lives at `fstack/features/<name>/` inside that store. This folder is the fallback used when no store is mounted. It stays on one machine.

```
features/<name>/
  feature.yaml
  requirements.md
  questions.md
  plan.md
  decisions.md
  advisors.md
  advisors/inputs/
  advisors/outputs/
  events/<nnnn>-<event>.yaml
  chunks/<NN-slug>.md
  prompts/<NN-slug>/a<attempt>/<action>.md
  verification/<NN-slug>/a<attempt>.yaml
  diffs/<NN-slug>/a<attempt>.diff
```

A coding agent receives the chunk spec in its launch prompt. It does not read this tree from git. Pull request text is a summary of the code change. It does not include implementer notes, advisor critiques, or verify prompts.
