# Pre-action clarification — interaction flow

Status: design-clear
Last updated: 2026-07-31
Route: clear-single-session

> Sage performs a clarification pass before implementation, but asks the human
> only for missing, human-owned information that changes the outcome. A direct,
> actionable request—especially a focused fix with the error, failing behavior,
> relevant context, or reproduction details—continues without a ceremonial
> interview.

Related decisions:

- [`route-by-fog-and-session-span`](../protocol/decisions/route-by-fog-and-session-span.md)
- [`continue-until-material-gate`](../protocol/decisions/continue-until-material-gate.md)

## Design decisions

- Every code-changing request receives a pre-action clarification pass before
  design or implementation.
- The pass is an internal sufficiency check, not a mandatory user-facing
  question.
- Sage first separates repository facts from human-owned decisions. It looks up
  facts itself and asks only about decisions whose answers materially change
  implementation shape, scope, public behavior, or risk.
- A request is actionable when its intended outcome and bounded target are
  clear enough to proceed without guessing. A direct command can be actionable
  even when it is short.
- A bug-fix request is normally actionable when it provides enough diagnostic
  evidence to start investigation, such as an error message or stack trace,
  observed versus expected behavior, a failing test, logs, a reproduction, or
  a precise affected location. Not every field is required when the repository
  can supply the rest.
- Missing facts that Sage can discover from code, tests, logs, schema, config,
  or documentation do not justify interrupting the human.
- When a question is necessary, Sage asks the smallest useful set: up to three
  independent decisions together, or the single most-blocking dependent
  decision. Each question includes a recommendation and a concise reason.
- Clarification never bypasses central risk gates. A fully detailed request
  still requires explicit approval for HIGH, destructive, irreversible, or
  otherwise gated actions.

## Out of scope

- Replacing the locked five-item run checklist or its `mode:auto|ask` behavior.
- Asking the user to confirm facts available in the repository or environment.
- Requiring a fixed bug-report template or every possible diagnostic field.
- Re-interviewing decisions already settled in a Grill, Wayfinder, Flow, or
  approved specification.
- Weakening security, destructive-action, trust-boundary, or external-mutation
  gates.
- Adding a new `.sage-local.json` setting for whether clarification is enabled.
- Turning routine progress updates into questions that pause the run.

## 1. Actors and ownership

| Actor / system | Responsibility | Ownership boundary |
| --- | --- | --- |
| Human | Supplies intent and makes material product/domain decisions | Human-owned choices and explicit risk approvals |
| Parent `/sage` | Performs the pre-action pass, routes the request, and continues the run | Active request state and interruption budget |
| Repository evidence | Supplies discoverable facts from code, tests, schema, config, logs, and docs | Factual current-state evidence |
| `/sage-grill` | Resolves missing single-session product/domain decisions | `foggy-single-session` questions and `requirements-clear` handoff |
| `/sage-wayfinder` | Coordinates decision fog that cannot fit one session | `large-multi-session` map and `spec-ready` handoff |
| `/sage-flow` | Resolves implementation design against real code/schema | Design questions and `design-clear` handoff |
| Risk policy | Determines mandatory approvals and controls | Gates that clarification policy cannot suppress |

The trust boundary is between discoverable facts and human-owned decisions.
Sage must not offload its repository research to the human, and it must not
self-answer a material decision merely to avoid asking.

## 2. End-to-end overview

```text
[Code-changing request]
          |
          v
[Pre-action clarification pass]
          |
          +-- What is missing?
          |      |
          |      +-- repository fact ------> inspect source/tests/schema/docs
          |      |
          |      `-- human-owned decision -> does it materially change outcome?
          |                                      |
          |                                      +-- no --> choose reversible
          |                                      |          repo default + record
          |                                      |
          |                                      `-- yes -> classify dependency
          |                                                   |
          |                                                   +-- independent:
          |                                                   |   ask <= 3 together
          |                                                   |
          |                                                   `-- dependent:
          |                                                       ask one blocker
          |
          +-- Nothing material missing
          |      |
          |      +-- focused/direct request ----------------------+
          |      +-- detailed error/repro/failing test -----------+--> act now
          |      `-- approved spec or prior clear handoff --------+
          |
          v
[Confirm route after repository scan]
          |
          +-- clear-single-session --> Flow/build
          +-- foggy-single-session --> Grill --> requirements-clear --> continue
          `-- large-multi-session --> Wayfinder --> spec-ready --> continue
```

The pass optimizes for two simultaneous outcomes: Sage should expose genuine
unknowns before making an expensive wrong turn, and it should preserve momentum
when the user has already given an actionable request.

## 3. Step-by-step behavior

### Step 1 — Parse the requested outcome and target

Identify:

- the desired end state;
- the named file, component, system, behavior, or error when supplied;
- explicit in-scope and out-of-scope boundaries;
- diagnostic evidence included by the human;
- prior artifacts or decisions that already make requirements clear.

Do not require the human to use Sage terminology. A direct instruction such as
“Fix this null dereference; here is the stack trace and failing test” already
signals an intended outcome and an investigation starting point.

### Step 2 — Build a missing-information inventory

For each apparent unknown, label it:

- `fact` — discoverable from repository or environment evidence;
- `internal-reversible` — an implementation preference Sage can choose using
  repository convention and record as an assumption;
- `human-material` — a choice that changes product behavior, canonical meaning,
  scope, ownership, public contract, risk acceptance, or another hard-to-reverse
  outcome.

Sage must inspect facts before finalizing the route. An apparent product
question may disappear after reading the implementation, and a direct fix may
reveal a real behavior decision only after diagnosis.

### Step 3 — Evaluate actionability

Treat the request as actionable when all of the following hold:

1. The intended outcome is clear enough to tell success from failure.
2. The initial target or investigation surface is bounded enough to begin.
3. No unresolved `human-material` decision blocks the next safe frontier.
4. Required risk approval, if any, has been obtained.

Evidence that commonly makes a fix actionable includes:

- a precise error message or stack trace;
- failing command or test output;
- observed and expected behavior;
- reproducible steps or input;
- logs tied to the failing path;
- a named file, symbol, endpoint, or recent regression;
- an approved issue/spec with acceptance criteria.

These are examples, not a mandatory checklist. Sage uses whatever evidence is
available and discovers the rest when it can.

### Step 4 — Choose whether to ask

Use this decision table:

| Request state | Behavior |
| --- | --- |
| Actionable direct instruction, no material decision missing | Do not ask a clarification question; state any reversible assumption and proceed |
| Focused bug fix with sufficient diagnostic evidence | Start diagnosis/fix immediately; ask later only if evidence exposes a material branch |
| Missing information is repository-discoverable | Inspect it; do not ask the human |
| Only an internal reversible preference is open | Follow repo convention/recommendation, record the assumption, and proceed |
| One material dependent decision blocks safe work | Ask the single most-blocking question, with recommendation and reason |
| Two or three independent material decisions block safe work | Ask them in one checkpoint, each with recommendation and reason |
| More than three independent decisions are open | Ask at most the configured maximum, record answers, then compute the next checkpoint |
| Decisions cannot fit one session | Route to Wayfinder instead of conducting an endless interview |
| HIGH/destructive/irreversible action is ready | Ask for the explicit central risk approval even if every implementation detail is known |

Questions must be concrete enough that the answer changes a named branch.
Avoid broad prompts such as “What else should I know?” when Sage can instead
name the missing choice and its consequence.

### Step 5 — Ask minimally when a gate exists

For every user-facing clarification:

1. State the missing decision in plain language.
2. Explain which implementation branch its answer changes.
3. Recommend one answer and give one concise reason.
4. Batch only independent decisions, never more than
   `maxQuestionsPerCheckpoint`.
5. Wait only when the answer blocks the next safe frontier.

If some work remains safe and independent of the unanswered decision,
`runPolicy: until-gate` continues that frontier before returning.

### Step 6 — Continue immediately when the request is actionable

When no blocking human-owned decision remains:

- confirm `Route: clear-single-session`;
- perform risk assessment and declare controls;
- enter Flow when enabled/applicable, otherwise implementation;
- do not invent a confirmation checkpoint;
- preserve normal progress commentary without turning it into a question.

A later discovery can reopen clarification only when it introduces new evidence,
a wider target, a different public behavior, or a real human-owned trade-off.
The agent names the new evidence and the decision it exposes.

### Step 7 — Validate the interaction contract

Regression coverage must prove both sides:

- vague requests with implementation-shaping product decisions route to Grill
  and ask dependency-safe questions;
- direct actionable requests and detailed bug reports route clear and do not
  trigger ceremonial questioning;
- facts are looked up rather than asked;
- prior clear handoffs are consumed without re-interview;
- risk gates still override the fast path.

## 4. State and data handling

No new runtime state or config field is introduced.

| State | Source | Lifecycle |
| --- | --- | --- |
| Request evidence | Current user request and attached artifacts | Parsed at the beginning; augmented by repository inspection |
| Missing-information inventory | Parent `/sage` reasoning | Recomputed after evidence, answers, or route handoffs |
| Route | Parent `/sage` | Preliminary before scan; confirmed after scan |
| Material answers | Grill/Wayfinder checkpoint or active conversation | Recorded before dependent work continues |
| Reversible assumptions | Active plan/flow/summary | Recorded when chosen; revisited only if evidence conflicts |
| Risk approval | Central risk gate | Required independently of actionability |

The clarification pass does not add persistence because its output already maps
to existing route, checkpoint, assumption, and risk-gate state.

## 5. API and configuration contract

No API, schema, or `.sage-local.json` shape changes.

The behavioral contract is:

```text
pre_action_clarification(request, repository_evidence):
  inspect_discoverable_facts()
  classify_remaining_unknowns()

  if blocking_human_material_decisions:
      route_to_grill_or_wayfinder()
      ask_dependency_safe_minimum()
  else:
      route_clear()
      continue_without_clarification_question()

  central_risk_gate_always_applies()
```

`interaction.questionPolicy` controls how necessary questions are grouped. It
does not force Sage to create questions when none are needed.

## 6. Failure and edge cases

| Case | Required behavior |
| --- | --- |
| User says only “fix it” with no visible target or context | Inspect current task/repo context first; ask one focused question only if no bounded investigation surface can be found |
| User gives an error but not expected behavior | Infer expected behavior only when tests/spec/contracts make it factual; otherwise ask if different valid outcomes remain |
| Stack trace points to a symptom, not the cause | Begin diagnosis; do not ask the human to identify the root cause |
| Direct request conflicts with code/schema | Surface the contradiction and ask which behavior should become authoritative when that is a human-owned decision |
| Multiple possible fixes preserve the same behavior | Choose the repo-conventional reversible approach and record it |
| Possible fixes change public behavior differently | Ask the material behavior decision before implementation |
| Fix is detailed but destructive | Stop at the central destructive/HIGH approval gate |
| An earlier Grill/Flow already answered the question | Consume the recorded answer; do not ask again without contradictory evidence |
| User explicitly asks to be interviewed first | Run a focused Grill, while still looking up repository facts rather than asking for them |
| User explicitly says not to ask unnecessary questions | Apply the same minimum-question contract; this never suppresses required risk approval |
| New evidence appears mid-fix | Reassess route/risk; ask only if it creates a new blocking human-owned decision |

## 7. Security and continuity

- Less questioning must not be interpreted as broader mutation authority.
- Actionable error details may contain secrets or PII; Sage avoids copying them
  into logs, docs, fixtures, or knowledge files and follows redaction controls.
- Direct fixes affecting auth, payment, ownership, or public contracts still
  receive their required risk controls and specialist review when applicable.
- Question batching must not combine dependent trust-boundary decisions.
- Continuity is preserved by continuing across clear handoffs and avoiding
  confirmation-only questions.
- Correctness is preserved by reopening only decisions supported by new,
  implementation-shaping evidence.

## 8. Build checklist

### Canonical protocol

- [x] Add the pre-action clarification pass to `AGENTS.md` routing.
- [x] Define “ask only for missing material decisions” and the actionable
      direct-fix fast path.
- [x] Keep fact lookup, reversible defaults, and central risk gates explicit.

### Commands and knowledge

- [x] Mirror the contract in `agents/sage/commands/sage.md`.
- [x] Keep `/sage-grill` reserved for real decision fog.
- [x] Capture the reusable protocol decision and index it.
- [x] Ensure installer-managed assets distribute the new contract.

### Proof and public docs

- [x] Add positive fixtures for vague requests that require questions.
- [x] Add negative fixtures for direct actionable fixes that should proceed.
- [x] Add regression assertions for minimal questions and risk-gate precedence.
- [x] Update human-facing interaction documentation.
- [x] Run the focused protocol tests and the full repository suite.

## 9. Skeptical verification

- **Weak point:** “Ask before doing” could be read as a mandatory question on
  every code request.
  **Resolution:** The protocol names an always-run internal clarification pass
  and separately states that user-facing questions occur only for blocking
  human-owned decisions.
- **Weak point:** “Detailed error” could become a rigid bug-report template.
  **Resolution:** Diagnostic fields are examples; the actionability test is
  outcome + bounded surface + no material blocker, and Sage discovers facts
  itself.
- **Weak point:** The fast path could bypass approval because the request is
  precise.
  **Resolution:** Risk approval is orthogonal and explicitly overrides the fast
  path.
- **Weak point:** Agents may ask broad “anything else?” questions to satisfy the
  clarification instruction.
  **Resolution:** Every question must name a decision and the branch it changes;
  broad ceremonial prompts are prohibited.
- **Weak point:** Avoiding questions could cause silent product assumptions.
  **Resolution:** Only internal reversible preferences may be auto-decided;
  product behavior, scope, ownership, public contract, and hard-to-reverse
  trade-offs remain human-owned.
- **Simpler route considered:** Add one sentence saying “ask questions first.”
  **Rejected because:** It would conflict with `until-gate`, fact lookup, and
  direct-fix continuity, leaving agents free to over-question.

## 10. Open questions

None. The implementation-shaping decisions are resolved:

- the clarification pass always runs internally;
- user-facing questions are conditional on missing material decisions;
- direct actionable and sufficiently evidenced bug-fix requests proceed;
- necessary questions use the existing dependency-aware batching policy;
- central risk gates remain unchanged.
