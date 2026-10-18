# Harness adapters

Harness-specific details live in harness skills (`claude-code`, `codex`, `opencode`) if you have them. Adding a harness means adding a row here, nothing else.

| Harness | Interactive (tmux) | Headless | Model flag | Remote watch |
|---|---|---|---|---|
| Claude Code | `claude --remote-control <name> --model <m>` | `claude -p "<brief>" --model <m>` | `--model opus\|sonnet\|haiku\|fable\|opusplan`, `--effort` | Claude app / claude.ai/code |
| Codex | `codex --model <m>` | `codex exec "<brief>"` | `-m <m>`, reasoning effort config | tmux attach over SSH |
| OpenCode | `opencode` | `opencode run "<brief>"` | `--model <provider/m>` | tmux attach over SSH |

If the orchestrator's shell doesn't have tmux on `PATH` (common for agents started by a service manager), call it by its full path, recorded in the override.
