---
id: continue-until-material-gate
type: team_decision
title: Continue until a material gate
domain: protocol
tags: [continuation, autonomy, handoff, wayfinder]
status: proposed
enforcement: block
applies_to: [protocol, "AGENTS.md", "agents/sage/commands/**"]
source: ai
supersedes: ""
related: [risk-drivers-own-controls, route-by-fog-and-session-span]
timestamp: 2026-07-30T00:00:00Z
---

Treat completion of a command, ticket, checkpoint, handoff, or phase as a state
transition, never a terminal condition while safe unblocked work remains.
The active parent run recomputes its frontier and continues immediately.

Return to the human only for a material decision, central risk gate, missing
access/manual external action, failed critical control, rejection, or true
completion. Child commands return clear/spec-ready/design-clear handoffs to the
parent instead of ending the run.
