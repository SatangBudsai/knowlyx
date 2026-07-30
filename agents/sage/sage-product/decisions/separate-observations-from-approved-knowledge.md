---
id: separate-observations-from-approved-knowledge
type: team_decision
title: Separate observations from approved knowledge
domain: sage-product
tags: [project-dna, provenance, approval, safety]
status: proposed
enforcement: block
applies_to: [sage-product, "project-dna/**"]
source: ai
supersedes: ""
related: [prepare-dna-before-runtime-reasoning]
timestamp: 2026-07-30T00:00:00Z
---

Every DNA claim must be classified as `observed`, `declared`, or `inferred` and
must expose evidence, confidence, scope, freshness, and conflicts. Scanner
heuristics never become binding conventions or business rules automatically.

Observed facts may refresh automatically because they are disposable cache
derived from source. AI-created knowledge may persist only in a non-binding
proposal staging area; an authenticated human must approve an exact revision
before it enters active memory or inheritance.
