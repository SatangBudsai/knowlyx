# Sage product context

## Project DNA

**Definition:** A versioned, queryable snapshot of evidence-backed project
understanding prepared before request-time reasoning.
**Invariants:** Every claim exposes provenance, freshness, confidence, scope,
and conflicts; derived summaries never replace their source.
**Includes:** Business, Architecture, Workflow, Design, Critical Flow,
Convention, Reusable Asset, Impact, and Risk-signal facets.
**Excludes:** unapproved business intent, raw secret content, or an AI agent's
private chain of thought.
**Related:** DNA snapshot, Observed fact, Inference, Approved knowledge.

## Observed fact

**Definition:** A claim directly evidenced by code, schema, configuration,
history, or another inspectable project source.
**Invariants:** It may refresh automatically because it is a disposable view of
the source; it cannot silently override approved policy.
**Includes:** an exported symbol, configured test command, generated-client
configuration, or import edge.
**Excludes:** a folder-name guess presented as architecture truth or business
intent inferred from common practice.
**Related:** Inference, Approved knowledge, Freshness.

## Inference

**Definition:** A detector or AI conclusion supported by signals but not proven
or approved as binding truth.
**Invariants:** It remains advisory, carries confidence and contrary evidence,
and cannot lower a safety gate.
**Includes:** a likely architecture pattern or probable domain ownership.
**Excludes:** direct source facts and human-approved rules.
**Related:** Observed fact, Approved knowledge.

## Approved knowledge

**Definition:** A business, policy, convention, or ownership declaration
ratified by an authorized human.
**Invariants:** Approval binds an exact revision and scope; replacement is
audited through supersession rather than silent overwrite.
**Includes:** business invariants, blocking conventions, and cross-repo
ownership decisions.
**Excludes:** scanner output, cached summaries, and AI-created proposals.
**Related:** Inference, Project DNA.

## DNA snapshot

**Definition:** An immutable, internally consistent view of Project DNA for one
scope and source fingerprint.
**Invariants:** Readers see only validated snapshots and pin one snapshot ID
through a reasoning run.
**Includes:** assertions, edges, facet manifests, provenance, and conflicts.
**Excludes:** a partially written refresh or mutable active record.
**Related:** Freshness, Project DNA.

## Freshness

**Definition:** Evidence that a DNA snapshot still matches its source inputs,
detector versions, and schema.
**Invariants:** A timestamp alone never proves freshness; source fingerprints
and invalidation state must agree.
**Includes:** `fresh`, `partial`, `stale`, and `degraded` states.
**Excludes:** “recently generated” without a matching source revision.
**Related:** DNA snapshot, Observed fact.
