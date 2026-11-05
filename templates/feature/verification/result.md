# Verification: {{chunk_id}} attempt {{attempt}}

The orchestrator writes this file from the verifier's reply. The verifier does not write it.

v0.1 receives this and does not judge the chunk:

```yaml
chunk: {{chunk_id}}
attempt: {{attempt}}
verdict: not_implemented
message: Verification is not implemented yet, so these changes cannot be verified.
base_sha:
head_sha:
applied: false
```

`not_implemented` is not a pass. The orchestrator sets `awaiting_verification_decision`, relays the message through `tldr`, and waits for a logged `accept_unverified` or `stop`.

`applied: false` means the verdict is filed and the chunk status has not been updated yet. The orchestrator applies it and sets `applied: true` in the same turn.
