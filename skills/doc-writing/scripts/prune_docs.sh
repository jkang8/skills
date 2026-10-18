#!/bin/sh
# Doc pruning: one deletion-only PR that makes a repo's docs shorter. Never merges or pushes main.
#   prune_docs.sh <repo-checkout>      (the edit is made in a fresh worktree of origin/main)
# Runs prune-docs.md headless (opus, file tools only). Then this script commits, refuses unless the diff
# touches only existing .md files and is net-negative (additions at most a quarter of deletions), checks
# that doc_check.py got no worse, runs the repo's gate, and opens the PR. Prints one summary line.
# Env: PRUNE_GATE (default `make gate`), PRUNE_TEXT_CHECK (optional command run on the PR title and body
# files, e.g. a privacy check), PRUNE_PROTECT (regex of paths it may never touch), PRUNE_HOME (runs and
# worktrees; outside the repo), PRUNE_TIME_LIMIT (seconds), PRUNE_BASE, PRUNE_DRY_RUN=1 (no push, no PR).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "${1:?usage: prune_docs.sh <repo-checkout>}" && pwd)"
NAME="$(basename "$REPO")"
GATE="${PRUNE_GATE:-make gate}"
PROTECT="${PRUNE_PROTECT:-(^|/)(\.github|scripts)/}"
LIMIT="${PRUNE_TIME_LIMIT:-1500}"
BASE="${PRUNE_BASE:-origin/main}"
HOME_DIR="${PRUNE_HOME:-${XDG_STATE_HOME:-$HOME/.local/state}/prune-docs/$NAME}"
RUNS="$HOME_DIR/runs" WTS="$HOME_DIR/worktrees"
say() { echo "doc pruner ($NAME): $*"; }
json() { python3 -c 'import json,sys
try: v = json.load(open(sys.argv[1])).get(sys.argv[2], "")
except Exception: v = ""
print(v)' "$1" "$2"; }
hits() { python3 "$HERE/doc_check.py" "$1" | grep -cv 'clean$'; }

mkdir -p "$RUNS" "$WTS"
mkdir "$RUNS/.lock" 2>/dev/null || { say "another run is active, skipped"; exit 0; }
STAMP="$(date +%Y%m%d-%H%M%S)"; RUN="$RUNS/$STAMP"; BR="prune/$STAMP"; WT="$WTS/prune-$STAMP"
cleanup() {
  [ -d "$WT" ] && git -C "$REPO" worktree remove --force "$WT" 2>/dev/null
  git -C "$REPO" branch -D "$BR" >/dev/null 2>&1
  rmdir "$RUNS/.lock"
}
trap cleanup EXIT
trap 'exit 1' INT TERM
mkdir -p "$RUN"
ls -dt "$RUNS"/2* 2>/dev/null | tail -n +13 | while read -r old; do rm -rf "$old"; done  # keep the last 12 runs

if [ "${PRUNE_DRY_RUN:-}" != 1 ]; then
  open="$(cd "$REPO" && gh pr list --state open --json headRefName --jq '[.[] | select(.headRefName | startswith("prune/"))] | length')" \
    || { say "can't list PRs (gh), skipped"; exit 1; }
  [ "$open" = 0 ] || { say "a pruning PR is already open, skipped"; exit 0; }
  git -C "$REPO" fetch -q origin || { say "fetch failed"; exit 1; }
fi
git -C "$REPO" worktree add -q -b "$BR" "$WT" "$BASE" || { say "worktree failed"; exit 1; }

python3 "$HERE/doc_check.py" "$WT" > "$RUN/doc_check_before.txt"; before="$(hits "$WT")"
# The prompt names the run folder literally: the agent has file tools only and can't read env vars.
sed "s|\$PRUNE_RUN|$RUN|g" "$HERE/prune-docs.md" > "$RUN/prompt.md"
(cd "$WT" && perl -e 'alarm shift; exec @ARGV' "$LIMIT" \
  claude -p --model opus --output-format json --no-session-persistence --restricted --tools "Read,Edit,Write,Glob,Grep" \
    --permission-mode acceptEdits --add-dir "$RUN" < "$RUN/prompt.md" > "$RUN/claude.json" 2> "$RUN/claude.err") 2>/dev/null
# (prompt on stdin: --add-dir takes several values and would swallow a prompt argument)
rc=$?
status="$(json "$RUN/result.json" status)"
[ "$rc" = 142 ] && { say "no PR: timed out after ${LIMIT}s [logs: $RUN]"; exit 1; }
[ "$status" = nothing ] && { say "no PR: $(json "$RUN/result.json" reason | head -c 300)"; exit 0; }
[ "$status" = ready ] || { say "no PR: run ended without a result (exit $rc) [logs: $RUN]"; exit 1; }

# Check the edit ourselves: existing .md files only, nothing protected, net-negative, additions <= deletions/4.
git -C "$WT" add -A
bad="$(git -C "$WT" diff --cached --name-status "$BASE" | grep -vE '^M[[:space:]].*\.md$'; git -C "$WT" diff --cached --name-only "$BASE" | grep -E "$PROTECT")"
[ -z "$bad" ] || { say "no PR: touched more than existing, unprotected .md files: $(echo $bad | head -c 200) [logs: $RUN]"; exit 1; }
set -- $(git -C "$WT" diff --cached --numstat "$BASE" | awk '{a+=$1; d+=$2} END {print a+0, d+0}'); added=$1; removed=$2
[ "$removed" -gt "$added" ] && [ $((added * 4)) -le "$removed" ] \
  || { say "no PR: +$added -$removed lines is not deletion-only enough [logs: $RUN]"; exit 1; }
python3 "$HERE/doc_check.py" "$WT" > "$RUN/doc_check_after.txt"; after="$(hits "$WT")"
[ "$after" -le "$before" ] || { say "no PR: doc_check got worse ($before -> $after hits) [logs: $RUN]"; exit 1; }
title="$(json "$RUN/result.json" title)"; [ -n "$title" ] || title="Prune docs"
git -C "$WT" commit -q -m "$title" -m "Deletion-only doc pruning by prune_docs.sh: +$added -$removed lines." \
  || { say "commit failed [logs: $RUN]"; exit 1; }
(cd "$WT" && sh -c "$GATE") > "$RUN/gate.txt" 2>&1 || { say "no PR: the gate fails [logs: $RUN]"; exit 1; }

used="$(python3 -c 'import json,sys; print(", ".join(json.load(open(sys.argv[1])).get("modelUsage", {})))' "$RUN/claude.json" 2>/dev/null)"
{
  cat "$RUN/pr_body.md" 2>/dev/null
  printf '\n## Size\n+%s -%s lines (net %s). doc_check hits: %s -> %s.\n\n## Gate\n```\n%s\n```\n\n## Produced by\n' \
    "$added" "$removed" "$((added - removed))" "$before" "$after" "$(tail -20 "$RUN/gate.txt")"
  echo "- \`claude -p --model opus\` (effort: default), file tools only. Models used: ${used:-unknown}"
  printf '\n🤖 Generated with [Claude Code](https://claude.com/claude-code) via prune_docs.sh\n'
} > "$RUN/pr_body_final.md"
printf '%s\n' "$title" > "$RUN/pr_title.txt"
if [ -n "${PRUNE_TEXT_CHECK:-}" ]; then
  sh -c "$PRUNE_TEXT_CHECK \"\$@\"" _ "$RUN/pr_title.txt" "$RUN/pr_body_final.md" > "$RUN/text_check.txt" 2>&1 \
    || { say "no PR: the PR text failed PRUNE_TEXT_CHECK [logs: $RUN]"; exit 1; }
fi

[ "${PRUNE_DRY_RUN:-}" = 1 ] && { say "dry run, would open: $title (+$added -$removed) [body: $RUN/pr_body_final.md]"; exit 0; }
git -C "$WT" push -q -u origin "$BR" 2>"$RUN/push.err" || { say "push failed [logs: $RUN]"; exit 1; }
url="$(cd "$WT" && gh pr create --base "${BASE#origin/}" --head "$BR" --title "$title" --body-file "$RUN/pr_body_final.md")" \
  || { say "gh pr create failed [logs: $RUN]"; exit 1; }
say "opened $url"
