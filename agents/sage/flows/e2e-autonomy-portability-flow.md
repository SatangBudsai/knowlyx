# E2E autonomy and portability flow

วันที่: 2026-08-20

## 1. Header and design decisions

ปรับ `/sage-e2e-test` ให้ plan, explore, implement, run, debug และ validate ต่อเนื่อง
โดยไม่ถาม routine choices ทุกขั้น ใช้ capability-based behavior เพื่อให้ canonical
command เดียวทำงานได้กับ Codex และ agent อื่น ส่วน Terra/Luna/Sol เป็น optional
mapping เมื่อ host รองรับเท่านั้น

## 2. Actors & Systems

| Actor/System | Responsibility | Ownership |
| --- | --- | --- |
| User | ระบุ flow/feature และ business constraints | product intent |
| E2E coordinator | เลือก journey, สำรวจ, classify failure, ปิด evidence | test strategy |
| Bounded worker | ทำ mechanical test work เมื่อ host รองรับ delegation | scoped implementation |
| Interactive browser | สำรวจ behavior/runtime ที่ logs อธิบายไม่ได้ | observation only |
| E2E runner | encode และ rerun regression เช่น Playwright/Cypress | repeatable evidence |
| Application stack | UI/API/database/services ที่ถูกทดสอบ | behavior source of truth |

Trust boundary: browser observation และ source code เป็น evidence แต่ไม่อนุญาตให้
ทดสอบเงินจริง/production mutation หรือข้าม auth/approval controls

## 3. End-to-end overview

```text
request -> detect stack/capabilities -> rank critical journeys
        -> explore real behavior when available -> record expectations
        -> implement targeted E2E -> run -> classify failure
        -> fix test | report/fix authorized app bug | repair environment
        -> rerun targeted + relevant suite -> completion evidence
```

## 4. Step-by-step

1. ตรวจ framework, flow docs, app commands, accounts/seeds และ browser capability
2. เลือก happy path, meaningful failure, auth boundary และ high-risk journey ที่คุ้มค่า
3. สำรวจ UI จริงเมื่อเปิดได้; ไม่เดาจาก source อย่างเดียว
4. บันทึก starting state, action, UI/navigation/data/API outcome ก่อนเขียน test
5. ใช้ framework เดิม; ถ้าไม่มี ให้ใช้ ecosystem default โดย Playwright เป็น default
   สำหรับ JS/TS browser app เว้นแต่ repo policy กำหนดต่าง
6. ใช้ accessible locators, meaningful waits, isolated data และ real stack เท่าที่ปลอดภัย
7. รัน targeted test ทันที แล้ว classify failure เป็น Test/Application/Environment
8. ใช้ logs/traces ก่อน browser reinspection และ delegate เฉพาะงาน bounded เมื่อรองรับ
9. rerun จน deterministic แล้วรัน relevant suite
10. สรุป coverage, bugs, blockers และ residual risk

## 5. State / data handling

- Test fixture/seed ต้องมี owner และ cleanup/reset path
- Auth session ใช้ test account/sandbox ไม่ใช้ credential production
- Screenshot/trace/log เก็บเฉพาะที่ framework/repo กำหนดและไม่เผย secrets
- Expected-behavior record อยู่ใน test name/setup/assertions หรือ planning note ชั่วคราว

## 6. API spec

ไม่มี API ใหม่ Command contract คือ `/sage-e2e-test <flow>` และ output เป็น test
files + run evidence + failure classification + residual risk

## 7. Status lifecycle

```text
planned -> observed -> encoded -> running -> classified -> stable -> complete
                                  |-> test-fix -> running
                                  |-> app-defect -> report/authorized-fix
                                  |-> env-blocked -> repair-or-gate
```

## 8. Data model touchpoints

ไม่มี Sage schema เพิ่มขึ้น Project data ที่ test สร้างต้อง isolated, deterministic,
cleanup ได้ และห้ามใช้ destructive production state

## 9. Edge cases & error handling

| Scenario | Handling |
| --- | --- |
| ไม่มี interactive browser | ใช้ executable tests/source/contracts และระบุ observation gap |
| ไม่มี E2E framework | เลือก ecosystem default ถ้าเป็น reversible dev dependency; หยุดเมื่อ policy ต้องตัดสินใจ |
| locator/timing fail | classify เป็น test issue ก่อนแก้; ห้ามเพิ่ม sleep/timeout แบบไม่วิเคราะห์ |
| application bug | ไม่ลด assertion; รายงานและแก้เฉพาะเมื่อ request authorize |
| service/database unavailable | classify environment; repair safe local setup หรือ report gate |
| host ไม่มี subagent/model switching | coordinator ทำเอง; ไม่อ้างว่า delegate/switch แล้ว |

## 10. Security & concurrency

- production,เงินจริง, email จริง และ destructive data ต้องมี explicit approval
- ทดสอบ authz ด้วย negative permissions และ ownership boundaries เมื่อเกี่ยวข้อง
- parallel workers รับไฟล์/context เท่าที่จำเป็นและไม่แก้ target ซ้อนกัน
- retries ต้องไม่ซ่อน flaky behavior หรือ duplicate side effect

## 11. Build checklist

- [ ] Rewrite canonical `sage-e2e-test.md` ด้วย autonomous workflow
- [ ] เพิ่ม provider-neutral tiers + optional Codex mapping
- [ ] เพิ่ม browser-vs-runner contract และ expected-behavior record
- [ ] เพิ่ม Test/Application/Environment classification
- [ ] เพิ่ม completion criteria และ context/delegation rules
- [ ] เพิ่ม regression tests และ changelog
- [ ] รัน full repository suite

## 12. Out of scope

- ไม่บังคับ Playwright เมื่อ repo มี established E2E framework
- ไม่บังคับ Terra/Luna/Sol หรือ subagents กับ host ที่ไม่มี capability
- ไม่ทำ production/destructive E2E ให้อัตโนมัติ
- ไม่เปลี่ยน adapters เพราะทุกตัวชี้ canonical command อยู่แล้ว

## 13. Open questions

ไม่มี Portability rule และ safe autonomy boundary สรุปได้จาก repository protocol,
คำขอ และ capability model ปัจจุบัน

## Verification verdict

`design-clear` — workflow รักษา real behavior และ autonomy โดยไม่ผูก provider,
ไม่ลด safety gates และไม่สร้าง duplicated adapter policy
