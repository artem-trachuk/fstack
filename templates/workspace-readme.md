# Feature workspace

Per-feature state is not stored on the chunk branches.

`state.backend: git` keeps it on `fstack/<feature>/state`, in a worktree under `.fstack-worktrees/<feature>/`. Chunk branches do not contain that branch.

`state.backend: local` keeps it in `.fstack/local/<feature>/`. That copy stays on one machine. setup says so.

```
features/<name>/
  feature.yaml
  requirements.md
  questions.md
  plan.md
  decisions.md
  advisors.md
  events/<nnnn>-<event>.yaml
  chunks/<NN-slug>.md
  prompts/<NN-slug>/a<attempt>/<action>.md
  verification/<NN-slug>/a<attempt>.yaml
  diffs/<NN-slug>/a<attempt>.diff
```

The verify prompt is built by the orchestrator. It does not include a feature directory or a pull request URL.
