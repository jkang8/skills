---
name: doc-writing
description: "Use when writing docs, READMEs or agent context files."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [docs, writing, readme, agents-md, claude-md, diataxis, stripe]
    related_skills: [coding-orchestration, ui-design-system, repo-setup]
---

# Doc writing

## When to use
Any doc in a repo you own: README, guides, API reference, architecture notes, ADRs, and the agent context files (CLAUDE.md / AGENTS.md). Put these rules in the coding agent's brief (see coding-orchestration). Reference point: Stripe's docs.

## Local overrides
If `doc-writing.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here and its rules add to these; where they conflict, the override wins.

## What makes Stripe's docs work
- **Ordered by the reader's questions, not the org chart.** What is it, can I try it now, how do I do my task, what are the exact fields.
- **Runnable examples beside the prose.** Every concept sits next to code that works as pasted, with real-looking values and the output shown.
- **Docs are part of the product.** They're written by the people who build it, reviewed like code, and validated at build time (links and samples fail the build, not the reader).
- **One voice.** Short, plain, second person, consistent terms across docs, API reference and UI.

## Pick the doc type first (Diátaxis)
Each page is exactly one of these. Mixing them is the most common reason docs feel muddy.
- **Tutorial:** a guaranteed first success for a newcomer. One path, no choices, every step shows the result.
- **How-to:** a recipe for one real task, for someone who already knows the basics. Title it as the task ("Rotate an API key").
- **Reference:** exact, complete, dry. Fields, types, defaults, errors, limits. Generated from code when possible.
- **Explanation:** why it's built this way, tradeoffs, history. No steps.

## Writing rules (Stripe + Google developer style guide)
- Lead with what the reader gets, in one sentence. Then the steps.
- Second person and active voice: "You run…", not "The command is run…". Put the condition before the instruction ("If the build fails, run…").
- Numbered lists for sequences, bullets for everything else. Sentence-case headings. Code font for code, paths, commands and values; bold for UI labels.
- One idea per sentence, one task per page. Cut "simply", "just", "easy", "powerful", "seamless".
- Use the same term for the same thing everywhere, matching the code and the UI.
- Descriptive link text ("see the rounding rules"), never "click here".
- Examples must run as written: real commands, realistic data, expected output shown. Never show a sample you haven't run.
- Unambiguous dates (2026-10-18) and units. Don't pre-announce features.
- Before publishing prose, do a pass for AI-writing tells (a humanizer skill, if you have one).

## Docs vs code for agents learning the codebase
Agents read code well; they can't read intent, history or the parts outside the repo. So docs carry what code can't, and code carries everything else.

**Code is the source of truth for:** what functions do, signatures, data shapes, control flow. Make it self-explaining with clear names, types (pydantic models, TS types), small modules and tests that read as examples. Don't restate any of this in prose; it drifts and agents then trust the wrong one.

**Docs carry:**
- **Why:** decisions and rejected alternatives (one short ADR per real decision, `docs/decisions/NNNN-title.md`). Format below; keep it a record, not a story.
- **Where:** a map of the repo, one line per top-level directory and the entry points.
- **Invariants and traps:** things that must stay true and aren't visible locally ("never commit real customer data", "the held-out eval set is frozen", "this folder is a live install").
- **How to run, test and verify:** exact commands, and how to know they worked.
- **Domain language:** a short glossary of terms the code uses (e.g. tenant, seat, settlement, chargeback).
- **Outside the repo:** services, credentials' locations (never values), data sources, who decides what.

**Decision records (ADRs): terse, current, not narrative.**
- Fixed shape, about 10-15 lines: Status (accepted / superseded by NNNN), Date, Decision (one sentence, present tense), Why (2-3 bullets of reasons that still apply), Rejected (one line each: option, why not), Consequences (what this rules in or out for future work).
- State the decision as it stands, not how the team got there. No "we first tried", "after a long discussion", timelines, who said what, or dead ends that no longer constrain anything.
- Only record decisions an agent or newcomer would otherwise undo: a non-obvious choice, a constraint, or a tempting alternative that's wrong here. Routine choices get no ADR.
- When a decision changes, write a new ADR and mark the old one superseded in its first line. Don't append history to the old one.
- Git log and PR descriptions hold the narrative; link a PR if the full story matters.

**The agent context file (CLAUDE.md, with AGENTS.md symlinked to it):**
- Under ~100 lines. It loads into every session, so every line costs context on every task.
- Contents, in order: one-paragraph purpose; repo map; commands (setup, run, test, lint, gate); conventions that differ from defaults; hard rules and traps; pointers to deeper docs.
- Point, don't paste: "rounding rules: see `billing/rounding.py` and `docs/decisions/0003-rounding.md`", not the rules themselves.
- Only what an agent would get wrong without being told. Skip anything a linter, formatter, type checker or test already enforces.
- Per-directory CLAUDE.md files only where a subtree has its own rules.

**Comments:** explain why, a constraint or a non-obvious choice, in one line. Never narrate what the next line does.

## What goes in vs. what stays out
Test for every line: would a capable agent or new engineer, reading only the code, get this wrong or waste time without it? If not, cut it.

**Goes in:**
- Rules that hold everywhere and aren't visible locally ("no real customer data", "never merge PRs", "this folder is live").
- Commands you'd otherwise have to guess, with how to tell they worked.
- Where things are: entry points, the one file that owns a concern.
- Decisions an agent would plausibly reverse, with the reason that still applies.
- Domain terms the code uses but doesn't define.
- Things outside the repo: services, data sources, where credentials live, who approves what.
- Known traps: the bug that looks like a feature, the test that's slow on purpose.

**Stays out:**
- Anything the code, types, tests, linter or formatter already says or enforces.
- Function-by-function descriptions, file listings deeper than the top level, restated schemas.
- History and process: who decided, what was tried first, meeting outcomes, timelines. That's what git log and PRs are for.
- Status that goes stale fast: current sprint, TODO lists, "in progress" notes, version numbers that a lockfile already holds.
- Generic advice any engineer knows ("write tests", "use meaningful names").
- Aspirations and roadmap ("we plan to add…").
- Secrets and personal data, ever.

**Gray zone, decide once:** examples go in reference and how-tos only if they run; architecture diagrams go in only when the flow spans 3+ components and isn't obvious from the entry point; a decision goes in only if undoing it would cost real time.

## Fighting doc bloat
Agents append by default: every task adds a line, nobody removes one. Treat doc length as a budget, not a log.
- **Hard budgets, checked in CI:** CLAUDE.md ≤100 lines, README ≤150, each ADR ≤15, each how-to ≤1 screen of steps. Over budget fails the check; the fix is cutting, not raising the cap.
- **Edit, don't append.** A change to a doc first looks for the existing line it supersedes and rewrites it. New sections need a reason a current one can't hold the content.
- **Net-zero by default.** A PR that grows docs states in its body what it replaced or why growth is necessary. A doc diff that's only additions gets a second look in review.
- **One home per fact.** If a fact exists in two places, delete one and link. Duplicates are where drift starts.
- **Staleness checks in CI:** paths, commands and symbols named in docs must still exist (grep the repo; run the commands where cheap). Broken references fail the build.
- **A pruning pass on a schedule.** A separate agent run (monthly, or every N merged PRs) whose only job is deletion: remove what fails the in/out test, merge near-duplicates, collapse superseded ADRs to their one-line pointer. Measured by lines removed; it may not add content.
- **Agents' notes go elsewhere.** Session learnings, task logs and "I discovered that…" belong in the PR description or the agent's own memory, not the repo docs, unless they pass the in/out test.

## Keeping docs true
- Docs change in the same PR as the code they describe. A PR that changes behavior without touching its doc gets sent back.
- Generate reference from code (OpenAPI from FastAPI/pydantic, typed API clients) instead of writing it by hand.
- Check in CI where cheap: broken links, commands in the README that actually run, examples that execute.
- Delete stale docs. A missing doc is better than a wrong one.

## Review checklist
`make gate` must call `scripts/doc_check.py <repo>` (stdlib Python; line budgets and stale backticked paths).
1. Each page is one Diátaxis type, and its title says what the reader gets or does.
2. The first sentence states the outcome. Steps are numbered and each one is verifiable.
3. Every command and sample was run, and its output is shown.
4. Nothing restates what the code already says. Why, where, invariants and commands are present.
5. CLAUDE.md is under ~100 lines and points to detail instead of containing it.
6. ADRs follow the fixed shape, read as the current rule, and contain no story of how it was decided.
7. Every line passes the in/out test above; nothing in the stays-out list made it in.
8. Docs are within budget, and any growth in the diff is justified in the PR.
9. Terms match the code and UI. No filler words, no "click here", no future promises.

## Sources
Not re-read for this version; they were cited by the skill it was generalized from, so treat the summaries above as known rather than freshly read.
- Stripe docs: teardowns by Moesif ([moesif.com/blog](https://www.moesif.com/blog)) and Mintlify ([mintlify.com/blog](https://mintlify.com/blog)).
- [Diátaxis](https://diataxis.fr).
- [Google developer documentation style guide highlights](https://developers.google.com/style/highlights).
- [Write the Docs: Docs as Code](https://www.writethedocs.org/guide/docs-as-code/).
- Agent context files: Anthropic's Claude Code docs on [memory and CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory), plus what has held up in practice (general knowledge).
