---
name: setup-project
description: >
  Initialize a project for fstack and resolve Cursor model names into .fstack/resolved.yaml.
  Use when fstack.yaml is missing, when .fstack/resolved.yaml is missing, or when the human asks to set up fstack or recheck models.
---

# Setup project

Prepare the project. Do not write session model slugs into `fstack.yaml`.

## When to use

- The project has no `fstack.yaml`.
- `.fstack/resolved.yaml` is missing.
- The human asks to set up fstack or to recheck models.

## Plugin root

The plugin root is the directory that contains `.cursor-plugin/plugin.json` whose `name` is `fstack`. Templates and `state/transitions.yaml` are read from that root, or from `.fstack/templates/` after this skill copies them. Do not hardcode a machine path.

## Steps

1. If `fstack.yaml` is missing, copy the plugin's `fstack.yaml` into the project root. If it exists, leave it. Do not rewrite it to store resolved slugs.

2. Read `fstack.yaml`. Stop if `version` is not `0.1` or `state_version` is not `1`, and say the project must be migrated. Stop if `workspace` is absolute or contains `..`. Stop if `human_gates` differs from merge, release, and outward_messages `require_approval`, or `collect_requirements` `manual_only`. Do not silently change those keys.

3. Copy the plugin `templates/` tree to `.fstack/templates/` and write `.fstack/install.json` with the plugin version from `.cursor-plugin/plugin.json` and `state_version: 1`. Copy `templates/workspace-readme.md` to `<workspace>/README.md` when that file is absent.

4. Make sure `.gitignore` ignores `.fstack/resolved.yaml`, `.fstack/approvals/`, `.fstack/local/`, and `.fstack-worktrees/`. Do not ignore `.fstack/templates/`. Gitignore is not what keeps state off chunk branches. The state branch does that.

5. Resolve models into `.fstack/resolved.yaml` using `templates/resolved.yaml`. Detect the Cursor slugs this session can pass to a subagent. If you cannot detect any, set each model to `inherit`, set `source` to `unresolved`, and say so. Do not invent a slug.

   For `opus` and `argon`, walk `models.<name>.match`, then walk `effort` in list order. A slug matches a prefix when it equals the prefix or starts with the prefix plus a hyphen. The first detected slug whose effort token matches the next effort in the list wins. If the family exists but no effort matches, use the first family slug and record that under `fallbacks`. If the family is missing, use `inherit` and record why.

6. Role models stay `inherit` unless `fstack.yaml` names `opus` or `argon` for that role. Resolve that short name the same way. The launcher of a subagent reads this file. Agents do not switch their own model.

7. Set `runtime` to `cloud` when this session can start a Cursor cloud agent that opens a pull request against a non-default base. Otherwise set `local_worktree` and tell the human, through the `tldr` skill, that implementers will use a separate worktree. Record the reason in `runtime_note`.

8. For each `advisors.fallback` entry, record availability in `.fstack/resolved.yaml` under `advisor_cli`. Do not rewrite `fstack.yaml`.

   Skip an entry whose `enabled` is not true. The `command` must be a single name with no slash. Reject a path. Find it with `command -v` and keep only the exit status. Do not write the resolved path into the file or the chat.

   For `runtime: claude-cli`, run `<command> auth status` and keep only the exit status. Exit 0 means signed in. Do not print or store the command's output. Do not read token files, environment values, or a keychain. If the status subcommand is missing, mark the entry unavailable.

   Set `available` and `signed_in` from those exit statuses. A local CLI runs under the user's own subscription terms.

9. Branch protection is not checked. Say that the check was not run. See `stubs/enforcement.md`.

## Events

This skill does not record a feature event.

## Next

Stop when the human invoked `/setup-project` directly, and tell them the next step is `/collect-requirements`. When another skill sent you here, return to it. Do not start requirements collection.
