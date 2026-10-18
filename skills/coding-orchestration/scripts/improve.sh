#!/bin/sh
# Improve loop: one gated, foundational change per run, as a PR a human reviews and merges. Never merges or pushes main.
#   improve.sh <repo-checkout> [signals-data-path]      (the change is made in a fresh worktree of origin/main)
# The repo provides `make gate`, an executable `scripts/signals` (prints weak spots; gets signals-data-path as $1
# when given) and `IMPROVE.md` (what a good fix is here, what's off-limits).
# Flow: worktree -> haiku summarizes the signals -> opus builds one change from improve.md -> gate. If opus fails
# the gate twice on its change, one retry with fable; if it quit early or skipped the test, one retry with opus
# --effort high. A passing change becomes a PR with model and effort in the body. Prints one summary line.
# Env: IMPROVE_GATE (default `make gate`), IMPROVE_TEXT_CHECK (optional command run on the PR title, body and commit
# messages, e.g. a privacy check), IMPROVE_HOME (runs and worktrees; outside the repo), IMPROVE_TIME_LIMIT (seconds
# per attempt), IMPROVE_BASE, IMPROVE_DRY_RUN=1 (no gh, no push, no PR).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "${1:?usage: improve.sh <repo-checkout> [signals-data-path]}" && pwd)"
DATA="${2:-}"
NAME="$(basename "$REPO")"
GATE="${IMPROVE_GATE:-make gate}"
LIMIT="${IMPROVE_TIME_LIMIT:-1500}"  # per attempt: two attempts fit a 1-hour cron timeout
BASE="${IMPROVE_BASE:-origin/main}"
HOME_DIR="${IMPROVE_HOME:-${XDG_STATE_HOME:-$HOME/.local/state}/improve/$NAME}"
RUNS="$HOME_DIR/runs" WTS="$HOME_DIR/worktrees"
DRY="${IMPROVE_DRY_RUN:-}"
say() { echo "improver ($NAME): $*"; }
json() { python3 -c 'import json,sys
try: v = json.load(open(sys.argv[1])).get(sys.argv[2], "")
except Exception: v = ""
print(v)' "$1" "$2"; }

mkdir -p "$RUNS" "$WTS"
mkdir "$RUNS/.lock" 2>/dev/null || { say "another run is active, skipped"; exit 0; }
STAMP="$(date +%Y%m%d-%H%M%S)"; RUN="$RUNS/$STAMP"; BR="improve/$STAMP"; WT="$WTS/improve-$STAMP"
cleanup() {
  [ -d "$WT" ] && git -C "$REPO" worktree remove --force "$WT" 2>/dev/null
  git -C "$REPO" branch -D "$BR" >/dev/null 2>&1
  rmdir "$RUNS/.lock"
}
trap cleanup EXIT
trap 'exit 1' INT TERM
mkdir -p "$RUN"
ls -dt "$RUNS"/2* 2>/dev/null | tail -n +13 | while read -r old; do rm -rf "$old"; done  # keep the last 12 runs

if [ "$DRY" = 1 ]; then echo "[]" > "$RUN/issues.json"; echo "[]" > "$RUN/open_prs.json"
else
  open="$(cd "$REPO" && gh pr list --state open --json headRefName,labels \
    --jq '[.[] | select((.headRefName | startswith("improve/")) or any(.labels[]; .name == "improver"))] | length')" \
    || { say "can't list PRs (gh), skipped"; exit 1; }
  [ "$open" = 0 ] || { say "an improver PR is already open, skipped"; exit 0; }
  git -C "$REPO" fetch -q origin || { say "fetch failed"; exit 1; }
  (cd "$REPO" && gh issue list --label improvement --state open --limit 20 --json number,title,body) > "$RUN/issues.json" 2>/dev/null \
    || echo "[]" > "$RUN/issues.json"
  (cd "$REPO" && gh pr list --state open --json number,title,body) > "$RUN/open_prs.json" 2>/dev/null || echo "[]" > "$RUN/open_prs.json"
fi
git -C "$REPO" worktree add -q -b "$BR" "$WT" "$BASE" || { say "worktree failed"; exit 1; }
[ -x "$WT/scripts/signals" ] && [ -f "$WT/IMPROVE.md" ] || { say "$BASE has no scripts/signals or IMPROVE.md, skipped"; exit 1; }

# Signals: the repo's script runs here, then haiku (a cheap, read-only summarizing job) condenses it. The builder
# only sees the summary, which marks private items so they're described generically.
(cd "$WT" && ./scripts/signals ${DATA:+"$DATA"}) > "$RUN/signals_raw.txt" 2>&1 || say "scripts/signals exited non-zero; using its output anyway"
# (prompts go on stdin: --tools and --add-dir take several values and would swallow a prompt argument)
echo "Summarize signals_raw.txt (a repo's weak spots: failures, misses, metrics) for an engineer choosing one improvement. List each distinct problem with counts, then the patterns across them. Mark any item that quotes private data (names, emails, user text, personal records) as PRIVATE and describe it generically. Under 60 lines. Output the summary only." \
  | (cd "$RUN" && perl -e 'alarm shift; exec @ARGV' 600 claude -p --model haiku --no-session-persistence --restricted --tools "Read" \
    > "$RUN/signals.md" 2> "$RUN/signals.err")
[ -s "$RUN/signals.md" ] || { say "no PR: the signals summary failed [logs: $RUN]"; exit 1; }

TOOLS="Bash,Read,Edit,Write,Glob,Grep"
DENY="Bash(git push*) Bash(gh *)"
attempt() { # $1 = attempt number, rest = model flags
  n=$1; shift
  A="$RUN/a$n"; mkdir -p "$A"; cp "$RUN/signals.md" "$RUN/issues.json" "$RUN/open_prs.json" "$A/"
  [ -d "$RUN/previous" ] && cp -R "$RUN/previous" "$A/"
  sed "s|IMPROVE_RUN_DIR|$A|g" "$HERE/improve.md" > "$A/prompt.md"
  [ -f "$A/previous/retry.md" ] && { echo; cat "$A/previous/retry.md"; } >> "$A/prompt.md"
  echo "$*" > "$A/flags"
  (cd "$WT" && perl -e 'alarm shift; exec @ARGV' "$LIMIT" \
    claude -p --output-format json --no-session-persistence --restricted --tools "$TOOLS" \
      --permission-mode acceptEdits --allowedTools "$TOOLS" --disallowedTools "$DENY" \
      --add-dir "$A" "$@" < "$A/prompt.md" > "$A/claude.json" 2> "$A/claude.err")
  echo $? > "$A/exit"
}

verdict() { # $1 = attempt number -> ready | nothing | gate_failed | quit_early: <why> | rejected: <why>
  A="$RUN/a$1"
  case "$(json "$A/result.json" status)" in
    nothing) echo nothing; return ;;
    gate_failed) [ -s "$A/gate_1.txt" ] && [ -s "$A/gate_2.txt" ] && { echo gate_failed; return; }
                 echo "quit_early: said the gate failed twice without two gate runs"; return ;;
    ready) ;;
    *) [ "$(cat "$A/exit")" = 142 ] && { echo "quit_early: timed out after ${LIMIT}s"; return; }
       echo "quit_early: $(json "$A/result.json" reason | head -c 300) (exit $(cat "$A/exit"))"; return ;;
  esac
  # Don't take its word for it.
  [ -z "$(git -C "$WT" status --porcelain)" ] || { echo "quit_early: uncommitted changes"; return; }
  changed="$(git -C "$WT" diff --name-only "$BASE"...HEAD)"
  [ -n "$changed" ] || { echo "quit_early: ready but no commit"; return; }
  echo "$changed" | grep -qE '^(scripts/|\.github/|Makefile$|IMPROVE\.md$)' && { echo "rejected: edited the gate, signals or CI"; return; }
  echo "$changed" | grep -qE '(^|/)tests?/|(^|/)test_[^/]*$|_test\.[a-z]+$|\.test\.[a-z]+$' || { echo "quit_early: no test added or changed"; return; }
  [ -s "$A/pr_body.md" ] && [ -n "$(json "$A/result.json" title)" ] || { echo "quit_early: no PR title or body"; return; }
  (cd "$WT" && sh -c "$GATE") > "$A/gate_check.txt" 2>&1 || { echo "quit_early: claimed ready but the gate fails"; return; }
  echo ready
}

reset_for_retry() { # keep what attempt $1 did as context for the next one, then start clean
  A="$RUN/a$1"; mkdir -p "$RUN/previous"
  git -C "$WT" add -A && git -C "$WT" diff --cached "$BASE" > "$RUN/previous/attempt.diff"
  cp "$A"/gate_*.txt "$A/result.json" "$RUN/previous/" 2>/dev/null
  git -C "$WT" reset -q --hard "$BASE" && git -C "$WT" clean -qfdx
  printf '%s\n' "## Previous attempt" "" "$2" "" \
    "Its diff is \`previous/attempt.diff\` in your run folder; its result and gate output are in \`previous/\`." \
    "The worktree has been reset to $BASE. Build on what it learned; don't repeat its mistake." > "$RUN/previous/retry.md"
}

attempt 1 --model opus; v="$(verdict 1)"; n=1; why=""
case "$v" in
  gate_failed)
    why="opus failed the gate twice on the same change; retried with fable"
    reset_for_retry 1 "An attempt with opus failed the gate twice on the same change, with the gate output in hand. Diagnose why before changing anything; pick a different change only if this one can't pass."
    attempt 2 --model fable; v="$(verdict 2)"; n=2 ;;
  quit_early*)
    why="opus ${v#quit_early: }; retried with --effort high"
    reset_for_retry 1 "An attempt stopped short: ${v#quit_early: }. Do every step: a failing test first, the implementation, two gate runs at most, the result file."
    attempt 2 --model opus --effort high; v="$(verdict 2)"; n=2 ;;
esac
A="$RUN/a$n"
[ "$v" = ready ] || { say "no PR ($v) $(json "$A/result.json" reason | head -c 300) [logs: $RUN]"; exit 0; }

used="$(python3 -c 'import json,sys; print(", ".join(json.load(open(sys.argv[1])).get("modelUsage", {})))' "$A/claude.json" 2>/dev/null)"
effort="$(sed -n 's/.*--effort \([a-z]*\).*/\1/p' "$A/flags")"
{
  cat "$A/pr_body.md"
  printf '\n## Gate\n```\n%s\n```\n\n## Produced by\n' "$(tail -30 "$A/gate_check.txt")"
  echo "- \`claude -p $(cat "$A/flags")\` (effort: ${effort:-default}), attempt $n of 2${why:+: $why}"
  echo "- Models used: ${used:-unknown}; signals summarized by haiku"
  printf '\n🤖 Generated with [Claude Code](https://claude.com/claude-code) via improve.sh\n'
} > "$RUN/pr_body_final.md"
json "$A/result.json" title > "$RUN/pr_title.txt"
git -C "$WT" log "$BASE"..HEAD --format=%B > "$RUN/commits.txt"
if [ -n "${IMPROVE_TEXT_CHECK:-}" ]; then
  sh -c "$IMPROVE_TEXT_CHECK \"\$@\"" _ "$RUN/pr_title.txt" "$RUN/pr_body_final.md" "$RUN/commits.txt" > "$RUN/text_check.txt" 2>&1 \
    || { say "no PR: the PR text or commit messages failed IMPROVE_TEXT_CHECK [logs: $RUN]"; exit 1; }
fi

[ "$DRY" = 1 ] && { say "dry run, would open: $(cat "$RUN/pr_title.txt") [body: $RUN/pr_body_final.md]"; exit 0; }
(cd "$REPO" && gh label create improver --color 5319e7 --description "Opened by improve.sh" >/dev/null 2>&1)
git -C "$WT" push -q -u origin "$BR" 2>"$RUN/push.err" || { say "push failed [logs: $RUN]"; exit 1; }
url="$(cd "$WT" && gh pr create --base "${BASE#origin/}" --head "$BR" --label improver \
  --title "$(cat "$RUN/pr_title.txt")" --body-file "$RUN/pr_body_final.md")" || { say "gh pr create failed [logs: $RUN]"; exit 1; }
say "opened $url"
