# Plan: {{feature}}

## Summary

## Stack

Chunks in one code location stack on each other. The first chunk in a location is based on that location's default branch. Each later chunk in that location is based on the previous chunk's branch there. A dependency in another location does not change the git base. One chunk is implemented at a time.

Chunk id, status, branch, and allowed files live in the chunk page properties.

## Release

What a production update means here. Leave this blank when merging the approved stack is the whole release. The text here is what `release.command` must match if a command is set.

## Risks
