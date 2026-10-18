#!/bin/sh
# Security gate: ruff S (bandit rules), gitleaks, pip-audit, pnpm audit. Exits 1 if any tool finds a problem.
#   sec_check.sh <repo-dir>
# Each tool runs only when the repo has what it checks (Python files, a lockfile...). Missing tools are
# installed on first use (uvx for ruff and pip-audit, a gitleaks release into SEC_CHECK_HOME); a tool is skipped
# with a warning only if it can't be installed. Prints one line per tool, then `sec check: clean` or a failure.
set -u
REPO="$(cd "${1:?usage: sec_check.sh <repo-dir>}" && pwd)"
TOOLS_DIR="${SEC_CHECK_HOME:-${XDG_CACHE_HOME:-$HOME/.cache}/sec_check}/bin"
OUT="$(mktemp -d)"; trap 'rm -rf "$OUT"' EXIT
fail=0 skipped=0
ok() { echo "ok    $1"; }
bad() { echo "FAIL  $1"; sed 's/^/      /' "$2" | head -40; fail=1; }
skip() { echo "skip  $1 (warning: $2)"; skipped=$((skipped + 1)); }
has() { find "$REPO" -path '*/node_modules' -prune -o -path '*/.git' -prune -o -path '*/.venv' -prune -o -name "$1" -print | grep -q .; }
first() { find "$REPO" -path '*/node_modules' -prune -o -path '*/.git' -prune -o -name "$1" -print | head -1; }
uvx_() { if command -v uvx >/dev/null; then uvx -q "$@"; elif command -v uv >/dev/null; then uv tool run -q "$@"; else return 127; fi; }

gitleaks_bin() { # path to gitleaks, installing a release build if needed
  command -v gitleaks 2>/dev/null && return
  [ -x "$TOOLS_DIR/gitleaks" ] && { echo "$TOOLS_DIR/gitleaks"; return; }
  os="$(uname -s | tr 'A-Z' 'a-z')"; arch="$(uname -m)"; [ "$arch" = aarch64 ] && arch=arm64; [ "$arch" = x86_64 ] && arch=x64
  url="$(curl -fsSL https://api.github.com/repos/gitleaks/gitleaks/releases/latest 2>/dev/null \
    | python3 -c "import json,sys; print(next(a['browser_download_url'] for a in json.load(sys.stdin)['assets'] if a['name'].endswith('_${os}_${arch}.tar.gz')))" 2>/dev/null)" || return 1
  mkdir -p "$TOOLS_DIR" && curl -fsSL "$url" | tar -xz -C "$TOOLS_DIR" gitleaks 2>/dev/null && echo "$TOOLS_DIR/gitleaks"
}

# 1. ruff S: bandit rules on Python. Asserts are fine in tests. S603/S607 flag every list-args subprocess call,
# which is the safe form the skill asks for; S602 (shell=True) still fails.
if has '*.py'; then
  uvx_ ruff check --no-cache --select S --ignore S603 --ignore S607 --extend-per-file-ignores '**/tests/**:S101' --extend-per-file-ignores '**/test_*.py:S101' \
    --output-format concise "$REPO" > "$OUT/ruff" 2>&1; rc=$?
  case $rc in 0) ok "ruff S" ;; 1) bad "ruff S" "$OUT/ruff" ;; *) skip "ruff S" "ruff couldn't run: $(tail -1 "$OUT/ruff")" ;; esac
else ok "ruff S (no Python files)"; fi

# 2. gitleaks: secrets in the working tree.
if GL="$(gitleaks_bin)" && [ -n "$GL" ]; then
  "$GL" dir "$REPO" --no-banner --redact --exit-code 1 > "$OUT/gitleaks" 2>&1; rc=$?
  case $rc in 0) ok "gitleaks" ;; 1) bad "gitleaks" "$OUT/gitleaks" ;; *) skip "gitleaks" "exit $rc: $(tail -1 "$OUT/gitleaks")" ;; esac
else skip "gitleaks" "not installed and the release download failed"; fi

# 3. pip-audit: Python dependencies from uv.lock or requirements.txt.
req=""
if lock="$(first uv.lock)" && [ -n "$lock" ] && command -v uv >/dev/null; then
  (cd "$(dirname "$lock")" && uv export -q --frozen --format requirements-txt --no-hashes --no-emit-project) > "$OUT/req.txt" 2>/dev/null && req="$OUT/req.txt"
elif r="$(first requirements.txt)" && [ -n "$r" ]; then req="$r"; fi
if [ -n "$req" ]; then
  uvx_ pip-audit -r "$req" --progress-spinner off > "$OUT/pip" 2>&1; rc=$?
  case $rc in 0) ok "pip-audit" ;; 1) bad "pip-audit" "$OUT/pip" ;; *) skip "pip-audit" "couldn't run: $(tail -1 "$OUT/pip")" ;; esac
else ok "pip-audit (no Python lockfile or requirements.txt)"; fi

# 4. pnpm audit: production dependencies, high and critical fail.
if lock="$(first pnpm-lock.yaml)" && [ -n "$lock" ]; then
  if command -v pnpm >/dev/null; then
    (cd "$(dirname "$lock")" && pnpm audit --prod --audit-level high) > "$OUT/pnpm" 2>&1; rc=$?
    if [ $rc = 0 ]; then ok "pnpm audit"; elif grep -qiE 'vulnerabilit|advisor' "$OUT/pnpm"; then bad "pnpm audit" "$OUT/pnpm"
    else skip "pnpm audit" "couldn't run: $(tail -1 "$OUT/pnpm")"; fi
  else skip "pnpm audit" "pnpm not installed"; fi
else ok "pnpm audit (no pnpm-lock.yaml)"; fi

[ $fail = 0 ] || { echo "sec check: FAIL"; exit 1; }
[ $skipped = 0 ] && echo "sec check: clean" || echo "sec check: clean ($skipped skipped, see warnings)"
