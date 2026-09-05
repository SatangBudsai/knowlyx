# Run until gate และ checklist picker

> Sage v3 แยก “เลือก workflow อะไร” ออกจาก “ควรคืน control ให้มนุษย์เมื่อไร”
> เพื่อให้งานเดินต่อข้าม command/ticket/phase โดยไม่ลด safety และเลือก checklist
> ผ่าน UI ที่ดีที่สุดซึ่ง host มีจริง อ้างอิง protocol ณ 2026-07-31

## 1. Actors & Systems

| System | Responsibility | Ownership |
| --- | --- | --- |
| Human | ตอบ material decisions และอนุมัติการกระทำที่เสี่ยง | HITL/HIGH/destructive authority |
| Parent `/sage` | เลือก checklist, run frontier และ terminal state | Active run |
| Host UI | แสดง multi-select, single-select หรือ text input | Native widgets |
| Grill/Flow/Wayfinder | สร้าง clear handoff ให้ parent | Child artifacts |
| Risk policy | ตัดสิน gate และ required controls | Safety source of truth |
| `.sage-local.json` | เก็บ checklist + interaction preferences ต่อเครื่อง | Local config |

**Trust boundary:** Host UI เป็นเจ้าของหน้าตา picker; `AGENTS.md` สั่งให้ใช้
widget ได้แต่สร้าง checkbox native ขึ้นเองไม่ได้ Interaction config ควบคุม
continuation แต่อนุมัติ HIGH/destructive/HITL แทน Human ไม่ได้

## 2. End-to-end overview

```text
[Code-changing request]
   |
   v
[/sage] pre-action clarification pass
   |
   +-- repository fact --> inspect it; do not ask
   +-- missing material decision --> Grill/Wayfinder question gate
   `-- actionable direct/fix request --> continue without ceremonial question
   |
   v
[/sage] อ่าน .sage-local.json v3
   |
   +-- mode:auto --> แสดง recommended set --> ทำต่อโดยไม่เปิด picker
   |
   `-- mode:ask
         +-- host มี multi-select --> checkbox 5 รายการ
         +-- host มี single-select --> Recommended / Defaults / Customize
         `-- ไม่มี structured UI --> recommended | defaults | +/-exceptions
   |
   v
[/sage] route + risk + plan
   |
   +-- Grill requirements-clear --+
   +-- Wayfinder spec-ready -------+--> parent ทำ frontier ถัดไป
   +-- Flow design-clear ----------+
   |
   +-- material gate --> คืน control ให้ Human
   `-- no gate ------> implementation --> validation --> docs --> complete
```

**หัวใจ:** Provider name ไม่ได้พิสูจน์ picker capability และการจบ child command
ไม่ได้แปลว่างานทั้ง run เสร็จ ส่วน clarification pass เป็น internal sufficiency
check ไม่ใช่ข้อบังคับว่าต้องถามผู้ใช้ทุกงาน

## 3. Checklist selection

Checklist มีสอง run options และลำดับล็อก:

1. `suggest-switch-model`
2. `plan-flow`

ทุก host ต้องแสดง recommendation + reason ของทั้งสองรายการก่อน selection
แต่รูปแบบ input เปลี่ยนตาม capability จริง

`unit-test`, `e2e-test` และ `security-review` เป็น specialist command ที่ Human
ต้องเรียกเอง `/sage` จะไม่ recommend หรือ invoke อัตโนมัติ โดยเฉพาะการสร้างหรือ
แก้ test file ต้องมี `/sage-unit-test`, `/sage-e2e-test` หรือคำสั่งตรงจาก Human
ก่อนเสมอ ส่วนการรัน existing tests เป็น validation ยังทำได้

### Native multi-select

เมื่อ session มี callable multi-select tool ให้ใช้ checkbox native โดยตรง
Claude Code ที่เปิด capability นี้จึงเลือกหลายรายการในครั้งเดียวได้

### Structured single-select

เมื่อ host มีเฉพาะปุ่ม/radio แบบเลือกหนึ่ง ให้แสดง:

- `Run recommended` — ค่าแนะนำ
- `Use saved defaults`
- `Customize`

เมื่อเลือก `Customize` ให้ถาม on/off toggles เป็นชุดตามข้อจำกัดของ tool ผู้ใช้
ไม่ต้องพิมพ์รายการหมายเลขเอง

### No structured input

เมื่อ host ไม่มี structured picker ให้รับคำสั้น ๆ:

- `recommended`
- `defaults`
- `-plan-flow`

Numeric reply เช่น `1` ยังอ่านได้เพื่อ backward compatibility แต่ไม่ใช่
primary UX

### `mode:auto`

Auto mode ไม่เปิด picker แม้ host จะมี checkbox Sage คำนวณ recommended set,
แสดง checklist เพื่อความโปร่งใส แล้วทำต่อทันที

## 4. Run-until-gate lifecycle

Parent `/sage` คำนวณ Run frontier จากงานที่ `open + unblocked`:

1. รัน pre-action pass: แยก repository facts ออกจาก human-owned decisions
2. ถ้า request actionable อยู่แล้ว ให้ทำต่อโดยไม่สร้างคำถามเชิงพิธี
3. ทำงานอิสระพร้อมกันเมื่อ environment รองรับ
4. ทำงาน dependent หลัง prerequisite เสร็จ
5. เลือก default สำหรับ internal + reversible preference และบันทึก assumption
6. เมื่อจำเป็นต้องถาม ให้ batch human decisions ที่อิสระไม่เกิน 3 ข้อ
7. ถาม dependent decision tree ทีละข้อ
8. Consume `requirements-clear`, `spec-ready`, `design-clear`
9. Recompute frontier และเดินต่อ

การจบ ticket, command, handoff, checkpoint หรือ phase เป็น state transition
ไม่ใช่ terminal condition

## 5. Wayfinder frontier waves

Wayfinder chart map แล้วเข้า frontier wave แรกทันที:

- AFK `research`/`task` ที่อิสระ → claim และทำ parallel
- Independent HITL tickets → batch ตาม question policy
- Dependent HITL tickets → ถาม most-blocking branch ทีละข้อ
- Ticket ปิด → บันทึก evidence/gist → recompute frontier
- Map complete → synthesize spec → active parent ไป Flow ต่อ

Local claims ยังไม่ atomic ทุก ticket จึงต้อง re-read ก่อน claim, skip conflict
และ parallel เฉพาะ dependency/side effects ที่อิสระ

## 6. `.sage-local.json` v3

```json
{
  "version": 3,
  "mode": "auto",
  "checklist": {
    "suggest-switch-model": true,
    "plan-flow": true
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

Migration จาก v2 เก็บ `mode`, `checklist` และ unknown fields แล้วเติม
`interaction` defaults ผู้ใช้เปลี่ยนค่าผ่าน `/sage-setting` ไม่ต้องแก้ JSON เอง

### Interaction values

| Field | Meaning |
| --- | --- |
| `runPolicy: until-gate` | ทำทุก frontier wave จนเจอ material gate หรือ complete |
| `runPolicy: strict` | คืน control ตาม command checkpoints |
| `questionPolicy: batch-independent` | รวมเฉพาะคำถามที่ไม่เปลี่ยน branch ของกัน |
| `questionPolicy: one-at-a-time` | ถามทุก decision แยก |
| `maxQuestionsPerCheckpoint` | จำนวน independent questions ต่อ checkpoint: 1–3 |
| `autoDecideReversible` | เลือก internal reversible default พร้อม assumption |
| `continueAfterHandoff` | ให้ active parent consume child handoff แล้วทำต่อ |

## 7. Stop conditions

`until-gate` หยุดเฉพาะ:

- material human-owned decision
- HIGH หรือ destructive/irreversible action
- scope/destination/public contract เปลี่ยนอย่างมีนัยสำคัญ
- auth/payment/PII trust-boundary decision
- missing access หรือ manual external action
- failed critical control
- matched block/reject
- งานและ validation เสร็จจริง

`strict` เพิ่ม command checkpoints ได้ แต่ไม่มี interaction field ใดลบรายการ
ข้างต้นได้

## 8. Edge cases

| Case | Handling |
| --- | --- |
| Direct bounded instruction | รัน clarification pass ภายใน แล้วทำต่อทันทีเมื่อไม่มี material decision ขาด |
| Bug fix มี error/stack trace/test/repro เพียงพอ | เริ่ม diagnose/fix; ไม่ถามเชิงพิธี และถามภายหลังเฉพาะเมื่อหลักฐานใหม่เปิด human-owned branch |
| ข้อมูลที่ขาดหาได้จาก repo | อ่าน code/tests/schema/config/logs/docs เอง; ไม่ถาม Human |
| Request actionable แต่ action เป็น HIGH/destructive | risk gate ยังบังคับ explicit approval |
| Codex/agent name ดูเหมือนรองรับ picker | ตรวจ callable tool/schema ของ session; ห้ามเดา |
| Host มีแค่ single-select | Recommended/Defaults/Customize |
| Host ไม่มี widget | Keyword/exception fallback |
| Auto mode บน host ที่มี checkbox | ไม่เปิด checkbox |
| Independent questions เกิน 3 | แบ่ง checkpoints |
| คำถามหนึ่งเปลี่ยนอีกคำถาม | Reclassify เป็น dependent |
| Child command ถูกเรียก standalone | แสดง artifact/summary แล้ว return |
| Active parent ได้ clear handoff | ทำ frontier ถัดไปทันที |
| Runtime จบ turn โดยหลีกเลี่ยงไม่ได้ | เขียน durable checkpoint และรายงาน limitation |
| Interaction config พยายามข้าม HIGH | Risk policy ปฏิเสธ |

## 9. Security & concurrency

- Picker selection ไม่ใช่ risk approval
- `mode:auto` ไม่อนุมัติ destructive/HIGH action
- `autoDecideReversible` ใช้กับ public contract/trust boundary ไม่ได้
- External tracker writes ต้องอยู่ใน user scope
- Parallel Wayfinder tickets ต้องไม่มี dependency/side-effect overlap
- Failed critical control หยุด dependent work แม้ frontier อื่นยังเปิด

## 10. Validation contract

Protocol tests ตรวจ:

- pre-action clarification pass แยก fact ออกจาก human-owned decision
- direct actionable/error-rich fix ไม่ถูกถามเชิงพิธี
- vague material decision ยัง route เข้า Grill และถามตาม dependency
- actionable fast path ข้าม HIGH/destructive gate ไม่ได้
- config v3 migration/defaults
- native-first capability routing
- auto mode ไม่เปิด picker
- child handoff continuation
- Wayfinder frontier waves
- independent/dependent question policy
- narrower `plan-flow` trigger
- compact approved roles ที่ไม่มี local gates
- interaction settings ปิด safety gates ไม่ได้

คำสั่งหลัก:

```text
python -m unittest discover -s tests -v
```

## 11. Open questions

ไม่มี — Native checkbox ใช้เมื่อ host expose multi-select เท่านั้น ส่วน host อื่น
ใช้ structured one-click หรือ compact fallback โดยไม่สัญญา UI ที่ไม่มีจริง
