---
name: coding-orchestration
description: "Use when writing code: plan, delegate, parallelize agents."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [orchestration, coding-agents, parallel, worktrees, claude-code, codex, opencode]
    related_skills: [ui-design-system, repo-setup, doc-writing]
---

# Coding orchestration (harness-agnostic)

The rule: when you write code, the orchestrator (a long-running agent such as Hermes, or a top-level Claude Code session) delegates to coding-agent sessions; it doesn't edit code itself. The orchestrator plans, splits, briefs, launches, monitors, gates and reports. The user merges.

Harness-specific commands live in harness skills (`claude-code`, `codex`, `opencode`) if you have them; this skill is the process. Install only the harnesses you use; adding one means adding a row to the adapter table, nothing else.

## Local overrides
If `coding-orchestration.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here and its rules add to these; where they conflict, the override wins.

## UI work
Any task with a user interface follows the `ui-design-system` skill. The brief tells the agent to load it (Claude Code sees it as a user skill in `~/.claude/skills/ui-design-system`; for other harnesses, paste its rules into the brief). The orchestrator runs its review checklist before showing the user screenshots or video.

## New repos
Scaffold with the `repo-setup` skill (default stack: uv, Pydantic, FastAPI, Postgres, pnpm, Vite, React and TS) unless the user names another.

## Docs
Any doc an agent writes (README, guides, CLAUDE.md/AGENTS.md, ADRs) follows the `doc-writing` skill. Docs change in the same PR as the code.

## Harness adapters

| Harness | Interactive (tmux) | Headless | Model flag | Remote watch |
|---|---|---|---|---|
| Claude Code | `claude --remote-control <name> --model <m>` | `claude -p "<brief>" --model <m>` | `--model opus\|sonnet\|haiku\|fable\|opusplan`, `--effort` | Claude app / claude.ai/code |
| Codex | `codex --model <m>` | `codex exec "<brief>"` | `-m <m>`, reasoning effort config | tmux attach over SSH |
| OpenCode | `opencode` | `opencode run "<brief>"` | `--model <provider/m>` | tmux attach over SSH |

Verify a harness's flags with `<cmd> --help` before first use; install one only if the user asks. If the orchestrator's shell doesn't have tmux on `PATH` (common for agents started by a service manager), call it by its full path, recorded in the override.

## Model routing (tiers, any harness)

From Anthropic's guidance: the right model is the cheapest one whose output you'd ship; start at defaults.
- **Frontier** (Fable / equivalent): work bigger than one sitting, hard architecture, or a task the default tier failed with full context.
- **Default** (Opus / equivalent): normal features, PRs, debugging. Default for every session.
- **Fast** (Sonnet / equivalent): mechanical bulk edits, renames, boilerplate, test scaffolding.
- **Cheap** (Haiku / equivalent): read-only search, log/eval summaries, classification.

Miss diagnosis: had context and still wrong -> stronger model. Skipped files/tests or quit early -> more effort, same model. Cost policy (for example, a flat-rate plan the user wants fully used, so never downshift to save cost) belongs in the override. Record model + effort in each PR body.

## 0. Brief and hand off

- Write a brief file under `<agents-dir>/<repo>/` (a coordination folder outside the repo): goal, stack, constraints, ordered tasks, the gate command, what to report back. Send it as "Read <brief> and carry it out; flag anything that looks wrong before you build, then keep going". Agents reliably catch real flaws in the orchestrator's plan at that step (frozen-eval leakage, privacy leaks into PR bodies, stale live checkouts); relay their questions to the user and their fixes into the plan.
- The orchestrator doesn't write the code, scaffolding included. If it already started editing before handing off, list those uncommitted files in the brief and stay out of the folder afterwards.
- New repos: create private with `gh repo create <owner>/<name> --private --source . --push`, seed `docs/` with the source material and a `CLAUDE.md` of ground rules (scope, data rules, employer-overlap limits) so every session starts with them.
- Stack and design defaults for builds are in `references/build-defaults.md`. Paste the relevant parts into the brief.
- Report status in the user's terms when they ask ("how's X"): read the pane/status, check the gate and screenshots, then give the short version with links.

## 1. Plan and split

- Write the plan as a task board before launching anything: `<agents-dir>/<repo>/board.md`, outside the repo so it never gets committed.
- Each task: id, goal, **owned paths** (files/dirs it may edit), depends-on, harness + model, branch, status (todo/claimed/in-review/blocked/done).
- Parallelize only tasks whose owned paths don't overlap and that don't depend on each other. Overlap or dependency -> serialize (the second waits for the first PR to merge). Shared hot files (lockfiles, schemas, `__init__`, config, migrations) get exactly one owner per round.
- Prefer 2-4 parallel agents; more rarely pays off because merges serialize anyway.

## 2. Isolate

- One **git worktree + branch per agent**, never a shared working tree: `git -C <repo> worktree add ../<repo>-wt/<task-id> -b agent/<task-id> origin/main`.
- A live checkout that the orchestrator or a service runs from (for example, a plugin folder your agent loads at startup) is off-limits to agents; it only moves by `git pull --ff-only` after a merge.
- One tmux session per agent, named `<repo>-<task-id>`, started in its worktree.
- Shared mutable state outside git (DBs, ports, caches, eval scratch) gets a per-agent copy or path (`TMPDIR`, port offset, a scratch agent home such as `HERMES_HOME`). Read-only shared inputs are fine.

## 3. Coordinate

- **Claims are atomic directories**: `mkdir <agents-dir>/<repo>/claims/<task-id>` succeeds for exactly one claimer. Write the session name into it; remove it on done or abandon.
- **Path locks** for anything an agent must touch outside its owned paths: `mkdir <agents-dir>/<repo>/locks/<path-with-slashes-as-__>`; release after commit. If the lock exists, the agent stops and reports `blocked: <path> held by <task>` instead of editing.
- **Status files**: each agent appends one-line updates to `<agents-dir>/<repo>/status/<task-id>.md` (started, PR opened, blocked on X, done). The orchestrator reads these plus `tmux capture-pane`. Agents don't message each other directly; the orchestrator relays when one agent's output is another's input.
- Every brief includes: the task row, owned paths, the claim/lock/status rules above, "edit nothing outside owned paths without a lock", "rebase on origin/main before opening the PR", the repo's gate command, and "never merge, never force-push to main".

## 4. Integrate

- Each agent: test first, implement, rebase on `origin/main`, run the gate, open a PR, write status `in-review`.
- The orchestrator checks each PR's diff against its owned paths (out-of-scope edits -> send back), checks gate output and CI, then starts an independent reviewer run (`references/review.md`) and relays its verdict. It reports to the user with links once the reviewer passes. Merge order follows the board's dependencies.
- After a merge, tell the in-flight agents to rebase; conflicts go back to the agent that owns the conflicting path, never resolved by the orchestrator.
- Clean up: `git worktree remove`, kill the tmux session, delete the claim, mark the board row done.

## Pitfalls

- The orchestrator's turns end; long sessions must live in tmux (or the harness's background mode), and the orchestrator isn't notified when they finish. Say so, and check on request or with a cron poll.
- Never run two agents in one worktree "just for a quick fix"; that is the collision this skill prevents.
- A task board inside the repo leaks into commits; keep coordination files under `<agents-dir>/`.
