# Independent review run

Moved to the `review` skill so there is one reviewer prompt, not two: `skills/review/SKILL.md` (steps, routing, loop) and `skills/review/references/reviewer-prompt.md` (the exact prompt). `skills/review/scripts/review.sh <repo> <branch>` runs steps 1-3 and prints the prompt and launch command. When a review runs is that skill's "When to use"; when one does, the orchestrator launches the reviewer and relays its verdict, and never reviews the work itself.
