# Why the orchestration rules exist

- **The orchestrator doesn't write code.** Its job is the plan and the gate. Once it edits, it reviews its own work and can collide with the agents it launched.
- **"Flag anything that looks wrong, then keep going."** At that step, agents reliably catch real flaws in the plan: frozen-eval leakage, privacy leaks into PR bodies, stale live checkouts. They also keep going instead of stalling on a question.
- **Seed new repos with `docs/` and an `AGENTS.md`.** Every session then starts with the ground rules instead of rediscovering them.
- **Owned paths and one owner per hot file.** Two agents editing the same lockfile or migration produce a conflict that neither can resolve alone.
- **2-4 parallel agents.** More rarely pays off, because merges serialize anyway.
- **Worktree per agent.** A shared working tree means one agent's half-finished edit breaks another's tests.
- **Live checkouts off-limits.** A service running from a checkout picks up whatever is on disk; an agent's branch there ships unreviewed code.
- **`mkdir` for claims and locks.** It is atomic on every local filesystem, so exactly one claimer wins without a lock server.
- **Agents don't message each other.** Relaying through the orchestrator keeps one place that knows the state of every task.
- **Conflicts go to the path owner.** The owner knows the intent of the conflicting code; the orchestrator would be guessing.
- **Independent reviewer.** The author and the orchestrator share the brief's assumptions. A fresh session with only the checklist doesn't. See the `review` skill.
- **Board outside the repo.** A board inside the repo ends up in commits.
