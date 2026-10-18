# Why these rules: what makes Stripe's docs work

- **Ordered by the reader's questions, not the org chart.** What is it, can I try it now, how do I do my task, what are the exact fields.
- **Runnable examples beside the prose.** Every concept sits next to code that works as pasted, with real-looking values and the output shown.
- **Docs are part of the product.** They're written by the people who build it, reviewed like code, and validated at build time (links and samples fail the build, not the reader).
- **One voice.** Short, plain, second person, consistent terms across docs, API reference and UI.

## Why docs carry only what code can't
Agents read code well; they can't read intent, history or the parts outside the repo. Prose that restates code drifts, and agents then trust the wrong one. So code carries behavior (with clear names, types such as pydantic models and TS types, small modules, and tests that read as examples) and docs carry the why, the where, the invariants, the commands and the outside world.

## Why budgets
Agents append by default: every task adds a line and nobody removes one. A context file that loads into every session costs context on every task, so length is a budget, not a log.
