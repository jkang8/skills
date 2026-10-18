# skills

Eight agent skills for Claude Code and Hermes. Each is a folder: `SKILL.md` holds the rules and a checklist, `references/` the reasoning and examples, and `scripts/` the checks a repo's `make gate` calls. Anything personal, like a registry name, a machine path or a cost policy, goes in a local override file, so the shared text stays generic.

| Skill | Use it when | What it gives the agent |
|---|---|---|
| `coding-orchestration` | an agent should plan and delegate code work to other agent sessions | brief format, task board with owned paths, one worktree per agent, atomic claims and locks, model routing, integration rules |
| `ui-design-system` | building any product UI | tokens, a closed component set, UX and interaction rules, AI-native patterns, a banned-slop list, a review checklist |
| `doc-writing` | writing a README, guide, ADR or AGENTS.md | Diátaxis doc types, writing rules, what goes in vs. stays out, ADR shape, doc-bloat budgets, a review checklist |
| `architecture` | structuring or reviewing code | deep modules, one-way dependencies, functional core, when to extract or inline a helper, smells, a review checklist |
| `security` | code touches input, auth, secrets, deps or data | secrets, input validation, auth per object, privacy, supply chain, agent-specific risks; `sec_check.sh` runs ruff S, gitleaks, pip-audit, pnpm audit |
| `demo-video` | recording a captioned walkthrough of a running app | storyboard-first method, one script per scene, stitching with a caption band, burned-in captions plus `.srt`, a frame check at every caption; scripts for running scenes, stitching and checking, with fixture tests |
| `review` | reviewing a branch (the skill says when one runs) | diff scope, routing to the skills that apply, mechanical checks, one fresh-reviewer prompt; `review.sh` does steps 1-3 |
| `repo-setup` | starting a new repo | a uv + Pydantic + FastAPI + Postgres backend, a pnpm + Vite + React + TS frontend, a shadcn registry layout, Makefile gate, done-when criteria |

The skills reference each other (orchestration briefs pull in the others), so install them together.

## Install for Claude Code

Claude Code loads user skills from `~/.claude/skills/<name>/SKILL.md`, and a symlinked folder works.

```sh
git clone https://github.com/<owner>/skills ~/code/skills
for s in coding-orchestration architecture security review ui-design-system doc-writing repo-setup demo-video; do
  ln -s ~/code/skills/skills/$s ~/.claude/skills/$s
done
```

To copy instead of link, use `cp -R ~/code/skills/skills/<name> ~/.claude/skills/`. Copies don't pick up `git pull`.

Start a new session and ask for a skill by name to check it loaded.

## Install for Hermes

Hermes loads skills from `$HERMES_HOME/skills/<category>/<name>/SKILL.md`. `HERMES_HOME` defaults to the `.hermes` folder in your home directory; set it in your shell if it isn't already.

Hermes's skill index follows symlinked folders, but some of its tools (usage tracking, skill lookup for edits) skip them. Make a real folder and link the files inside it:

```sh
link() { # $1 skill, $2 category
  d="$HERMES_HOME/skills/$2/$1"; mkdir -p "$d"
  for f in ~/code/skills/skills/$1/*; do ln -s "$f" "$d/"; done
}
link coding-orchestration autonomous-ai-agents
link ui-design-system creative
link doc-writing productivity
link repo-setup software-development
link architecture software-development
link security software-development
link review software-development
link demo-video creative
```

The categories are only folders; pick any. If Hermes edits a linked `SKILL.md` itself, it may replace the link with a plain file. Check with `ls -l` after a self-edit and move real changes into the repo or your override.

## Overrides

Each skill tells the agent to read `<name>.local.md` before following the skill, from either the skill's own folder or `overrides/` at the root of this checkout (the agent resolves symlinks to find it). Values in the override fill the skill's placeholders; rules in it add to the skill's and win on conflict.

1. Copy the template: `cp overrides/repo-setup.example.md overrides/repo-setup.local.md`.
2. Fill in your values (for example, your registry namespace and commit identity). `*.local.md` is gitignored, so the file never reaches a commit.

To keep overrides outside the checkout, symlink them in: `ln -s ~/private/repo-setup.local.md overrides/`.

## Checks and evals

`make gate` is this repo's check; the `Makefile` lists what it runs (script tests, `doc_check`, `arch_check`, `design_lint` on the TS examples, `sec_check` and the privacy check). It passes when it ends with `PRIVACY CHECK PASS`. `sec_check.sh` is in the gate and needs the network the first time: it downloads a pinned, checksum-verified gitleaks and runs ruff and pip-audit through `uvx`. If a tool that applies can't run, the gate fails (exit 2) instead of passing unchecked. Three heavier checks stay outside the gate because they fetch dependencies: `skills/architecture/scripts/check_templates.sh`, `skills/architecture/references/examples/check.sh` and `skills/security/scripts/test_sec_check.sh`. Run them when you change what they test.

`evals/run.sh <skill>` runs a skill's tasks headless, without and with the skill, and prints a comparison table. `evals/README.md` covers how to run and read it.

## Privacy gate

`scripts/privacy_check.sh` scans everything git would commit (tracked, staged and new files), plus commit messages, and fails on personal data. It runs:
- `scripts/privacy_scan.py` (stdlib, in this repo): real email addresses, secret-shaped strings and a denylist of terms, and
- a grep for generic leaks (home-directory paths, personal mail domains) plus your own terms.

Its config is a shell file at `.privacy.local` (gitignored) or the path in `$PRIVACY_CONFIG`:

```sh
PRIVACY_DENYLIST=/path/to/denylist.txt      # one term per line, never committed
PRIVACY_TERMS='handle|employer|family-name'  # extended regex, case-insensitive
PRIVACY_ALLOW='LICENSE:Copyright (c) 2026 Your Name'  # exact lines to let through
PRIVACY_PYTHON=/path/to/python3              # optional; defaults to python3
```

Without the config or the denylist, the check fails rather than passing silently. `.privacy.local` is per checkout, so in a git worktree set `PRIVACY_CONFIG` instead. Make it run before every commit:

```sh
printf '#!/bin/sh\nexec "$(git rev-parse --show-toplevel)/scripts/privacy_check.sh"\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

A clean run ends with `PRIVACY CHECK PASS`.

## License

MIT. See `LICENSE`.
