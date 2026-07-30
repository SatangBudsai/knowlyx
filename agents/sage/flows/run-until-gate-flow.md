# Run until gate — Sage v3 interaction flow

> ปรับ Sage จากการหยุดตามขอบเขตของ command/ticket/phase เป็นการทำงานต่อเนื่อง
> จนถึง gate ที่ต้องใช้มนุษย์หรือหลักฐานภายนอก โดยคง risk controls เดิมทั้งหมด
> เอกสารนี้อ้างอิง `AGENTS.md`, command contracts, role files และ protocol tests
> จริง ณ วันที่ 2026-07-30

## Design decisions

- `/sage` เป็นเจ้าของ run loop; Grill, Flow และ Wayfinder ส่ง exit state/handoff
  กลับไปยัง parent แทนการจบ run เอง
- เก็บ `mode` เป็นชื่อ config เดิมสำหรับ checklist policy เพื่อไม่ทำลาย
  `.sage-local.json` v2 และเพิ่ม `interaction` เป็น policy แยกใน config v3
- ค่าเริ่มต้นคือ `runPolicy: "until-gate"`; ผู้ใช้เลือก `"strict"` ได้สำหรับ
  workflow ที่ต้องการหยุดตาม command checkpoint เดิม
- คำถามอิสระรวมได้สูงสุด 3 ข้อต่อ checkpoint; คำถามที่คำตอบเปลี่ยนคำถามถัดไป
  ยังคงถามทีละข้อ
- Safety gates มาจาก risk policy กลางเท่านั้น และ config ทุกตัวใน `interaction`
  ทำให้ gate อ่อนลงไม่ได้
- Wayfinder ticket ยังคงเป็น decision/unblocking work ไม่ใช่ implementation
  slice แต่หนึ่ง run ทำงานได้หลาย ticket เป็น frontier waves
- Role เป็น lens สั้น ๆ สำหรับ failure modes ไม่ใช่เจ้าของ `ask`, `wait`,
  `stop` หรือ approval และไม่เก็บ version/path/reusable asset
- Checklist picker เลือกจาก capability จริงของ environment ไม่ใช่ชื่อ provider:
  native multi-select ก่อน, structured single-select ถัดมา และ text fallback
  เป็นทางสุดท้าย

## Out of scope

- ไม่เปลี่ยน locked checklist ห้ารายการหรือลำดับของรายการ
- ไม่ลด HIGH/destructive/irreversible, auth/payment/PII, external-access หรือ
  failed-critical-control gates
- ไม่ทำ runtime scheduler ที่ปลุก agent หลังส่ง final แล้ว
- ไม่เปลี่ยน Wayfinder ให้จัดการ implementation tickets หรือ project delivery
- ไม่เพิ่ม MCP/server/database/package dependency ให้ Sage
- ไม่แก้ installer/adapters ที่เป็น thin pointer และไม่ได้ duplicate behavior
- ไม่รับประกัน checkbox UI เหมือนกันทุก agent เพราะ `AGENTS.md` ควบคุม runtime
  widget ของ host ไม่ได้

## 1. Actors & Systems

| System | Responsibility | Ownership |
| --- | --- | --- |
| Human | กำหนด product intent, material HITL decision และอนุมัติ destructive/HIGH action | เป็นเจ้าของ irreversible choice และ external authority |
| Parent `/sage` | route, checklist, run loop, risk gate, phase scheduling และ terminal summary | เป็น source of truth ของ run state |
| `/sage-grill` | เปลี่ยน single-session fog เป็น `requirements-clear` | เป็นเจ้าของ product/domain questions |
| `/sage-flow` | เปลี่ยน clear requirements เป็น `design-clear` | เป็นเจ้าของ implementation-shaping design |
| `/sage-wayfinder` | chart และ resolve multi-session decision fog | เป็นเจ้าของ map/tickets/frontier |
| Risk policy | ประเมิน driver, required control, verdict และ residual risk | เป็นเจ้าของ gate ที่ config ปิดไม่ได้ |
| `.sage-local.json` | เก็บ checklist และ interaction preferences ต่อเครื่อง | เป็น user-local preference ไม่ใช่ team policy |
| Role files | เพิ่ม expertise/failure-mode lens แบบสั้น | เป็น advisory lens; ไม่มีสิทธิ์สร้าง gate |
| Protocol tests | ตรวจ invariant และห้าม contract สำคัญ drift | เป็น validation evidence ของ Markdown protocol |
| Host picker capability | แสดง native multi-select, single-select หรือ text input | Host/runtime เป็นเจ้าของ widget; Sage เลือก fallback |

**Trust boundary:** interaction config ควบคุมความถี่ในการหยุดและรูปแบบคำถาม
เท่านั้น มันห้ามอนุมัติ HIGH risk, destructive effect, sensitive human-owned
decision หรือ external mutation แทน Human และ child command ห้ามส่ง final เพื่อ
ตัด parent run ก่อน terminal state

## 2. End-to-end overview

```text
[Human] ส่ง code-changing request
   |
   v
[/sage] โหลด config + route + knowledge + risk controls
   |
   v
[Checklist] auto --> แสดง selection + ทำต่อ (ไม่ถาม)
   |         ask + multi-select --> native checkbox
   |         ask + single-select --> Recommended / Defaults / Customize
   |         ask + no widget --> "recommended" หรือ +/-exceptions
   |
   v
   +-- route clear --------------------------+
   +-- route foggy --> [Grill] --------------+--> requirements-clear
   +-- route large --> [Wayfinder waves] ----+--> spec-ready
                                                      |
                                                      v
                                  plan-flow on? --> [Flow] --> design-clear
                                                      |
                                                      v
[/sage] ทำทุก implementation/validation/docs phase ที่ยัง unblocked
   |
   +-- reversible/internal choice --> เลือก default + บันทึก assumption + ทำต่อ
   |
   +-- independent human decisions --> รวม 2–3 ข้อเป็น checkpoint + รอคำตอบ
   |
   +-- dependent human decision --> ถาม most-blocking ข้อเดียว + รอคำตอบ
   |
   +-- HIGH/destructive/sensitive/manual access/critical failure --> หยุดที่ gate
   |
   `-- ไม่มีงานเหลือ + controls ปิดครบ --> final summary
```

**หัวใจ:** การจบ command, ticket, handoff หรือ phase เป็น state transition
ไม่ใช่ stop condition; parent `/sage` เดินต่อจนพบ gate จริงหรือ terminal state

## 3. Step-by-step

### STEP 1 — โหลด config v3 โดยไม่ทำลายค่าเดิม

**System:** Parent `/sage` + `/sage-setting`

- เมื่อ `.sage-local.json` ไม่มีไฟล์ → สร้าง config v3 พร้อม `mode`,
  `checklist` และ `interaction` defaults
- เมื่อไฟล์เป็น v2 → คง `mode`/`checklist`/unknown fields, เติม `interaction`,
  ตั้ง `version: 3`
- เมื่อมี legacy `askMode` → แปลงเป็น `mode`, เติม v3 fields และลบเฉพาะ
  `askMode`
- เมื่อ user เลือก `strict` → ใช้ command checkpoints เดิม แต่ risk policy
  ไม่อ่อนลง
- เมื่อ field interaction ผิดชนิด/เกินขอบเขต → ใช้ safe defaults ของ field นั้น
  และรายงาน assumption; ห้ามตีความเป็นการปิด gate

### STEP 2 — Route และสร้าง run frontier

**System:** Parent `/sage`

- ก่อน route execution ให้เลือก checklist ตาม picker capability:
  - `mode:auto` → คำนวณ recommended set, echo checklist แล้วทำต่อ; ห้ามถามเลข
  - `mode:ask` + native multi-select → แสดง checkbox ห้ารายการตาม locked order
  - `mode:ask` + structured single-select → ให้กด `Run recommended`,
    `Use saved defaults` หรือ `Customize`
  - เมื่อเลือก `Customize` → ถาม toggles เป็นชุดตามจำนวนที่ tool รองรับ;
    ไม่บังคับให้พิมพ์หมายเลข
  - ไม่มี structured input → รับ `recommended`, `defaults` หรือ exceptions เช่น
    `-e2e +security`; numbered list เป็น legacy fallback เท่านั้น
- Capability detection ใช้ callable tool/schema ของ session; ห้ามสรุปว่า
  “Codex/Claude/provider X รองรับเสมอ” จากชื่อ provider
- Route ยังใช้ `clear-single-session | foggy-single-session |
  large-multi-session` ตาม decision fog ไม่ใช่จำนวนไฟล์
- Parent เก็บ phase/ticket ที่ `open + unblocked` เป็น run frontier
- งานอิสระที่ environment รองรับ → ทำเป็น wave เดียวและ parallel
- งานที่ขึ้นกับผลก่อนหน้า → รอ dependency แล้วเข้า wave ถัดไปทันที
- การเลือก internal implementation ที่ reversible → ใช้ repo convention หรือ
  recommended default, บันทึก assumption และไม่ถาม

### STEP 3 — Resolve Grill จนถึง requirements-clear

**System:** `/sage-grill` + Human + Parent `/sage`

- Facts → อ่านจาก source/schema/docs โดยไม่ถาม Human
- Independent decisions → รวม 2–3 ข้อต่อ checkpoint พร้อม recommendation
- Dependent decision tree → ถาม most-blocking ข้อเดียว, บันทึกคำตอบ แล้วคำนวณ
  คำถามถัดไป
- Material decisions → stress-test ด้วย boundary/counterexample ก่อนปิด
- เมื่อได้ `requirements-clear` และ `continueAfterHandoff: true` ใน active parent
  run → ส่ง handoff กลับ parent และเดินต่อทันที
- เมื่อเรียก `/sage-grill` แบบ standalone หรือ `continueAfterHandoff: false`
  → แสดง summary/handoff แล้วคืน control ให้ Human

### STEP 4 — Resolve Wayfinder เป็น frontier waves

**System:** `/sage-wayfinder` + Parent `/sage` + optional sub-agents + Human

- Chart destination/map/tickets แล้วคำนวณ frontier ทันที; ห้ามหยุดเพียงเพราะ
  chart เสร็จ
- Claim ticket ก่อนทำตาม backend contract เดิม
- Frontier ที่เป็น AFK `research`/`task` → claim และทำพร้อมกันเมื่อปลอดภัย
- ปิด ticket พร้อม evidence → update map → recompute frontier → เริ่ม wave ถัดไป
- Frontier ที่เป็น independent HITL decisions → batch ได้ตาม question policy
- Frontier ที่เป็น dependent HITL decision → ถามทีละ branch
- หยุดเฉพาะเมื่อ frontier ทั้งหมดติด material HITL/manual access/risk gate หรือ
  ไม่มี runnable work
- เมื่อ map complete → synthesize spec; ถ้า active parent run และ
  `continueAfterHandoff: true` ให้กลับเข้า Flow/implementation ใน run เดียว

### STEP 5 — สร้างและ verify Flow โดยไม่บังคับ approval ซ้ำ

**System:** `/sage-flow` + Parent `/sage` + Human

- Intent block ใช้ verdict จาก risk policy:
  - `proceed|warn` → สร้างและ verify flow ต่อ
  - `ask|reject` → หยุดก่อน file/code mutation ตาม gate
- Skeptical review แยก facts ออกจาก decisions
- Independent design decisions → batch 2–3 ข้อ; dependent decisions → ทีละข้อ
- เมื่อไม่มี implementation-shaping question เหลือ → ตั้ง `design-clear`
- เมื่อ `design-clear` และ `continueAfterHandoff: true` ใน active parent run
  → parent เริ่ม implementation ทันที ไม่ต้อง confirmation gate ทั่วไป

### STEP 6 — Implement และ validate จนถึง terminal state

**System:** Parent `/sage` + implementation roles + QA

- ทำทุก phase ที่ unblocked ต่อเนื่อง; phase completion เพียงเปิด dependency ถัดไป
- Failed non-critical check → รายงาน, เก็บ risk ตามหลักฐาน และทำงานอิสระที่ยัง
  ปลอดภัยต่อ
- Failed critical control → หยุด dependent work และคืน gate พร้อมหลักฐาน
- เมื่อ discover driver/target กว้างขึ้น → reassess; ถ้า approval envelope เปลี่ยน
  ให้ขอใหม่
- เมื่อ code, tests, docs, controls และ knowledge capture ครบ → คำนวณ residual
  risk และส่ง final summary ครั้งเดียว

### STEP 7 — จำกัด Role ให้เป็น cognition lens

**System:** Parent `/sage` + role files

- โหลด primary role หนึ่งครั้ง; handoff เฉพาะเมื่อ phase ใหม่มี failure modes
  ต่างอย่างมีนัยสำคัญ
- Role file ใช้ frontmatter `status: approved|proposed` และเนื้อหา
  `Expertise / Pitfalls / How I work` ประมาณ 80–150 คำ
- Missing role → สร้าง `status: proposed`; ใช้เป็น advisory lens ใน run ปัจจุบัน
  แต่ห้ามถือเป็น binding team policy
- Role ห้ามมี `ask`, `wait`, `stop`, `approval` policy; ส่ง risk driver ให้
  central risk policy ตัดสิน
- Version/path/reusable asset → เก็บใน domain knowledge/source เท่านั้น

## 4. State / data handling

### `.sage-local.json` v3

```json
{
  "version": 3,
  "mode": "auto",
  "checklist": {
    "auto-switch-model": true,
    "plan-flow": true,
    "unit-test": true,
    "e2e-test": false,
    "security-review": false
  },
  "interaction": {
    "runPolicy": "until-gate",
    "questionPolicy": "batch-independent",
    "maxQuestionsPerCheckpoint": 3,
    "autoDecideReversible": true,
    "continueAfterHandoff": true
  }
}
```

| State | Canonical location | Lifecycle |
| --- | --- | --- |
| Checklist policy | `.sage-local.json.mode` + `checklist` | load/migrate at run start; change via `/sage-setting` |
| Picker capability | current host/session tool surface | detect per run; do not persist provider assumptions |
| Interaction policy | `.sage-local.json.interaction` | load/migrate at run start; never overrides safety |
| Active parent run | current `/sage` execution | `running → gated → resumed → complete` |
| Run frontier | current `/sage` execution | recompute after every closed/unblocked task |
| Assumptions | active plan/spec/summary | record when auto-deciding internal reversible choice |
| Grill checkpoint | `agents/sage/flows/<slug>-spec.md` | update after human answer |
| Wayfinder map/tickets | configured canonical backend | chart/claim/close/recompute until complete |
| Flow state | `agents/sage/flows/<slug>-flow.md` | drafting → verified → design-clear/gated |
| Role status | `agents/sage/roles/role-<lens>.md` | new AI role is proposed; human may approve |

## 5. API spec — N/A

ไม่มี network API หรือ runtime service ใหม่ Public contract ที่เปลี่ยนคือ
Markdown protocol, `.sage-local.json` schema และ command exit/handoff behavior
เท่านั้น Thin adapters อ้าง canonical command files จึงไม่ duplicate logic

## 6. Status lifecycle

```text
RUN_CREATED
  |
  v
RUNNING
  |-- child handoff clear/spec-ready/design-clear --> RUNNING
  |-- phase/ticket closed -------------------------> RUNNING
  |-- reversible internal choice -----------------> RUNNING (assumption recorded)
  |
  +-- material HITL/HIGH/manual access/critical failure --> GATED
  |                                                     |
  |<---------------------- human/evidence resolves gate-+
  |
  `-- no work + validations/controls complete ---------> COMPLETE --> FINAL

WAYFINDER_ACTIVE
  |-- frontier AFK wave closed --> recompute frontier --> WAYFINDER_ACTIVE
  |-- HITL frontier -----------> GATED
  `-- no fog/open tickets -----> SPEC_READY --> parent RUNNING
```

Illegal transitions:

- `child handoff → FINAL` ขณะที่ active parent ยังมี unblocked work
- `phase/ticket closed → GATED` โดยไม่มี material gate
- `interaction config → approve HIGH/destructive/sensitive decision`
- `HITL ticket → closed` โดยไม่มีคำตอบ Human
- `blocked/claimed ticket → work` โดยไม่ผ่าน claim/re-read rules
- `proposed role → binding team rule` โดยไม่มีการ approve

## 7. Data model touchpoints

| File/artifact | Change |
| --- | --- |
| `AGENTS.md` | canonical run-until-gate loop, question batching, narrower Flow trigger, role boundary |
| `agents/sage/commands/sage.md` | config v3, interaction policy, recommendation engine, run/stop contract |
| `agents/sage/commands/sage-setting.md` | view/change/migrate interaction settings |
| `agents/sage/commands/sage-grill.md` | batch independent questions + parent handoff |
| `agents/sage/commands/sage-flow.md` | verdict-based gate + design-clear continuation |
| `agents/sage/commands/sage-wayfinder.md` | frontier-wave algorithm + multiple tickets per run |
| `agents/sage/protocol/context.md` | canonical Run frontier/Gate vocabulary; update Grill/Wayfinder invariants |
| `agents/sage/roles/*.md` | status + no local gates; keep compact |
| `tests/*.py` + fixtures | positive/negative contract tests |
| `agents/sage/flows/request-routing-wayfinder-flow.md` | replace one-ticket/session flow with frontier waves |
| `docs/request-routing-wayfinder.md` | human-facing run-until-gate behavior |
| `README.md` + `CHANGELOG.md` | config/behavior/migration summary |

## 8. Edge cases & error handling

| Case | Handling |
| --- | --- |
| v2 config ไม่มี `interaction` | เติม defaults, preserve `mode`/checklist/unknown fields, set v3 |
| unknown future config fields | preserve on rewrite |
| invalid `maxQuestionsPerCheckpoint` | clamp/use default 3; ห้ามกลายเป็น unlimited prompt wall |
| `autoDecideReversible: true` แต่ public contract เปลี่ยน | ถือเป็น material decision; config ไม่ให้เลือกเอง |
| independent questions มากกว่า 3 | แบ่ง checkpoints ละไม่เกิน 3 |
| คำถามดูอิสระแต่คำตอบหนึ่งเปลี่ยนอีกคำถาม | reclassify เป็น dependent และถามทีละข้อ |
| Wayfinder มี AFK และ HITL frontier พร้อมกัน | ทำ AFK wave ก่อน/พร้อมกัน; gate เฉพาะ branch ที่ต้อง Human |
| local ticket claim ชนกัน | re-read ก่อน claim; ไม่ overwrite; เลือก frontier อื่น |
| child command เรียก standalone | summary + return; ไม่มี parent ให้ continue |
| active parent แต่ tool/runtime บังคับจบ turn | checkpoint durable state; รายงาน limitation ตรงไปตรงมา |
| Flow verification ไม่พบ open question | ตั้ง `design-clear` และ continue; ไม่สร้าง confirmation เทียม |
| critical test ล้มเหลวแต่ docs ทำต่อได้ | หยุด dependent implementation; ทำเฉพาะงานอิสระที่ไม่ทำให้ผลล้มเหลวถูกกลบ |
| role เก่ามี gate/version/path | ย้าย gate ไป central policy, ย้าย fact ไป domain/source, เพิ่ม regression scan |
| `mode:auto` บน host ที่มี picker | ไม่เปิด picker; auto mode ต้องทำต่อโดยไม่รอ |
| `mode:ask` แต่มีเพียง single-select | ใช้ Recommended/Defaults/Customize แล้วแตก toggle เฉพาะเมื่อจำเป็น |
| host ไม่มี structured input | ใช้ keyword/exception fallback; อย่าบังคับตอบเลขหลายรายการ |
| host อ้างว่าเป็น Codex/Claude แต่ tool ไม่ callable | เชื่อ capability ปัจจุบัน ไม่เชื่อ provider label |

## 9. Security & concurrency

- HIGH/destructive/irreversible ต้อง explicit approval ระบุ target/effect เสมอ
- Auth/payment/PII decision ที่เปลี่ยน trust boundary เป็น material HITL แม้
  `autoDecideReversible` เปิด
- External tracker writes ต้องอยู่ใน scope และมี authority; frontier-wave
  ไม่เพิ่ม permission
- Local claims ยัง cooperative ไม่ atomic; re-read ก่อน claim และห้าม overwrite
- Parallel wave ใช้เฉพาะ ticket/task ที่ dependencies และ side effects อิสระ
- Question batching รวมเฉพาะ decisions ที่ไม่เปลี่ยน branch ของกันและกัน
- Config migration preserve unknown fields และไม่เผย secrets/PII
- Tests ต้องมี negative assertions ว่า interaction config ไม่สามารถ bypass
  risk gates
- Picker fallback ห้ามเปลี่ยน locked order หรือซ่อน recommendation/reason ของ
  checklist ทั้งห้า

## 10. Build checklist

### Canonical protocol

- [x] เพิ่ม config v3 + run-until-gate algorithm ใน `AGENTS.md`
- [x] เพิ่ม capability-aware picker และห้าม `mode:auto` ถามเลือกหมายเลข
- [x] จำกัด `plan-flow` trigger ตาม cross-boundary/public-contract/schema/
      sensitive/architecture uncertainty
- [x] เปลี่ยน question policy เป็น batch-independent + dependent one-at-a-time
- [x] ให้ central risk policy เป็นเจ้าของ stop/gate จุดเดียว

### Commands

- [x] อัปเดต `/sage` config migration, run loop และ terminal conditions
- [x] อัปเดต `/sage-setting` ให้ดู/เปลี่ยน interaction policy
- [x] อัปเดต Grill/Flow/Wayfinder ให้ return handoff เข้า parent run
- [x] เปลี่ยน Wayfinder เป็น repeated frontier waves

### Roles and knowledge

- [x] เพิ่ม role status และลบ local gate wording
- [x] แก้ protocol glossary/knowledge index ที่ยังอ้าง one-ticket/Ikigai
- [x] capture run-until-gate/picker patterns เป็น proposed decisions

### Proof and docs

- [x] เพิ่ม tests สำหรับ config, continuation, batching, safety invariants,
      narrower Flow trigger, picker capability และ role contract
- [x] อัปเดต routing/Wayfinder flow + human docs
- [x] อัปเดต README/CHANGELOG
- [x] รัน `python -m unittest discover -s tests -v`
- [x] รัน consumer/legacy scans สำหรับ unconditional stops และ config v2 docs
- [x] ตรวจ `git diff --check` และ diff audit รอบสุดท้าย

## 11. Open questions

ไม่มี implementation-shaping question ที่บล็อก:

- ใช้ `mode` ต่อเป็น checklist policy เพื่อ backward compatibility ตาม
  conservative default
- `interaction.runPolicy` รองรับ `until-gate | strict`
- defaults ใช้ค่าตามข้อเสนอของผู้ใช้ และ safety gates ปิดไม่ได้
- native checkbox ใช้เมื่อ host มี multi-select; Codex/agent ที่ไม่มี capability
  เดียวกันใช้ one-click structured choice หรือ keyword/exception fallback

## 12. Skeptical verification

- **จุดอ่อน:** “ทำต่อจน gate” อาจถูกตีความเป็นทำ destructive work ต่อ
  **คำตอบ:** แยก interaction policy ออกจาก central risk policy และระบุ illegal
  transition/negative tests ชัดเจน
- **จุดอ่อน:** batch questions อาจสร้าง wall of questions
  **คำตอบ:** จำกัด 3 ข้อและ batch เฉพาะ independent decisions
- **จุดอ่อน:** frontier-wave อาจเพิ่ม collision
  **คำตอบ:** คง claim/re-read, parallel เฉพาะ independent tickets และ recompute
  หลังทุก wave
- **จุดอ่อน:** child command ที่ standalone ไม่มี parent
  **คำตอบ:** continuation ทำเฉพาะ active parent; standalone ยังคง return summary
- **จุดอ่อน:** config rename ทำลายของเดิม
  **คำตอบ:** ไม่ rename `mode`; migration เติม nested interaction เท่านั้น
- **จุดอ่อน:** role handoff ไม่ได้ลบ context จริง
  **คำตอบ:** ลดจำนวน handoff, จำกัดขนาด/หน้าที่ role และห้าม duplicate facts/gates
- **จุดอ่อน:** เอกสารอาจสัญญา checkbox ใน Codex ทั้งที่ current surface ไม่มี
  multi-select
  **คำตอบ:** detect callable capability ต่อ session และรับประกันเฉพาะ
  “ไม่ต้องพิมพ์เลขเมื่อมี structured UI” ไม่รับประกัน widget ชนิดเดียวกัน
- **ทางที่ง่ายกว่า:** แก้ Wayfinder อย่างเดียว
  **เหตุผลที่ไม่เลือก:** unconditional stops กระจายอยู่ใน Grill/Flow/parent
  contract; ถ้าไม่แก้ source of truth กลาง behavior จะ drift กลับ

**Verification result:** `design-clear` — flow ครอบคลุม config migration,
parent/child state transitions, Wayfinder concurrency, question dependencies,
role boundaries, safety invariants, tests และ docs โดยไม่มี open HITL decision
ก่อน implementation
