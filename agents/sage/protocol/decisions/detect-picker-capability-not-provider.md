---
id: detect-picker-capability-not-provider
type: team_decision
title: Detect picker capability, not provider
domain: protocol
tags: [checklist, picker, portability, interaction]
status: proposed
enforcement: warn
applies_to: [protocol, "AGENTS.md", "agents/sage/commands/sage*.md"]
source: ai
supersedes: ""
related: [continue-until-material-gate]
timestamp: 2026-07-30T00:00:00Z
---

Choose checklist UX from callable session capabilities, never from the provider
name. Prefer native multi-select, then structured single-select with
Recommended/Defaults/Customize, then compact keyword/exception input.

`mode:auto` never opens a picker. Do not promise host-native checkboxes from a
Markdown protocol when the host does not expose a multi-select tool.
