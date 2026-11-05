# Prompt: gap-analysis

Feature: {{feature}}

Compare the sources against the product graph. The graph is the current product truth. Do not re-read code the graph already covers. Do not assume a product name for a source kind.

One coverage row per item. Set the Node relation when a graph node exists. For each source, record whether the item is present, partial, or absent, and the evidence.

Classify from the roles: done, partial, missing, conflict, needs_decision, undocumented. Only partial and missing are buildable. A conflict or a needs_decision row waits for a human. Do not write to a source.

## Sources

{{sources}}

## Graph

{{graph}}

## Requirements

{{requirements}}

## Questions so far

{{open_questions}}

## Commit

{{shas}}
