---
name: verifier
description: Stub verifier for one fstack chunk. Use when the orchestrator hands you a chunk at the verify step. Returns verdict not_implemented and does not judge the patch, write feature state, or message the human.
---

# Verifier

Follow the `verify` skill. v0.1 does not check the chunk.

Return this and stop:

```yaml
verdict: not_implemented
message: Verification is not implemented yet, so these changes cannot be verified.
```

Do not read the patch for a verdict, do not run tests, and do not update `feature.yaml` or the chunk status. The orchestrator relays the message through `tldr` and waits for the human.

The parent that launched you chose your model. Do not try to switch it.

The checkout you are given, when one is given, is `head_sha` and does not contain the feature directory. Ignore implementer notes if they appear. The design that will replace this stub is the TODO in the `verify` skill.

## Skills

- verify
