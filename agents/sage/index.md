# Sage knowledge

This folder is your team's knowledge — the rules and decisions Sage's agent
reads when `/sage` is explicitly invoked (see [`AGENTS.md`](AGENTS.md)).

**It starts empty on purpose.** Add domains as your project needs them — there
are no generic, pre-baked rules to delete. Sage's agent also fills this in for
you: when you state a rule in chat, it writes one here as `status: proposed`.

## Layout

```text
agents/sage/
  index.md                  # this file
  commands/<name>.md        # canonical command bodies — the tool adapters point here
  docs-style-template.md    # the /sage-docs + /sage-flow markdown style-guide
  flow-workspaces.md        # canonical layout, evidence ladder, legacy migration
  flows/<slug>/             # all artifacts for one effort
    index.md                # human entry point and artifact/evidence map
    spec.md                 # resolved product decisions from /sage-grill
    flow.md                 # implementation-ready design from /sage-flow
    tickets.md              # ordered implementation tickets from /sage-ticket
    evidence/               # indexed screenshots, traces, and focused logs
  wayfinders/<slug>/        # durable map + decision tickets for multi-session fog
  roles/role-<lens>.md      # compact senior lenses — see AGENTS.md §2
  <domain>/                 # e.g. billing, search, your own domains
    context.md              # canonical glossary, created lazily
    rules.md                # the domain's standing rules
    decisions/<slug>.md     # one team decision per file
```

`commands/` holds every Sage command in full, once; the per-tool files under
`integrations/` are thin pointers to it, so editing a command in one place
updates every agent.

`flows/risk-controls-flow.md` defines the current end-to-end contract for turning
risk drivers into required controls, validation evidence, and residual risk.
`flows/pre-action-clarification-flow.md` defines when Sage asks before acting and
when an actionable direct instruction or evidenced bug fix proceeds immediately.
`flows/installer-managed-assets-flow.md` defines the exact install/upgrade
ownership and preservation contract. `flows/project-dna-flow.md` defines the
specified (not yet shipped) Project DNA cognition data plane.

Flat `flows/*.md` files are installer-managed reference flows or legacy user
artifacts. New Grill/Flow/Ticket output uses `flows/<slug>/`; existing user files
are migrated only when next updated, according to
[`flow-workspaces.md`](flow-workspaces.md). The installer never recursively
replaces or moves flow directories.

`roles/` is Sage's library of compact senior lenses: Expertise, Pitfalls, and How
I work. Approved roles are binding; newly AI-created roles start as
`status: proposed`. Roles describe domain failure modes, not approval gates,
version facts, paths, or reusable assets.

[`installed-assets.md`](installed-assets.md) lists the exact files the official
installer owns and refreshes. All unlisted knowledge and flow paths remain
team-owned.

## Example entry

`agents/sage/billing/decisions/use-ledger-service.md`:

```markdown
---
title: Use the Ledger service for money movement
domain: billing
status: approved
enforcement: block
applies_to: [billing, "billing/**"]
source: human
---

All money movement goes through `ledger.transfer()`. Never call the payment
provider SDK directly — it bypasses our audit trail.
```

Edit a file, commit, done — the agent follows your team's version.

## Domains

- [sage-product](sage-product/) - Sage product architecture, Project DNA, and cognition data governance.
- [protocol](protocol/) - Sage cognition policy, risk controls, and cross-command contracts.
