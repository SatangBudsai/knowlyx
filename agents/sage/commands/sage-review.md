# /sage-review — review a change for correctness and conformance before it ships

Review a real change — the working tree, a branch, a PR, or named paths — against
what it was supposed to do. Find defects that would actually bite: wrong
behavior, a requirement the change does not meet, an unhandled branch, a control
that was promised and never produced evidence, a simpler route that already
exists in the repo.

**This is the correctness review.** Its siblings own narrower jobs and are not
substitutes: `/sage-security-review` hunts exploitable holes,
`/sage-refactoring-code` rewrites for readability, `/sage-unit-test` and
`/sage-e2e-test` produce test evidence. When this review finds a security driver,
hand that finding to `/sage-security-review` rather than half-reviewing it here.

**Read-only by default.** Reviewing and fixing are different jobs with different
risk. Report findings first; apply fixes only when the human asks, and then
through `/sage` so the change gets its own role, risk header, and validation.

---

## Model & effort

Run at the full session model + effort ceiling. A review that misses the defect
costs more than the tokens it saved. Never downgrade the verify pass in Step 4.
If the environment hides model/effort, state `current agent @ effort:unavailable`.

---

## Step 1 — Establish the target and the standard

**Target.** Resolve exactly what is under review, in this order: the paths or PR
the human named → the branch diff against its merge base → the uncommitted
working tree. State the resolved target and how many files it covers. Never
review a target you inferred silently.

**Standard.** A finding needs something to be wrong _against_. Load whichever
exist, in order:

1. `agents/sage/flows/<slug>/tickets.md` — the acceptance criteria the change
   claimed to satisfy, and the controls each ticket owed
2. `agents/sage/flows/<slug>/flow.md` — systems, API spec, state, error paths,
   security and concurrency
3. `agents/sage/flows/<slug>/spec.md` — resolved product intent, canonical terms,
   scope and out-of-scope
4. `agents/sage/flows/<slug>/evidence/index.md` — focused visual/trace/log
   evidence linked by those artifacts
5. `agents/sage/<domain>/` — `context.md`, `rules.md`, `decisions/*.md`, with
   each rule's `enforcement` (`block` · `warn` · `advise`, see `AGENTS.md` §5)

When none of these exist, say so and review against the code's own contracts:
callers, tests, schema, and public signatures. A review with no standard is an
opinion — label it as such rather than dressing it up as a defect list.

Read `agents/sage/flow-workspaces.md` first and use its legacy fallback when a
canonical workspace does not yet exist.

---

## Step 2 — Read the change in its context

Never review a diff in isolation. For each changed unit:

- open the surrounding file, not just the hunk;
- find the **callers** of every changed signature and confirm they still hold;
- read the schema/migration a data change depends on;
- read the tests that cover it — and notice when none do.

Fan out with parallel search agents when the surface is large, and take back the
conclusions rather than the file dumps.

---

## Step 3 — Review along the dimensions that matter

Cover each dimension deliberately. Skip one only by saying it does not apply.

| Dimension        | What to hunt                                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| **Conformance**  | every acceptance criterion in the tickets/spec — met, partially met, or missed. Scope creep beyond out-of-scope. |
| **Correctness**  | wrong logic, off-by-one, inverted condition, wrong operator precedence, lost error, swallowed exception          |
| **Edge cases**   | empty, null, zero, single element, duplicate, expired, partial failure, retry, concurrent write, refresh mid-flow |
| **Contracts**    | changed public signature, response shape, status code, event payload — and whether every consumer was updated    |
| **State & data** | lifecycle gaps: created but never cleared, cached past its TTL, trusted from the client, written non-atomically  |
| **Controls**     | every control the flow or ticket owed — is its evidence actually here, or was it quietly dropped?                |
| **Reuse**        | code that reimplements an existing util/hook/service/validator already in the repo                               |
| **Simplicity**   | speculative layers, dead branches, an abstraction with one caller, a simpler route the repo already uses         |
| **Knowledge**    | a matched `block` rule violated, a `decisions/` entry contradicted without citing new evidence                   |

Facts are yours to establish, not to ask about. Run the type check, the linter,
and the relevant tests when they exist, and use their **real output** — never
report a test as passing that you did not run.

---

## Step 4 — Verify each finding before reporting it

A false finding costs more trust than a missed one. For each candidate, try to
**refute** it before you keep it:

1. Re-read the code path end to end and name the concrete failure: the input or
   state, the line that goes wrong, the observable wrong outcome.
2. Look for the guard elsewhere — a caller, a middleware, a schema constraint, a
   database default — that already prevents it.
3. Check whether an existing test would catch it. If one would, the finding is
   about the test, not the code.
4. Keep it only as **CONFIRMED** when you traced the failure, or **PLAUSIBLE**
   when the mechanism is real but you could not fully verify it. Drop everything
   else — style preferences, hypotheticals, and "consider maybe" are not
   findings.

Rank what survives by real consequence, not by how easy it was to spot.

---

## Step 5 — Report, then stop

Report findings; do not edit. For each one give the location as
`path/to/file.ts:42`, the defect in one sentence, the concrete failure scenario,
and the smallest fix that resolves it.

If the human then asks for the fixes, apply them through `/sage` — one scoped
change with its own risk header and validation — or through
`/sage-refactoring-code` when the finding is purely about readability. Central
HIGH and destructive gates in `AGENTS.md` §1.4 still apply to every fix.

When the review turns up a genuine product question rather than a defect, that is
a `/sage-grill` decision, not a review comment. Name it and hand it over.

---

## Step 6 — Capture knowledge

A defect worth preventing twice becomes knowledge per `AGENTS.md` §3 — the
pattern and its Do/Avoid, not this change's specifics. Write it as
`enforcement: advise`, `source: ai`, `status: proposed` under
`agents/sage/<domain>/decisions/`. One decision per file. Otherwise state
`No new knowledge — <file> covers this`.

---

## Step 7 — Summary

```markdown
── Sage Review ───────────────────────────────────
**Role** · <lens> — <what was reviewed>
**Model** · <model> @ effort:<effort>
**Target** · <branch/PR/paths> — <n> files
**Standard** · <tickets/flow/spec/rules used, or "code contracts only">

**Conformance** · <met | partially met | missed> — <criterion → status>

**Findings** (most severe first)

- **[CONFIRMED|PLAUSIBLE]** `path/file.ts:42` — <defect in one sentence>
  Fails when: <input/state → wrong outcome>
  Fix: <smallest change that resolves it>

**Controls** · <owed control → evidence present | missing>
**Validation run** · <command → real result, or "none available — <why>">
**Handed off** · <security finding → /sage-security-review | decision → /sage-grill | none>
**Residual risk** · <LOW|MEDIUM|HIGH> — <what the review covered and what it could not>
**Knowledge** · [new | updated | none] `<path>` — <reason>
──────────────────────────────────────────────────
```

`**Findings** · none` is a valid and useful result when the change genuinely
holds up — say it plainly instead of manufacturing a finding to look thorough.

Avoid: reviewing the hunk without its callers; reporting style preferences as
defects; claiming a test passed without running it; re-litigating a decision
already recorded in `decisions/` without new evidence; editing files during a
review; ending with "looks good" and no evidence.
