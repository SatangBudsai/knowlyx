# Flow workspaces

Keep every durable artifact for one effort together so a human can find the
requirements, design, build plan, and debugging evidence from one entry point.

## Canonical layout

```text
agents/sage/flows/<flow-slug>/
  index.md                 # human entry point and artifact/evidence map
  spec.md                  # resolved decisions from /sage-grill or /sage-wayfinder
  flow.md                  # implementation design from /sage-flow
  tickets.md               # ordered build tickets from /sage-ticket
  evidence/
    index.md               # small catalog: what was captured, why, and result
    images/                # supplied/generated diagrams and supporting visuals
    screenshots/           # focused UI states used for diagnosis/validation
    traces/                # runner/browser traces only when they add evidence
    logs/                  # short, relevant extracts only; never raw log dumps
```

Create only files and directories the effort actually needs. Empty placeholder
folders add noise. `<flow-slug>` is one stable, kebab-case effort name shared
by Grill, Flow, Ticket, Review, and testing commands; do not create a second
slug just because the command changed.

## Start and maintain a flow workspace

Before writing a durable spec, flow, ticket file, or debug artifact:

1. Search `agents/sage/flows/*/index.md` for the request name, aliases, linked
   source paths, and matching scope. Reuse the existing workspace when it describes
   the same effort.
2. Otherwise derive a short stable slug from the user-visible effort, create
   `agents/sage/flows/<flow-slug>/index.md`, and record the title, status,
   scope, aliases, and artifact links.
3. Keep `index.md` current after every artifact write. Link only files that
   exist and use relative links so the flow folder remains movable.
4. Store reusable cross-flow knowledge separately in
   `agents/sage/<domain>/decisions/`; a flow workspace is the effort record,
   not a replacement for domain knowledge.

Use this compact entry-point shape:

```markdown
# <Flow title>

Status: discovery | requirements-clear | design-clear | building | complete | blocked
Updated: <ISO-8601>
Aliases: <searchable request/product terms, or none>

## Scope

<one short description and explicit boundary>

## Artifacts

| Artifact | Path | State |
| --- | --- | --- |
| Spec | [spec.md](spec.md) | grilling / requirements-clear |
| Flow | [flow.md](flow.md) | drafting / design-clear |
| Tickets | [tickets.md](tickets.md) | open / building / complete |
| Evidence | [evidence/index.md](evidence/index.md) | current |
```

Omit rows for files that do not exist. The flow index is a map, not a second
copy of their contents.

## Debug evidence ladder

Use the cheapest sufficient evidence and persist the smallest useful slice.
This applies to visual debugging and `/sage-e2e-test`; non-visual backend/CLI
failures may use a stack trace or log extract instead of inventing a screenshot.

1. Start with concise runner output and the first relevant stack trace/error.
2. For a reproducible visual failure, capture one focused screenshot of the
   failing state to `evidence/screenshots/<UTC-timestamp>-<step>-before.png`.
   Capture an `after` image when the fix changes a visible outcome. Prefer the
   smallest viewport/region that preserves the evidence.
3. Add a row to `evidence/index.md` immediately. Record timestamp, scenario,
   before/after, result, capture source, and relative path. Link the artifact
   from `spec.md`, `flow.md`, or `tickets.md` only when it supports a decision,
   acceptance criterion, or control.
4. Reuse the saved screenshot/trace/log instead of repeatedly reopening the
   browser or loading full browser state into model context.
5. Reproduce only the failing step with focused UI/accessibility, console,
   network, redirect, and state inspection when the saved evidence cannot
   classify test vs application vs environment failure.
6. Escalate to full browser/state debugging or the strongest reasoning allowed
   by the session ceiling only when focused reproduction is still insufficient,
   or the unresolved mechanism is a race, complex auth/session interaction, or
   cross-service failure. Record why escalation was necessary.

Screenshots are evidence, not automatic proof. Never capture secrets, tokens,
production PII, or unrelated user content. Use isolated test data; omit the
image and record the reason when a safe focused capture is unavailable. Do not
commit huge logs, redundant frames, videos, or traces when one smaller artifact
explains the result.

## Embed relevant images in Markdown

When a flow workspace contains a screenshot, diagram, mockup, or other image
that materially helps a reader understand an artifact, embed it in the Markdown
being created or updated. Use descriptive alt text and a relative path:

```markdown
![Checkout error before the fix](evidence/screenshots/<file>.png)
```

From a human doc under `docs/`, link back to the canonical workspace rather than
copying the image, for example:

```markdown
![Checkout sequence](../agents/sage/flows/<flow-slug>/evidence/images/<file>.png)
```

Keep the image near the paragraph, decision, step, ticket, or control it
supports. On update, verify that embedded paths exist; preserve relevant images,
replace stale ones, and remove broken references. Catalog every stored image in
`evidence/index.md`, but do not embed unrelated or redundant images merely to
make a document look richer.

`evidence/index.md` uses this shape:

```markdown
# Evidence

| Captured (UTC) | Kind | Scenario | Result | Source | Artifact |
| --- | --- | --- | --- | --- | --- |
| <timestamp> | screenshot-before | <failing step> | <observed state> | <tool/runner> | [file](screenshots/<file>.png) |
```

## Legacy compatibility

Older Sage versions wrote `agents/sage/flows/<slug>-spec.md`,
`<slug>-flow.md`, and `<slug>-tickets.md`. Search those exact paths when the
canonical flow file is absent. Do not bulk-move or delete legacy artifacts.
On the next material write to one, migrate its content into the matching flow
workspace file, update the workspace index, and replace the old file with a
short `Superseded by agents/sage/flows/<flow-slug>/<artifact>.md` pointer.
Readers must prefer the canonical workspace file and follow legacy pointers.

Classify every existing item before migration:

- Exact paths listed in `agents/sage/install-manifest.txt` are Sage-managed
  reference flows. Keep them flat and never migrate them into a user workspace.
- Existing `agents/sage/flows/<slug>/` directories are canonical user/team
  workspaces. Reuse them only when their `index.md` scope matches the effort.
- Flat `<slug>-spec.md`, `<slug>-flow.md`, and `<slug>-tickets.md` files not in
  the manifest are legacy generated artifacts. Migrate only the matching
  effort, only on its next write.
- Unknown files and directories are user-owned. Never rename, relocate,
  overwrite, or reorganize them automatically.

During migrate-on-write, move only the matching artifact set, preserve content
and history with the environment's VCS-aware move when practical, rewrite
internal relative links, create/update the workspace index, verify every new
path, then leave the legacy pointer. If the destination already contains
different content or its scope does not clearly match, stop and ask instead of
merging or overwriting.

Flat Markdown files directly under `agents/sage/flows/` remain valid for Sage's
installer-managed reference flows and legacy user artifacts. Generated effort
artifacts live only in subdirectories. Installers update only exact managed
files from `install-manifest.txt`; they must never recursively replace, move, or
delete a user's flow workspace or unknown file.
