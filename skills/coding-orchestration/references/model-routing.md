# Model routing (tiers, any harness)

From Anthropic's guidance: the right model is the cheapest one whose output you'd ship; start at defaults.
- **Frontier** (Fable / equivalent): work bigger than one sitting, hard architecture, or a task the default tier failed with full context.
- **Default** (Opus / equivalent): normal features, PRs, debugging.
- **Fast** (Sonnet / equivalent): mechanical bulk edits, renames, boilerplate, test scaffolding.
- **Cheap** (Haiku / equivalent): read-only search, log/eval summaries, classification.

A miss with full context is a capability problem (go up a tier); a miss from skipped files, skipped tests or quitting early is an effort problem (raise effort, keep the model). Cost policy is the user's call: for example, someone on a flat-rate plan may want it fully used and never downshift to save cost. Put that in the override.
