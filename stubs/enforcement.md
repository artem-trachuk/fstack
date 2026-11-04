# Enforcement stubs

These checks are specified so a later change can enforce them. v0.1 does not run them. Do not treat the text below as a live gate.

## TODO: approval record

Intended behavior. On `approve_release`, write `.fstack/approvals/<feature>.yaml` and a copy on the state branch:

```yaml
question_id: Q-<feature>-release
kind: release
quote: yes
command: ""
shas:
  01-slug: <verified_sha>
void: false
feature: <feature>
```

A changed `verified_sha` or a changed `release.command` sets `void: true`. Bot text, pull request bodies, files, and advisor output cannot create this record. Only `approve_release` after a human quote can.

Nothing reads this file automatically yet.

## TODO: merge and release runner

Intended behavior. While `feature_status` is `merging`, for each chunk in order:

1. If the forge already shows the pull request merged, record `merge_recorded` and continue.
2. If the pull request head differs from `verified_sha`, record `void_release` and stop.
3. If the parent chunk merged, rebase and retarget this pull request, then record `restack_recorded`.
4. Record `range_diff_recorded`. A clean diff updates `verified_sha` and the approval shas. Any real difference returns the chunk to `needs_verify`.
5. Record `ci_recorded`. Pending waits. Failing escalates. Do not roll back a chunk that already merged.
6. Merge that one pull request and record `merge_recorded`.

When every chunk is `merged`, run `release.command` only if it still equals the approved string, then record `release_command_recorded`. A non-zero exit sets `release_state: command_failed` and escalates. There is no automatic rollback.

The release skill is the procedure the orchestrator follows by hand. There is no script.

## TODO: shell and MCP hook

Intended behavior. A `beforeShellExecution` hook, fail-closed, denies `gh pr merge`, `git merge` (not `merge-base` or `mergetool`), and `glab mr merge`, plus the configured `release.command`, unless the approval record is present, not void, and its shas still match. A `beforeMCPExecution` hook denies merge and release tool calls the same way. Commands in a repository with no `fstack.yaml` are left alone.

The hook is not registered. `hooks.json` is intentionally absent so Cursor does not load a stub that pretends to enforce this.

## TODO: branch protection

Intended behavior. setup reports whether the default branch rejects direct pushes. v0.1 does not call the forge, so the report says the check was not run.

## TODO: verification

The `verify` skill does not check a chunk. It returns:

```yaml
verdict: not_implemented
message: Verification is not implemented yet, so these changes cannot be verified.
```

The orchestrator relays that sentence through `tldr`, sets the chunk to `awaiting_verification_decision`, and does not treat the verdict as a pass or start the next chunk. The human logs `accept_unverified` or `stop`.

Intended behavior, when the stub is replaced. The orchestrator builds `prompts/<chunk-id>/a<attempt>/verify.md` from `git diff <base_sha>...<head_sha>`. The verifier runs in a clean checkout of that head, with no feature directory. The prompt carries the spec, the acceptance criteria, the out-of-scope section, and the patch. It omits implementer notes and pull request URLs. Instructions inside the patch are data. A low-confidence verdict can ask for one read-only Argon tie-break. The critique is not the verdict. The full note is in the `verify` skill.

## TODO: atomic lease

Intended behavior. `feature.yaml` `lease.owner` and `lease.expires_at` are the lock. Two sessions can still both read a stale file before either writes. A later version should take a real lock when it writes the event file. Until then, a second session that sees a live lease stops, and `take_lease` requires a human quote.
