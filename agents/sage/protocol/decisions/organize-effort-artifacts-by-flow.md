---
id: organize-effort-artifacts-by-flow
type: convention
title: Organize effort artifacts and debug evidence by flow
domain: protocol
tags: [artifacts, flows, grill, tickets, debugging]
status: proposed
enforcement: warn
applies_to: [protocol, "agents/sage/flows/*/**"]
source: human
supersedes: ""
related: [continue-until-material-gate]
timestamp: 2026-09-08T00:00:00Z
---

Store each effort's spec, flow, implementation tickets, and focused debugging
evidence under one `agents/sage/flows/<flow-slug>/` workspace. Reuse one stable
flow slug across commands and keep its `index.md` as the human entry point.

For visual failures, preserve the smallest useful before/after screenshot and
reuse that evidence before loading full browser state. Escalate only when focused
evidence cannot classify the failure, or when race, auth/session, or
cross-service behavior requires wider inspection. Never capture secrets or PII.

Follow `agents/sage/flow-workspaces.md` for the canonical layout, evidence
catalog, and legacy migration rules.
