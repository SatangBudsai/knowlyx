# /sage-refactoring-code — write code people can understand and change

Write new code or refactor existing code so its behavior, names, structure, and
data model are easy for the next person to understand. Prefer the smallest clear
design that meets today's requirements and can be moved or changed at real
boundaries. Do not build flexibility for hypothetical cases.

This skill is language-, framework-, and database-agnostic. Use the repository
as evidence, not as an excuse to repeat accidental complexity.

> **Safety hierarchy:** Preserve correctness, security, data integrity, required
> performance, and public behavior before simplifying. Readability never
> authorizes removing validation, authorization, constraints, transactions,
> idempotency, locking, error handling, or compatibility controls.

---

## Step 1 — Understand before changing

Load `agents/sage/roles/role-dev.md`. For a schema-centered task, use the
database/architect lens during schema design and announce the handoff according
to `AGENTS.md`.

Read only the evidence needed to understand the target:

1. Open the target, its callers, tests, types/contracts, and nearby files.
2. For database work, open the actual schema, migrations, representative queries,
   constraints, and ownership boundaries.
3. State the observable behavior that must remain and any behavior the request
   intentionally changes.
4. Identify project vocabulary and conventions from real usage. Separate useful
   conventions from accidental complexity; frequency alone does not make a
   pattern good.
5. Reuse an existing component, function, or module only after reading its real
   contract. Do not reuse it merely because its name sounds relevant.

If a canonical product term or public contract is genuinely undecided, follow
Sage's route/gate policy. Internal, reversible structure choices use the clearest
reasonable default and continue.

## Step 2 — Find the source of difficulty

Name concrete readability costs before designing the change. Look for:

- nested conditionals, callbacks, component trees, or data shapes that hide the
  main path;
- functions or files that mix unrelated responsibilities;
- indirection that requires jumping through wrappers, factories, base classes,
  generic helpers, or configuration to discover simple behavior;
- vague names (`data`, `item`, `manager`, `processor`, `helper`) or unfamiliar
  abbreviations that hide domain meaning;
- broad `utils`, `common`, or `shared` buckets with no clear owner;
- duplicated code whose small differences carry important meaning;
- generic database tables, EAV, polymorphic relationships, or nested JSON used
  for stable core fields;
- abstractions designed for possible future cases rather than observed change.

Do not treat every long function or repeated line as a defect. Complexity is
justified when removing it would hide a real rule, boundary, failure path, or
performance constraint.

## Step 3 — Choose the simplest adaptable shape

Apply these priorities in order:

1. Correct and safe behavior.
2. A main path readable from top to bottom.
3. Names that use familiar project/domain words.
4. Locality: behavior that changes together stays together.
5. Explicit boundaries around things that actually change independently.
6. Consistency with readable project conventions.
7. Speculative flexibility only when the request provides a concrete case.

### Control flow

- Prefer guard clauses and early returns when they make the normal path linear.
- Extract a named step when the name adds domain meaning or isolates a real side
  effect. Do not split code into tiny functions that force constant jumping.
- Prefer direct sequencing over deeply chained callbacks, decorators, or
  middleware for a local workflow.
- Treat more than roughly two levels of nesting as a review signal, not a rigid
  ban. Keep deeper nesting when it is the clearest representation and explain why.
- Make error paths visible near the operation that can fail.

### Names

- Use the words already used by users, product rules, schema, and public APIs.
- Name functions with one clear action and values with the concept they contain.
- Avoid invented jargon, clever metaphors, redundant type words, and uncommon
  abbreviations. Keep standard ecosystem abbreviations when they are clearer.
- Use the same word for the same concept and different words for different
  concepts. Do not alternate synonyms for variety.

### Components, modules, functions, and utilities

- Group primarily by feature/domain ownership. Colocate a helper with its only
  consumer until a second real owner or boundary exists.
- Create shared code for a stable shared contract, not merely for similar-looking
  lines. Keep meaningful differences explicit.
- Prefer composition and small concrete modules over inheritance or generic base
  frameworks unless the project has a proven variation point.
- Keep I/O and side effects at visible boundaries; keep business calculations
  direct and testable.
- A file should answer one understandable question. Do not force one export per
  file when a small cohesive group reads better.

### Database design

- Model real entities, events, and relationships with names from the domain.
- Prefer explicit typed columns for stable core fields. Use JSON/document fields
  when the shape is truly variable, is not a core query/constraint surface, and
  the trade-off is stated.
- Normalize enough to protect consistency; do not split a concept across many
  tables solely for theoretical purity. Denormalize only for an observed read or
  ownership need and state how consistency is maintained.
- Use clear primary keys, foreign keys, uniqueness, nullability, defaults, and
  checks. Constraints document and protect the model.
- Name join tables after the relationship or the two concepts consistently with
  the repository. Avoid generic `links`, `records`, or `metadata` tables.
- Add indexes from real access paths and measured needs, not every possible query.
- Make likely changes local: prefer additive migrations, stable identifiers, and
  explicit ownership. For destructive/schema migrations, use Sage's required
  backup, dry-run, integrity, and rollback/forward-fix controls.
- Avoid a universal schema intended to represent every future entity. A clear
  migration later is cheaper than permanent ambiguity now.

### Flexibility without over-engineering

Create a boundary only when at least one is true:

- an external system, storage engine, clock, or other side effect must be isolated;
- two real implementations or consumers already exist;
- a requirement identifies a near-term replacement or move;
- tests need a seam around nondeterminism;
- ownership, security, or deployment differs across the boundary.

Otherwise start concrete. Make future change easy through clear names, small
cohesive modules, explicit inputs/outputs, and localized side effects—not layers
of interfaces and factories.

## Step 4 — State the change contract

Before editing, output a compact intent block:

```text
Role       : dev — readable implementation/refactor for <target>
Behavior   : <preserve/change explicitly>
Hard parts : <nesting/naming/grouping/schema/indirection found>
Keep       : <readable project conventions to retain>
Simplify   : <accidental complexity not to copy>
Boundaries : <real seams retained or introduced, with reason>
Risk       : LOW | MEDIUM | HIGH · confidence:<low|medium|high>
Controls   : <behavior/data/public-contract evidence>
Decision   : proceed | warn | ask | reject
```

Apply the central Sage risk verdict. This skill cannot lower a gate.

## Step 5 — Implement in bounded steps

- For a refactor, characterize behavior with existing or focused tests before
  restructuring when practical. Keep behavior changes in a separate step/diff.
- Make the smallest coherent change that removes the identified difficulty.
- Preserve public names and shapes unless the request explicitly changes them.
- Do not perform unrelated cleanup just because nearby code is also imperfect.
- Prefer an obvious implementation over a reusable mini-framework.
- Delete obsolete indirection only after confirming every caller and migration
  path; do not leave two competing ways to do the same thing.
- Add comments for why a non-obvious rule or constraint exists. Do not narrate
  syntax that clear code already expresses.

## Step 6 — Validate behavior and readability

Run the repository's real tests, build, lint, type checks, and migration checks
that apply. Report actual output.

Then review the result from the caller's path:

- Can a reader find the entry point and follow the main path without opening many
  unrelated files?
- Do names reveal the domain action and data without a private glossary?
- Is each abstraction backed by a real boundary or repeated contract?
- Are important rules, error paths, and side effects explicit?
- Can one likely requirement change stay local, or is behavior scattered?
- Does the schema show entities, relationships, constraints, and lifecycle clearly?
- Did simplification preserve every required safety and compatibility control?

If the answer is no, revise once more or report the irreducible complexity and
its reason. Do not claim readability from line count alone.

## Step 7 — Capture only project-specific knowledge

Capture a project convention only when the work proves a durable, non-obvious
pattern. Do not save generic advice from this skill as team knowledge, and do not
promote an observed complex pattern into an approved convention automatically.

## Step 8 — Summary

Close with:

```markdown
── Sage Refactoring Code ───────────────────────────
**Target** · <files/modules/schema>
**Behavior** · <preserved and intentionally changed behavior>

**Simplified**
- <nesting, naming, grouping, abstraction, or schema improvement>

**Deliberate boundaries**
- <boundary kept/added and the concrete reason, or "none">

**Validated**
<commands and actual results>

**Residual complexity** · <what remains and why, or "none">
**Residual risk** · <LOW|MEDIUM|HIGH> — <evidence or remaining gap>
**Knowledge** · [new | updated | none] `<path>` — <pattern or reason>
────────────────────────────────────────────────────
```

When invoked inside an active `/sage` run, return this evidence to the parent
and continue with the remaining run instead of adding a new confirmation gate.
