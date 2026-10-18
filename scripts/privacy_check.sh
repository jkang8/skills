#!/bin/sh
# Privacy gate: fails if anything that would be committed contains personal data. Run before every commit.
#   scripts/privacy_check.sh
# Personal terms, the denylist and the guard's location live in a local config, never in the repo:
# $PRIVACY_CONFIG, or .privacy.local at the repo root (gitignored). See README "Privacy gate".
set -eu
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${PRIVACY_CONFIG:-$REPO/.privacy.local}"
[ -f "$CONFIG" ] || { echo "privacy check: no config at $CONFIG (fails closed)"; exit 2; }
. "$CONFIG"
: "${PRIVACY_PYTHON:?}" "${PRIVACY_GUARD:?}" "${PRIVACY_DENYLIST:?}" "${PRIVACY_TERMS:?}"
[ -f "$PRIVACY_DENYLIST" ] || { echo "privacy check: denylist missing (fails closed)"; exit 2; }

# Generic leaks; bracketed so this file doesn't match itself.
GENERIC='/User[s]/|/home/[a-z]|@gmai[l]|~/\.herme[s]|\$HOME/\.herme[s]'

# Scan a copy of everything git would commit (tracked, staged and untracked-not-ignored),
# with the exact allowlisted lines removed.
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
cd "$REPO"
git ls-files --cached --others --exclude-standard -z | xargs -0 -I{} sh -c '[ -e "$1" ] || [ -L "$1" ] || exit 0; mkdir -p "$2/$(dirname "$1")"; cp -P "$1" "$2/$1"' _ {} "$WORK"
printf '%s\n' "${PRIVACY_ALLOW:-}" | while IFS= read -r rule; do
  [ -n "$rule" ] || continue
  f="${rule%%:*}"; line="${rule#*:}"
  if [ -f "$WORK/$f" ]; then grep -vxF "$line" "$WORK/$f" > "$WORK/.tmp" || true; mv "$WORK/.tmp" "$WORK/$f"; fi
done

fail=0
echo "== privacy guard (denylist, emails, secrets)"
git -C "$WORK" init -q && git -C "$WORK" add -A
PYTHONPATH="${PRIVACY_GUARD_PYTHONPATH:-}" MEMORY_STEM_DENYLIST="$PRIVACY_DENYLIST" \
  "$PRIVACY_PYTHON" "$PRIVACY_GUARD" "$WORK" || fail=1

echo "== term grep (contents, file names, commit messages)"
hits="$( (cd "$WORK" && grep -rniE --exclude-dir=.git "$GENERIC|$PRIVACY_TERMS" . || true)
  (cd "$WORK" && git ls-files | grep -iE "$GENERIC|$PRIVACY_TERMS" | sed 's/^/file name: /' || true)
  (git log --format=%B 2>/dev/null | grep -iE "$GENERIC|$PRIVACY_TERMS" | sed 's/^/commit message: /' || true) )"
if [ -n "$hits" ]; then echo "$hits"; fail=1; else echo "term grep: clean"; fi

[ "$fail" -eq 0 ] && echo "PRIVACY CHECK PASS" || { echo "PRIVACY CHECK FAIL"; exit 1; }
