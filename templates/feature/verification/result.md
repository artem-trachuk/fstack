# Verification: {{chunk_id}} attempt {{attempt}}

The orchestrator writes this file from the verifier's reply. The verifier does not write it.

```yaml
chunk: {{chunk_id}}
attempt: {{attempt}}
verdict: pass
confidence: high
base_sha:
head_sha:
checks: []
failure_summary:
ignored_extra_context: false
applied: false
```

`applied: false` means the verdict is filed and the chunk status has not been updated yet. The orchestrator applies it and sets `applied: true` in the same turn.
