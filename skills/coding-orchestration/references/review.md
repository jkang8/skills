# Independent review run

A reviewer is a fresh agent session that sees only the checklist, the diff and the screenshots. It never sees the brief's reasoning, the author's chat or the orchestrator's opinion, so it can't inherit their blind spots. The orchestrator launches it and relays its verdict; the orchestrator doesn't review the work itself.

## When
After the author agent opens a PR and its gate passes, before the orchestrator reports the PR to the user. Run it again after every fix round until every item passes.

## Inputs (and nothing else)
Put these in an empty review folder outside the repo, e.g. `<agents-dir>/<repo>/review/<task-id>/round-<n>/`:
1. `checklist.md`: the review checklist of each skill the task used (ui-design-system for UI, doc-writing for docs, repo-setup for scaffolds), copied verbatim, plus the task's owned paths.
2. `diff.patch`: `git -C <worktree> diff origin/main...HEAD > diff.patch`.
3. `screenshots/`: the author's screenshots (light, dark, 1440×900 and 390px), if the task has UI.
4. `gate.txt`: the gate output the author pasted in the PR.

Start the reviewer in that folder with read access to the worktree (so it can open full files for context) and no write access to it.

## Launch
Model: opus, high effort.

```sh
cd <agents-dir>/<repo>/review/<task-id>/round-<n>
claude -p "$(cat prompt.txt)" \
  --model opus --effort high \
  --add-dir <worktree> \
  --allowedTools "Read,Glob,Grep" \
  > verdict.md
```

For other harnesses, use their headless mode with the same prompt and a read-only sandbox.

## Reviewer prompt (exact)
Save this as `prompt.txt` in the review folder:

```text
You are reviewing a pull request. You did not write it and have no stake in it passing.

In this folder: checklist.md (the rules and the owned paths), diff.patch (the change), gate.txt (the
author's gate output) and, if present, screenshots/. The full worktree is readable at the extra
directory you were given; open files there when the diff lacks context. You cannot edit anything.

For every checklist item, and for "edits stay inside the owned paths", decide PASS or FAIL.
- FAIL needs evidence: file:line from the diff or worktree, or a screenshot file name plus what is
  wrong in it. Quote the offending text in one line.
- PASS needs one line saying what you checked. "Looks fine" is not a check.
- An item you cannot check from these inputs is FAIL with reason "not verifiable from inputs".
- Do not suggest improvements outside the checklist. Do not soften a FAIL.

Output exactly this, and nothing before or after it:

VERDICT: PASS | FAIL
| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | <checklist item, short> | PASS/FAIL | <file:line or screenshot + one line> |
...
FIXES (FAIL rows only, one line each, most important first):
- <item #>: <what must change, where>
```

## Loop
1. The orchestrator reads `verdict.md`. On `VERDICT: PASS`, it reports the PR to the user with the verdict linked.
2. On FAIL, it sends the FIXES block to the author agent unchanged ("Fix these, rerun the gate, push"). It doesn't add its own findings or argue with the reviewer's.
3. After the author pushes, start a new round (`round-<n+1>`) in a fresh session with fresh inputs. Never reuse the previous reviewer session; it would review against its own earlier notes.
4. If the same item fails three rounds in a row, stop and ask the user. Either the rule or the task is wrong.
