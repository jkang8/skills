# Plan, isolate, coordinate

## Plan and split
- Task board at `<agents-dir>/<repo>/board.md`, never in the repo.
- Each task: id, goal, **owned paths**, depends-on, harness + model, branch, status (todo/claimed/in-review/blocked/done).
- Parallelize only tasks with disjoint owned paths and no dependency; otherwise serialize. Shared hot files (lockfiles, schemas, `__init__`, config, migrations) get one owner per round.
- 2-4 parallel agents.

## Isolate (worktrees)
- One git worktree + branch per agent: `git -C <repo> worktree add ../<repo>-wt/<task-id> -b agent/<task-id> origin/main`.
- Live checkouts that the orchestrator or a service runs from are off-limits; they move only by `git pull --ff-only` after a merge.
- One tmux session per agent, `<repo>-<task-id>`, started in its worktree.
- Shared mutable state outside git (DBs, ports, caches, scratch) gets a per-agent copy or path (`TMPDIR`, port offset, scratch agent home such as `HERMES_HOME`). Read-only shared inputs are fine.

## Coordinate (claims, locks, status)
- Claim: `mkdir <agents-dir>/<repo>/claims/<task-id>` (atomic, one winner); write the session name in it; remove it on done or abandon.
- Lock anything outside owned paths: `mkdir <agents-dir>/<repo>/locks/<path-with-slashes-as-__>`; release after commit. Lock taken -> report `blocked: <path> held by <task>`, don't edit.
- Status: one-line appends to `<agents-dir>/<repo>/status/<task-id>.md`. The orchestrator reads these plus `tmux capture-pane` and relays between agents; agents don't message each other.
- Every brief includes: the task row, owned paths, these claim/lock/status rules, "edit nothing outside owned paths without a lock", "rebase on origin/main before the PR", the gate command, "never merge, never force-push to main".
