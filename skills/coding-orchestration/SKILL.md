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
- UI: the brief tells the agent to follow `ui-design-system` (Claude Code loads it as a user skill; for other harnesses, paste its rules). Run its review checklist before showing the user screenshots or video.
- Code: the brief tells the agent to follow `architecture`, and `security` when the change touches input, auth, secrets, deps or data.
- New repos: scaffold with `repo-setup` unless the user names another stack.
- Docs: follow `doc-writing`. Docs change in the same PR as the code.

## Harnesses and models
- Commands per harness (interactive, headless, model flag, remote watch): `references/harnesses.md`. Verify flags with `<cmd> --help` before first use; install a harness only if the user asks.
- Tiers: **frontier** for work bigger than one sitting or a default-tier failure with full context; **default** (Opus or equivalent) for normal work and every session by default; **fast** for mechanical bulk edits; **cheap** for read-only search and summaries.
- Had context and still wrong -> stronger model. Skipped files or quit early -> more effort, same model.
- Record model + effort in each PR body. Cost policy lives in the override.

## 0. Brief and hand off
- Write a brief under `<agents-dir>/<repo>/` (outside the repo): goal, stack, constraints, ordered tasks, gate command, what to report.
- Send it as "Read <brief> and carry it out; flag anything that looks wrong before you build, then keep going". Relay the agent's flags to the user and its fixes into the plan.
- The orchestrator writes no code, scaffolding included. If it already edited files, list them in the brief and stay out of the folder.
- New repos: `gh repo create <owner>/<name> --private --source . --push`; seed `docs/` with the source material and an `AGENTS.md` of ground rules (`CLAUDE.md` = `@AGENTS.md`) (scope, data rules, employer-overlap limits).
- Paste the relevant parts of `references/build-defaults.md` into build briefs.
- When the user asks "how's X": read the pane/status, check the gate and screenshots, answer short with links.

## 1. Plan and split
- Task board at `<agents-dir>/<repo>/board.md`, never in the repo.
- Each task: id, goal, **owned paths**, depends-on, harness + model, branch, status (todo/claimed/in-review/blocked/done).
- Parallelize only tasks with disjoint owned paths and no dependency; otherwise serialize. Shared hot files (lockfiles, schemas, `__init__`, config, migrations) get one owner per round.
- 2-4 parallel agents.

## 2. Isolate
- One git worktree + branch per agent: `git -C <repo> worktree add ../<repo>-wt/<task-id> -b agent/<task-id> origin/main`.
- Live checkouts that the orchestrator or a service runs from are off-limits; they move only by `git pull --ff-only` after a merge.
- One tmux session per agent, `<repo>-<task-id>`, started in its worktree.
- Shared mutable state outside git (DBs, ports, caches, scratch) gets a per-agent copy or path (`TMPDIR`, port offset, scratch agent home such as `HERMES_HOME`). Read-only shared inputs are fine.

## 3. Coordinate
- Claim: `mkdir <agents-dir>/<repo>/claims/<task-id>` (atomic, one winner); write the session name in it; remove it on done or abandon.
- Lock anything outside owned paths: `mkdir <agents-dir>/<repo>/locks/<path-with-slashes-as-__>`; release after commit. Lock taken -> report `blocked: <path> held by <task>`, don't edit.
- Status: one-line appends to `<agents-dir>/<repo>/status/<task-id>.md`. The orchestrator reads these plus `tmux capture-pane` and relays between agents; agents don't message each other.
- Every brief includes: the task row, owned paths, these claim/lock/status rules, "edit nothing outside owned paths without a lock", "rebase on origin/main before the PR", the gate command, "never merge, never force-push to main".

## 4. Integrate
- Agent: test first, implement, rebase on `origin/main`, run the gate, open a PR, status `in-review`.
- Orchestrator: check the diff against owned paths (out of scope -> send back), check gate output and CI, then report to the user with links and the gate output. Merge order follows the board.
- **Review is explicit, never automatic.** Run the `review` skill only when the user asks for a review. Never on PR open, push or cron, and never as a merge gate. The default check is `make gate`.
- After a merge, tell in-flight agents to rebase. Conflicts go to the agent owning the path, never to the orchestrator.
- Clean up: `git worktree remove`, kill the tmux session, delete the claim, mark the row done.

## Improve loop (any repo, orchestrator-owned)
A scheduled run that makes one gated improvement per run, as a PR: `scripts/improve.sh <repo> [signals-data-path]`. Untrusted text (issue or PR bodies from non-members) never reaches the builder, and its Bash is an allowlist (gate, tests, local git), not blanket. The repo provides three things:
- `make gate`: tests plus any evals; must pass before a PR opens.
- `<repo>/scripts/signals`: prints weak spots (failures, misses, metrics). It may take a path to private data passed in by the orchestrator; the repo never hardcodes it.
- `IMPROVE.md`: what a good foundational fix looks like here, and what's off-limits (frozen evals, privacy rules).

The run: fetch -> new worktree + branch `improve/<stamp>` -> haiku summarizes signals (marking private items) -> opus picks ONE fix and builds it test-first -> gate. Two gate failures with full context -> one retry on fable; quit early or skipped the test -> one retry on opus at high effort. Pass -> PR with model + effort in the body and no private data. Fail -> discard the worktree, one-line note to the user. Never merges, and has no review step: the gate is its check, and a review runs only if the user asks. Opt a repo in by adding a cron for it, e.g. weekly: `0 6 * * 1 <skills-checkout>/skills/coding-orchestration/scripts/improve.sh <repo-checkout> [data-path]`.

## Pitfalls
- Long sessions live in tmux or the harness's background mode; the orchestrator isn't notified when they end. Say so, and poll on request or by cron.
- Never two agents in one worktree, not even for a quick fix.
- Coordination files stay under `<agents-dir>/`, never in the repo.

## Checklist before reporting a PR
1. The diff touches only the task's owned paths, or paths it held a lock for.
2. The gate passed after the final rebase, and its output is in the PR body.
3. If the user asked for a review (the `review` skill), its verdict is linked; otherwise none ran, and that's fine.
4. Model and effort are recorded in the PR body.
5. Claim and locks are released; the board row says `in-review`.

Why each rule exists: `references/why.md`.
