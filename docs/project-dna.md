# Project DNA — Software Cognition Layer ของ Sage

> เอกสารนี้อธิบาย target architecture ของ Project DNA จากการเตรียมความเข้าใจ
> ครั้งแรก ไปจนถึงการ query และ refresh แบบ incremental อ้างอิง repository และ
> design spec จริง ณ 2026-07-30 สถานะปัจจุบัน: **specification only — runtime
> implementation ยังไม่ shipped**

## 1. Actors & Systems

| System | Responsibility | Ownership |
| --- | --- | --- |
| Human | กำหนด business intent และอนุมัติ binding knowledge | Product decisions และ approval |
| AI agent | ขอ context เท่าที่จำเป็นแล้ว reason/challenge/plan/code | Request-time reasoning |
| Sage control plane | บังคับ route, risk, required controls และ human gates | `AGENTS.md` |
| Project DNA engine | prepare, refresh และ query structured cognition | Companion runtime ใน target architecture |
| Repository adapter | อ่าน code/config/schema/history ภายใน scope | Implementation facts |
| DNA store | เก็บ snapshot, evidence, edges, freshness และ proposals | Derived cache + governed knowledge |
| Tool adapter | expose core ผ่าน MCP, CLI หรือ host integration | Transport; ไม่ fork policy |

**Trust boundary**

- Source code/config/schema เป็น authority ของ implementation fact
- Approved human knowledge เป็น authority ของ business/policy intent
- AI inference เป็น advisory จนกว่าจะถูกอนุมัติ
- Secret/credential/PII bodies ไม่เข้า DNA
- Cached DNA ห้ามลด central risk gate หรือซ่อน stale/conflict

## 2. End-to-end overview

```text
[Human/Agent] เปิด project ครั้งแรก
   |
   v prepareProjectDNA(scope)
[Project DNA engine] inventory source -> detect facets -> validate
   |
   v atomic activate
[DNA store] ACTIVE snapshot
   |
   v getProjectDNA(level=0, tokenBudget=300)
[Agent] พร้อมรับ request ด้วย identity/context ขนาดเล็ก
   |
   v classify intent + domain + risk signals
   |
   +-- L0 small/local
   +-- L1 domain summary
   +-- L2 related files/assets
   +-- L3 risky/deep investigation
   `-- L4 cross-repo/public-contract analysis
   |
   v reason -> challenge -> plan -> code -> self-review
   |
[Git/file event] changed inputs
   |
   v refreshProjectDNA(changedPaths)
[Engine] rebuild affected facets -> validate -> atomic activate
```

**หัวใจ:** Sage เตรียม cognition ก่อนใช้งานและโหลดตามความจำเป็น แต่ route,
freshness, conflicts, risk และ human gates เป็น safety kernel ที่เปิดเสมอ

## 3. Step-by-step

### STEP 1 — Prepare Project DNA

**System:** Project DNA engine + Repository adapter

- resolve `company > workspace > project > repo > module > feature`
- canonicalize path/scope และตรวจสิทธิ์ก่อนอ่าน
- inventory manifests, source, schema, CI, generators, tests และ design system
- skip secrets, binaries, ignored/vendor/build outputs ตาม policy
- สร้าง Level 0 ก่อน facet ลึกเพื่อให้ project ใช้งานแบบ progressive ได้

### STEP 2 — Classify claims

**System:** DNA detectors + DNA store

- `observed`: มี evidence ตรงจาก source เช่น export/config/import edge
- `declared`: คนหรือระบบเจ้าของประกาศ
- `inferred`: detector/AI สรุปจาก signals แต่ยังไม่ใช่ binding truth
- `approved`: governance state ที่ authenticated human อนุมัติ
- ทุก claim มี provenance, confidence, scope, freshness และ conflicts

Scanner ห้ามเปลี่ยน folder-name heuristic หรือ majority pattern เป็นคำว่า `must`
โดยอัตโนมัติ

### STEP 3 — Activate a consistent snapshot

**System:** Project DNA engine + DNA store

- validate schema, references, scope boundaries และ facet completeness
- candidate ที่ critical validation fail ไม่แทน active snapshot เดิม
- non-critical failure อาจ publish `DEGRADED` พร้อม missing facets
- reader เห็น snapshot สมบูรณ์ล่าสุดเสมอ ไม่เห็นผล refresh ครึ่งชุด

### STEP 4 — Load progressive context

**System:** AI agent + Query kernel

| Level | โหลดอะไร | ใช้เมื่อ |
| --- | --- | --- |
| L0 | identity, architecture shape, critical domains, safety metadata | ทุก code request |
| L1 | domain terms/rules/summary | intent อยู่ใน domain เดียว |
| L2 | related files, real exports, assets, conventions | ต้องออกแบบ/เขียน implementation |
| L3 | raw evidence และ deep investigation | auth/money/migration/conflict/unknown |
| L4 | workspace dependency และ cross-repo impact | public contract หรือหลาย repo |

L0 มี target 100–300 tokens; budget อื่นเป็น hypothesis ที่ต้อง benchmark

### STEP 5 — Query only the needed facets

**System:** AI agent + Tool adapter

- component ใหม่ → `getReusableAssets`
- API/client change → `getWorkflowDNA` + `getConventions`
- architecture boundary → `getArchitectureDNA`
- sensitive change → `getImpact` + `getRisks` แล้วใช้ central gate ตัดสิน
- UI change → `getDesignDNA`
- business term/rule → `getBusinessContext`

Response ทุกตัว pin `snapshotId` เดียวและมี mandatory freshness/provenance/conflict
metadata; token budget ตัด metadata เหล่านี้ไม่ได้

### STEP 6 — Refresh only affected DNA

**System:** Repository adapter + Project DNA engine

- normalize Git/file/package/design changes เป็น `ChangeSet`
- map changed paths ไป detector/facet/edge/summary ที่ได้รับผล
- deduplicate refresh ด้วย scope + source fingerprint + detector set
- watcher ช่วยลด latency แต่ fingerprint reconciliation เป็น correctness control
- เมื่อ refresh fail → reader ใช้ last complete snapshot พร้อม stale/degraded state

### STEP 7 — Human-govern durable knowledge

**System:** AI agent + Human + DNA store

- AI สร้าง proposal พร้อม evidence และ rationale ใน non-binding staging
- proposal ไม่ถูก inject เป็น active memory
- human เลือก approve/reject/request changes ต่อ exact revision
- approval บันทึก actor, scope, timestamp และ supersession
- observed source facts refresh อัตโนมัติได้; binding memory เปลี่ยนเองไม่ได้

## 4. State / data lifecycle

### Project DNA facets

| Facet | Content |
| --- | --- |
| Project Identity | stack, repo role, architecture shape, critical domains |
| Business DNA | canonical terms, invariants, approved rules, ownership |
| Architecture DNA | modules, boundaries, dependencies, generated zones |
| Workflow DNA | build/test/lint/codegen/migration/deploy |
| Design DNA | tokens, primitives, component and interaction patterns |
| Critical Flow DNA | auth/payment/order flows และ trust boundaries |
| Reusable Assets | components, hooks, utils, services, types, exports |
| Convention Graph | observed patterns, exceptions, approved enforcement |
| Impact Graph | calls, dependencies, events, generation, consumers |
| Risk Signals | driver evidence; ไม่ใช่ authority ที่ลด gate |

### Snapshot lifecycle

```text
ABSENT -> PREPARING -> FRESH
FRESH -- source mismatch --> STALE
FRESH -- partial failure --> DEGRADED
STALE|DEGRADED -- validated refresh --> FRESH
```

Timestamp อย่างเดียวไม่พิสูจน์ freshness ต้องมี source fingerprint, schema
version, detector versions และ invalidation state

### Knowledge lifecycle

```text
PROPOSED -> APPROVED
PROPOSED -> REJECTED
PROPOSED -> CHANGES_REQUESTED -> PROPOSED(new revision)
APPROVED -> SUPERSEDED(human-approved replacement)
```

## 5. Tool API

### Preparation and capability

| Tool | Purpose |
| --- | --- |
| `getSageCapabilities` | ตรวจ schema/facets/levels/tools จาก capability จริง |
| `prepareProjectDNA` | initial/reconcile preparation แบบ idempotent |
| `refreshProjectDNA` | delta refresh จาก changed paths/fingerprint |
| `getProjectDNAStatus` | progress, active snapshot, diagnostics, stale reason |

### Query

| Tool | Purpose |
| --- | --- |
| `getProjectDNA` | โหลด bundle ตาม L0–L4 และ token budget |
| `getBusinessContext` | terms, invariants, approved rules, conflicts |
| `getArchitectureDNA` | modules, boundaries, dependencies, generated zones |
| `getWorkflowDNA` | build/test/lint/codegen/migration/deploy |
| `getDesignDNA` | tokens, primitives, components, interactions |
| `getImpact` | direct/indirect/cross-repo impacts พร้อม evidence |
| `getRisks` | risk drivers/controls to consider; ลด central gate ไม่ได้ |
| `getReusableAssets` | real exports/signatures/usage evidence |
| `getConventions` | pattern, exceptions, approved enforcement |

### Governance

| Tool | Purpose |
| --- | --- |
| `proposeKnowledge` | เขียน proposal ใน non-binding staging |
| `reviewKnowledgeProposal` | human approve/reject/request changes |

Common response envelope ต้องมี:

```jsonc
{
  "schemaVersion": "1.0",
  "snapshotId": "dna:01J...",
  "scope": { "scopeId": "repo:01J...", "kind": "repo" },
  "freshness": { "state": "fresh", "staleFacets": [] },
  "confidence": { "level": "high", "basis": [] },
  "provenance": [],
  "conflicts": [],
  "data": {},
  "continuation": null,
  "warnings": []
}
```

Errors ขั้นต่ำ: `DNA_NOT_PREPARED`, `DNA_STALE`, `DNA_DEGRADED`,
`SCOPE_NOT_FOUND`, `SCOPE_FORBIDDEN`, `BUDGET_TOO_SMALL`,
`REFRESH_IN_PROGRESS`, `UNSUPPORTED_SCHEMA`, `DNA_CONFLICT`,
`PARTIAL_RESULT`

## 6. Scope inheritance

```text
company -> workspace -> project -> repo -> module -> feature
```

- observed facts ไม่ inherit
- approved knowledge inherit เมื่อ `appliesTo` ครอบคลุม child
- non-safety preference ใช้ specific scope กว่า
- `block`/safety policy ใช้ most-restrictive wins
- child ผ่อน parent safety ได้เฉพาะ explicit human-approved supersedes
- unresolved conflicts ถูกส่งกลับให้ agent/gate ไม่ถูก resolve เงียบ ๆ

## 7. Data model

| Entity | Role |
| --- | --- |
| `Scope` | hierarchy + portable identity |
| `SourceRef` | path/symbol/hash provenance |
| `Snapshot` | immutable consistent DNA view |
| `FacetManifest` | completeness + detector/invalidation inputs |
| `Assertion` | observed/declared/inferred claim + governance |
| `Edge` | dependency/call/impact/ownership/conflict |
| `PreparationJob` | idempotent preparation/refresh lifecycle |
| `KnowledgeProposal` | human review lifecycle |
| `GovernanceEvent` | append-only approval audit |

Pilot แนะนำ embedded SQLite สำหรับ metadata/transactions และ content-addressed
payloads สำหรับ derived data แต่ public schema เป็น storage-agnostic Computed
cache ลบและ rebuild ได้ ส่วน approved knowledge ต้อง backup/export ได้

## 8. Edge cases & errors

| Case | Handling |
| --- | --- |
| Huge monorepo | publish L0 ก่อน; partition scan; progress per facet |
| Dirty tree/branch switch | fingerprint รวม working tree; mark stale เมื่อ mismatch |
| Unsupported language | report degraded/unknown; ไม่เดา architecture |
| Generated/vendor output | index generator/config/exports; skip noisy bodies |
| Runtime-only consumer/feature flag | report unknown; L3/L4/manual evidence |
| Symlink/path escape | canonicalize + reject path นอก approved root |
| Secret file | skip body; redacted classification only |
| Missed watcher event | fingerprint reconciliation จับ mismatch |
| Concurrent refresh | deduplicate writer; readers pin active snapshot |
| Corrupt cache | use last valid snapshot/rebuild computed data |
| Conflicting approved rules | return conflict + human/risk gate |
| Tool unavailable | protocol-only fallback + explicit validation gap |

## 9. Security & concurrency

- authorize scope ทุก prepare/query; cache key ไม่ใช่ permission
- deny secret/credential/PII body ingestion และ redact logs
- one writer lease ต่อ scope; lease expiry activate partial snapshot ไม่ได้
- active pointer และ governance event ใช้ atomic transaction/append
- pagination และทุก tool call ใน reasoning run pin snapshot เดียว
- approval retry idempotent ตาม proposal revision/action/actor
- concurrent conflicting approval ไม่ใช้ last-write-wins

## 10. Build checklist

### Phase 0 — Spec and evaluation

- [x] Project DNA schema, tools, lifecycle, safety และ migration contract
- [ ] labeled fixture repos + protocol-only baseline
- [ ] detector/impact precision, recall และ false-confidence evaluation

### Phase 1 — Local builder

- [ ] safe inventory + evidence-first detectors
- [ ] embedded store + atomic snapshots
- [ ] progressive initial prepare + CLI debug tools
- [ ] secret/path/concurrency negative tests

### Phase 2 — Query tools

- [ ] hierarchy/conflict/token query kernel
- [ ] L0–L4 context planner
- [ ] provider-neutral tool contract + first MCP adapter
- [ ] warm latency/token reduction benchmarks

### Phase 3 — Incremental and multi-repo

- [ ] ChangeSet/facet invalidation graph
- [ ] watcher + fingerprint reconciliation
- [ ] workspace dependency and L4 impact
- [ ] crash recovery/rollback/concurrent refresh tests

### Phase 4 — Human-governed shared cognition

- [ ] proposal/review/audit workflow
- [ ] approved knowledge import/export
- [ ] additional host adapters by capability
- [ ] hosted/shared architecture after local security proof

### Compatibility gates

- [ ] import current Markdown knowledge without losing enforcement/scope/history
- [ ] preserve `.sage-local.json`, slash commands and installer non-clobber
- [ ] no-tool agents remain honest protocol-only clients
- [ ] disabling the engine loses no approved knowledge
- [ ] update “no runtime” public contract only after runtime passes acceptance

## 11. Open questions

ไม่มี product decision ที่ block สเปก:

- SQLite เป็น pilot default ไม่ใช่ public dependency
- MCP เป็น first adapter แต่ core contract provider-neutral
- 2–10 minute preparation เป็น hypothesis ไม่ใช่ SLA
- shared cloud memory ถูกเลื่อนไปหลัง local correctness/security proof

รายละเอียด implementation และ acceptance contract เต็มอยู่ที่
[`agents/sage/flows/project-dna-flow.md`](../agents/sage/flows/project-dna-flow.md)
