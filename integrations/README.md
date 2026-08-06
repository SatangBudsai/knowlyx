# Sage integrations — one protocol, every agent

The protocol lives in **[`../agents/sage/AGENTS.md`](../agents/sage/AGENTS.md)** and every command's full
body lives once under **[`../agents/sage/commands/`](../agents/sage/commands/)**.
The files in this folder are **thin adapters** — each just points its tool at the
canonical files. Copy only what your tool needs (or run the one-command installer
in the root README, which does the detection for you).

## Usage

```bash
# Claude Code
cp -r integrations/.claude .

# Cursor
cp -r integrations/.cursor .

# Windsurf
cp -r integrations/.windsurf .

# Cline
cp -r integrations/.clinerules .

# GitHub Copilot
cp -r integrations/.github .

# Codex
cp -r integrations/.codex .

# Gemini CLI
cp integrations/gemini.md ./GEMINI.md
```

## What gets placed

| Copy           | Destination             | For            |
| -------------- | ----------------------- | -------------- |
| `.claude/`     | `.claude/commands/`     | Claude Code    |
| `.cursor/`     | `.cursor/commands/` + `.cursor/rules/` | Cursor |
| `.windsurf/`   | `.windsurf/workflows/` + `.windsurf/rules/` | Windsurf |
| `.clinerules/` | `.clinerules/`          | Cline          |
| `.github/`     | `.github/prompts/` + `.github/instructions/` | GitHub Copilot |
| `.codex/`      | `.codex/prompts/` and `.codex/skills/sage/SKILL.md` | Codex |
| `gemini.md`    | `GEMINI.md` + `.gemini/commands/sage.toml` | Gemini CLI |

**OpenCode, Google Antigravity** (and Codex) read `AGENTS.md` natively — the
adapters above just add the slash-command entry points. Keep `AGENTS.md` at your
repo root either way.

Each adapter is intentionally tiny: it points at `agents/sage/AGENTS.md` and the
canonical command under `agents/sage/commands/`. Edit the protocol or a command
in **one** place and every agent stays in step.

Codex has two discovery surfaces: `.codex/prompts/` is typically exposed as
`/prompts:sage`, while `.codex/skills/sage/SKILL.md` is typically exposed as
`$sage`. Claude Code and rule-based adapters can expose the shorter `/sage`
label directly. The host owns the final label; Sage cannot force every host to
use identical syntax.

## Commands included

| Command                 | What it does                                                           |
| ----------------------- | ---------------------------------------------------------------------- |
| `/sage`                 | Run the cognition pipeline + run checklist before any code change      |
| `/sage-grill`           | Resolve single-session fog, glossary, and checkpoint decisions         |
| `/sage-wayfinder`       | Map multi-session fog as durable decision tickets                      |
| `/sage-flow`            | Turn a feature/journey into an implementation-ready business flow      |
| `/sage-unit-test`       | Write unit tests that match how this repo already tests                |
| `/sage-e2e-test`        | Drive the app end-to-end (Playwright/k6/…) and prove the flow          |
| `/sage-security-review` | Review a change for real, exploitable security holes                   |
| `/sage-docs`            | Turn any document into a plain-Markdown flow doc (`docs/<slug>.md`)    |
| `/sage-learning`        | Learn this repo's patterns + research best practices for its stack     |
| `/sage-update`          | Update Sage in this repo to the latest version (re-runs the installer) |
| `/sage-setting`         | View/change how `/sage` runs (mode: auto/ask, default steps)           |

`/sage` is the one you use most — its §0 route guard sends fog to Grill or
Wayfinder, then its checklist decides which build/validation specialists apply.

> Don't see your agent? Most modern agents support either `AGENTS.md` or a
> rules/instructions file — point it at `AGENTS.md` the same way.
