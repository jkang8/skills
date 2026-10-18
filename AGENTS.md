# skills

Eight agent skills (coding orchestration, architecture, security, review, UI design system, doc writing, repo setup, demo video), written to work as-is in Claude Code and Hermes. The repo is meant to be public: everything personal lives in local override files that are never committed.

## Map
- `skills/<name>/SKILL.md`: one skill per folder, frontmatter `name`, `description`, `license`. Supporting files in `skills/<name>/references/`; checks in `skills/<name>/scripts/` (stdlib Python, tests on `fixtures/`).
- `overrides/<name>.example.md`: template for a user's local `<name>.local.md`.
- `scripts/privacy_check.sh`: the privacy gate; `scripts/privacy_scan.py` is its stdlib scanner.
- `evals/`: with/without-skill evals (`evals/run.sh <skill>`; see `evals/README.md`).

## Commands
- Gate: `make gate`. Passes when it ends with `PRIVACY CHECK PASS`.
- Privacy check alone: `scripts/privacy_check.sh`. Install it as `.git/hooks/pre-commit` (see README).

## Rules
- Run the gate before every commit. It fails closed without its local config; don't work around that.
- No names, handles, registries, machine paths, employers or domain examples from a real user. Use placeholders (`<your-registry>`, `<org>`, `<agents-dir>`) and neutral examples; the specifics go in an override.
- Never commit `*.local.md`, `.privacy.local`, or any denylist; they're gitignored for a reason.
- Templates are `*.example.md`, not `*.local.md`, because the gitignore pattern would hide them.
- Keep every rule and its reason when editing a skill. Cut only what's personal.
- Docs follow `skills/doc-writing/SKILL.md` (AGENTS.md ≤100 lines, README ≤150).
- AGENTS.md is the agent context file; CLAUDE.md holds only `@AGENTS.md`. No symlinks.
- Sources: link, don't quote. Mark each as read or known (general knowledge).
