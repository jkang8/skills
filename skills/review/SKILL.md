---
name: review
description: "Use when the user asks for a branch review: run every relevant skill."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [review, pr, quality-gate, orchestration]
    related_skills: [coding-orchestration, architecture, security, ui-design-system, doc-writing, repo-setup]
---

# Review a branch

## When to use
Only when the user asks for a review of a branch (from a coding session, an improve-loop run, or their own work). **Never automatically**: not on PR open, not on push, not from cron or the improve loop, and never as a merge gate. The default check is `make gate`. When asked, one entry point picks the skills that apply and runs them. The reviewer is never the agent that wrote the code, and never the orchestrator.

`scripts/review.sh <repo> <branch> [base]` does steps 1-3 and writes the step-4 inputs and prompt to a folder it prints.

## Local overrides
If `review.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. It can add skills to the routing table (for example a minimal-change skill for code, a humanizer for prose).

## 1. Scope the diff
`git diff --name-status origin/<base>...<branch>` (base = the PR's base, usually `main`). Note the PR's goal and owned paths (from the task board, if any). Changes outside owned paths are a finding by themselves.

## 2. Pick the skills (route by what changed)
| Changed | Skills |
|---|---|
| any code (`.py .ts .tsx .js .jsx`) | architecture, security (light pass) |
| UI (`.tsx .jsx .css`, components, routes, pages) | ui-design-system (+ screenshots in both themes) |
| docs (`.md`: AGENTS.md, README, ADRs, SKILL.md) | doc-writing |
| scaffold/tooling (pyproject, package.json, Makefile, compose, CI, lockfiles) | repo-setup, security (deps + CI) |
| input handling, auth, secrets, deps, file/network I/O, LLM calls, personal/health data | security (full pass) |
| tests only | architecture items on a pure core and no heavy mocks |

List the chosen skills and why at the top of the verdict. Skip the rest explicitly ("no UI changed: ui-design-system n/a").

## 3. Mechanical checks first
Run the repo's `make gate`, then the scripts of the chosen skills: `arch_check.py`, `design_lint.py`, `doc_check.py`, `stack_check.py`, `sec_check.sh`. Use the repo's vendored copies if it has them, otherwise this skills checkout. `review.sh` captures the raw output of the gate and every check in `checks.txt`; that output, never a pasted summary, is what the reviewer gets, and `review.sh` puts it (with the goal and the checklists) inline in the prompt so the reviewer doesn't have to find a file. A failing check is a blocking finding; the reviewer doesn't re-argue it.

## 4. Judgment pass: a fresh reviewer
Start a new headless session in a read-only checkout of the branch: default tier (opus), high effort. Give it ONLY the PR goal and owned paths, the diff, the check output, screenshots if UI, and the checklists of the chosen skills. Not the author's transcript and not the orchestrator's opinion. The exact prompt is `references/reviewer-prompt.md`; `review.sh` fills it in and prints the launch command:

```sh
claude -p "$(cat prompt.md)" --model opus --effort high --add-dir <branch-checkout> --tools "Read,Glob,Grep" --disallowedTools "Edit,Write,NotebookEdit,Bash" > verdict.md
```

`--tools` limits what the session can use at all. `--allowedTools` only pre-approves tools, so with it alone a user setting such as `acceptEdits` still lets the reviewer edit the branch (tested: it did). Keep both flags.

## 5. Loop
`VERDICT: CHANGES` -> send the BLOCKING lines (not the nits) to the author session unchanged; it fixes on the same branch; re-run steps 3-4 in a new reviewer session (never reuse the last one). Max 2 rounds; still failing -> report to the user with the findings. Nits go on the PR in one line and never block.

## 6. Record
Post the verdict as a PR comment (`gh pr comment`): skills applied, check results, blocking findings and how they were resolved, nits. The orchestrator relays a two-line summary to the user. The reviewer never merges.

## Pitfalls
- Wiring review into automation (PR-open or push triggers, hooks, cron, a required status check): don't. It runs when the user asks, and the gate is the merge check.
- Reviewing your own code: the author agent and the orchestrator don't run step 4; a fresh session does.
- Running every skill on every diff: route in step 2, or the review drowns in N/A noise.
- Skipping security because the diff is small: the light pass always runs on code.
- Summarized gate output: the reviewer marks it "not verifiable". Pass the raw output.
- Reviews of a PR the author is still reworking return stale CHANGES; re-review on the new head SHA instead of relaying old findings.
- Check scripts can false-positive (e.g. a design lint flagging color literals in the tokens file, where they belong). Confirm a mechanical hit is in scope before blocking on it, and send the script bug to whoever owns the script.
- Many PRs at once: run `review.sh` per PR, each with its own review folder and a fresh read-only reviewer session; never share a reviewer across PRs.
