---
id: ask-only-when-actionability-is-missing
type: team_decision
title: Ask only when actionability is missing
domain: protocol
tags: [clarification, routing, continuity, bug-fix]
status: proposed
enforcement: block
applies_to: [protocol, "AGENTS.md", "agents/sage/commands/**"]
source: ai
supersedes: ""
related: [route-by-fog-and-session-span, continue-until-material-gate]
timestamp: 2026-07-31T00:00:00Z
---

Run a pre-action clarification pass for every code-changing request, but do not
turn that pass into a mandatory interview. Look up repository facts, auto-decide
only internal reversible preferences, and ask the human only for a missing
material decision whose answer changes the outcome.

Direct bounded instructions and focused bug fixes with enough diagnostic
evidence to begin are actionable: proceed without a ceremonial question.
Errors, stack traces, observed versus expected behavior, failing tests, logs,
reproductions, named locations, and approved acceptance criteria are useful
evidence, not a required template. Ask later only when new evidence exposes a
genuine human-owned branch.

Actionability never weakens central risk gates. HIGH, destructive, irreversible,
and other explicitly gated actions still require their named approval.
