#!/bin/sh
# Sage installer — one command, any repo. Sets up (or updates) Sage:
#
#   bash -c "$(curl -fsSL https://cdn.jsdelivr.net/gh/qorstack/sage@latest/install.sh)"
#
# Lets you pick which AI tools to wire up with a checkbox picker:
#   press 1-7 to toggle a row (instant, no Enter needed)
#   a = select/clear all         Enter = confirm
# Number keys are plain characters, so this works in every console — including
# git-bash/MSYS, which swallows arrow keys.
# It updates only exact Sage-owned paths; custom knowledge/flows/docs survive.
#
# Non-interactive? Prefix with SAGE_TOOLS:
#   SAGE_TOOLS='claude,cursor' bash -c "$(curl -fsSL .../install.sh)"   (or 'all')
# Local development/tests may set SAGE_INSTALL_SOURCE to a Sage checkout.
set -eu

REPO="https://github.com/qorstack/sage"
ALL="claude codex cursor copilot gemini windsurf cline"
NTOOLS=7
TTY_STTY=""
TMP=""
SOURCE_ROOT=""
INSTALL_LIST=""
ADAPTER_LIST=""

cleanup() {
  [ -n "$TTY_STTY" ] && stty "$TTY_STTY" </dev/tty 2>/dev/null || true
  ( printf '\033[?25h' >/dev/tty ) 2>/dev/null || true
  [ -n "$TMP" ] && rm -rf "$TMP" || true
}
trap cleanup EXIT INT TERM

num_to_key() {
  case "$1" in
    1) echo claude ;; 2) echo codex ;; 3) echo cursor ;; 4) echo copilot ;;
    5) echo gemini ;; 6) echo windsurf ;; 7) echo cline ;; *) echo "" ;;
  esac
}
key_src() {
  case "$1" in
    claude) echo ".claude" ;; cursor) echo ".cursor" ;; windsurf) echo ".windsurf" ;;
    cline) echo ".clinerules" ;; copilot) echo ".github" ;; codex) echo ".codex" ;;
    gemini) echo "gemini" ;; *) echo "" ;;
  esac
}
key_name() {
  case "$1" in
    claude) echo "Claude Code" ;; cursor) echo "Cursor" ;; windsurf) echo "Windsurf" ;;
    cline) echo "Cline" ;; copilot) echo "GitHub Copilot" ;; codex) echo "Codex" ;;
    gemini) echo "Gemini CLI" ;; *) echo "" ;;
  esac
}

adapter_managed_path() { # $1 = tool key, $2 = Sage adapter basename
  case "$1" in
    claude) echo ".claude/commands/$2.md" ;;
    codex) echo ".codex/prompts/$2.md" ;;
    cursor) echo ".cursor/rules/$2.mdc" ;;
    copilot) echo ".github/instructions/$2.instructions.md" ;;
    windsurf) echo ".windsurf/rules/$2.md" ;;
    cline) echo ".clinerules/$2.md" ;;
    *) echo "" ;;
  esac
}

fail() {
  echo "Sage: $1"
  exit 1
}

parse_tools() { # $1 = raw string -> sets $picked
  picked=""
  case "$(printf '%s' "$1" | tr 'A-Z' 'a-z' | tr -d ' ')" in
    a | all | "") picked="$ALL"; return ;;
  esac
  for tok in $(printf '%s' "$1" | tr ',' ' '); do
    case "$tok" in
      [1-7]) k=$(num_to_key "$tok") ;;
      claude | cursor | windsurf | cline | copilot | codex | gemini) k="$tok" ;;
      *) k="" ;;
    esac
    [ -n "$k" ] && case " $picked " in *" $k "*) : ;; *) picked="$picked $k" ;; esac
  done
}

collect_picked() {
  picked=""
  for k in $ALL; do eval "v=\$chk_$k"; [ "$v" = 1 ] && picked="$picked $k"; done
}

toggle_row() { # $1 = row number
  tk=$(num_to_key "$1")
  eval "tv=\$chk_$tk"
  if [ "$tv" = 1 ]; then eval "chk_$tk=0"; else eval "chk_$tk=1"; fi
}

# Checkbox picker over /dev/tty using stty raw reads (dd) — the input path that
# works on git-bash/MSYS as well as macOS/Linux. Number keys toggle instantly;
# no cursor, no arrows — nothing a console can swallow.
# Returns 1 when unusable so the caller falls back to the numbered prompt.
select_tools_tui() {
  [ -r /dev/tty ] && [ -w /dev/tty ] || return 1
  command -v stty >/dev/null 2>&1 || return 1
  command -v dd >/dev/null 2>&1 || return 1
  TTY_STTY=$(stty -g </dev/tty 2>/dev/null) || return 1
  stty -echo -icanon min 1 time 0 </dev/tty 2>/dev/null || { TTY_STTY=""; return 1; }
  printf '\033[?25l' >/dev/tty

  CR=$(printf '\r')
  for k in $ALL; do eval "chk_$k=0"; done

  printf '\nSage: select AI tools — press 1-7 to toggle, a = all, Enter = confirm\n\n' >/dev/tty
  drawn=0
  while :; do
    [ "$drawn" = 1 ] && printf '\033[%dA' "$NTOOLS" >/dev/tty
    drawn=1
    i=1
    for k in $ALL; do
      eval "v=\$chk_$k"
      if [ "$v" = 1 ]; then
        printf '\r\033[K  \033[36m[x] %d) %s\033[0m\n' "$i" "$(key_name "$k")" >/dev/tty
      else
        printf '\r\033[K  [ ] %d) %s\n' "$i" "$(key_name "$k")" >/dev/tty
      fi
      i=$((i + 1))
    done
    c=$(dd bs=1 count=1 2>/dev/null </dev/tty) || c=""
    case "$c" in
      "" | "$CR") break ;; # Enter (NL is stripped by $(...), CR arrives raw)
      [1-7]) toggle_row "$c" ;;
      a | A)
        on=1; for k in $ALL; do eval "v=\$chk_$k"; [ "$v" = 0 ] && on=0; done
        nv=1; [ "$on" = 1 ] && nv=0
        for k in $ALL; do eval "chk_$k=$nv"; done ;;
    esac
  done

  stty "$TTY_STTY" </dev/tty 2>/dev/null || true
  TTY_STTY=""
  printf '\033[?25h\n' >/dev/tty
  collect_picked
  return 0
}

# One-shot numbered prompt — plain POSIX, works in any shell with any tty.
select_tools_prompt() {
  if [ -t 0 ]; then
    src=""
  elif [ -r /dev/tty ]; then
    src="/dev/tty"
  else
    return 1
  fi
  {
    printf '\nSage: which AI tools should I wire up?\n'
    i=1
    for k in $ALL; do printf '  %d) %s\n' "$i" "$(key_name "$k")"; i=$((i + 1)); done
    printf 'Enter numbers (e.g. 1,2,5), names, or "a" for all: '
  } >&2
  if [ -n "$src" ]; then
    IFS= read -r line <"$src" || return 1
  else
    IFS= read -r line || return 1
  fi
  parse_tools "$line"
  return 0
}

# --- choose tools: SAGE_TOOLS override, else checkbox picker, else prompt, else all ---
if [ -n "${SAGE_TOOLS:-}" ]; then
  parse_tools "$SAGE_TOOLS"
elif select_tools_tui; then
  :
elif select_tools_prompt; then
  :
else
  picked="$ALL"
fi

if [ -z "$(printf '%s' "$picked" | tr -d ' ')" ]; then
  echo "Sage: no tools selected. Nothing to do. (Tip: SAGE_TOOLS='all' to skip the picker.)"
  exit 0
fi

if [ -z "${SAGE_INSTALL_SOURCE:-}" ] && ! command -v git >/dev/null 2>&1; then
  echo "Sage: git is required but was not found. Install Git, then re-run."
  exit 1
fi

TMP="$(mktemp -d)"
if [ -n "${SAGE_INSTALL_SOURCE:-}" ]; then
  [ -d "$SAGE_INSTALL_SOURCE" ] || fail "SAGE_INSTALL_SOURCE is not a directory: $SAGE_INSTALL_SOURCE"
  printf 'Sage: loading local install source ...\n'
  SOURCE_ROOT=$(cd "$SAGE_INSTALL_SOURCE" && pwd -P) || fail "could not resolve SAGE_INSTALL_SOURCE."
  TARGET_ROOT=$(pwd -P)
  [ "$SOURCE_ROOT" != "$TARGET_ROOT" ] || fail "SAGE_INSTALL_SOURCE must not be the target repository."
  printf '  \342\234\223 source ready\n'
else
  printf 'Sage: fetching latest from qorstack/sage ...\n'
  SOURCE_ROOT="$TMP/source"
  if ! git clone --depth 1 --quiet "$REPO" "$SOURCE_ROOT" >/dev/null 2>&1; then
    echo "Sage: git clone failed. Check your network and try again."
    exit 1
  fi
  printf '  \342\234\223 fetched\n'
fi

# --- preflight every distribution input before the first target write ---
[ -f "$SOURCE_ROOT/agents/sage/AGENTS.md" ] || fail "source is missing agents/sage/AGENTS.md."
[ -d "$SOURCE_ROOT/agents/sage/commands" ] || fail "source is missing agents/sage/commands/."
[ -f "$SOURCE_ROOT/agents/sage/index.md" ] || fail "source is missing agents/sage/index.md."
[ -d "$SOURCE_ROOT/agents/sage/roles" ] || fail "source is missing agents/sage/roles/."
[ -f "$SOURCE_ROOT/agents/sage/install-manifest.txt" ] || fail "source is missing agents/sage/install-manifest.txt."
[ -f "$SOURCE_ROOT/agents/sage/adapter-manifest.txt" ] || fail "source is missing agents/sage/adapter-manifest.txt."

INSTALL_LIST="$TMP/.sage-install-files"
ADAPTER_LIST="$TMP/.sage-adapter-files"
: >"$INSTALL_LIST"
: >"$ADAPTER_LIST"

while IFS= read -r raw || [ -n "$raw" ]; do
  rel=$(printf '%s' "$raw" | tr -d '\r')
  case "$rel" in ""|\#*) continue ;; esac
  case "$rel" in
    /* | [A-Za-z]:* | *\\* | */ | . | .. | ./* | ../* | */./* | */../* | */. | */.. | *" "* | *"	"*)
      fail "unsafe install manifest path: $rel" ;;
  esac
  [ -f "$SOURCE_ROOT/$rel" ] || fail "install manifest source is missing: $rel"
  grep -Fqx "$rel" "$INSTALL_LIST" && fail "duplicate install manifest path: $rel"
  printf '%s\n' "$rel" >>"$INSTALL_LIST"
done <"$SOURCE_ROOT/agents/sage/install-manifest.txt"
[ -s "$INSTALL_LIST" ] || fail "install manifest contains no managed files."

while IFS= read -r raw || [ -n "$raw" ]; do
  base=$(printf '%s' "$raw" | tr -d '\r')
  case "$base" in ""|\#*) continue ;; esac
  case "$base" in *[!a-z0-9-]* | -* | *-) fail "unsafe adapter manifest basename: $base" ;; esac
  grep -Fqx "$base" "$ADAPTER_LIST" && fail "duplicate adapter manifest basename: $base"
  printf '%s\n' "$base" >>"$ADAPTER_LIST"
done <"$SOURCE_ROOT/agents/sage/adapter-manifest.txt"
[ -s "$ADAPTER_LIST" ] || fail "adapter manifest contains no managed basenames."

for k in $picked; do
  if [ "$k" = gemini ]; then
    [ -f "$SOURCE_ROOT/integrations/gemini.md" ] || fail "source is missing the Gemini adapter."
    [ -d "$SOURCE_ROOT/integrations/.gemini" ] || fail "source is missing the Gemini slash-command adapter."
  else
    src=$(key_src "$k")
    [ -d "$SOURCE_ROOT/integrations/$src" ] || fail "source is missing the $(key_name "$k") adapter."
  fi
done
printf '  \342\234\223 preflight passed\n'

# --- protocol + Sage-owned files. Exact manifest paths are reserved; all other
#     knowledge, role edits, flows, docs, adapters, and .sage-local.json survive. ---
printf 'Sage: writing protocol + commands ...\n'
mkdir -p agents/sage
cp "$SOURCE_ROOT/agents/sage/AGENTS.md" ./agents/sage/AGENTS.md
rm -f ./AGENTS.md
printf '  \342\234\223 agents/sage/AGENTS.md\n'
rm -rf agents/sage/commands                       # 100% Sage-owned; clears any old/renamed command
mkdir -p agents/sage
cp -r "$SOURCE_ROOT/agents/sage/commands" agents/sage/commands
printf '  \342\234\223 agents/sage/commands/ (%s commands)\n' "$(ls "$SOURCE_ROOT/agents/sage/commands"/*.md 2>/dev/null | grep -c . )"

managed_count=0
while IFS= read -r rel; do
  mkdir -p "$(dirname "./$rel")"
  cp "$SOURCE_ROOT/$rel" "./$rel"
  managed_count=$((managed_count + 1))
done <"$INSTALL_LIST"
printf '  \342\234\223 managed assets (%s files)\n' "$managed_count"

# migrate old layout: the style-guide used to sit in agents/sage/docs/ next to
# generated docs — remove only the old Sage assets there, never the folder itself.
rm -f agents/sage/docs/docs-style-template.md agents/sage/docs/sage-docs.css agents/sage/docs/sage-docs.js

# --- starter knowledge (seed only if absent: never clobber the team's edits) ---
[ -f agents/sage/index.md ] || cp "$SOURCE_ROOT/agents/sage/index.md" agents/sage/index.md
[ -d agents/sage/roles ] || cp -r "$SOURCE_ROOT/agents/sage/roles" agents/sage/roles

# --- install the selected tools' thin adapters ---
printf 'Sage: wiring up adapters ...\n'
installed=""
for k in $picked; do
  if [ "$k" = gemini ]; then
    cp "$SOURCE_ROOT/integrations/gemini.md" ./GEMINI.md
    mkdir -p .gemini
    cp -r "$SOURCE_ROOT/integrations/.gemini/commands" .gemini/
  else
    src=$(key_src "$k")
    mkdir -p "$src"
    while IFS= read -r base; do
      managed_path=$(adapter_managed_path "$k" "$base")
      [ -n "$managed_path" ] && rm -f "$managed_path"
    done <"$ADAPTER_LIST"
    cp -r "$SOURCE_ROOT/integrations/$src/." "$src/"
  fi
  printf '  \342\234\223 %s\n' "$(key_name "$k")"
  installed="$installed $(key_name "$k"),"
done

cat <<EOF

Sage installed. Adapters for:${installed%,}
Project DNA spec: agents/sage/flows/project-dna-flow.md

Commands now available:
  /sage                 run before a code change when explicitly invoked
  /sage-grill           resolve single-session fog + glossary/checkpoint decisions
  /sage-wayfinder       map multi-session fog as durable decision tickets
  /sage-flow            design + verify an implementation-ready flow before coding
  /sage-ticket          cut clear requirements into implementation tickets, then build them
  /sage-review          review a change for correctness + requirement conformance
  /sage-unit-test       write unit tests that match this repo's stack
  /sage-e2e-test        drive the app end-to-end (Playwright/Cypress/k6/…) and prove the flow
  /sage-security-review review a change for real, exploitable security holes
  /sage-docs            turn a spec/flow into a plain-Markdown doc in docs/
  /sage-learning        learn this repo's patterns + research best practices for its stack
  /sage-refactoring-code write/refactor readable code and schemas without speculative layers
  /sage-setting         change how /sage runs (mode: auto/ask, default steps)
  /sage-update          re-run this installer to update Sage

Next: run  /sage-learning  to seed knowledge from your codebase.
EOF
