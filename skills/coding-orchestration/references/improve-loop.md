# Improve loop (any repo, orchestrator-owned)

A scheduled run that makes one gated improvement per run, as a PR: `scripts/improve.sh <repo> [signals-data-path]`. Items from non-members (issues and PRs, titles included) are dropped before the builder sees anything. The builder's Bash is an allowlist (gate, tests, local git), which limits mistakes but isn't containment: it can run code it writes through the test commands. So its environment is scrubbed of credentials, and `IMPROVE_WRAP` takes a sandbox command prefix; use one on a public repo. The repo provides three things:
- `make gate`: tests plus any evals; must pass before a PR opens.
- `<repo>/scripts/signals`: prints weak spots (failures, misses, metrics). It may take a path to private data passed in by the orchestrator; the repo never hardcodes it.
- `IMPROVE.md`: what a good foundational fix looks like here, and what's off-limits (frozen evals, privacy rules).

The run: fetch -> new worktree + branch `improve/<stamp>` -> haiku summarizes signals (marking private items) -> opus picks ONE fix and builds it test-first -> gate. Two gate failures with full context -> one retry on fable; quit early or skipped the test -> one retry on opus at high effort. Pass -> PR with model + effort in the body and no private data. Fail -> discard the worktree, one-line note to the user. Never merges, and has no review step: the gate is its check. Opt a repo in by adding a cron for it, e.g. weekly: `0 6 * * 1 <skills-checkout>/skills/coding-orchestration/scripts/improve.sh <repo-checkout> [data-path]`.
