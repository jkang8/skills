# coding-orchestration: local override (template)

Copy to `coding-orchestration.local.md` (gitignored) and fill in. Values here replace the skill's `<placeholders>`; rules here add to the skill's and win on conflict.

## Who and where
- User: `<name>`. Orchestrator: `<agent, e.g. Hermes>` running on `<machine>`.
- `<agents-dir>`: `<path outside any repo, e.g. a folder under the orchestrator's home>`.
- Installed harnesses: `<e.g. Claude Code only>`.
- tmux binary: `<full path, if not on the orchestrator's PATH>`.

## Policy
- Cost: `<e.g. flat-rate plan, use it fully: never downshift a model to save cost>`.
- Live checkouts agents must not touch: `<paths>`.
- Where Claude Code sees shared skills: `<e.g. symlinks in ~/.claude/skills>`.
- Harness skills this pairs with: `<e.g. claude-code, codex, opencode>`.
