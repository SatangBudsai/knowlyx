# /sage-e2e-test — autonomously prove real user journeys

Plan, implement, run, debug, and validate reliable end-to-end coverage from
observed application behavior. Continue through every safe, unblocked step
without asking for routine confirmation.

Prioritize, in order:

1. Correctness.
2. Real user behavior.
3. Reproducibility.
4. Efficient model and context usage.
5. Minimal unnecessary application-code changes.

Use an interactive browser to discover or disambiguate behavior and an E2E
runner to encode repeatable regression coverage. Neither replaces the other.

This command is provider-, language-, and framework-neutral. Detect the
capabilities and established tools that actually exist; never pretend a browser,
subagent, model switch, credential, or service is available.

> **Explicit opt-in only.** Run this command only when the human invokes
> `/sage-e2e-test` or directly asks to add E2E tests. `/sage` never selects,
> recommends, or invokes it automatically.

---

## Model and work routing

The current session model and effort are the default and hard ceiling. Route by
task shape only when the host can actually route work:

- **Coordinator / normal reasoning** — plan journeys, understand requirements,
  explore behavior, handle auth/session flows, coordinate bounded work, and
  classify ambiguous failures. Keep this work on the current primary model.
- **Bounded worker / mechanical work** — generate already-specified cases,
  locators, assertions, repetitive CRUD scenarios, simple fixtures, formatting,
  deterministic test fixes, and targeted reruns. Delegate only when a lower-tier
  worker is available and the task has one objective plus clear verification.
- **Escalation / complex unresolved work** — use the strongest model permitted by
  the session ceiling only after normal investigation cannot resolve a race,
  cross-service failure, complex session behavior, or test-versus-app ambiguity.

**Optional Codex mapping when those models and delegation are exposed:** Terra
for coordination, Luna for bounded mechanical work, and Sol for genuinely
complex unresolved work. This mapping is an optimization, not a requirement.
Never exceed the session ceiling, switch silently, or block another agent because
these Codex model names do not exist there.

When delegation is unavailable or would cost more context than it saves, work
locally. A delegated task receives only the relevant files, verified behavior,
one objective, and its run criteria—not the whole repository.

---

## Step 1 — Load the QA lens and establish the safe envelope

Open `agents/sage/roles/role-qa.md` and adopt it according to `AGENTS.md`. Anchor
all knowledge and output paths to the repository that owns the flow entry point.
Read `agents/sage/flow-workspaces.md` and resolve or create the matching
`agents/sage/flows/<slug>/` workspace before persisting debug evidence.

Apply the central Sage route and risk policy. A request to create E2E coverage
authorizes safe local/sandbox exploration, test files, conventional dev-only test
dependencies, app startup, targeted reruns, and fixture cleanup. It does not
authorize production mutation, real money/email, destructive data changes,
credential creation, bypassing authorization, or unrelated application fixes.

Infer reversible choices from repository evidence. Stop only for a genuine
business/product decision, missing access or credential, destructive/production
effect requiring approval, matched block rule, failed critical control, or an
ambiguity that code, tests, logs, traces, and available browser state cannot
resolve safely.

## Step 2 — Detect the real stack, flow, and capabilities

Inspect before planning:

1. **Established E2E tool** — configs, scripts, dependencies, `e2e/` or
   `tests/e2e/`, fixtures, reporters, CI jobs, and 1–2 nearby tests. Reuse its
   runner, language, selectors, auth setup, base URL, and file conventions.
2. **Application stack** — manifests, routes/pages/endpoints, dev/preview command,
   services, database, and external dependencies. Do not infer from filenames.
3. **Flow contract** — prefer `agents/sage/flows/<slug>/flow.md`, then its
   workspace `spec.md` and `tickets.md`, product docs, acceptance criteria, and
   executable behavior. Trace the actual entry and exits; fall back to legacy
   flat flow artifacts only as defined by `flow-workspaces.md`.
4. **State prerequisites** — seed/factory, test account and roles, auth/session,
   required env vars, sandbox providers, data isolation, and cleanup/reset path.
5. **Available observation tools** — interactive in-app browser, signed-in Chrome
   control, screenshots, accessibility tree, console/network inspection, runner
   traces, video, and application logs. Use only capabilities actually exposed.

Prefer the repository's existing E2E framework. If none exists and the user
asked to create E2E coverage, choose the smallest ecosystem-compatible standard
without a ceremonial question: prefer Playwright for a browser application when
it fits the stack; otherwise choose the ecosystem's established E2E/load tool.
Ask only when project dependency policy, runtime ownership, or competing stacks
make that choice material.

## Step 3 — Plan high-value journeys first

Choose the smallest set of journeys that would materially protect users:

- critical happy paths;
- meaningful validation and failure exits;
- authentication, authorization, ownership, and session boundaries;
- state/data creation, update, deletion, and cleanup where relevant;
- redirects, refresh/back, duplicate action, timeout, loading, and error recovery;
- high-risk money, irreversible state, external side effects, and concurrency;
- load scenarios only when latency/throughput is part of the requested behavior.

Do not create many low-value “page renders” tests. Rank journeys by user impact,
likelihood, and risk controls. A happy-path pass is not evidence for a permission,
retry, rollback, or partial-failure behavior it never exercised.

Output the intent block and continue on `proceed|warn`:

```text
Repo       : <repo-root>
Role       : qa — E2E for <flow>
Model      : <current model @ effort; optional routing available>
Tool       : <existing runner or selected default>
Behavior   : <flow source + real-app observation source>
Journeys   : <ranked happy/failure/auth/high-risk paths>
State      : <base URL · seed/account · cleanup · sandbox externals>
Browser    : <available capability and when it will be used | unavailable>
Risk       : LOW | MEDIUM | HIGH · confidence:<low|medium|high>
Drivers    : <affected asset → failure mode>
Evidence   : <driver → planned assertion/artifact>
Decision   : proceed | warn | ask | reject
```

## Step 4 — Explore real behavior when possible

Use the real application before encoding an uncertain or important flow whenever
a safe interactive browser is available:

- perform login/logout, navigation, forms, dialogs, CRUD, redirects, validation,
  loading/error states, permissions, and session transitions that matter;
- observe visible UI, URL changes, accessibility state, relevant console errors,
  relevant network requests/responses, and resulting application state;
- use a sandbox/test account and isolated data;
- record behavior that contradicts source/docs instead of choosing the expected
  answer silently.

Do not repeatedly inspect the browser when runner output, logs, screenshots, or
traces already explain the behavior. If no interactive browser is available,
ground expectations in executable tests, source contracts, app responses, and
flow docs, then disclose the observation gap.

## Step 5 — Record expected behavior before each test

For every scenario, write a compact behavior record in the plan, test name, or
test structure:

```text
Given   : <starting user/session/data state>
When    : <real user actions>
Then UI : <visible result and accessibility state>
Then URL: <navigation/redirect, if any>
Then data: <observable state change and cleanup>
API     : <relevant request/response/side effect, only when needed>
```

Use observed behavior as the source of truth unless it conflicts with an
approved requirement. A conflict is a product/application finding, not a reason
to encode whichever result is easiest.

## Step 6 — Implement deterministic E2E coverage

- Reflect real user behavior rather than calling implementation internals.
- Prefer accessible locators: role, label, name, and stable visible text. Use a
  project-standard test ID when semantics are insufficient. Avoid brittle CSS or
  XPath selectors unless no stable public surface exists.
- Never use arbitrary sleeps. Wait for meaningful UI, URL, response, event, or
  state transitions.
- Keep tests independently runnable where practical. Give each test isolated
  setup and deterministic cleanup; control clock/randomness only at a real seam.
- Exercise the real application stack where practical. Do not overuse mocks in a
  true E2E test; mock only unsafe/unavailable external boundaries or scenarios
  that cannot be produced deterministically.
- Assert exact intended outcomes, including meaningful error text/status and
  data/side effects when those are part of the behavior.
- Make the smallest application change necessary for a stable public testing
  surface. Do not alter application behavior merely to make a test pass.
- For load tests, define VUs/ramp/duration and measurable latency/error thresholds.

## Step 7 — Run continuously

After implementing each scenario:

1. Run the narrowest spec/scenario.
2. Inspect the actual output and artifacts.
3. Classify and resolve a straightforward failure.
4. Rerun until the scenario is deterministic.
5. Run the broader relevant E2E suite after individual scenarios stabilize.

Use the repository's configured retry policy. Do not add retries to conceal
flakiness. Repeat critical new coverage enough to catch immediate nondeterminism
when runtime cost is reasonable, and report the number of successful runs.

## Step 8 — Classify every failure before fixing

Classify from evidence, never convenience:

### A. Test issue

Wrong locator/assertion, stale expected behavior, bad fixture/data, or an
incorrect wait. Fix the test, rerun the target, and confirm the assertion still
fails when the intended application behavior is broken.

### B. Application issue

API failure, broken validation, unexpected redirect, inconsistent state,
permission/session bug, JavaScript exception, backend error, or violated product
contract. Do not weaken the test. Report the defect clearly; modify application
code only when the user's request also authorizes the fix, then run the relevant
unit/integration checks as well as E2E.

### C. Environment/infrastructure issue

Unavailable service/database, missing safe credential, incorrect environment,
port conflict, corrupt seed, or unstable external dependency. Repair reversible
local test infrastructure when in scope; otherwise report the exact blocker and
the evidence it prevents.

Increasing a timeout, adding retries, catching an error, removing validation, or
skipping a branch is never a classification or a valid fix by itself.

## Step 9 — Debug with the cheapest sufficient evidence

Use concise runner output, the first relevant stack trace, screenshot/trace,
application log, console error, and network request before loading wider context.

Follow the workspace evidence ladder. For a reproducible visual failure, save
one focused `before` screenshot under
`agents/sage/flows/<slug>/evidence/screenshots/` and catalog it immediately in
`evidence/index.md`. After a visible fix, save a focused `after` screenshot.
Embed each relevant image with a relative Markdown link in the `spec.md`,
`flow.md`, or `tickets.md` section it proves when that document is updated.
Reuse these saved artifacts instead of repeatedly reading the same browser state.
For a non-visual failure or unsafe capture, record the focused log/trace evidence
or the reason no screenshot was stored.

- Obvious deterministic test failure → fix locally or route to a bounded worker.
- Ambiguous test-versus-application failure → coordinator inspects the relevant
  flow and artifacts.
- Runner evidence insufficient and browser available → reproduce only the failing
  step in the real browser; inspect relevant UI/accessibility, console, network,
  redirects, and state.
- Focused reproduction still cannot classify the failure, or a race, complex
  auth/session, or cross-service failure remains unresolved → record why wider
  inspection is needed, then use full browser/state debugging and the strongest
  model allowed by the session ceiling while narrowing the evidence passed.

Summarize discoveries before any handoff. Never send the whole repository, huge
logs, unrelated files, or full browser state when a small slice is sufficient.

## Step 10 — Completion criteria

A flow is complete only when:

- expected behavior was established from real evidence;
- repeatable E2E coverage exists in the repository's convention;
- targeted tests pass consistently and the broader relevant suite passes;
- assertions genuinely validate the intended UI/navigation/data/API outcome;
- no meaningful browser, console, network, backend, or runner error was ignored;
- no unnecessary fragile wait, selector, retry, mock, or application change remains;
- test data is isolated and cleaned up or reset deterministically;
- every parent-run risk control owned by E2E maps to an exact assertion/artifact;
- every persisted screenshot/trace/log is cataloged in the flow workspace and
  every relevant document update embeds the evidence it relies on;
- skipped or blocked scenarios and remaining risks are explicit.

Continue autonomously until these criteria are met or a material gate from Step 1
is reached. Do not stop at planning, first implementation, or first green run.

## Step 11 — Capture knowledge

Capture only a durable project-specific E2E convention or non-obvious seam under
`agents/sage/<domain>/decisions/` as `status: proposed`. Do not copy this generic
workflow into project knowledge.

## Step 12 — Summary

Output as plain Markdown:

```markdown
── Sage E2E Test ──────────────────────────────────
**Role** · qa — E2E for <flow>
**Model** · <coordinator and any actual bounded/escalated routing>
**Tool** · <runner> | **Initial risk** · <LOW|MEDIUM|HIGH>

**Flows covered**
- <journey and meaningful exits>

**Tests changed**
- `<path>` — <scenarios>

**Ran**
<exact targeted/broader commands, pass counts, and repeated-run evidence>

**Application bugs**
- <classification + evidence, or "none">

**Skipped / blocked**
- <scenario + exact blocker, or "none">

**Control evidence**
- <driver → assertion/artifact, or gap>

**Flow evidence** · `agents/sage/flows/<slug>/evidence/index.md`

**Residual risk** · <LOW|MEDIUM|HIGH> — <what remains>
**Knowledge** · [new | updated | none] `<path>` — <pattern or reason>
────────────────────────────────────────────────────
```

When invoked by an active `/sage` run, return the E2E evidence to the parent and
continue with remaining work. A standalone invocation returns only after the
flow is complete or materially gated.
