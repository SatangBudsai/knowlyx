---
id: separate-control-plane-from-dna-data-plane
type: team_decision
title: Separate the control plane from the DNA data plane
domain: sage-product
tags: [project-dna, tools, protocol, compatibility]
status: proposed
enforcement: warn
applies_to: [sage-product, "AGENTS.md", "project-dna/**"]
source: ai
supersedes: ""
related: [prepare-dna-before-runtime-reasoning]
timestamp: 2026-07-30T00:00:00Z
---

Keep Sage's route, risk, control, and human-gate policy in a portable control
plane while Project DNA becomes the structured data plane for prepared
architecture, workflow, design, reuse, and impact context.

The target runtime queries tools rather than reparsing Markdown for computed
DNA. Until that runtime passes compatibility, security, and quality gates, the
shipped Markdown protocol remains the honest fallback; adapters must never fork
cognition policy or claim unavailable automation.
