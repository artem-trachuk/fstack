---
name: setup-project
description: >
  Initialize a project for fstack and check the configured Cursor model names.
  Use when fstack.yaml is missing, when models.resolution is pending, or when
  the human asks to set up fstack or recheck models. Falls back to the parent
  Cursor model when a configured family is not available in this session.
---

# Setup project

Prepare the current project so the other fstack skills can run. Model names in the config are Cursor models. This skill checks them against the models this session can actually use.

## When to use

- The project has no `fstack.yaml`.
- `models.resolution` is `pending` or `unresolved`.
- The human asks to set up fstack or to recheck models.

## Plugin root

The plugin root is the directory that contains `.cursor-plugin/plugin.json` whose `name` is `fstack`. When this skill file was loaded from the plugin, that root is two directories above this file. Otherwise search the workspace and the installed Cursor plugin directories for that manifest. Use the root you found for templates. Do not hardcode a machine path or a home directory.

## Steps

1. If the project root has no `fstack.yaml`, copy the plugin's `fstack.yaml` there. The project root is the repository you were asked to work in.

2. Read `fstack.yaml`. Refuse to continue when `workspace` is absolute or contains `..`. The shipped value is `features`.

3. Restore human gates when someone has weakened them. Set `merge`, `release`, and `outward_messages` back to `require_approval`, and set `collect_requirements` back to `manual_only`. Tell the human which keys you restored.

4. Create the workspace directory if it is missing. Copy `templates/workspace-readme.md` from the plugin to `<workspace>/README.md` when that file is absent.

5. Detect Cursor model slugs. Use the slugs this session can pass to a Cursor subagent. If Cursor exposes a models list, prefer that list. If you cannot detect any slugs, set `models.resolution` to `unresolved`, leave `models.resolved` empty, and tell the human. Do not invent a slug.

6. Resolve each short name in `models` (`opus`, `argon`) and each `roles.*.model` that uses a short name or a slug.

   A family prefix has no effort token. The effort tokens are `max`, `xhigh`, `high`, `medium`, and `low`. A trailing `-fast` is not part of the family. `claude-opus-5-5` is a prefix. `claude-opus-5-5-xhigh` is a full slug.

   - Exact slug: use it when it is in the detected set.
   - Prefix: take detected slugs in that family. For `opus`, prefer effort `xhigh`, then the nearest available on the ladder `max`, `xhigh`, `high`, `medium`, `low`. For `argon`, prefer `high`, then the highest effort at or below `high`, then any remaining argon slug.
   - Family missing: set the resolved value to `inherit` and record a one-line reason under `models.fallbacks`.

   `inherit` is always valid. It means the role or advisor runs on the Cursor model of the parent chat, with no model override.

7. Write the results back into `fstack.yaml`. Keep the `advisors` block's `model` values as the short names `opus` and `argon`. Write slugs only under `models.resolved`. Set `models.resolution` to `resolved` when every short name got a slug or an explicit `inherit` fallback. Set it to `unresolved` when no slug list was available.

8. Tell the human which models resolved, and any fallback to `inherit`.

## Writes

- `fstack.yaml`
- `<workspace>/README.md` when it was absent

## Next

When the human invoked `/setup-project` directly, stop. Tell them the next step is `/collect-requirements` when they want to start a feature. When `collect-requirements` or the orchestrator sent you here, return to that skill. This skill never starts requirements collection on its own.
