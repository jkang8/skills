# Skill evals

`evals/run.sh <skill>` runs each task in `tasks/<skill>/` twice, without and with the skill, and prints a table comparing the two.

```sh
evals/run.sh ui-design-system            # one run per arm, opus agent, opus judge
evals/run.sh doc-writing -n 3 -m sonnet  # three runs per arm, sonnet agent
```

## What a run does
1. Copies the task's fixture (`fixtures/<name>/`) into a temp dir outside any repo, so no parent `CLAUDE.md` or `AGENTS.md` leaks in.
2. Runs `claude -p` on the task prompt with `--disable-slash-commands` (no skills) in both arms. The "with" arm adds the skill's `SKILL.md` and `references/*.md` via `--append-system-prompt-file`. Tools are file edits plus `python3` and `ls`.
3. Scores the result with the skill's check script (`design_lint.py`, `doc_check.py`, `stack_check.py`, `arch_check.py`; none for coding-orchestration), counted as hits.
4. A separate `claude -p` judge scores it against `tasks/<skill>/rubric.md`. The judge sees a copy whose path doesn't say which arm it is.
5. Appends one line per task and arm to `results.log` (committed). Raw outputs stay in the temp dir the script prints.

## Reading the numbers
- Lower check hits and higher judge scores are better.
- With `-n 1`, a single run per arm is noisy. Treat differences of a point or two as noise until `-n 3` agrees.
- Both arms load your user-level `~/.claude/CLAUDE.md`, if you have one, the same way.
- The rubrics follow each skill's intent, so they measure "does the skill get followed", not general quality.
