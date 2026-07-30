# /sage-wayfinder — chart and resolve work too foggy for one session

Plan a `large-multi-session` effort as a durable map of decision tickets. Name
the destination, chart only the visible frontier, and resolve every runnable
frontier wave until a material gate or nothing remains to decide before
`/sage-flow` or implementation.

**Plan, don't build.** Tickets answer decisions or unblock decisions; they are
not implementation slices. Wayfinder is a situational routing guard, not the
default spine and not a checklist item. If breadth-first discovery finds no fog,
early-exit to `/sage-grill` or `/sage-flow` instead of creating ceremony.

---

## Model & effort

Run map design and HITL decisions at the full session model + effort ceiling.
Mechanical map/ticket updates may use a lower tier within the ceiling. Never
exceed the session ceiling or downgrade the reasoning that defines destination,
scope, dependencies, or completion.

---

## Step 1 — Load the map's domain and choose one backend

Load `architect`, then relevant domain roles. Read domain `index.md`,
`context.md`, `rules.md`, and relevant decisions before charting.

Choose exactly one canonical backend per effort:

1. **Configured issue tracker** — use only when committed repo instructions name
   the tracker and its map/child/blocking/assignment operations, the required
   tool is available, and external writes are within user scope. Prefer native
   child issues, blocking links, and assignment.
2. **Local Markdown (default)** — when no tracker is configured/available, write
   `agents/sage/wayfinders/<slug>/map.md` and `tickets/*.md`.

Record the backend in the map. Never mirror live state across both; a decision
has one canonical home.

---

## Artifact contract

### Local map — low-resolution index

```markdown
---
id: <slug>
status: charting | active | complete
backend: local-markdown
updated: <ISO-8601>
---

# <Map name>

## Destination
<what clear completion looks like>

## Notes
<domains, skills, standing constraints>

## Decisions so far
- [<closed ticket title>](tickets/<id>.md) — <one-line gist>

## Not yet specified
- <in-scope fog not yet sharp enough to ticket>

## Out of scope
- <work beyond the destination; never graduates>

## Tickets
| Ticket | Type | Mode | Status | Assignee | Blocked by |
| --- | --- | --- | --- | --- | --- |
```

The map is an index, not the answer store. Open tickets appear in its table so a
local backend can derive the frontier; full question/resolution lives only in
the ticket. Refer to tickets by linked title, not bare id.

### Local ticket — one sharp decision

```markdown
---
id: <stable-slug>
title: <human-readable name>
type: research | prototype | grilling | task
mode: HITL | AFK
status: open | claimed | closed | out-of-scope
assignee: ""
blocked_by: []
updated: <ISO-8601>
---

# <Ticket title>

## Question
<one sharp question sized for one session>

## Context
<only facts/pointers needed to work it>

## Resolution
<empty until resolved; answer + evidence/source pointers>

## Assets
<links, never pasted duplicates>
```

---

## Ticket types and human boundary

- **`research` / AFK** — establish facts from code, docs, APIs, or other trusted
  sources. May run in parallel through research subagents when the environment
  permits; each returns evidence/source pointers.
- **`prototype` / HITL** — create a cheap artifact to make behavior/appearance
  concrete, then obtain human reaction. Prototype code is disposable unless a
  later build explicitly adopts it.
- **`grilling` / HITL** — use `/sage-grill` discipline and domain context to
  resolve one decision tree branch. The agent never supplies the human side.
- **`task` / HITL or AFK** — manual work required before a decision can be made
  (provision access, inspect/move sample data, create a sandbox). It earns a
  ticket only by unblocking a decision, not by delivering the destination.

---

## Mode A — Chart the map

1. **Name the destination.** Grill until the spec/decision/change this effort is
   finding a route to is precise. Destination fixes scope.
2. **Map breadth-first.** Fan across the space; do not resolve one branch deeply.
   Find sharp questions, dependencies, and in-scope fog.
3. **No-fog early exit.** If the whole route fits one session, do not create a
   map. Re-route to `foggy-single-session` or `clear-single-session`.
4. **Create the map.** Fill Destination, Notes, empty Decisions, fog, and
   explicit Out of scope.
5. **Create sharp tickets.** A question can be ticketed when it is precise now,
   even if blocked. Keep unphraseable fog in `Not yet specified`.
6. **Wire dependencies second.** Create ids first, then set `blocked_by`/native
   blocking links. The **frontier** is open + unblocked + unclaimed tickets.
7. **Start the runnable frontier.** AFK `research` and AFK `task` tickets may be
   resolved in parallel when independent; record each result in its canonical
   ticket.
8. Set map status `active`, recompute the frontier, and enter Mode B immediately
   under `runPolicy: "until-gate"`. Chart completion is a state transition, not
   a stop. Under `strict`, return the active-map checkpoint.

---

## Mode B — Work frontier waves

1. Load only the map low-resolution view and configured backend operations.
2. Compute all open + unblocked + unclaimed tickets. Respect a user-named ticket
   as the scoped frontier; otherwise use table/query order.
3. Re-read canonical state before each claim. A ticket with an open blocker,
   assignee, or non-open status is not claimable.
4. **Claim before work:** local → set `status: claimed` + `assignee`; tracker →
   assign using its native operation. If another session won, skip that ticket
   and continue with the remaining frontier.
5. Partition the claimed frontier:
   - AFK `research`/`task` → resolve in parallel when evidence and side effects
     are independent.
   - independent HITL `prototype`/`grilling`/`task` → combine at most
     `maxQuestionsPerCheckpoint` decisions with a recommendation for each.
   - dependent HITL decisions → ask the single most-blocking branch, record the
     answer, then recompute.
6. Resolve every unblocked ticket that does not require a material gate. Load
   related tickets/source only as needed. Use `/sage-grill` discipline for HITL
   decisions and update domain `context.md` inline when canonical terms settle.
7. For each resolution, record answer + evidence in the ticket, set `closed`,
   and append one linked gist to `Decisions so far`. Never duplicate full
   rationale on the map.
8. Graduate newly sharp fog into tickets and remove that patch from
   `Not yet specified`. Create tickets first, then wire dependencies.
9. If a ticket lies beyond Destination, set `out-of-scope`, record why under
   `Out of scope`, and omit it from Decisions so far.
10. Update/delete invalidated tickets and edges, refresh the map timestamp,
    recompute the frontier, and start the next wave immediately.
11. Return to the human only when every reachable frontier branch is blocked by
    material HITL, HIGH/destructive risk, missing access/manual external action,
    or failed critical evidence. Under `strict`, return after the completed wave.

Local Markdown claims are cooperative, not atomic: re-read immediately before
claim and report a simultaneous-write conflict rather than overwriting it.

---

## Completion and handoff

Complete the map only when:

- every ticket is `closed` or `out-of-scope`;
- `Not yet specified` is empty;
- Destination still matches the agreed scope;
- every decision gist links to its canonical resolution.

Set map `status: complete`, then synthesize
`agents/sage/flows/<slug>-spec.md` from resolved tickets without re-interviewing.
The spec contains Problem, Success outcome, Canonical terms, Decisions,
Out of scope, Evidence pointers, and `Open: none`. Hand it to `/sage-flow` for
implementation design. Wayfinder never sends an active/incomplete map to Flow.

When invoked by an active `/sage` run with
`interaction.continueAfterHandoff: true`, return `spec-ready` to the parent and
continue into `/sage-flow` or implementation immediately. Map completion is a
handoff, not a terminal condition. A standalone `/sage-wayfinder` still prints
its summary and returns because no parent run exists.

---

## Failure and concurrency rules

- Never store secrets or PII values in maps/tickets; link to an approved store.
- Tracker writes are external mutations; do not infer permission from local
  planning scope.
- A HITL ticket cannot close without a real human exchange.
- A blocked ticket cannot be claimed.
- One frontier wave may close multiple independent tickets; each still owns one
  sharp canonical resolution.
- Parallel work requires independent dependencies and side effects. Recompute
  the frontier after each wave.
- Newly discovered destination changes require human confirmation, then update
  scope/out-of-scope and invalidate affected tickets before continuing.

---

## Summary

```markdown
── Sage Wayfinder ────────────────────────────────
**Role** · architect — <effort>
**Mode** · chart | frontier-wave
**Backend** · local-markdown | <configured tracker>
**Map** · <path/link> | **Status** · charting|active|complete

**Destination** · <one line>
**Worked** · <linked ticket titles closed in this wave, or "chart only">
**Frontier** · <linked titles, or "none">
**Fog** · <count/summary, or "none">
**Out of scope** · <new boundary, or "unchanged">
**Handoff** · <spec path when complete, otherwise next frontier ticket>
**Knowledge** · [new | updated | none] `<path>` — <reason>
──────────────────────────────────────────────────
```

---

_Adapted from Matt Pocock's `wayfinder` and `domain-modeling` skills (MIT).
Sage adds its three-route dispatcher, local-first portable backend, knowledge
tree, risk controls, and explicit spec → Flow contract._
