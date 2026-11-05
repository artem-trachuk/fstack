# Prompt: gap-analysis

Feature: {{feature}}

Compare the sources you were given. Each source has a kind and text. Some kinds are authoritative. Do not assume a product name for a kind.

One coverage row per item. For each source, record whether the item is present, partial, or absent, and the evidence.

Classify from the roles: done, partial, missing, conflict, needs_decision, undocumented. Only partial and missing are buildable. A conflict or a needs_decision row waits for a human. Do not write to a source.

## Requirements

{{requirements}}

## Questions so far

{{open_questions}}

## Commit

{{shas}}
