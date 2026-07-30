---
id: prepare-dna-before-runtime-reasoning
type: team_decision
title: Prepare DNA before runtime reasoning
domain: product
tags: [project-dna, preparation, cache, performance]
status: proposed
enforcement: warn
applies_to: [product, "project-dna/**"]
source: ai
supersedes: ""
related: [separate-control-plane-from-dna-data-plane]
timestamp: 2026-07-30T00:00:00Z
---

Build Project DNA progressively when a project is first opened, then serve
request-time cognition from the active snapshot and refresh only the facets
affected by changed inputs. Repository-wide rescanning on every request is a
fallback reconciliation path, not the normal runtime flow.

Event watchers improve latency but do not prove correctness. Source
fingerprints, detector versions, and periodic reconciliation own freshness, and
readers continue using the last complete snapshot while a refresh is running.
