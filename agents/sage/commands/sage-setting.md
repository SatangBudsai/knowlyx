# /sage-setting — view and change how /sage runs (per machine)

Read and update `/sage`'s per-machine preferences in `.sage-local.json` so the
user never hand-edits JSON. This is a small, mechanical command — no §0 checklist,
no plan, no code analysis. Just show or change settings, then confirm.

`.sage-local.json` is **gitignored and per-machine** — it is never shared with the
team or committed.

---

## Config shape (`.sage-local.json`, at the repo root)

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

- **`mode`** — `"auto"` (decide the steps and proceed without prompting) or
  `"ask"` (show the checklist and wait for the human, every code change).
- **`checklist`** — the defaults for model suggestion and flow planning. Specialist
  checks are explicit commands, not `/sage` checklist entries.
- **`interaction.runPolicy`** — `"until-gate"` (continue through unblocked work
  and child handoffs) or `"strict"` (return at command checkpoints).
- **`interaction.questionPolicy`** — `"batch-independent"` or
  `"one-at-a-time"`; dependent decision trees are always one-at-a-time.
- **`maxQuestionsPerCheckpoint`** — 1–3, applied only to independent questions.
- **`autoDecideReversible`** — choose and record internal reversible defaults;
  never bypasses a public-contract, trust-boundary, or safety decision.
- **`continueAfterHandoff`** — return clear/spec-ready/design-clear child
  handoffs to an active parent run instead of ending it.

**Migration:** if the file has the old `askMode` field, convert it first —
`askMode: "smart"` → `mode: "auto"`, `askMode: "always"` → `mode: "ask"`.
For version 2, keep `mode`/`checklist`, add the version 3 `interaction` defaults,
set `version: 3`, drop only `askMode`, and **preserve unknown fields**.

---

## What to do

**1. Read** `.sage-local.json` at the active repo root (migrate old `askMode` if
present; create it with the defaults above if missing; add `.sage-local.json` to
`.gitignore` if not already ignored).

**2. Act on the request:**

| The user says…                         | Do this                                                                                                                             |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| "show settings" / just `/sage-setting` | Print the active repo, checklist mode/defaults, interaction policy, and whether `.sage-local.json` is gitignored. Then offer the changes below. |
| "ask me every time" / "mode ask"       | Set `mode: "ask"`.                                                                                                                  |
| "don't ask / auto" / "mode auto"       | Set `mode: "auto"`.                                                                                                                 |
| "default steps" / names                | Set `suggest-switch-model` and/or `plan-flow`; specialist commands are run explicitly. |
| "all steps on"                         | Set both `/sage` options `true`. |
| "run until gate" / "continue automatically" | Set `interaction.runPolicy: "until-gate"` and `continueAfterHandoff: true`. |
| "strict checkpoints"                   | Set `interaction.runPolicy: "strict"`.                                                                                              |
| "batch questions"                      | Set `questionPolicy: "batch-independent"` and ask for a max of 1–3 only if not supplied.                                            |
| "one question at a time"               | Set `questionPolicy: "one-at-a-time"`.                                                                                              |
| "reset"                                | Restore the default config above (keep the file gitignored).                                                                        |

If the request is ambiguous, use the best callable picker capability:

- native multi-select → checklist checkboxes;
- structured single-select → `Run recommended`, `Use saved defaults`, or
  `Customize`, then ask compact toggle batches;
- no structured input → accept `recommended`, `defaults`, or `+/-` exceptions.

Never assume `AskUserQuestion` or a Codex/other picker exists from the provider
name. Ask only for the setting that is actually ambiguous.

**3. Write** the updated `.sage-local.json` (valid JSON, preserve unknown fields
except on reset) and **echo the result** on one line, e.g.:

```text
Sage settings · mode: ask · run: until-gate · questions: batch-independent/3 · default steps: suggest-switch-model, plan-flow · .sage-local.json (gitignored)
```

Then stop. No summary block, no knowledge capture — this only edits local config.
