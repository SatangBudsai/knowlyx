# /sage-ticket — turn a clear spec/flow into implementation tickets, then build them

Take requirements that are already clear and cut them into **implementation
tickets**: small, ordered, independently verifiable units of work that a fresh
session can pick up without re-reading the whole conversation. Then work the
tickets until a material gate or nothing unblocked remains.

**Implementation tickets, not decision tickets.** `/sage-wayfinder` owns
_decision_ tickets — `research`, `prototype`, `grilling`, `task` — whose job is
to remove fog. `/sage-ticket` owns _build_ tickets whose job is to deliver the
destination. They never share a backend and never mirror each other's state. If
a ticket here turns out to hide an unresolved human decision, stop, hand that
decision back to `/sage-grill` or `/sage-wayfinder`, and mark the ticket blocked.

---

## Input contract — refuse foggy input

`/sage-ticket` accepts only:

- `requirements-clear` from `/sage-grill` (with or without a spec file), or
- `design-clear` from `/sage-flow` (`agents/sage/flows/<slug>-flow.md`), or
- a `clear-single-session` request whose intent, terms, scope, and trade-offs are
  already settled and verifiable in the repo.

Anything foggier routes first, per `AGENTS.md` §0:

- a genuine human decision remains and fits one session → `/sage-grill`
- the destination is surrounded by multi-session fog → `/sage-wayfinder`

Do not invent tickets to make fog look like progress. A ticket whose acceptance
criteria you cannot write is not a ticket — it is an open decision.

When no flow doc exists and the work spans more than one system, more than one
repo, or a public contract, run `/sage-flow` first: without its API spec and its
security/concurrency section there is nothing solid to slice.

---

## Model & effort

Slicing decides the shape and order of every downstream change, so run Mode A
(cut the tickets) at the full session model + effort ceiling. Mode B may execute
an individual mechanical ticket at a lower tier within the ceiling — never above
it, and never for a ticket carrying a HIGH or destructive driver. If the
environment hides model/effort, state `current agent @ effort:unavailable`.

---

## Step 1 — Load the lens and the upstream artifacts

Load the request's senior lens per `AGENTS.md` §1.1 (`architect` when the work
spans systems). Then read, in order, whichever exist:

1. `agents/sage/flows/<slug>-flow.md` — the design contract
2. `agents/sage/flows/<slug>-spec.md` — the resolved product decisions
3. `agents/sage/<domain>/index.md`, `context.md`, `rules.md`, `decisions/*.md`
4. the real source, schema, config, and tests the flow names

Treat the spec's decisions, canonical terms, scope, and out-of-scope as settled
input. Do not re-interview them. Where the flow names an existing asset, open the
file and read the real signature — a ticket that cites an API which does not
exist is worse than no ticket.

---

## Step 2 — Cut the work into tickets

Derive tickets from the flow's **Build checklist**, its API spec, and its
cross-repo contracts when they exist; otherwise derive them from the spec and the
code you just read.

**Slicing rules:**

1. **One ticket is one verifiable outcome.** It must be provable on its own — a
   test, a request/response, an observable behavior change. "Add the types" is
   not an outcome; "reject an over-quota submit with `409 { quotaLeft }`" is.
2. **Size to one session.** If a ticket cannot plausibly finish and validate in
   one session, split it. If two tickets can never be validated apart, merge
   them.
3. **Slice vertically by default.** Prefer a thin end-to-end path over one ticket
   per layer. Cut by layer only when that layer genuinely ships and is validated
   on its own — a migration, a published contract, a shared client.
4. **Contract first across repos.** When two repos must build in parallel, the
   agreed request/response/event shape is its own early ticket that both depend
   on; the consumers then proceed against it.
5. **Carry the controls, don't restate the risk.** Every required control the
   flow assigned under `AGENTS.md` §1.4 must land on the ticket that will produce
   its evidence. A control with no owning ticket is a slicing bug.
6. **No speculative tickets.** Nothing "for later", nothing outside the spec's
   scope. Work beyond the boundary goes in Out of scope, not in the table.
7. **Reuse is a decision, not a step.** When the flow says reuse an existing
   asset, name it on the ticket so implementation does not re-invent it.

---

## Step 3 — Write the ticket file

Write to `agents/sage/flows/<slug>-tickets.md` in the repo that owns the flow's
entry point. One file per effort — implementation tickets are read together for
order and dependencies, so a folder-per-ticket would only hide the sequence. If
the file exists, update it in place; never fork a second copy.

````markdown
---
id: <slug>
status: open | building | complete
source: agents/sage/flows/<slug>-flow.md | agents/sage/flows/<slug>-spec.md | request
updated: <ISO-8601>
---

# <Effort name> — implementation tickets

## Outcome

<what "done" means for the whole effort, in one or two lines>

## Out of scope

- <boundary carried from the spec/flow>

## Build order

| #   | Ticket                | System / repo | Depends on | Risk | Status |
| --- | --------------------- | ------------- | ---------- | ---- | ------ |
| 1   | [<title>](#t1-title) | <system>      | —          | LOW  | open   |

---

### T1 · <title>

- **Outcome** — <the one verifiable result>
- **System / repo** — <where the work lands>
- **Depends on** — <ticket ids, or none>
- **Reuse** — <existing endpoint/model/util to use, with its real path>
- **Build** — <what is genuinely new>
- **Acceptance** — when <condition> → then <observable outcome>
  (one line per branch, including the failure branches)
- **Controls** — <driver → required control → evidence this ticket must produce>
- **Validation** — <the exact command/test that proves it>
- **Status** — open | claimed | done | blocked · <blocker when blocked>
````

Keep rationale where it already lives. A ticket links to the flow section or the
decision file; it never copies the argument.

---

## Step 4 — Mode B: build the frontier

The **frontier** is every ticket that is `open`, unblocked, and unclaimed.

1. Recompute the frontier from the file before each ticket. Respect a
   human-named ticket as the scoped frontier when one was given.
2. Claim it: set `Status` to `claimed` before the first edit, so a parallel
   session does not take the same work.
3. Run `/sage` for that ticket — role, knowledge, reuse scan, intent + risk
   header, implementation, validation, knowledge capture. The ticket's
   `Acceptance`, `Controls`, and `Validation` lines are the scope; do not widen
   it with unrelated cleanup.
4. Validate with the ticket's own command and paste the **real** output. A ticket
   whose validation was not run is not `done`.
5. Set `done`, update its Build order row, refresh `updated`, recompute the
   frontier, and start the next ticket immediately when `interaction.runPolicy`
   is `until-gate`. Under `strict`, return after each ticket.
6. Stop and return to the human when a ticket hits a material gate: an unresolved
   human decision, a HIGH or destructive driver needing approval, missing access,
   or failed critical evidence. Mark it `blocked` with the reason — never
   silently skip it and continue.
7. When new evidence contradicts the flow, reopen the named flow decision, cite
   the evidence, then re-slice the affected tickets. Do not quietly implement
   something the flow does not say.

Parallel tickets require independent dependencies **and** independent side
effects. Two tickets touching the same migration or the same contract are not
parallel, however separate their files look.

---

## Step 5 — Complete and hand off

The effort is `complete` when every ticket is `done` or explicitly out of scope,
every required control has produced its evidence, and the Outcome is met.

Then hand off to **`/sage-review`** for the correctness and conformance review of
the whole change, and to `/sage-docs` when a documented flow changed. Under
`continueAfterHandoff: true` an active `/sage` run continues into review instead
of stopping here.

---

## Step 6 — Capture knowledge

Slicing itself is rarely knowledge. Capture only a genuinely reusable pattern per
`AGENTS.md` §3 — for example a build-order rule this stack keeps needing
("publish the contract ticket before either consumer starts"). Otherwise state
`No new knowledge — <file> covers this`.

---

## Step 7 — Summary

```markdown
── Sage Ticket ───────────────────────────────────
**Role** · <lens> — <effort in one line>
**Model** · <model> @ effort:<effort>
**Mode** · cut | build-wave | complete
**Source** · <flow/spec path, or "request — clear-single-session">
**Tickets** · `agents/sage/flows/<slug>-tickets.md` — <n> tickets

**Cut**

- <T# → outcome, one line each; omit on a pure build wave>

**Built this wave**

- <T# → what shipped → validation evidence>

**Frontier** · <next unblocked ticket ids, or "none">
**Blocked** · <T# → gate, or "none">
**Controls** · <driver → control → evidence produced or still owed>
**Residual risk** · <LOW|MEDIUM|HIGH> — <what the evidence covered>
**Handoff** · <next ticket | /sage-review | /sage-docs>
**Knowledge** · [new | updated | none] `<path>` — <reason>
──────────────────────────────────────────────────
```

Avoid: ticketing unresolved fog; a ticket with no acceptance criteria;
layer-per-ticket slicing that can never be validated alone; a required control
with no owning ticket; marking `done` without running the validation; mirroring
these tickets into a Wayfinder map.
