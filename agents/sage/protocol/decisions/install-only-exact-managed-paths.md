---
id: install-only-exact-managed-paths
type: team_decision
title: Install only exact managed paths
domain: protocol
tags: [installer, upgrade, preservation, distribution]
status: proposed
enforcement: block
applies_to: [protocol, "install.sh", "install.ps1", "agents/sage/*-manifest.txt"]
source: ai
supersedes: ""
related: [risk-drivers-own-controls]
timestamp: 2026-07-30T00:00:00Z
---

Installer upgrades may overwrite or delete only exact Sage-owned paths declared
in the shared install and adapter manifests. Broad name globs or recursive
cleanup outside the commands directory are forbidden because user knowledge,
flows, docs, and adapter files may share Sage-like names.

Preflight every manifest entry and selected adapter before the first target
write. Reject rooted/traversal paths and preserve all unlisted files across both
fresh installs and upgrades.
