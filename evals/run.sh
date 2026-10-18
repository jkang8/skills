#!/bin/sh
# Run a skill's eval tasks headless, without and with the skill, and print a comparison table.
#   evals/run.sh <skill> [-n runs-per-arm] [-m agent-model] [-j judge-model]
# Both arms run with all skills disabled; the "with" arm gets SKILL.md + references/ appended to the
# system prompt. Work happens in a temp dir outside any repo, so no CLAUDE.md above it leaks in.
# Raw outputs stay in that temp dir; one summary line per task and arm goes to evals/results.log.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="${1:?usage: evals/run.sh <skill> [-n runs] [-m model] [-j judge-model]}"; shift
N=1 MODEL=opus JUDGE=opus
while getopts n:m:j: o; do case $o in n) N=$OPTARG;; m) MODEL=$OPTARG;; j) JUDGE=$OPTARG;; *) exit 2;; esac; done
TASKS="$ROOT/evals/tasks/$SKILL"
[ -d "$TASKS" ] || { echo "no tasks for $SKILL"; exit 2; }
RUN="$(mktemp -d)/$SKILL"; mkdir -p "$RUN"
echo "raw outputs: $RUN"

{ cat "$ROOT/skills/$SKILL/SKILL.md"
  for f in "$ROOT/skills/$SKILL"/references/*.md; do
    [ -f "$f" ] && printf '\n\n---\n# references/%s\n\n' "$(basename "$f")" && cat "$f"
  done; } > "$RUN/skill.md"

check() { # $1 work dir, $2 output file -> number of check-script hits, or "-" for skills without one
  case $SKILL in ui-design-system|doc-writing|repo-setup|architecture) ;; *) echo "-"; return 0 ;; esac
  case $SKILL in
    ui-design-system) python3 "$ROOT/skills/ui-design-system/scripts/design_lint.py" "$1/web" ;;
    doc-writing) python3 "$ROOT/skills/doc-writing/scripts/doc_check.py" "$1" ;;
    repo-setup) python3 "$ROOT/skills/repo-setup/scripts/stack_check.py" "$1" ;;
    architecture) python3 "$ROOT/skills/architecture/scripts/arch_check.py" "$1" ;;
  esac > "$2" 2>&1 || true
  grep -cvE 'clean$' "$2" || true
}

run_one() { # $1 task, $2 arm, $3 run index
  d="$RUN/$1/$2-$3"; w="$d/work"; mkdir -p "$w"
  cp -R "$ROOT/evals/fixtures/$(cat "$TASKS/$1/fixture")/." "$w/"
  git -C "$w" init -q && git -C "$w" add -A && git -C "$w" -c user.name=eval -c user.email=eval@example.com commit -qm fixture
  extra=""; [ "$2" = with ] && extra="--append-system-prompt-file $RUN/skill.md"
  # shellcheck disable=SC2086
  (cd "$w" && claude -p "$(cat "$TASKS/$1/prompt.md")" --model "$MODEL" --disable-slash-commands \
    --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Glob,Grep,Bash(python3:*),Bash(ls:*)" \
    $extra > "$d/agent.txt" 2>&1) || true
  git -C "$w" add -A && git -C "$w" diff --cached > "$d/changes.diff"; rm -rf "$w/.git"
  # The judge can't run anything, so the task's tests run here and it reads their raw output.
  [ -f "$TASKS/tests" ] && { (cd "$w" && sh -c "$(cat "$TASKS/tests")") > "$d/tests.txt" 2>&1; echo "(exit $?)" >> "$d/tests.txt"; }
  hits="$(check "$w" "$d/check.txt")"
  # Judge blind: a copy whose path doesn't name the arm.
  b="$(mktemp -d "$RUN/blind.XXXXXX")"; cp -R "$w/." "$b/"; cp "$d/changes.diff" "$b/.changes.diff"
  [ -f "$d/tests.txt" ] && cp "$d/tests.txt" "$b/.tests.txt"
  python3 - "$ROOT/evals/judge.md" "$TASKS/$1/prompt.md" "$TASKS/rubric.md" > "$b/.judge-prompt" <<'PY'
import sys
j, t, r = (open(p).read() for p in sys.argv[1:])
print(j.replace("TASK_PROMPT", t.strip()).replace("RUBRIC", r.strip()))
PY
  (cd "$b" && claude -p "$(cat .judge-prompt)" --model "$JUDGE" --disable-slash-commands \
    --tools "Read,Glob,Grep" --disallowedTools "Edit,Write,NotebookEdit,Bash" > "$d/judge.txt" 2>&1) || true  # the judge only reads; --tools, not just --allowedTools, makes that true
  score="$(sed -n 's/^SCORE: *\([0-9]*\/[0-9]*\).*/\1/p' "$d/judge.txt" | tail -1)"
  echo "$1 $2 $3 $hits ${score:-?}" > "$d/result.txt"
}

for t in "$TASKS"/*/; do
  t="$(basename "$t")"
  for arm in without with; do
    i=1; while [ "$i" -le "$N" ]; do run_one "$t" "$arm" "$i" & i=$((i + 1)); done
  done
done
wait

# Table and log lines: per task and arm, mean check hits and mean judge score over the runs.
cat "$RUN"/*/*/result.txt | python3 "$ROOT/evals/summarize.py" "$SKILL" "$MODEL" "$JUDGE" "$ROOT/evals/results.log"
