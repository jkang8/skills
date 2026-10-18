# Harness adapters and model routing

Harness-specific details live in harness skills (`claude-code`, `codex`, `opencode`) if you have them. Adding a harness means adding a row here, nothing else.

| Harness | Interactive (tmux) | Headless | Model flag | Remote watch |
|---|---|---|---|---|
| Claude Code | `claude --remote-control <name> --model <m>` | `claude -p "<brief>" --model <m>` | `--model opus\|sonnet\|haiku\|fable\|opusplan`, `--effort` | Claude app / claude.ai/code |
| Codex | `codex --model <m>` | `codex exec "<brief>"` | `-m <m>`, reasoning effort config | tmux attach over SSH |
| OpenCode | `opencode` | `opencode run "<brief>"` | `--model <provider/m>` | tmux attach over SSH |

If the orchestrator's shell doesn't have tmux on `PATH` (common for agents started by a service manager), call it by its full path, recorded in the override.

## Model routing
From Anthropic's guidance: the right model is the cheapest one whose output you'd ship; start at defaults.
- **Frontier** (Fable / equivalent): work bigger than one sitting, hard architecture, or a task the default tier failed with full context.
- **Default** (Opus / equivalent): normal features, PRs, debugging.
- **Fast** (Sonnet / equivalent): mechanical bulk edits, renames, boilerplate, test scaffolding.
- **Cheap** (Haiku / equivalent): read-only search, log/eval summaries, classification.

A miss with full context is a capability problem (go up a tier); a miss from skipped files, skipped tests or quitting early is an effort problem (raise effort, keep the model). Cost policy is the user's call: for example, someone on a flat-rate plan may want it fully used and never downshift to save cost. Put that in the override.
