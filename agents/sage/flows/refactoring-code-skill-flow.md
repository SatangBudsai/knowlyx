# Sage Refactoring Code skill flow

วันที่: 2026-08-18

สกิล `/sage-refactoring-code` ทำให้การเขียนโค้ดใหม่และการ refactor เริ่มจาก
ความเข้าใจของคนที่จะดูแลโค้ดต่อ ไม่ใช่จาก abstraction หรือความยืดหยุ่นที่อาจไม่เคยใช้
สกิลยังคงรักษา correctness, security, data integrity และ public contract
ก่อนลดความซับซ้อนเสมอ

## 1. Design decisions

- ใช้ canonical command หนึ่งไฟล์ใน `agents/sage/commands/` และให้ adapters
  ชี้กลับมาที่ไฟล์นี้
- อ่าน style ของโปรเจกต์เพื่อหา vocabulary และ convention ที่ดี แต่ไม่คัดลอก
  nesting, abstraction หรือโครงสร้างที่อ่านยากโดยอัตโนมัติ
- ใช้ heuristic และคำถามทบทวนแทนเพดานตัวเลขที่บังคับทุกภาษา
- ครอบคลุมทั้ง application code, component, function, utility, module และ
  database schema โดยไม่ผูกกับ stack

## 2. Actors & systems

| Actor/System | Responsibility | Ownership |
| --- | --- | --- |
| ผู้ใช้ | ระบุงานเขียนใหม่หรือ refactor และข้อจำกัดของ behavior | product intent |
| AI agent | สำรวจโปรเจกต์ เลือกโครงสร้างที่ง่าย และแก้โค้ด | implementation |
| Project repository | เป็นแหล่งจริงของ contracts, vocabulary, tests และ conventions | source of truth |
| Database/schema | เก็บ domain data ด้วยชื่อและ relationship ที่ตรวจสอบได้ | data integrity |
| Sage command | กำหนด workflow และ readability guardrails | cognition policy |
| Tool adapter | ทำให้แต่ละ agent เรียก canonical command เดียวกัน | discovery only |

Trust boundary: agent ห้ามเดา behavior, schema หรือ project style จากชื่อไฟล์
เพียงอย่างเดียว และห้ามลด validation, authorization, constraints หรือ transaction
เพื่อทำให้ implementation ดูสั้นลง

## 3. End-to-end overview

```text
User request
  -> Sage reads repository facts and nearby code
  -> classifies readable conventions vs accidental complexity
  -> chooses the smallest clear design that meets current requirements
  -> writes/refactors code and schema in bounded steps
  -> validates behavior, contracts, data integrity, and readability
  -> reports remaining complexity and deliberate trade-offs
```

Repository source and executable tests remain the source of truth. The skill is
guidance; it does not replace a project's approved blocking rules.

## 4. Step-by-step

1. เมื่อเริ่มงาน ให้ agent อ่าน target, callers, tests, schema และไฟล์ใกล้เคียง
   เท่าที่จำเป็น แล้วสรุป behavior ที่ต้องรักษา
2. เมื่อพบ project convention ให้แยกว่า convention นั้นช่วยให้เข้าใจง่ายหรือเป็น
   accidental complexity; reuse เฉพาะส่วนที่ดีและ compatible
3. ก่อนออกแบบ ให้ agent ตั้งชื่อด้วยคำใน domain ที่ผู้ใช้และโปรเจกต์ใช้จริง
4. เมื่อ flow มี nesting ที่หลีกเลี่ยงได้ ให้ใช้ guard clause, named step หรือ
   linear orchestration โดยไม่ซ่อน behavior ไว้หลายชั้น
5. เมื่อ abstraction ยังมีผู้ใช้เพียงกรณีเดียวและไม่มี seam ที่เปลี่ยนจริง ให้เขียน
   implementation ตรง ๆ ก่อน
6. เมื่อ code ต้องแชร์ ให้จัดกลุ่มตาม feature/domain และ contract ที่ชัดเจน;
   ไม่ย้ายทุกอย่างเข้า `utils` หรือ base abstraction
7. เมื่อแตะ database ให้ model แนวคิดและ relationship จริง ใช้ constraints และ
   explicit fields สำหรับข้อมูลหลัก และออกแบบ migration/rollback ตาม risk policy
8. เมื่อ refactor ให้รักษา observable behavior และ public contract แยก behavior
   change ออกจาก structural cleanup
9. หลังแก้ ให้รัน tests/build/lint ที่เกี่ยวข้อง และตรวจ readability จากเส้นทางใช้งานจริง
10. หากความซับซ้อนยังจำเป็น ให้บันทึกเหตุผลใกล้ boundary ที่ทำให้มันจำเป็น ไม่ใช่
    อธิบายทุกบรรทัดของ implementation

## 5. State and data handling

สกิลไม่สร้าง runtime state ของตัวเอง ข้อมูลที่ใช้ทั้งหมดมาจาก repository:

- source code และ tests: behavior/contract ปัจจุบัน
- schema และ migrations: data shape, constraints และ compatibility
- `agents/sage/<domain>/`: approved vocabulary และ project rules
- version control diff: ขอบเขตการเปลี่ยนแปลง

ห้าม persist inference ว่า pattern ที่พบบ่อยคือ pattern ที่ดีโดยอัตโนมัติ

## 6. API spec

ไม่มี network API ใหม่ Canonical interface คือ:

- Command: `/sage-refactoring-code <target or task>`
- Codex skill: `$sage-refactoring-code`
- Input: target/task, current repository, และ optional user constraints
- Output: code/schema changes พร้อม validation evidence และ readability summary

Adapters ต้องมีเฉพาะ metadata และ pointer ไปยัง
`agents/sage/commands/sage-refactoring-code.md`

## 7. Status lifecycle

```text
inspect -> behavior-known -> simplify/design -> implement -> validate -> complete
                    \-> material decision -> ask
validate failed -> diagnose -> revise -> validate
```

`complete` เกิดได้เมื่อ behavior และ required controls ผ่านจริงเท่านั้น

## 8. Data model touchpoints

ไม่มี table ของ Sage เพิ่มขึ้น เมื่อสกิลออกแบบ schema ของโปรเจกต์ ให้พิจารณา:

- entity และ relationship ที่มีความหมายใน domain
- primary/foreign keys, uniqueness, nullability และ lifecycle
- query ที่มีอยู่จริงก่อนเพิ่ม index
- additive migration หรือ rollback/forward-fix ที่ตรวจสอบได้
- หลีกเลี่ยง catch-all JSON/EAV/polymorphic model สำหรับ core data หากไม่มีเหตุผลจริง

## 9. Edge cases & error handling

| Scenario | Handling |
| --- | --- |
| โปรเจกต์มี style ที่อ่านยาก | รักษา public compatibility แต่เลือกโครงสร้างภายในที่ง่ายกว่าและบอก deviation |
| ความสั้นขัดกับ correctness/security | รักษา control ก่อน ยอมให้โค้ดยาวขึ้นพร้อมแยกขั้นตอนชัดเจน |
| abstraction มีหลาย consumer จริง | คง boundary ไว้ แต่ลด generic layers ที่ไม่เพิ่มความหมาย |
| ไม่มี tests | characterize จาก callers/contracts และรายงาน validation gap; ไม่อ้างว่า behavior คงเดิมแน่นอน |
| schema ต้องรองรับ migration | ใช้ risk controls ของ Sage; ไม่ทำ destructive migration จากสกิลนี้โดยอัตโนมัติ |
| ชื่อ domain ยังไม่ชัด | ใช้คำที่มีอยู่ใน product/schema หรือถามเมื่อเป็น human-owned canonical decision |

## 10. Security & concurrency

- ห้ามลบ authz, validation, escaping, transaction, idempotency หรือ locking
  เพียงเพื่อให้ code path สั้นลง
- ตรวจ caller และ side effect ก่อนย้าย function/module
- schema refactor ต้องรักษา constraints และมี integrity evidence
- behavior-preserving refactor ต้องไม่เปลี่ยน retry/error semantics โดยไม่ตั้งใจ

## 11. Build checklist

- [ ] เพิ่ม canonical command `sage-refactoring-code.md`
- [ ] สร้าง Codex skill folder ด้วย skill initializer และ UI metadata
- [ ] เพิ่ม thin adapters สำหรับ Claude, Codex prompt, Cursor, Copilot, Windsurf,
      Cline และ Gemini
- [ ] เพิ่ม basename ใน adapter manifest
- [ ] อัปเดต command indexes, installer output และ README ที่เกี่ยวข้อง
- [ ] เพิ่ม regression tests สำหรับ guardrails และ adapter parity
- [ ] รัน skill validator, Python tests และ Markdown lint ถ้ามี

## 12. Out of scope

- ไม่บังคับ rewrite codebase ทั้งหมดให้เป็น style เดียว
- ไม่กำหนด maximum line count, function count หรือ nesting เป็นกฎตายตัวทุกภาษา
- ไม่เพิ่ม formatter, linter, ORM, database หรือ runtime dependency
- ไม่เปลี่ยน behavior หรือ public API ภายใต้คำว่า refactor
- ไม่ทำให้ทุก feature รองรับ hypothetical use case

## 13. Open questions

ไม่มีคำถามที่กั้น implementation ชื่อ, scope, distribution model และ safety
boundaries ชัดเจนจากคำขอและโครงสร้าง repository แล้ว

## Verification verdict

`design-clear` — flow ใช้ canonical source เดียว, กระจายผ่าน adapter เดิม,
รักษา project-specific approved rules และวาง correctness/data integrity ไว้เหนือ
ความสั้นหรือความง่ายเชิงผิวเผิน
