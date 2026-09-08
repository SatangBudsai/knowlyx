# Protocol context

Canonical vocabulary for Sage's request-shaping lifecycle. This file defines
terms only; rationale and implementation contracts live in decisions and flows.

## Route

**Definition:** The single shaping path Sage assigns before design based on
remaining decision fog and expected session span.
**Invariants:** Exactly one current Route owns the next shaping step; re-route
only when new facts change the amount or span of Fog.
**Includes:** `clear-single-session`, `foggy-single-session`,
`large-multi-session`.
**Excludes:** Risk level, task type, file count, checklist selection.
**Related:** Fog, Grill, Wayfinder, Flow.

## Fog

**Definition:** In-scope product/domain uncertainty that prevents design or
implementation without guessing.
**Invariants:** A repository fact that the agent can verify is never Fog and is
never delegated to the human as a product decision.
**Includes:** unresolved intent, terminology, scope, ownership, priorities, or
trade-offs; suspected questions not yet sharp enough to phrase.
**Excludes:** facts discoverable from code/schema/docs; work beyond Destination.
**Related:** Not yet specified, Out of scope, Frontier.

## Grill

**Definition:** A dependency-aware HITL session that resolves single-session Fog
into confirmed requirements.
**Invariants:** The human owns HITL decisions; Grill batches only independent
questions and records every answer before computing a dependent branch.
**Includes:** fact lookup, recommendations, scenario challenges, glossary
updates, checkpoint decisions.
**Excludes:** implementation design, product code, multi-session coordination.
**Related:** Requirements-clear, Flow, Wayfinder.

## Wayfinder

**Definition:** A durable multi-session planning map that coordinates decision
tickets until the route to a Destination is clear.
**Invariants:** The map indexes state while each ticket owns its resolution; a
run claims before work and closes every independent ticket reachable in the
current Frontier wave before returning at a material Gate.
**Includes:** Destination, decision tickets, blocking, claims, Frontier,
Not yet specified, Out of scope.
**Excludes:** implementation tickets and delivery of the Destination.
**Related:** Map, Frontier, Grill, Flow.

## Destination

**Definition:** The explicit end state Wayfinder is finding a decision route to.
**Invariants:** It is bounded enough that map completion can be tested without
delivering the implementation itself.
**Includes:** a spec-ready handoff, an approved decision, or another named
planning outcome.
**Excludes:** unbounded future work or implementation tasks beyond that outcome.
**Related:** Out of scope, Map complete.

## Frontier

**Definition:** Open, unblocked, unclaimed Wayfinder tickets that a session may
work now.
**Invariants:** It is recomputed from ticket status, dependencies, and claims;
blocked or claimed tickets never appear in it; completion of one wave immediately
opens the next wave under `runPolicy: until-gate`.
**Includes:** tickets whose `blocked_by` dependencies are closed.
**Excludes:** blocked, claimed, closed, or out-of-scope tickets; unphraseable Fog.
**Related:** Ticket, Not yet specified.

## Run frontier

**Definition:** Every open + unblocked task the active parent `/sage` can perform
without a new human-owned decision or external authority.
**Invariants:** Closing a command, ticket, handoff, checkpoint, or phase
recomputes the Run frontier; it is not itself a terminal condition.
**Includes:** independent research, implementation, validation, docs, and child
handoffs whose prerequisites are complete.
**Excludes:** work behind a Gate, blocked dependencies, out-of-scope work.
**Related:** Frontier, Gate, Flow.

## Gate

**Definition:** A condition that requires human authority, new access/evidence,
or safe rejection before affected work may continue.
**Invariants:** Interaction preferences may add checkpoints but can never remove
a central risk Gate.
**Includes:** material HITL decisions, HIGH/destructive work, trust-boundary
approval, missing access/manual external action, failed critical controls.
**Excludes:** completing a ticket/phase, reversible internal preferences, routine
child handoffs.
**Related:** Run frontier, Requirements-clear, Design-clear.

## Requirements-clear

**Definition:** Grill's exit state: product intent, canonical terms, scope, and
trade-offs are resolved with no implementation-shaping HITL decision left open.
**Invariants:** Flow may reopen a settled product decision only when it cites
new contradictory code or schema evidence.
**Includes:** a confirmed chat handoff or checkpoint spec.
**Excludes:** completed implementation design.
**Related:** Grill, Flow, Design-clear.

## Flow

**Definition:** Implementation design performed from clear requirements against
real code/schema.
**Invariants:** Flow owns implementation decisions and does not repeat Grill's
product interview.
**Includes:** systems, APIs, state, failures, security, concurrency, rollout.
**Excludes:** re-interviewing resolved product decisions or coordinating
multi-session Fog.
**Related:** Requirements-clear, Design-clear.

## Flow workspace

**Definition:** The single human-searchable folder that keeps one effort's
requirements, design, implementation tickets, and focused evidence together.
**Invariants:** Grill, Flow, Ticket, Review, and testing reuse one stable slug;
`index.md` is the entry point; durable images remain beside the effort and are
embedded by relative link where they support a document.
**Includes:** `spec.md`, `flow.md`, `tickets.md`, and indexed evidence when those
artifacts exist.
**Excludes:** reusable domain knowledge, Wayfinder decision-ticket storage,
installer-managed reference flows, unrelated files already in `flows/`.
**Related:** Grill, Flow, Requirements-clear, Design-clear.
