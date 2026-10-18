#!/bin/sh
# Privacy gate: fails if anything that would be committed contains personal data. Run before every commit.
#   scripts/privacy_check.sh
# Personal terms and the denylist's location live in a local config, never in the repo:
# $PRIVACY_CONFIG, or .privacy.local at the repo root (gitignored). See README "Privacy gate".
# Self-contained: scripts/privacy_scan.py (stdlib) does the email, secret and denylist checks.
set -eu
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${PRIVACY_CONFIG:-$REPO/.privacy.local}"
[ -f "$CONFIG" ] || { echo "privacy check: no config at $CONFIG (fails closed)"; exit 2; }
. "$CONFIG"
: "${PRIVACY_DENYLIST:?}" "${PRIVACY_TERMS:?}"
PY="${PRIVACY_PYTHON:-python3}"
[ -f "$PRIVACY_DENYLIST" ] || { echo "privacy check: denylist missing (fails closed)"; exit 2; }

# Generic leaks; bracketed so this file doesn't match itself.
GENERIC='/User[s]/|/home/[a-z]|@gmai[l]|~/\.herme[s]|\$HOME/\.herme[s]'

# Scan a copy of everything git would commit (tracked, staged and untracked-not-ignored),
# with the exact allowlisted lines removed.
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
cd "$REPO"
git ls-files --cached --others --exclude-standard -z | xargs -0 -I{} sh -c '[ -e "$1" ] || [ -L "$1" ] || exit 0; mkdir -p "$2/$(dirname "$1")"; cp -P "$1" "$2/$1"' _ {} "$WORK"
# Git hooks export GIT_DIR/GIT_INDEX_FILE; past this point every git call must target the temp copy
# or the real repo explicitly, never whatever the hook environment points at.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_COMMON_DIR GIT_OBJECT_DIRECTORY
printf '%s\n' "${PRIVACY_ALLOW:-}" | while IFS= read -r rule; do
  [ -n "$rule" ] || continue
  f="${rule%%:*}"; line="${rule#*:}"
  if [ -f "$WORK/$f" ]; then grep -vxF "$line" "$WORK/$f" > "$WORK/.tmp" || true; mv "$WORK/.tmp" "$WORK/$f"; fi
done

# GitHub's generated commit text names the branch's owner, which is public in the remote URL. Only that exact merge line and the
# owner's noreply Co-authored-by trailer, for the owner read from the remote, are skipped in commit messages; the owner stays denied everywhere else.
OWNER="$(git -C "$REPO" remote get-url origin 2>/dev/null | sed -nE 's#^(https://github\.com/|git@github\.com:)([A-Za-z0-9-]+)/.*#\2#p')"
MERGE_LINE="Merge pull request #[0-9]+ from ${OWNER:-no-owner}/[A-Za-z0-9._/-]+"
# Likewise the whole Co-authored-by line when its address is the owner's public noreply one: the name beside it is
# the same identity as every commit's author field. A trailer with any other address is still scanned.
TRAILER_LINE="Co-authored-by: [^<]*<([0-9]+\\+)?${OWNER:-no-owner}@users\\.noreply\\.github\\.com>"

fail=0
echo "== privacy scan (denylist, emails, secrets)"
git -C "$WORK" init -q && git -C "$WORK" add -A
"$PY" "$REPO/scripts/privacy_scan.py" "$WORK" "$PRIVACY_DENYLIST" || fail=1

echo "== term grep (contents, file names, commit messages)"
hits="$( (cd "$WORK" && grep -rniE --exclude-dir=.git "$GENERIC|$PRIVACY_TERMS" . || true)
  (cd "$WORK" && git ls-files | grep -iE "$GENERIC|$PRIVACY_TERMS" | sed 's/^/file name: /' || true)
  (git -C "$REPO" log --format=%B 2>/dev/null | grep -vxE "$MERGE_LINE" | grep -vxiE "$TRAILER_LINE" | grep -iE "$GENERIC|$PRIVACY_TERMS" | sed 's/^/commit message: /' || true) )"
if [ -n "$hits" ]; then echo "$hits"; fail=1; else echo "term grep: clean"; fi

[ "$fail" -eq 0 ] && echo "PRIVACY CHECK PASS" || { echo "PRIVACY CHECK FAIL"; exit 1; }
