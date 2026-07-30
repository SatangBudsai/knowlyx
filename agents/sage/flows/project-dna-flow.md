# Project DNA — preparation-first cognition layer

> สเปกสถาปัตยกรรมสำหรับเปลี่ยน Sage จากการอ่านและวิเคราะห์ใหม่ทุก request
> ไปเป็นการเตรียมความเข้าใจของ project ล่วงหน้า แล้วให้ AI agent โหลดเฉพาะ
> context ที่ต้องใช้ อ้างอิง repository และประวัติ implementation จริง ณ
> 2026-07-30 สถานะ: `design-clear`; runtime implementation ยังไม่เริ่ม

## 1. Header + design decisions

Project DNA เป็น data plane ของ Sage: สแกน source, config, schema, workflow,
design system และความรู้ที่อนุมัติแล้วเป็น snapshot ที่ query ได้ ส่วน
`AGENTS.md` เป็น control plane ที่กำหนดว่า agent ต้องคิด ตัดสิน risk และหยุดที่
gate อย่างไร ระหว่างที่ Project DNA runtime ยังไม่ถูกสร้าง รุ่นปัจจุบันยังทำงาน
ด้วย Markdown protocol ตามเดิม

การตัดสินใจหลัก:

- ใช้ `preparation-first`: เตรียม DNA ครั้งแรกแบบ progressive แล้ว refresh เฉพาะ
  facet ที่ input เปลี่ยน ไม่สแกนทั้ง repo ทุก request
- Tool API เป็นช่องทางหลักของ computed DNA ใน target architecture; agent ไม่ต้อง
  parse Markdown เพื่อค้นหา architecture, workflow, assets หรือ impact เอง
- Markdown knowledge ยังเป็น human-reviewable policy source, Git-portable
  bootstrap และ fallback แต่ไม่ใช่ computed cache
- Full Project DNA เป็น companion engine ที่จำเป็นสำหรับ tool-first features
  แต่ protocol-only mode ยังเป็น supported compatibility mode ระหว่าง migration;
  adapter ต้องตรวจ capability และห้ามจำลอง DNA ที่ไม่มีด้วยข้อความมั่นใจเกินจริง
- แยก `observed`, `inferred` และ `approved` ห้าม scanner ยกระดับ heuristic
  ให้เป็น binding rule โดยอัตโนมัติ
- ทุกผลลัพธ์มี scope, freshness, confidence, provenance และ conflicts; stale หรือ
  low-confidence DNA ห้ามถูกนำเสนอเหมือน fact ที่สดและแน่นอน
- snapshot เป็น immutable และ activate แบบ atomic; reader เห็น snapshot สมบูรณ์
  ล่าสุดเสมอ ไม่เห็นผลสแกนครึ่งชุด
- schema เป็น provider-neutral; MCP, CLI, IDE หรือ agent adapter เป็น transport
  รอบ core เดียวกัน ไม่สร้าง cognition logic แยกตาม provider

Related decisions:

- [`prepare-dna-before-runtime-reasoning`](../sage-product/decisions/prepare-dna-before-runtime-reasoning.md)
- [`separate-observations-from-approved-knowledge`](../sage-product/decisions/separate-observations-from-approved-knowledge.md)
- [`separate-control-plane-from-dna-data-plane`](../sage-product/decisions/separate-control-plane-from-dna-data-plane.md)

### Out of scope

- ไม่เขียน scanner, database, daemon, MCP server หรือ agent adapter ในรอบนี้
- ไม่อ้างว่า Project DNA ใช้งานได้แล้วใน release ปัจจุบัน
- ไม่บังคับ cloud service, vector database หรือ LLM provider ใดเป็น dependency
- ไม่ทำ shared company memory sync, RBAC dashboard หรือ hosted control plane
- ไม่ให้ AI approve, reject หรือแก้ binding knowledge แทนมนุษย์
- ไม่รับประกันเวลา prepare 2–10 นาทีเป็น SLA จนมี benchmark บน repo จริง
- ไม่แทนที่ source code/schema ด้วย summary; source จริงยังเป็น authority
- ไม่ย้ายหรือลบ Markdown knowledge และ protocol ปัจจุบันก่อน migration สำเร็จ
- ไม่อ้างว่า static analysis มองเห็น runtime-only calls, deployed versions,
  feature flags หรือ external consumers ได้ครบ

## 2. Actors & Systems

| System | Responsibility | Ownership |
| --- | --- | --- |
| Human | กำหนด business intent, workspace hierarchy และอนุมัติ binding knowledge | เป็นเจ้าของ product decision และ approval |
| AI agent | classify request, ขอ DNA เท่าที่ต้องใช้, reason/challenge/plan/code | ใช้ข้อมูลตาม confidence และห้ามลด risk จาก inference |
| Sage control plane | บังคับ route, risk gates, required controls และ human approval | `AGENTS.md` ในรุ่นปัจจุบัน |
| Preparation coordinator | รับ initial/refresh job, deduplicate, จัดลำดับ detector และ publish snapshot | เป็นเจ้าของ job lifecycle |
| Repository adapter | อ่าน Git state, files, manifests, schemas และ generated markers ภายใน scope | source code/config เป็น implementation authority |
| DNA detectors | สร้าง observations สำหรับ architecture, workflow, design, conventions และ assets | สร้าง evidence-backed observations เท่านั้น |
| DNA store | เก็บ immutable snapshots, assertions, edges, provenance และ proposal state | cache local; binding knowledge มี governance แยก |
| Query kernel | resolve hierarchy, freshness, conflicts, context level และ token budget | เป็นเจ้าของ response contract |
| Tool adapters | expose query/prepare/status ผ่าน MCP, CLI หรือ host integration | transport เท่านั้น ห้ามมี policy fork |

**Trust boundary**

- Repository content พิสูจน์ implementation fact; generated summary ห้าม override
  code/schema ที่ขัดกัน
- Approved human knowledge พิสูจน์ business/policy intent; observation ที่ขัดกัน
  ต้องสร้าง conflict ไม่ใช่ overwrite
- AI inference เป็น advisory เสมอจนมนุษย์อนุมัติ
- Agent client ส่ง `requestIntent` ได้แต่ห้ามกำหนด `risk=LOW`, `confidence=high`
  หรือ `approved=true` ให้ตัวเอง
- Tool adapter ต้องส่ง scope identity ที่ตรวจสอบแล้ว; ห้าม query ข้าม workspace
  เพราะ path หรือชื่อ repo ตรงกัน
- Secret values, credentials และ PII ไม่เป็น DNA payload; เก็บได้เพียง safe
  metadata เช่น “มี secret reference ใน deployment config”

## 3. End-to-end overview

```text
[Human/Agent] เปิด project ครั้งแรก
   |
   v prepareProjectDNA(scope)
[Preparation coordinator] resolve workspace/repo + source fingerprint
   |
   +-- Repository adapter: inventory manifests, code, schema, CI, design assets
   +-- DNA detectors: emit observed assertions + evidence + confidence
   +-- Knowledge loader: load approved declarations; keep proposals separate
   |
   v validate snapshot -> atomic activate
[DNA store] ACTIVE snapshot + facet dependency graph
   |
   v getProjectDNA(level=0, tokenBudget=300)
[Agent] พร้อมรับ request ด้วย project identity ขนาดเล็ก
   |
   v request -> tiny classify intent/domain/risk signals
   |
   +-- small/local ----------> load L0
   +-- domain work ----------> load L0 + L1
   +-- related implementation> load L0 + L1 + L2
   +-- risky/unknown --------> run L3 investigation
   `-- cross-repo/public ----> run L4 workspace analysis
   |
   v reason -> challenge -> plan -> generate -> self-review
[Git/file event] changed paths + new fingerprint
   |
   v refreshProjectDNA(changedPaths)
[Coordinator] invalidate affected facets/edges only
   |
   v build candidate snapshot -> validate -> atomic activate
[Readers] receive new ACTIVE snapshot; old complete snapshot remains recoverable
```

**หัวใจ:** Project DNA ลดงานอ่านซ้ำ แต่ไม่ลดมาตรฐานการพิสูจน์ แหล่งข้อมูล,
freshness และความขัดแย้งต้องติดไปกับ context ทุกชิ้น

## 4. Step-by-step

### STEP 1 — Resolve scope and identity

**System:** Preparation coordinator + Repository adapter

- เมื่อ client ส่ง path → canonicalize path, resolve symlink และหา repo root
- เมื่อ workspace config มีหลาย repo → map repo ไป `workspace > project > repo`
- เมื่อ repo ไม่มี Git → ใช้ content fingerprint และระบุ
  `sourceRevision.kind="content-hash"`
- เมื่อ scope อยู่นอกสิทธิ์ของ caller → จบด้วย `SCOPE_FORBIDDEN`; ห้ามเริ่ม scan
- สร้าง stable `scopeId` จาก canonical locator ไม่ใช้ display name เป็น identity

### STEP 2 — Build a safe inventory

**System:** Repository adapter

- อ่าน tracked/eligible files, manifests, lockfiles, schema, CI, generator config,
  test config และ design-system entry points
- เคารพ VCS ignore, Sage ignore, binary/size limits และ symlink boundary
- ไม่อ่าน secret file bodies เช่น `.env`, private keys, credential stores
- ระบุ generated/vendor/build outputs แยกจาก authored source
- คำนวณ `SourceRef` และ content hash ที่ detector ใช้เป็น evidence

### STEP 3 — Produce evidence-backed observations

**System:** DNA detectors

- Architecture detector สร้าง candidate pattern พร้อม signals ที่สนับสนุนและ
  signals ที่ขัดแย้ง
- Workflow detector อ่าน config/export จริงของ OpenAPI/codegen/ORM/CI/build/test
- Asset detector ระบุ symbol, export, path, usage evidence และ scope
- Convention detector วัดตัวอย่าง/ข้อยกเว้น; ไม่เปลี่ยน majority pattern เป็นคำว่า
  `must` โดยไม่มี approved declaration
- Design detector อ่าน tokens, component APIs, layout primitives และ interaction
  patterns พร้อม provenance
- Business/Critical Flow detector รวม approved knowledge กับ code/schema evidence
  แต่ติดป้าย inference แยกจาก human declaration

### STEP 4 — Merge declarations without erasing conflicts

**System:** Query kernel + DNA store

- `observed` คือสิ่งที่ scanner พิสูจน์จาก source
- `declared` คือข้อความที่คนหรือระบบเจ้าของประกาศ
- `inferred` คือข้อสรุปของ AI/detector ที่ยังต้องตรวจ
- `approved` เป็น governance state ของ declaration ไม่ใช่ confidence score
- เมื่อ observed implementation ขัด approved policy → เก็บทั้งคู่และสร้าง
  `DNA_CONFLICT`; ห้ามเลือกข้างเงียบ ๆ
- เมื่อ child scope override parent → ใช้กฎ inheritance ใน §5.4

### STEP 5 — Validate and activate a snapshot

**System:** Preparation coordinator + DNA store

- ตรวจ schema version, referential integrity, scope boundary และ provenance
- คำนวณ facet completeness และ validation warnings
- เขียน candidate snapshot แบบ immutable
- เมื่อ critical facet validation fail → candidate เป็น `FAILED`; active snapshot
  เดิมไม่เปลี่ยน
- เมื่อ non-critical facet fail → candidate เป็น `DEGRADED` พร้อม missing facets
- activate pointer แบบ atomic หลัง validation เท่านั้น

### STEP 6 — Serve Level 0 immediately

**System:** Query kernel

- ตอบ project identity, architecture shape, critical domains, essential
  conventions และ freshness ภายใน target budget 100–300 tokens
- เมื่อ initial preparation ยังไม่เสร็จแต่ L0 พร้อม → ตอบ
  `freshness.state="partial"` และระบุ facets ที่ยังทำงาน
- เมื่อไม่มี active snapshot → `DNA_NOT_PREPARED` พร้อม recommended action
- ห้ามสร้าง prose ยาวเกิน budget แล้วตัด provenance/conflict ออก

### STEP 7 — Classify a request and load progressively

**System:** AI agent + Query kernel

- tiny classifier หา action, domain, likely scope และ risk signals
- request เล็กที่ไม่แตะ behavior → L0
- domain-local change → L0 + L1 domain summary
- change ที่ต้องเลือก files/assets → L2 related files and reusable assets
- auth, money, migration, destructive, external side effect หรือ confidence gap →
  L3 deep investigation
- public contract หรือหลาย repo → L4 cross-repo impact
- risk gate ใน control plane ยังมีผลแม้ DNA บอก risk ต่ำ
- safety kernel ได้แก่ route, source/freshness/conflict disclosure, risk drivers
  และ human gates เป็น always-on; progressive loading ลด domain context ได้แต่
  ห้ามลด kernel นี้

### STEP 8 — Query focused facets

**System:** AI agent + Tool adapter + Query kernel

- agent เรียก tool เฉพาะความต้องการ เช่น `getReusableAssets` ก่อนสร้าง component
- query kernel filter ด้วย scope, domain, paths, kinds และ token budget
- response มี evidence summaries และ stable IDs เพื่อให้ agent ขอรายละเอียดต่อ
- เมื่อ budget ไม่พอสำหรับ mandatory safety/conflict metadata → ตอบ
  `BUDGET_TOO_SMALL` แทนการซ่อนข้อมูล
- ทุก response บอก snapshot ID เดียวกันเพื่อป้องกัน context ข้าม version

### STEP 9 — Refresh from change events

**System:** Repository adapter + Preparation coordinator

- Git/file/package/design event สร้าง normalized `ChangeSet`
- map changed paths → detectors → facets → edges → summaries ที่ได้รับผล
- job key คือ `scopeId + sourceFingerprint + detectorSet`; retry แล้วไม่สร้างงานซ้ำ
- readers ใช้ active snapshot เดิมระหว่าง refresh
- เมื่อ candidate ใหม่สำเร็จ → atomic activate; mark snapshot เดิม superseded
- เมื่อ event หายหรือ watcher ไม่พร้อม → status query ตรวจ fingerprint mismatch
  และเสนอ full reconciliation

### STEP 10 — Propose and approve durable knowledge

**System:** AI agent + Human + DNA store

- AI ส่ง `proposeKnowledge` พร้อม claim, scope, evidence, rationale และ conflicts
- proposal เริ่ม `PROPOSED` ใน staging store; คำว่า “memory” ในสเปกนี้หมายถึง
  active inherited knowledge ดังนั้น proposal ที่ persist เพื่อ review ยังไม่ใช่
  memory update และไม่ถูก inject เป็น binding context
- human review อาจ `APPROVE`, `REJECT` หรือ `REQUEST_CHANGES`
- approval บันทึก actor, time, scope, exact revision และ supersedes
- approved declaration ทำให้ affected summaries stale และ trigger refresh
- observed facts refresh อัตโนมัติได้ เพราะเป็น cache จาก source; การเปลี่ยน
  binding memory ต้องผ่าน human เสมอ

## 5. State / data handling

### 5.1 Scope

```jsonc
{
  "scopeId": "repo:01J...",
  "kind": "repo", // company | workspace | project | repo | module | feature
  "parentScopeId": "project:01J...",
  "displayName": "checkout-api",
  "locator": {
    "canonicalRemote": "https://example.invalid/org/checkout-api.git",
    "rootFingerprint": "sha256:..."
  }
}
```

- `scopeId` คงที่แม้ local path เปลี่ยน
- local path เป็น runtime locator ไม่ใช่ portable identity
- module/feature scope อ้าง repo + canonical path/symbol selector

### 5.2 Snapshot

```jsonc
{
  "snapshotId": "dna:01J...",
  "schemaVersion": "1.0",
  "scopeId": "repo:01J...",
  "status": "ACTIVE",
  "sourceRevision": {
    "kind": "git",
    "value": "8b38a11...",
    "dirtyFingerprint": "sha256:..."
  },
  "generatedAt": "2026-07-30T12:00:00Z",
  "freshness": {
    "state": "fresh",
    "checkedAt": "2026-07-30T12:00:01Z",
    "staleFacets": []
  },
  "facetCompleteness": {
    "architecture": "complete",
    "workflow": "complete",
    "design": "not_applicable"
  }
}
```

Snapshot lifecycle:

- candidate ถูกสร้างเมื่อ initial prepare หรือ refresh
- active pointer เปลี่ยนหลัง validation สำเร็จ
- superseded snapshot เก็บตาม retention เพื่อ rollback/debug
- failed candidate เก็บ diagnostics แต่ไม่ถูก query เป็น active
- cache deletion ลบ computed snapshots ได้; approved knowledge มี retention และ
  recovery contract แยก

### 5.3 DNA assertion and edge

```jsonc
{
  "assertionId": "assert:01J...",
  "facet": "workflow",
  "subject": "api-client",
  "predicate": "generated_by",
  "value": "orval",
  "origin": "observed", // observed | declared | inferred
  "governance": "ephemeral", // ephemeral | proposed | approved | rejected
  "confidence": 0.98,
  "scopeId": "repo:01J...",
  "evidence": [
    {
      "sourceRef": "src:01J...",
      "path": "orval.config.ts",
      "symbol": "default",
      "contentHash": "sha256:...",
      "detector": "workflow.orval/v1"
    }
  ],
  "conflictsWith": [],
  "supersedes": null
}
```

Edge ใช้ shape เดียวกันแต่มี `fromId`, `relationship`, `toId`; relationship
ขั้นต่ำคือ `belongs_to`, `depends_on`, `generated_by`, `calls`, `publishes`,
`consumes`, `impacts`, `implements`, `governed_by` และ `conflicts_with`

### 5.4 Hierarchy and inheritance

```text
company -> workspace -> project -> repo -> module -> feature
```

- Observed facts ไม่ inherit; แต่ละ scope ต้องมี evidence ของตัวเอง
- Approved business/policy declarations inherit ลงด้านล่างเมื่อ `appliesTo`
  ครอบคลุม child scope
- สำหรับ non-safety preference: scope ที่ specific กว่าชนะ
- สำหรับ `enforcement=block` หรือ safety policy: most restrictive applicable
  rule ชนะ; child จะผ่อน parent ได้เมื่อมี explicit human-approved supersedes
- Proposed/rejected entries ไม่เข้าชุด binding inheritance
- ความขัดแย้งที่ resolve ไม่ได้ต้องอยู่ใน `conflicts`; query ห้ามเลือกเงียบ ๆ

### 5.5 Project DNA facets

| Facet | Contains | Typical sources |
| --- | --- | --- |
| Project Identity | stack, repo role, architecture shape, critical domains | manifests, folder graph, workspace config |
| Business DNA | canonical terms, invariants, approved rules, ownership | approved knowledge, schema, flow docs |
| Architecture DNA | modules, boundaries, dependencies, generated zones | imports, configs, schemas, repo graph |
| Workflow DNA | build/test/lint/codegen/migration/deploy sequences | package scripts, CI, generator/ORM config |
| Design DNA | tokens, primitives, component hierarchy, interaction patterns | design system, styles, component exports |
| Critical Flow DNA | auth/payment/order/etc. steps and trust boundaries | approved flows, routes, events, schemas |
| Reusable Assets | components, hooks, utils, services, types and exports | source symbols + usage edges |
| Convention Graph | observed pattern + exceptions + approved enforcement | code samples, lint/test config, knowledge |
| Impact Graph | calls, depends_on, publishes/consumes, generated_by | imports, APIs, events, workspace graph |
| Risk Signals | driver evidence; never final authority to lower a gate | sensitive paths, side effects, approved rules |

### 5.6 Context levels

| Level | Purpose | Initial target budget | Trigger |
| --- | --- | --- | --- |
| L0 | project identity ที่ต้องรู้เสมอ | 100–300 tokens | ทุก code request |
| L1 | domain summary | 300–800 tokens/domain | intent ระบุ domain |
| L2 | related files, exports, assets, conventions | 1,000–3,000 tokens | implementation ต้องอ่าน surface |
| L3 | deep investigation พร้อม raw evidence | request-defined | risk driver, conflict หรือ unknown สำคัญ |
| L4 | workspace/cross-repo impact | request-defined | public contract หรือหลาย repo |

Budget เป็น target ที่ benchmark ต้องยืนยัน ไม่ใช่เหตุให้ตัด conflict, freshness,
required control หรือ provenance ขั้นต่ำ

## 6. Tool API spec

Tool names เป็น logical contract; transport อาจเป็น MCP, CLI, IDE RPC หรือ direct
library call แต่ request/response semantics ต้องเหมือนกัน

### 6.1 Common response envelope

```jsonc
{
  "schemaVersion": "1.0",
  "requestId": "req:01J...",
  "snapshotId": "dna:01J...",
  "scope": { "scopeId": "repo:01J...", "kind": "repo" },
  "freshness": {
    "state": "fresh", // fresh | partial | stale | degraded
    "checkedAt": "2026-07-30T12:00:01Z",
    "staleFacets": []
  },
  "confidence": {
    "level": "high",
    "basis": ["2 direct config signals", "0 unresolved conflicts"]
  },
  "provenance": [
    { "sourceRef": "src:01J...", "path": "package.json" }
  ],
  "conflicts": [],
  "data": {},
  "continuation": null,
  "warnings": []
}
```

Mandatory envelope fields ห้ามถูกตัดตาม token budget ส่วน `data` ต้อง honor
budget และใช้ continuation เมื่อผลยาว

### 6.2 Preparation tools

#### `prepareProjectDNA`

Request:

```jsonc
{
  "scope": { "path": "C:/work/checkout-api" },
  "mode": "initial", // initial | reconcile
  "requestedFacets": ["all"]
}
```

Response:

```jsonc
{
  "jobId": "job:01J...",
  "status": "QUEUED",
  "scopeId": "repo:01J...",
  "sourceFingerprint": "sha256:..."
}
```

- Side effect: enqueue idempotent preparation job
- Idempotency: request fingerprint เดิมคืน job เดิมหรือ active snapshot เดิม
- Guard: caller ต้องมี read access ต่อทุก path ใน resolved scope

#### `refreshProjectDNA`

Request:

```jsonc
{
  "scopeId": "repo:01J...",
  "changedPaths": ["orval.config.ts", "src/api/generated/index.ts"],
  "sourceFingerprint": "sha256:..."
}
```

- Side effect: invalidate facets ตาม dependency map และ enqueue delta job
- เมื่อ `changedPaths` ไม่เชื่อถือได้ → run reconcile inventory ก่อน
- เมื่อ fingerprint ตรง active snapshot → return `NO_CHANGE`

#### `getProjectDNAStatus`

คืน job status, active snapshot, progress by facet, diagnostics, stale reason และ
recommended action ไม่มี side effect

#### `getSageCapabilities`

คืน schema versions, supported facets, context levels, tool names, transport
features, maximum budgets และ governance capabilities เพื่อให้ adapter เลือก
เส้นทางจาก capability จริง ไม่เดาจากชื่อ provider

### 6.3 Query tools

| Tool | Purpose | Required filters |
| --- | --- | --- |
| `getProjectDNA` | โหลด L0–L4 bundle ตาม intent/budget | `scopeId`, `level`, `tokenBudget` |
| `getBusinessContext` | terms, invariants, approved rules, conflicts | `scopeId`, `domain` |
| `getArchitectureDNA` | boundaries, modules, dependencies, generated zones | `scopeId`, optional paths/domain |
| `getWorkflowDNA` | build/test/lint/codegen/migration/deploy workflow | `scopeId`, optional workflow kind |
| `getDesignDNA` | tokens, primitives, components, interaction patterns | `scopeId`, optional surface |
| `getImpact` | direct/indirect/cross-repo impact with paths/edges | `scopeId`, `requestIntent` or changed paths |
| `getRisks` | risk drivers + evidence + controls to consider | `scopeId`, `requestIntent`, impact snapshot |
| `getReusableAssets` | real exports/signatures/usage evidence | `scopeId`, `query`, kinds/domain |
| `getConventions` | observed pattern, exceptions, approved enforcement | `scopeId`, paths/domain |

`getRisks` ให้ driver evidence ไม่ใช่ authority ที่ลด central Sage verdict; AI
และ control plane อาจเพิ่มความเข้ม แต่ห้ามใช้ cached result เพื่อ bypass gate

### 6.4 Knowledge governance tools

#### `proposeKnowledge`

- รับ claim, domain, scope, appliesTo, evidence, rationale, enforcement suggestion
- สร้าง `PROPOSED`; ห้าม inject เป็น binding context
- ถ้าใกล้เคียง approved entry → return duplicate/conflict candidates

#### `reviewKnowledgeProposal`

- action: `APPROVE | REJECT | REQUEST_CHANGES`
- ต้องมี authenticated human actor และ exact proposal revision
- approval ที่ scope กว้างหรือ `enforcement=block` ต้องแสดง affected descendants
- side effect: append governance event; mark affected summaries stale

### 6.5 Error contract

| Code | Meaning | Client action |
| --- | --- | --- |
| `DNA_NOT_PREPARED` | ไม่มี active snapshot | เรียก `prepareProjectDNA` |
| `DNA_STALE` | source fingerprint ไม่ตรง | ใช้ stale แบบเปิดเผยหรือ refresh |
| `DNA_DEGRADED` | บาง facet สร้างไม่สำเร็จ | อ่าน `missingFacets`; เพิ่ม risk/scan |
| `SCOPE_NOT_FOUND` | locator resolve ไม่ได้ | ตรวจ workspace/path |
| `SCOPE_FORBIDDEN` | caller ไม่มีสิทธิ์ | หยุด; ห้าม fallback ข้าม scope |
| `BUDGET_TOO_SMALL` | budget ต่ำกว่า mandatory metadata | เพิ่ม budget หรือขอลด facet |
| `REFRESH_IN_PROGRESS` | มี job active สำหรับ fingerprint | poll status; ไม่ enqueue ซ้ำ |
| `UNSUPPORTED_SCHEMA` | client/server schema ไม่ compatible | upgrade adapter/core |
| `DNA_CONFLICT` | binding/inference conflict กระทบคำตอบ | โหลด conflict แล้วให้ gate ตัดสิน |
| `PARTIAL_RESULT` | query มี continuation | ขอหน้าถัดไปด้วย token/cursor |

## 7. Status lifecycle

### 7.1 Preparation job

```text
QUEUED
  -> INVENTORY
  -> DETECTING
  -> MERGING
  -> VALIDATING
  -> READY
  -> ACTIVE

Any running state -> FAILED | CANCELLED
ACTIVE -> SUPERSEDED
```

- coordinator เท่านั้นที่เปลี่ยน job state
- `ACTIVE` เกิดหลัง atomic pointer swap
- cancelled/failed job ห้ามเปลี่ยน active snapshot

### 7.2 Freshness

```text
ABSENT -> PREPARING -> FRESH
FRESH --fingerprint mismatch--> STALE
FRESH --partial detector failure--> DEGRADED
STALE|DEGRADED --validated refresh--> FRESH
```

- watcher event เป็น optimization; fingerprint reconciliation เป็น correctness
- `STALE` ระบุ affected facets และ last known source revision
- query ใช้ stale snapshot ได้เฉพาะเมื่อ caller เห็น warning และ central risk
  policy อนุญาต

### 7.3 Knowledge proposal

```text
PROPOSED -> APPROVED
PROPOSED -> REJECTED
PROPOSED -> CHANGES_REQUESTED -> PROPOSED(new revision)
APPROVED -> SUPERSEDED(human-approved replacement)
```

- AI สร้างได้ถึง `PROPOSED`
- authenticated human เท่านั้นที่ทำ `APPROVED`, `REJECTED`, `SUPERSEDED`

## 8. Data model touchpoints

Reference implementation ใช้ embedded local store ใน OS user-data directory
โดยไม่ commit computed cache เข้า repo แต่ logical schema ห้ามผูกกับ database
vendor

| Entity | Role |
| --- | --- |
| `Scope` | hierarchy และ portable identity |
| `SourceRef` | path/symbol/hash ที่เป็น provenance |
| `Snapshot` | immutable consistent view ของ DNA หนึ่ง revision |
| `FacetManifest` | completeness, detector versions, invalidation inputs |
| `Assertion` | observed/declared/inferred claim พร้อม governance |
| `Edge` | dependency, call, impact, ownership และ conflict relation |
| `PreparationJob` | idempotent scan/refresh state + diagnostics |
| `KnowledgeProposal` | human approval lifecycle |
| `GovernanceEvent` | append-only audit ของ approve/reject/supersede |

Recommended physical baseline สำหรับ pilot:

- metadata, assertions, edges และ job state: SQLite
- large derived payloads: content-addressed blobs หรือ compressed JSON
- active snapshot pointer: transaction เดียวกับ validation result
- computed snapshots: disposable/rebuildable
- approved knowledge/governance events: backup/export ได้และไม่หายตาม cache purge

## 9. Edge cases & error handling

| Case | Handling |
| --- | --- |
| Huge monorepo | สร้าง L0 ก่อน; partition ตาม repo/module; queue facets; report progress |
| Dirty working tree | fingerprint รวม dirty content hash; provenance ระบุ `working-tree` |
| Branch switch/rebase | source fingerprint mismatch; invalidate affected snapshot |
| Generated/vendor/build output จำนวนมาก | index generator/config + public exports; skip bodies ตาม policy |
| Unsupported language | inventory + manifest facts ยังได้; facet เป็น degraded ไม่เดา architecture |
| Symlink loop/path escape | canonicalize, detect loop, reject path นอก approved root |
| Secret-looking file | skip body; record redacted classification เท่านั้น |
| Watcher พลาด event | status/reconcile ตรวจ fingerprint ก่อนตอบว่า fresh |
| Rename/move | match content/symbol IDs เมื่อมั่นใจ; ไม่มั่นใจให้ delete+add พร้อม impact warning |
| Concurrent refresh | deduplicate job; one writer per scope/fingerprint; readers ใช้ active snapshot |
| Detector version upgrade | mark facets stale; rebuild facet ก่อนอ้าง compatible result |
| Store corruption | fail closed, keep backup/last valid snapshot, rebuild computed data |
| Partial detector failure | publish `DEGRADED` ได้เมื่อ core integrity ผ่าน; list missing facets |
| Conflicting approved rules | return conflict + central gate; ห้ามเลือก specific rule ถ้า safety semantics ขัดกัน |
| Tool unavailable | current Markdown protocol/repo inspection เป็น fallback; disclose validation gap |
| Token budget ต่ำ | preserve envelope; return `BUDGET_TOO_SMALL` หรือ continuation |
| Repo removed from workspace | tombstone scope; retain governance audit; deny fresh query |
| Shared package affects many repos | L4 impact follows version/import edges; unresolved consumers remain warning |

## 10. Security & concurrency

- Scope authorization ตรวจทั้ง query และ preparation; cache key ไม่ใช่ authorization
- Canonical path ต้องอยู่ใต้ approved roots หลัง resolve symlink
- Secret scanning policy เป็น deny-by-default สำหรับ `.env`, keys, credentials,
  browser/session stores, binary dumps และ user-config directories
- Logs เก็บ detector ID, hash, counts และ error class; ไม่เก็บ secret/file body
- Tool response คืน source excerpts เฉพาะจำเป็นและตาม caller permission
- Multi-tenant/shared deployment ในอนาคตต้องแยก encryption key และ access policy
  ต่อ company/workspace; ยังอยู่นอก pilot
- Preparation job ใช้ idempotency key จาก scope/fingerprint/detector set
- Writer ใช้ lease ต่อ scope; lease expiry ต้องไม่ activate partial snapshot
- Activation และ governance event เป็น transaction/atomic append
- Readers pin `snapshotId` ตลอดหนึ่ง reasoning run; pagination ห้ามข้าม snapshot
- Retried approval ต้อง idempotent ตาม proposal revision + action + actor
- Conflicting concurrent approvals ของ revision เดียวจบเป็น conflict ไม่ใช้
  last-write-wins

## 11. Build checklist

### Phase 0 — Specification and evaluation fixtures

- [x] กำหนด control-plane/data-plane boundary
- [x] กำหนด scope hierarchy, facets, assertion/provenance และ governance
- [x] กำหนด progressive context, freshness, tool envelope และ lifecycle
- [x] ระบุ failure/security/concurrency controls
- [ ] สร้าง labeled fixture repos: small app, monorepo, multi-repo, generated API,
  design system และ contradictory conventions
- [ ] กำหนด benchmark baseline ของ protocol ปัจจุบัน: latency, tokens, recall,
  false-confidence และ reuse hit rate

### Phase 1 — Local Project DNA builder

- [ ] สร้าง repository adapter + safe inventory
- [ ] สร้าง Scope/Snapshot/SourceRef/Assertion schema
- [ ] สร้าง detectors แบบ evidence-first สำหรับ stack/workflow/assets/conventions
- [ ] สร้าง initial prepare แบบ progressive และ atomic snapshot
- [ ] เพิ่ม CLI `prepare`, `status`, `inspect` สำหรับ debug
- [ ] พิสูจน์ secret/path/symlink guards ด้วย negative tests

### Phase 2 — Query kernel and first tool adapter

- [ ] สร้าง hierarchy resolution, conflict handling และ token budgeting
- [ ] สร้าง L0–L4 context planner
- [ ] implement query tools ตาม §6 ด้วย response envelope เดียว
- [ ] เริ่ม MCP adapter จาก core contract; CLI ใช้ core เดียวกัน
- [ ] เพิ่ม contract tests ป้องกัน transport-specific behavior drift
- [ ] วัด warm-query latency และ token reduction เทียบ baseline

### Phase 3 — Incremental refresh and cross-repo impact

- [ ] สร้าง ChangeSet + facet dependency/invalidation graph
- [ ] สร้าง watcher event ingestion พร้อม fingerprint reconciliation
- [ ] สร้าง workspace/project/repo hierarchy และ dependency edges
- [ ] implement L4 impact พร้อม unresolved-consumer warning
- [ ] ทดสอบ concurrent refresh, crash recovery และ snapshot rollback

### Phase 4 — Human-governed shared cognition

- [ ] สร้าง proposal/review/audit workflow
- [ ] export/import approved knowledge โดยไม่ผูก computed cache
- [ ] เพิ่ม adapters สำหรับ agent hosts ตาม capability
- [ ] ออกแบบ hosted/shared deployment หลัง local pilot ผ่าน security review

### Acceptance evidence ก่อนประกาศ runtime พร้อมใช้

- [ ] warm request ไม่ rescan repo ทั้งชุดเมื่อ fingerprint ไม่เปลี่ยน
- [ ] L0 อยู่ใน 100–300 token target บน fixture set
- [ ] stale snapshot ถูกเปิดเผยทุก transport; ไม่มี silent stale read
- [ ] ทุก binding rule มี human approval event
- [ ] heuristic convention แสดง samples/exceptions และไม่กลายเป็น `must` เอง
- [ ] query ทุกชนิดมี provenance/conflict/freshness ครบ
- [ ] changed path refresh เฉพาะ dependency closure ที่ถูกต้อง
- [ ] reader ไม่เห็น partial snapshot ระหว่าง concurrent refresh
- [ ] secret fixtures ไม่ปรากฏใน store, log หรือ tool response
- [ ] impact fixtures วัด precision/recall และ unresolved consumers ได้
- [ ] current Markdown fallback ยังทำงานเมื่อ tool unavailable

### Quality evaluation

- [ ] วัด architecture/workflow/convention/asset detector precision และ recall
  กับ labeled fixtures; รายงานแต่ละ facet แยกกัน
- [ ] วัด impact precision/recall แยก direct, indirect และ unresolved consumer;
  hard-coded domain cascade ห้ามนับเป็น proof
- [ ] วัด false-confidence rate: unsupported inference ต้องไม่ถูกส่งเป็น
  observed/approved หรือไม่มี contrary evidence
- [ ] วัด cold preparation, progressive L0 ready time, warm query และ delta
  refresh; 2–10 นาทีเป็น hypothesis จนกว่าจะมี distribution จริง
- [ ] วัด request token use เทียบ protocol-only baseline โดยรักษา safety kernel
  และ answer quality
- [ ] ทดสอบ runtime-only blind spots เช่น feature flags/deployed versions แล้ว
  ตรวจว่า response ระบุ unknown แทนการเดา

### Compatibility and migration

- [ ] เพิ่ม capability negotiation ก่อน agent เรียก DNA tool
- [ ] import approved `agents/sage/<domain>/**` เป็น declared assertions โดยคง
  status, enforcement, applies_to, supersedes และ provenance
- [ ] export approved knowledge กลับเป็น reviewable format ได้; computed cache
  ไม่ถูก commit หรือใช้แทน source
- [x] รักษา `.sage-local.json`, slash commands และ installer non-clobber
  guarantees จนมี explicit major-version migration
- [ ] no-tool agents ใช้ protocol-only mode พร้อมเปิดเผยว่าไม่มี cached DNA;
  ห้าม adapter claim ว่า Project DNA พร้อม
- [ ] rollback ปิด companion engine แล้วกลับ protocol-only ได้โดยไม่ทำ approved
  knowledge สูญหาย
- [ ] เปลี่ยน README, `llms.txt`, `CLAUDE.md` และ `CONTRIBUTING.md` จาก
  “no runtime” เมื่อ implementation ผ่าน acceptance เท่านั้น

## 12. Open questions

ไม่มี implementation-shaping product decision ที่ต้องถามก่อนรับสเปกนี้:

- physical store ใช้ SQLite เป็น pilot default แต่ logical contract
  storage-agnostic; benchmark เปลี่ยน implementation ได้โดยไม่เปลี่ยน API
- MCP เป็น first adapter เพราะใช้กับ agent ได้หลายราย แต่ core contract
  provider-neutral; host adapter อื่นตามหลังโดยไม่ fork cognition
- เวลา prepare 2–10 นาทีเป็น hypothesis สำหรับ product experience ไม่ใช่ SLA;
  progressive L0 และ benchmark เป็น acceptance ที่ตรวจได้จริงกว่า
- shared company memory และ hosted RBAC ถูกเลื่อนไปหลัง local correctness/security
  proof เพื่อไม่ทำให้ MVP กลับไปหนักแบบ runtime เดิม

## 13. Skeptical verification

- **ควรทิ้ง Markdown ทันทีหรือไม่?** ไม่ควร รุ่นปัจจุบันยังไม่มี tool runtime
  การลบ fallback ตอนนี้จะทำให้ product ใช้ไม่ได้ Target state ใช้ tools สำหรับ
  computed DNA แต่คง Markdown เป็น policy/bootstrap ที่มนุษย์ review ได้
- **DNA เป็นแค่ documentation cache หรือไม่?** ไม่ใช่ เพราะมี structured
  assertions, graph edges, snapshot consistency, provenance, freshness,
  query levels และ governance แต่ summary ทั้งหมดยัง rebuild จาก source ได้
- **ของเดิม reuse ได้แค่ไหน?** reuse แนวคิด scanner, assets, conventions,
  workspace, graph, atomic storage และ approval lifecycle ได้ แต่ hard-coded
  domain/cascade rules และ heuristic `must` ต้องถูกแทนด้วย evidence/confidence
- **cache ทำให้ AIมั่นใจผิดหรือไม่?** ลดความเสี่ยงด้วย source fingerprint,
  stale/degraded state, conflicts และ central risk policy ที่ห้าม cached result
  ลด gate
- **event watcher เพียงพอหรือไม่?** ไม่พอ watcher เป็น latency optimization;
  fingerprint reconciliation เป็น correctness control
- **human approval ขัดกับ automatic refresh หรือไม่?** ไม่ขัด Observed facts คือ
  disposable cache จาก source; binding business/policy memory เท่านั้นที่ต้อง
  human approval
- **hierarchy override เปิดช่องให้ child ลด safety หรือไม่?** ไม่ เพราะ
  most-restrictive wins สำหรับ block/safety และการผ่อนต้องมี explicit approved
  supersedes
- **spec ผูก implementation เร็วเกินไปหรือไม่?** ผูกเฉพาะ public semantics และ
  safety invariants ส่วน storage/transport ถูกแยกหลัง interface เพื่อทดลองได้
- **มีเส้นทาง terminal ที่หายหรือไม่?** initial/refresh/query/proposal ทุกทางจบ
  ด้วย active data, explicit stale/degraded/error หรือ human gate ไม่มี silent
  success

ผลการ grill: `design-clear` สำหรับ Phase 0 evaluation fixtures และ Phase 1 local
builder; ไม่มีคำถามที่ต้องให้มนุษย์ตัดสินใจก่อนจบสเปก
