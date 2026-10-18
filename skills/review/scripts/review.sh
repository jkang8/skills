#!/bin/sh
# Review steps 1-3 for a branch, then the step-4 reviewer prompt: scope the diff, route to skills, run checks.
#   review.sh <repo-checkout> <branch> [base]      (base defaults to main)
# Writes goal.md, checklists.md, diff.patch, checks.txt and prompt.md to a review folder (REVIEW_OUT or a new temp
# dir), keeps a read-only-by-convention checkout of the branch in it, and prints the prompt plus the launch command.
# Exits 1 if any mechanical check fails (the prompt is still written).
# Env: REVIEW_GATE (default `make gate` when the Makefile has a gate target), REVIEW_GOAL (PR goal and owned paths
# when `gh pr view` can't supply them), REVIEW_SKIP_SEC=1 (skip sec_check.sh), REVIEW_NO_FETCH=1.
set -u
SKILLS="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="$(cd "${1:?usage: review.sh <repo-checkout> <branch> [base]}" && pwd)"
BRANCH="${2:?usage: review.sh <repo-checkout> <branch> [base]}"
BASE="${3:-main}"
OUT="${REVIEW_OUT:-$(mktemp -d)}"; mkdir -p "$OUT"
WT="$OUT/branch"

# 1. Scope the diff.
[ "${REVIEW_NO_FETCH:-}" = 1 ] || git -C "$REPO" fetch -q origin 2>/dev/null || true
base_ref="$BASE"; git -C "$REPO" rev-parse -q --verify "origin/$BASE" >/dev/null && base_ref="origin/$BASE"
head_ref="$BRANCH"; git -C "$REPO" rev-parse -q --verify "$BRANCH" >/dev/null || head_ref="origin/$BRANCH"
git -C "$REPO" diff --name-status "$base_ref...$head_ref" > "$OUT/files.txt" || { echo "review: can't diff $base_ref...$head_ref"; exit 2; }
git -C "$REPO" diff "$base_ref...$head_ref" > "$OUT/diff.patch"
cut -f2- "$OUT/files.txt" | awk '{print $NF}' > "$OUT/paths.txt"
goal="${REVIEW_GOAL:-$(cd "$REPO" && gh pr view "$BRANCH" --json title,body -q '"# " + .title + "\n\n" + .body' 2>/dev/null)}"
printf '%s\n\nBranch `%s` against `%s`. Files changed:\n\n%s\n' "${goal:-# Goal not given (set REVIEW_GOAL)}" "$BRANCH" "$base_ref" "$(cat "$OUT/files.txt")" > "$OUT/goal.md"

# 2. Route by what changed.
p() { grep -qE "$1" "$OUT/paths.txt"; }
added() { grep -E '^\+' "$OUT/diff.patch" | grep -qiE "$1"; }
skills="" why=""
use() { case " $skills " in *" $1 "*) ;; *) skills="$skills $1"; why="$why
- $1: $2";; esac; }
code='\.(py|ts|tsx|js|jsx)$'
if p "$code"; then
  if grep -E "$code" "$OUT/paths.txt" | grep -qvE '(^|/)tests?/|(^|/)test_[^/]*$|_test\.[a-z]+$|\.test\.[a-z]+$'; then
    use architecture "code changed"
  else use architecture "tests only: check the pure-core and no-heavy-mocks items"; fi
  use security "code changed (light pass)"
fi
p '\.(tsx|jsx|css|scss|html|vue|svelte)$|(^|/)(components|routes|pages)/' && use ui-design-system "UI changed (needs screenshots in both themes)"
p '\.md$' && use doc-writing "docs changed"
p '(^|/)(pyproject\.toml|package\.json|Makefile|justfile|compose\.ya?ml|docker-compose\.ya?ml|uv\.lock|pnpm-lock\.yaml)$|^\.github/' && {
  use repo-setup "scaffold or tooling changed"; use security "deps or CI changed"; }
added 'password|secret|token|auth|cookie|session|subprocess|shell=|eval\(|pickle|yaml\.load|open\(|requests\.|httpx|fetch\(|upload|execute\(|anthropic|openai|llm' \
  && why="$why
- security: full pass (the diff touches input, auth, secrets, I/O or LLM calls)"
skipped=""; for s in architecture security ui-design-system doc-writing repo-setup; do
  case " $skills " in *" $s "*) ;; *) skipped="$skipped $s";; esac; done

# 3. Mechanical checks on a checkout of the branch.
[ -d "$WT" ] || git -C "$REPO" worktree add -q --detach "$WT" "$head_ref" || { echo "review: worktree failed"; exit 2; }
fail=0
run() { # $1 label, rest = command (run in the branch checkout)
  label="$1"; shift
  printf '## %s\n$ %s\n' "$label" "$*" >> "$OUT/checks.txt"
  (cd "$WT" && "$@") >> "$OUT/checks.txt" 2>&1; rc=$?
  if [ $rc = 0 ]; then echo "ok    $label"; echo "(exit 0)" >> "$OUT/checks.txt"
  else echo "FAIL  $label"; echo "(exit $rc: blocking)" >> "$OUT/checks.txt"; fail=1; fi
  echo >> "$OUT/checks.txt"
}
: > "$OUT/checks.txt"
if [ -n "${REVIEW_GATE:-}" ]; then run gate sh -c "$REVIEW_GATE"
elif [ -f "$WT/Makefile" ] && grep -qE '^gate:' "$WT/Makefile"; then run gate make gate
else echo "skip  gate (no Makefile gate target; set REVIEW_GATE)"; printf '## gate\nskipped: no gate target\n\n' >> "$OUT/checks.txt"; fi
for s in $skills; do case $s in
  architecture) run arch_check python3 "$SKILLS/architecture/scripts/arch_check.py" . ;;
  ui-design-system) run design_lint python3 "$SKILLS/ui-design-system/scripts/design_lint.py" . ;;
  doc-writing) run doc_check python3 "$SKILLS/doc-writing/scripts/doc_check.py" . ;;
  repo-setup) if [ -d "$WT/api" ] || [ -d "$WT/web" ]; then run stack_check python3 "$SKILLS/repo-setup/scripts/stack_check.py" .
              else echo "skip  stack_check (no api/ or web/: not an app scaffold)"; printf '## stack_check\nskipped: not an app scaffold\n\n' >> "$OUT/checks.txt"; fi ;;
  security) [ "${REVIEW_SKIP_SEC:-}" = 1 ] && echo "skip  sec_check (REVIEW_SKIP_SEC=1)" || run sec_check sh "$SKILLS/security/scripts/sec_check.sh" . ;;
esac; done

# 4. Inputs and prompt for the fresh reviewer.
checklist() { # the review checklist section of a skill (repo-setup's is "Done when")
  awk '/^## (Review checklist|Checklist|Done when)/{f=1; print; next} f && /^## /{exit} f' "$SKILLS/$1/SKILL.md"
}
{ echo "# Checklists for this diff"; echo; echo "Chosen:$why"; echo; echo "Not applicable:$skipped"
  for s in $skills; do echo; echo "# $s"; checklist "$s"; done; } > "$OUT/checklists.md"
# The goal, check output and checklists go inline in the prompt (capped; the files stay in the folder too): a reviewer
# that has to find them as files has been seen to report them missing.
MAX="${REVIEW_MAX_INLINE:-200000}"
inline() { # $1 title, $2 file
  printf '\n\n=== %s ===\n' "$1"
  if [ "$(wc -c < "$2")" -gt "$MAX" ]; then
    head -c "$MAX" "$2"; printf '\n[truncated at %s bytes; the full file is %s in the review folder]\n' "$MAX" "$(basename "$2")"
  else cat "$2"; fi
}
{ awk '/^```text/{f=1; next} f && /^```/{exit} f' "$SKILLS/review/references/reviewer-prompt.md"
  inline "goal.md" "$OUT/goal.md"; inline "checks.txt" "$OUT/checks.txt"; inline "checklists.md" "$OUT/checklists.md"
} > "$OUT/prompt.md"

cat "$OUT/prompt.md"
cat <<EOF

---
skills:$skills
not applicable:$skipped
review folder: $OUT
launch the reviewer (fresh session, read-only):
  cd "$OUT" && claude -p "\$(cat prompt.md)" --model opus --effort high --add-dir "$WT" --tools "Read,Glob,Grep" --disallowedTools "Edit,Write,NotebookEdit,Bash" > verdict.md
clean up afterwards:
  git -C "$REPO" worktree remove --force "$WT"
EOF
exit $fail
