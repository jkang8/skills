Score each item 1 (clearly met) or 0 (not met or can't tell). Judge the files under plan/.
1. The orchestrator writes no code itself; all code work is delegated.
2. Each task lists its owned paths (files/dirs it may edit), dependencies and status.
3. Tasks that touch the same file are serialized or have exactly one owner; only disjoint tasks run in parallel.
4. Each agent works in its own git worktree and branch.
5. Briefs include the gate command, "rebase before the PR", and "never merge / never force-push".
6. There is a claim or lock mechanism (or explicit rule) for touching paths outside owned paths.
7. Coordination files (board, briefs, status) live outside the repo.
8. A model or effort choice is stated per task, with a reason that fits the task's difficulty.
9. Reports to the user are short, in the user's terms, with what's blocked and what's needed from them.
10. Review is done before the user sees the work (gate output and a review step), and the user merges.
