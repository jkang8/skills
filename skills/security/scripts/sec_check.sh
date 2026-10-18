#!/bin/sh
# Security gate: ruff S (bandit rules), gitleaks, pip-audit, pnpm audit. Exits 1 if any tool finds a problem.
#   sec_check.sh <repo-dir>
# Each tool runs only when the repo has what it checks (Python files, a lockfile...). Missing tools are
# installed on first use (uvx for ruff and pip-audit, a gitleaks release into SEC_CHECK_HOME); a tool is skipped
# with a warning only if it can't be installed. Prints one line per tool, then `sec check: clean` or a failure.
#
# Tool versions are pinned, so a gate run is reproducible and a compromised "latest" can't slip in. gitleaks is
# downloaded only for the exact version below and only if its SHA-256 matches the one pinned here (taken from the
# release's own gitleaks_<version>_checksums.txt). To upgrade: change the version, copy the four checksums from
# that file, and run test_sec_check.sh. A gitleaks already on PATH is used as is: that is your own install.
GITLEAKS_VERSION=8.30.1
GITLEAKS_SHA256="darwin_arm64=b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5
darwin_x64=dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709
linux_arm64=e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080
linux_x64=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
RUFF_VERSION=0.17.1
PIP_AUDIT_VERSION=2.10.1
# For tests only: where releases come from, and replacement checksums to match a fake release.
GITLEAKS_BASE="${SEC_CHECK_GITLEAKS_BASE:-https://github.com/gitleaks/gitleaks/releases/download}"
GITLEAKS_SHA256="${SEC_CHECK_GITLEAKS_SHA256:-$GITLEAKS_SHA256}"
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

sha256_of() { if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

# Prints the path to gitleaks (the reason on stderr). Return 1: can't install (skip with a warning); 2: the
# download doesn't match its pinned checksum (a failure: it is never run).
gitleaks_bin() {
  command -v gitleaks 2>/dev/null && return
  bin="$TOOLS_DIR/gitleaks-$GITLEAKS_VERSION/gitleaks"
  [ -x "$bin" ] && { echo "$bin"; return; }
  os="$(uname -s | tr 'A-Z' 'a-z')"; arch="$(uname -m)"; [ "$arch" = aarch64 ] && arch=arm64; [ "$arch" = x86_64 ] && arch=x64
  want="$(printf '%s\n' "$GITLEAKS_SHA256" | sed -n "s/^${os}_${arch}=//p")"
  [ -n "$want" ] || { echo "no pinned checksum for ${os}_${arch}" >&2; return 1; }
  tgz="$OUT/gitleaks.tar.gz"
  curl -fsSL "$GITLEAKS_BASE/v$GITLEAKS_VERSION/gitleaks_${GITLEAKS_VERSION}_${os}_${arch}.tar.gz" -o "$tgz" 2>/dev/null \
    || { echo "download of gitleaks $GITLEAKS_VERSION failed" >&2; return 1; }
  [ "$(sha256_of "$tgz")" = "$want" ] || { echo "gitleaks $GITLEAKS_VERSION download does not match its pinned SHA-256" >&2; return 2; }
  mkdir -p "$(dirname "$bin")" && tar -xzf "$tgz" -C "$(dirname "$bin")" gitleaks 2>/dev/null && [ -x "$bin" ] \
    || { echo "gitleaks archive did not unpack" >&2; return 1; }
  echo "$bin"
}

# 1. ruff S: bandit rules on Python. Asserts are fine in tests. S603/S607 flag every list-args subprocess call,
# which is the safe form the skill asks for; S602 (shell=True) still fails.
if has '*.py'; then
  uvx_ "ruff@$RUFF_VERSION" check --no-cache --select S --ignore S603 --ignore S607 --extend-per-file-ignores '**/tests/**:S101' --extend-per-file-ignores '**/test_*.py:S101' \
    --output-format concise "$REPO" > "$OUT/ruff" 2>&1; rc=$?
  case $rc in 0) ok "ruff S" ;; 1) bad "ruff S" "$OUT/ruff" ;; *) skip "ruff S" "ruff couldn't run: $(tail -1 "$OUT/ruff")" ;; esac
else ok "ruff S (no Python files)"; fi

# 2. gitleaks: secrets in the working tree.
GL="$(gitleaks_bin 2> "$OUT/gl.why")"; glrc=$?
case $glrc in
  0) "$GL" dir "$REPO" --no-banner --redact --exit-code 1 > "$OUT/gitleaks" 2>&1; rc=$?
     case $rc in 0) ok "gitleaks" ;; 1) bad "gitleaks" "$OUT/gitleaks" ;; *) skip "gitleaks" "exit $rc: $(tail -1 "$OUT/gitleaks")" ;; esac ;;
  2) bad "gitleaks" "$OUT/gl.why" ;;
  *) skip "gitleaks" "$(cat "$OUT/gl.why")" ;;
esac

# 3. pip-audit: Python dependencies from uv.lock or requirements.txt.
req=""
if lock="$(first uv.lock)" && [ -n "$lock" ] && command -v uv >/dev/null; then
  (cd "$(dirname "$lock")" && uv export -q --frozen --format requirements-txt --no-hashes --no-emit-project) > "$OUT/req.txt" 2>/dev/null && req="$OUT/req.txt"
elif r="$(first requirements.txt)" && [ -n "$r" ]; then req="$r"; fi
if [ -n "$req" ]; then
  uvx_ "pip-audit@$PIP_AUDIT_VERSION" -r "$req" --progress-spinner off > "$OUT/pip" 2>&1; rc=$?
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
