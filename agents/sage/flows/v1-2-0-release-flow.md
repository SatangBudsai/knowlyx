# Sage v1.2.0 release flow

วันที่: 2026-08-19

## 1. Header and design decisions

ออก `v1.2.0` เป็น minor release เพราะเพิ่ม public command/skill
`sage-refactoring-code` โดยไม่ทำลาย contract เดิม การ release ต้องชี้ tag ไปยัง
commit ที่มี landing version, changelog และ test fix ครบ ไม่ tag commit feature
เดิมโดยตรง

## 2. Actors & Systems

| Actor/System | Responsibility |
| --- | --- |
| Maintainer | อนุมัติการออกเวอร์ชันผ่านคำขอครั้งนี้ |
| Local `main` | เตรียม release commit และเป็น source ที่ทดสอบ |
| GitHub `origin/main` | รับ release commit |
| Git tag `v1.2.0` | ระบุ immutable release revision |
| GitHub Actions | รับ tag push และ purge jsDelivr `@latest` cache |
| jsDelivr | แจก installer จาก tag ล่าสุดให้ผู้ใช้ |
| Landing page | แสดงเวอร์ชันปัจจุบันให้ตรงกับ tag |

Trust boundary: ห้าม push tag จน local commit ผ่าน tests, ตรงกับ remote main,
และ tag name ยังไม่มี ห้าม force-move tag หลังเผยแพร่

## 3. End-to-end overview

```text
feature on origin/main
  -> prepare CHANGELOG + landing version + protocol test fix
  -> run full validation
  -> commit release metadata
  -> push main
  -> create annotated v1.2.0 tag on tested commit
  -> push tag
  -> GitHub Actions purges jsDelivr @latest
  -> verify remote main/tag point to the expected commits
```

## 4. Step-by-step

1. ตรวจว่า `main` clean, ตรงกับ `origin/main`, และ `v1.2.0` ไม่มีทั้ง local/remote
2. เพิ่ม changelog entry ของ `sage-refactoring-code` และจัดของเดิมเป็น `v1.1.0`
3. เปลี่ยน landing version ทั้ง meta, badges และ aria labels เป็น `v1.2.0`
4. เติม contract `plan-flow` ที่ test เดิมระบุ เพื่อปิด validation gap ก่อน release
5. รัน full unittest suite และ `git diff --check`
6. commit เป็น `chore: release v1.2.0` แล้ว push `main`
7. สร้าง annotated tag `v1.2.0` ที่ release commit แล้ว push tag
8. fetch/ls-remote เพื่อตรวจว่า remote main และ tag ชี้ revision ที่คาด

## 5. State / data handling

- Version source สำหรับ release นี้: annotated git tag `v1.2.0`
- Landing mirror: `landing/index.html` ต้องมี version เดียวกันทุกตำแหน่ง
- Release notes: `CHANGELOG.md`
- CDN state: invalidated โดย `.github/workflows/purge-jsdelivr.yml` หลัง tag push
- ไม่มี database หรือ user data mutation

## 6. API spec

ไม่มี API ใหม่ Public distribution contract คือ URL jsDelivr เดิมที่ใช้ `@latest`;
หลัง purge ต้อง resolve ไป tag `v1.2.0` โดยไม่เปลี่ยน URL ของผู้ใช้

## 7. Status lifecycle

```text
prepared -> validated -> main-pushed -> tagged -> tag-pushed -> verified
       \-> validation-failed -> fix -> validated
```

ห้ามข้ามจาก `prepared` ไป `tag-pushed`

## 8. Data model touchpoints

N/A — release นี้ไม่มี schema/database change

## 9. Edge cases & error handling

| Scenario | Handling |
| --- | --- |
| `v1.2.0` มีอยู่แล้ว | หยุด ไม่ย้าย/ลบ tag |
| remote main เปลี่ยนระหว่างเตรียม | fetch แล้วหยุดเพื่อ reconcile ก่อน push |
| tests fail | ห้าม commit/tag จนแก้หรือมี human decision ใหม่ |
| main push fail | หยุด; ไม่สร้าง tag |
| tag push fail | ตรวจ remote tag ก่อน retry; ไม่ force |
| purge workflow fail | release tag ยังอยู่ แต่รายงาน CDN freshness gap |

## 10. Security & concurrency

- ใช้ non-force push ทั้ง branch และ tag
- ตรวจ exact remote ref ก่อนและหลัง mutation
- annotated tag ผูก release name กับ commit ที่ผ่าน validation
- ไม่เปิดเผย token หรือ credential ใน output

## 11. Build checklist

- [ ] Changelog ระบุ `v1.2.0` และ feature ใหม่
- [ ] Landing แสดง `v1.2.0` ครบทุกตำแหน่ง
- [ ] Full suite ผ่าน
- [ ] Diff/working tree มีเฉพาะ release preparation
- [ ] Release commit ถูก push ไป `origin/main`
- [ ] Annotated tag ถูก push โดยไม่ force
- [ ] Remote refs ตรงกับ local refs

## 12. Out of scope

- ไม่สร้าง GitHub Release object แยก หาก repo ใช้ tag เป็น release trigger
- ไม่แก้ installer/CDN URL หรือ workflow behavior
- ไม่ force-update/delete tag เก่า
- ไม่รวม feature อื่นหลัง commit `ba94c6c`

## 13. Open questions

ไม่มี `v1.2.0` เป็น SemVer minor ที่ตรงกับ additive public skill และคำขอให้ออก
เวอร์ชันถือเป็น authorization สำหรับ release นี้

## Verification verdict

`design-clear` — release sequence ป้องกัน tag ก่อน validation, ระบุ rollback boundary
ชัดเจน และใช้ workflow/tag contract ที่มีอยู่จริงใน repository
