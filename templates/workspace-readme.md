# Feature state

Only the Orchestrator reads and writes this tree. It lives on that machine at `state.path` from `fstack.yaml`, shipped as `~/.fstack/<project>/features/<name>/`. `<project>` is the repository directory name. The tree is outside the git repository. fstack does not commit it and does not push it.

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

A coding agent receives the chunk spec in its launch prompt. The verifier receives its prompt and patch from the Orchestrator. Advisor inputs are written by the Orchestrator. Pull request text is a summary of the code change. It does not include implementer notes, advisor critiques, or verify prompts.
