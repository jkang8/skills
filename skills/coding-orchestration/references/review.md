# Independent review run

Moved to the `review` skill so there is one reviewer prompt, not two: `skills/review/SKILL.md` (steps, routing, loop) and `skills/review/references/reviewer-prompt.md` (the exact prompt). `skills/review/scripts/review.sh <repo> <branch>` runs steps 1-3 and prints the prompt and launch command. Review is explicit: run it only when the user asks. Never on PR open, push or cron, and never as a merge gate; the default check is `make gate`. When asked, the orchestrator launches the reviewer and relays its verdict; it never reviews the work itself.
