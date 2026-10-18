---
name: coding-orchestration
description: "Use when writing code: plan, delegate, parallelize agents."
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [orchestration, coding-agents, parallel, worktrees, claude-code, codex, opencode]
    related_skills: [architecture, security, review, ui-design-system, repo-setup, doc-writing]
---

# Coding orchestration (harness-agnostic)

When you write code, the orchestrator (a long-running agent such as Hermes, or a top-level Claude Code session) delegates to coding-agent sessions and doesn't edit code itself. It plans, splits, briefs, launches, monitors, gates and reports. The user merges.

## Local overrides
If `coding-orchestration.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here; its rules add to these and win on conflict.

## Other skills
- UI: the brief tells the agent to follow `ui-design-system` (Claude Code loads it as a user skill; for other harnesses, paste its rules). The agent checks screenshots and video against its checklist before reporting; for an independent review, see the `review` skill.
- Code: the brief tells the agent to follow `architecture`, and `security` when the change touches input, auth, secrets, deps or data.
- New repos: scaffold with `repo-setup` unless the user names another stack.
- Docs: follow `doc-writing`. Docs change in the same PR as the code.

## Harnesses and models
- Commands per harness (interactive, headless, model flag, remote watch): `references/harness-adapters.md`. Verify flags with `<cmd> --help` before first use; install a harness only if the user asks.
- Tiers (`references/model-routing.md`): **frontier** for work bigger than one sitting or a default-tier failure with full context; **default** (Opus or equivalent) for normal work and every session by default; **fast** for mechanical bulk edits; **cheap** for read-only search and summaries.
- Had context and still wrong -> stronger model. Skipped files or quit early -> more effort, same model.
- Record model + effort in each PR body. Cost policy lives in the override.

## 0. Brief and hand off
- Write a brief under `<agents-dir>/<repo>/` (outside the repo): goal, stack, constraints, ordered tasks, gate command, what to report.
- Send it as "Read <brief> and carry it out; flag anything that looks wrong before you build, then keep going". Relay the agent's flags to the user and its fixes into the plan.
- The orchestrator writes no code, scaffolding included. If it already edited files, list them in the brief and stay out of the folder.
- New repos: `gh repo create <owner>/<name> --private --source . --push`; seed `docs/` with the source material and an `AGENTS.md` of ground rules (`CLAUDE.md` = `@AGENTS.md`) (scope, data rules, employer-overlap limits).
- Paste the relevant parts of `references/build-defaults.md` into build briefs.
- When the user asks "how's X": read the pane/status, check the gate and screenshots, answer short with links.

## 1-3. Plan, isolate, coordinate
- Task board at `<agents-dir>/<repo>/board.md`, never in the repo. Each task has owned paths; parallelize only tasks with disjoint owned paths and no dependency, 2-4 agents at most.
- One git worktree + branch per agent, one tmux session per agent. Live checkouts that the orchestrator or a service runs from are off-limits.
- Claims and path locks are `mkdir`s (atomic, one winner); agents append one-line status updates and don't message each other.
- Every brief includes: the task row, owned paths, the claim/lock/status rules, "edit nothing outside owned paths without a lock", "rebase on origin/main before the PR", the gate command, "never merge, never force-push to main".
- Exact commands and reasons: `references/coordination.md`.

## 4. Integrate
- Agent: test first, implement, rebase on `origin/main`, run the gate, open a PR, status `in-review`.
- Orchestrator: check the diff against owned paths (out of scope -> send back), check gate output and CI, then report to the user with links and the gate output. Merge order follows the board.
- Review isn't a step of this loop. For an independent review, see the `review` skill (its "When to use" says when one runs).
- After a merge, tell in-flight agents to rebase. Conflicts go to the agent owning the path, never to the orchestrator.
- Clean up: `git worktree remove`, kill the tmux session, delete the claim, mark the row done.

## Improve loop (any repo, orchestrator-owned)
A scheduled run that makes one gated improvement per run, as a PR: `scripts/improve.sh <repo> [signals-data-path]`. It never merges and has no review step: the gate is its check. The repo provides `make gate`, `<repo>/scripts/signals` and `IMPROVE.md`. Non-member items are dropped, the builder's environment is scrubbed, and a public repo should use `IMPROVE_WRAP`. The run, the trust rules and the cron line: `references/improve-loop.md`.

## Pitfalls
- Long sessions live in tmux or the harness's background mode; the orchestrator isn't notified when they end. Say so, and poll on request or by cron.
- Never two agents in one worktree, not even for a quick fix.
- Coordination files stay under `<agents-dir>/`, never in the repo.

## Checklist before reporting a PR
1. The diff touches only the task's owned paths, or paths it held a lock for.
2. The gate passed after the final rebase, and its output is in the PR body.
3. Any verdict from a `review` run is linked.
4. Model and effort are recorded in the PR body.
5. Claim and locks are released; the board row says `in-review`.

Why each rule exists: `references/why.md`.
