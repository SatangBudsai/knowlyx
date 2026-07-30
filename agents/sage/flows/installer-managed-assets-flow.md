# Sage installer — managed assets without user-data loss

> Flow สำหรับ fresh install และ upgrade ผ่าน `install.sh` / `install.ps1`
> โดยกระจาย Project DNA และ Sage system assets ครบทั้งสอง platform แต่เขียนทับ
> เฉพาะ exact paths ที่ Sage ประกาศว่าเป็นเจ้าของ อ้างอิง installer จริง ณ
> 2026-07-30 สถานะ: `design-clear`

## 1. Header + design decisions

Installer ใช้ manifest เดียวเป็น source of truth ของ Sage-managed files ทั้ง
Bash และ PowerShell ทุก path ใน manifest ต้องเป็น relative file path ที่ชัดเจน
และผ่าน preflight ก่อนมีการแก้ target repository ส่วน commands ยังเป็น
Sage-owned directory ที่ replace ทั้งชุดเพื่อกำจัด command ที่ถูกถอดหรือเปลี่ยนชื่อ

การตัดสินใจหลัก:

- ใช้ `agents/sage/install-manifest.txt` เป็น exact allowlist ของ managed files
- ใช้ `agents/sage/adapter-manifest.txt` เป็น append-only list ของ adapter
  basenames ที่ Sage มีสิทธิ์ลบ/แทนที่
- overwrite เฉพาะ `AGENTS.md`, `agents/sage/commands/`, manifest paths และ
  selected adapter paths ที่ระบุชัด
- preserve custom domains, roles, non-managed flows, docs, `.sage-local.json`
  และ custom adapter files แม้ชื่อขึ้นต้นด้วย `sage`
- preflight source, manifest paths และ selected adapters ทั้งหมดก่อนเขียน
- Bash และ PowerShell ต้องอ่าน manifest เดียวกันและให้ผล filesystem เท่ากัน
- `SAGE_INSTALL_SOURCE` เป็น local-source override สำหรับ development/tests;
  production default ยัง clone official repository
- Project DNA human overview ที่ `docs/project-dna.md` ไม่ถูก copy เข้า target
  เพราะ `docs/` เป็นพื้นที่เอกสารของ project ผู้ใช้; full installed contract อยู่
  ที่ `agents/sage/flows/project-dna-flow.md`

### Out of scope

- ไม่ติดตั้ง Project DNA runtime, database, scanner หรือ MCP server
- ไม่เปลี่ยน checkbox/tool selection UX
- ไม่แก้ `.sage-local.json` หรือ persisted checklist defaults
- ไม่ merge/rewrite user-owned `agents/sage/index.md`
- ไม่ update user-created role หรือ domain knowledge
- ไม่ลบ unknown/legacy files ด้วย glob กว้าง
- ไม่แก้ remote URL, release channel หรือ CDN behavior
- ไม่ทำ concurrent installer locking ในรอบนี้; concurrent run ถูกระบุเป็น
  unsupported edge case

## 2. Actors & Systems

| System | Responsibility | Ownership |
| --- | --- | --- |
| Human/automation | เลือก adapters และเรียก installer ใน target repo | Target repo + tool choice |
| Bash installer | ทำ install/upgrade บน POSIX/Git Bash | `install.sh` |
| PowerShell installer | ทำ install/upgrade บน Windows | `install.ps1` |
| Source repository | ให้ protocol, commands, manifests, managed files, adapters | Official clone หรือ explicit local source |
| Install manifest | ระบุ exact Sage-managed files | Sage distribution contract |
| Adapter manifest | ระบุ exact command basenames ที่ cleanup ได้ | Sage adapter lifecycle |
| Target repository | เก็บ Sage files ร่วมกับ user knowledge/docs/config | User owns every non-reserved path |
| Regression fixtures | พิสูจน์ fresh/upgrade/parity/preservation | Test-only temp directories |

**Trust boundary**

- Installer เชื่อ source เฉพาะหลัง resolve สำเร็จและ preflight required files ครบ
- Manifest เป็น executable write authority จึงต้อง reject absolute path,
  traversal, directory entry และ missing source
- Environment override มีผลเฉพาะเมื่อ human/CI ตั้ง `SAGE_INSTALL_SOURCE`
- Target content นอก exact managed paths เป็น user-owned แม้ basename เริ่ม `sage`
- Selected adapter จำกัด cleanup/copy ให้อยู่ใต้ adapter root ของ tool นั้น

## 3. End-to-end overview

```text
[Human/CI] run installer + SAGE_TOOLS
   |
   v select tools (env -> picker -> fallback)
[Installer] resolve source
   |
   +-- production -> git clone official repository
   `-- test/dev ---> read explicit SAGE_INSTALL_SOURCE
   |
   v preflight AGENTS + commands + manifests + every managed source + adapters
   |
   +-- invalid/missing/path traversal -> fail before target writes
   `-- valid ------------------------> continue
   |
   v write AGENTS.md + replace agents/sage/commands/
[Installer] copy each exact install-manifest path
   |
   v seed agents/sage/index.md + roles only when absent
[Installer] remove only exact adapter-manifest paths for selected tools
   |
   v copy selected adapter source
[Target repo] managed assets current; user sentinels unchanged
   |
   v print installed adapters + Project DNA spec path
[Installer] cleanup temp source
```

**หัวใจ:** manifest ขยายสิ่งที่ Sage ติดตั้งได้โดยไม่ขยายขอบเขตสิ่งที่ Sage มี
สิทธิ์ลบ

## 4. Step-by-step

### STEP 1 — Resolve selected tools

**System:** Bash/PowerShell installer

- เมื่อมี `SAGE_TOOLS` → parse keys/numbers และไม่เปิด picker
- เมื่อไม่มี env และ console รองรับ → ใช้ native/number picker เดิม
- เมื่อไม่มี console → Bash default `all`; PowerShell ใช้ fallback menu เดิม
- เมื่อ selection ว่าง → return “Nothing to do” ก่อน fetch/write
- invalid tokens ถูก ignore; valid keys ถูก deduplicate

### STEP 2 — Resolve installation source

**System:** Installer + Source repository

- เมื่อ `SAGE_INSTALL_SOURCE` ไม่ว่าง → resolve directory และอ่านเป็น source
  แบบ read-only โดยตรง; temp ใช้เก็บ normalized manifest lists เท่านั้น
- เมื่อ local source ไม่มี/ไม่ใช่ directory → fail ก่อน target write
- เมื่อ local source resolve เป็น target repo เดียวกัน → fail เพื่อไม่ให้
  commands cleanup ลบ source ที่กำลัง copy
- เมื่อไม่มี override → require Git และ shallow clone official repository
- source temp ถูก cleanup ใน success, failure, interrupt และ exception paths
- local override ไม่ถูกพิมพ์เป็น production recommendation; มีไว้สำหรับ
  development/test ที่ caller ควบคุม source

### STEP 3 — Parse and validate manifests

**System:** Installer

- require `agents/sage/install-manifest.txt`
- require `agents/sage/adapter-manifest.txt`
- trim CR/whitespace และ skip blank/comment lines
- install manifest entry ต้องเป็น relative forward-slash file path
- reject absolute path, drive-qualified path, `.`/`..` segment, backslash และ
  trailing slash/directory
- require source file ของทุก install entry
- adapter basename ต้อง match `[a-z0-9][a-z0-9-]*`
- reject duplicate/invalid entries; ห้ามเริ่ม write เมื่อ preflight fail

### STEP 4 — Preflight selected adapters

**System:** Installer

- map tool key ไป source integration path และ target adapter root
- require source file/directory ของ selected tool
- Gemini require `integrations/gemini.md`
- directory adapters require expected integration root
- preflight สำเร็จครบทุก selected tool ก่อนแก้ `AGENTS.md`

### STEP 5 — Install protocol and commands

**System:** Installer + Target repository

- copy source `AGENTS.md` → target `AGENTS.md`
- remove exact directory `agents/sage/commands`
- copy source commands directory ทั้งชุด
- commands เป็น directory เดียวที่ replace recursively เพราะเป็น
  100% Sage-owned และต้องลบ renamed/retired commands
- ไม่ enumerate path จาก shell หนึ่งแล้วส่งไปอีก shell

### STEP 6 — Install exact managed files

**System:** Installer + Install manifest

- iterate validated entries
- create parent directory ของแต่ละ destination
- copy source file ไป exact destination ด้วย overwrite
- copy manifest ตัวเองเพื่อให้ target ตรวจ ownership ได้
- managed Project DNA/protocol/flow files update ทุกครั้ง
- unknown sibling files ใน `flows/`, `protocol/` หรือ `sage-product/` ไม่ถูกลบ

### STEP 7 — Run bounded migration and starter seeding

**System:** Installer

- remove exact legacy style assets เดิมสาม path เท่านั้น
- copy `agents/sage/index.md` เฉพาะเมื่อ target ไม่มี
- copy `agents/sage/roles/` เฉพาะเมื่อ target ไม่มีทั้ง directory
- ไม่แก้ existing index/roles เพราะทีมอาจ customize
- `.sage-local.json` และ `docs/` ไม่ถูกอ่าน/เขียน

### STEP 8 — Clean selected adapter files safely

**System:** Installer + Adapter manifest

- สำหรับ basename แต่ละตัว map exact target ตาม tool:
  - Claude: `.claude/commands/<name>.md`
  - Codex: `.codex/prompts/<name>.md`
  - Cursor: `.cursor/rules/<name>.mdc`
  - Copilot: `.github/instructions/<name>.instructions.md`
  - Windsurf: `.windsurf/rules/<name>.md`
  - Cline: `.clinerules/<name>.md`
- remove exact mapped file only
- `sage-custom.*`, workflows, settings และ unrelated adapter content อยู่ครบ
- Gemini overwrite `GEMINI.md` เฉพาะเมื่อถูกเลือก

### STEP 9 — Copy selected adapters

**System:** Installer

- create adapter target root
- copy selected integration contents recursively
- source contains thin pointers เท่านั้น
- unselected adapters ไม่ถูกแตะ
- report label ของ adapters ที่ติดตั้งจริง

### STEP 10 — Close and report

**System:** Installer

- print command list
- print `Project DNA spec: agents/sage/flows/project-dna-flow.md`
- print next step `/sage-learning`
- cleanup temp directory
- non-zero exit/terminating error เมื่อ preflight หรือ copy ล้มเหลว

## 5. State / data handling

| State | Created | Updated | Cleared |
| --- | --- | --- | --- |
| `picked` | หลัง env/picker | ระหว่าง deduplicate | process exit |
| temp source | หลัง selection | clone/copy source | trap/finally |
| install entries | หลัง parse manifest | ไม่เปลี่ยนหลัง preflight | process exit |
| adapter basenames | หลัง parse manifest | ไม่เปลี่ยนหลัง preflight | process exit |
| target managed files | หลัง preflight | overwrite exact path | คงอยู่หลัง install |
| user sentinels | มีอยู่ก่อน install | ไม่เปลี่ยน | installer ห้ามลบ |

ไม่มี database/runtime state เพิ่มเติม

## 6. External contract

ไม่มี network API ใหม่ Installer public inputs:

| Input | Meaning | Default |
| --- | --- | --- |
| `SAGE_TOOLS` | comma/space tool keys หรือ `all` | interactive/fallback selection |
| `SAGE_INSTALL_SOURCE` | local Sage repository root สำหรับ dev/tests | unset → official Git clone |

Managed-file contract:

- `agents/sage/install-manifest.txt` ระบุ exact overwrite paths
- `agents/sage/adapter-manifest.txt` ระบุ exact Sage adapter basenames
- entry ใหม่ใน manifest เป็น public installer change และต้องมี preservation test

## 7. Status lifecycle

```text
UNSTARTED
  -> TOOLS_SELECTED
  -> SOURCE_READY
  -> PREFLIGHTED
  -> PROTOCOL_WRITTEN
  -> MANAGED_ASSETS_WRITTEN
  -> ADAPTERS_WRITTEN
  -> COMPLETE

Any state before PREFLIGHTED -> FAILED(no target writes)
Any write state -> FAILED(partial upgrade reported by non-zero exit)
```

Preflight ลด partial failure จาก missing distribution assets แต่ filesystem
failure ระหว่าง write ยังเป็นไปได้ ผู้ใช้ rerun installer เพื่อ forward-fix เพราะ
ทุก operation idempotent

## 8. Data model touchpoints

| Target | Ownership | Operation |
| --- | --- | --- |
| `AGENTS.md` | Sage-owned | overwrite |
| `agents/sage/commands/` | Sage-owned directory | replace recursively |
| install-manifest entries | Sage-owned exact files | overwrite |
| legacy style assets | retired Sage-owned exact files | delete if present |
| `agents/sage/index.md` | team-owned after seed | create only when absent |
| `agents/sage/roles/` | team-owned after seed | create only when absent |
| non-managed domains/flows/docs | user/team-owned | no operation |
| selected exact adapter files | Sage-owned | remove then copy |
| other adapter files | user/tool-owned | preserve |
| `.sage-local.json` | machine/user-owned | preserve |

## 9. Edge cases & error handling

| Case | Handling |
| --- | --- |
| Manifest missing | fail preflight; no target write |
| Manifest contains traversal/absolute path | reject; no target write |
| Manifest source file missing | fail preflight; preserve current install |
| Invalid adapter basename | reject; no target write |
| Selected adapter source missing | fail preflight; no target write |
| Local source path missing | fail before temp/source ready |
| Local source equals target repo | reject before writes |
| Git unavailable with local source | continue; Git ไม่จำเป็น |
| Git unavailable without local source | fail with install guidance |
| Clone fails | fail; no target write |
| Fresh repo has no `agents/sage` | create parents and seed index/roles |
| Upgrade has custom domain/flow | exact manifest copy leaves sentinel unchanged |
| Custom adapter named `sage-custom` | preserve because absent from adapter manifest |
| Retired managed adapter | keep basename append-only in manifest; exact cleanup removes it |
| Existing `.sage-local.json` | preserve byte-for-byte |
| Existing docs | preserve byte-for-byte |
| Copy fails mid-upgrade | non-zero exit; rerun forward-fixes; no safe cross-platform transaction |
| Two installers run concurrently | unsupported; may race on commands; report as residual risk |
| No tools selected | exit without fetching/writing |

## 10. Security & concurrency

- normalize/validate manifest entries before joining destination paths
- `-LiteralPath` ใน PowerShell และ quoted variables ใน shell สำหรับ file paths
- exact deletion targets เท่านั้น ยกเว้น known `agents/sage/commands/`
- no `eval` กับ manifest content
- local source override เป็น explicit caller authority ไม่ถูกอ่านจาก repo config
- preflight selected adapters ป้องกันลบของเดิมแล้ว copy source ที่หาย
- temp directory สร้างด้วย `mktemp -d` / GUID ใต้ OS temp
- cleanup target ไม่ใช้ unresolved env/glob
- installer ไม่รับประกัน concurrent writers; future lock ต้องเป็น cross-platform
  และมี stale-lock recovery ก่อนเปิดใช้

## 11. Build checklist

### Distribution manifests

- [x] เพิ่ม exact managed-file manifest
- [x] เพิ่ม append-only adapter basename manifest
- [x] เพิ่ม installed-assets ownership documentation
- [x] รวม Project DNA, protocol และ Sage-owned flows ที่ index/reference ใช้

### Bash

- [x] เพิ่ม local source override
- [x] preflight manifests/paths/adapters ก่อน write
- [x] copy exact managed files
- [x] เปลี่ยน broad adapter deletion เป็น exact mapped deletion
- [x] report Project DNA spec path

### PowerShell

- [x] ทำ behavior เท่ากับ Bash
- [x] ใช้ `-LiteralPath` กับ manifest-derived paths
- [x] error แบบ terminating ก่อน write เมื่อ preflight fail
- [x] report Project DNA spec path

### Validation

- [x] static manifest/contract tests
- [x] fresh install fixtures ทั้ง Bash/PowerShell
- [x] upgrade managed files + preserve user sentinels
- [x] preserve `sage-custom` adapter file
- [x] reject traversal/missing manifest entries ก่อน writes
- [x] syntax parse ทั้งสอง scripts

## 12. Open questions

ไม่มี — exact allowlist เป็น boundary ที่ปลอดภัยและรองรับของใหม่ครบ Local source
override ใช้เฉพาะ explicit dev/test environment ส่วน production source ไม่เปลี่ยน

## 13. Skeptical verification

- **ทำไมไม่ copy `docs/project-dna.md`?** เพราะ target `docs/` เป็น user-owned
  และ installer สัญญาว่าไม่แตะ generated docs Full spec ที่ agent ต้องใช้ถูก
  ติดตั้งใน `agents/sage/flows/`
- **ทำไมไม่ copy ทั้ง `agents/sage/`?** เพราะจะทับ team knowledge, roles, flows
  และ local decisions; exact allowlist ให้ completeness โดยไม่ขยาย blast radius
- **manifest เองอันตรายหรือไม่?** ใช่ จึง preflight path traversal, rooted path,
  source existence และ file-only ก่อน target write
- **ทำไม commands ยัง replace directory?** Commands เป็น 100% Sage-owned และ
  ต้องลบ retired file; target ชัดเจนและมี preservation fixture รอบข้าง
- **adapter manifest ลบ custom file ได้ไหม?** ลบได้เฉพาะ basename ที่ Sage reserve
  แบบ append-only Custom `sage-*` ที่ไม่อยู่ใน manifest ไม่ถูกแตะ
- **Bash/PowerShell drift ได้ไหม?** ลดด้วย shared manifests และ E2E fixtures ที่
  assert target tree contract เดียวกัน
- **upgrade จากรุ่นเก่าปลอดภัยไหม?** broad cleanup ถูกแทน exact cleanup Existing
  knowledge/docs/config ถูก preserve; managed files update idempotently
- **มี silent partial success ไหม?** Missing distribution inputs fail ก่อน write;
  OS copy failure หลัง write ยัง possible และจบ non-zero พร้อม rerun path
