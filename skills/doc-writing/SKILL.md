---
name: doc-writing
description: "Use when writing docs, READMEs or agent context files."
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [docs, writing, readme, agents-md, claude-md, diataxis, stripe]
    related_skills: [coding-orchestration, ui-design-system, repo-setup]
---

# Doc writing

## When to use
Any doc in a repo you own: README, guides, API reference, architecture notes, ADRs, and the agent context file (AGENTS.md, with CLAUDE.md as a one-line pointer). Put these rules in the coding agent's brief (see coding-orchestration). Reference point: Stripe's docs (why they work: `references/why.md`).

## Local overrides
If `doc-writing.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here; its rules add to these and win on conflict.

## Pick the doc type first (Diátaxis)
Each page is exactly one of these; mixing them is what makes docs muddy.
- **Tutorial:** a guaranteed first success. One path, no choices, every step shows its result.
- **How-to:** a recipe for one real task. Title it as the task ("Rotate an API key").
- **Reference:** exact and complete: fields, types, defaults, errors, limits. Generated from code when possible.
- **Explanation:** why it's built this way and the tradeoffs. No steps.

## Writing rules
- Lead with what the reader gets, in one sentence. Then the steps.
- Second person, active voice. Condition before instruction ("If the build fails, run…").
- Numbered lists for sequences, bullets otherwise. Sentence-case headings. Code font for code, paths, commands, values; bold for UI labels.
- One idea per sentence, one task per page. Cut "simply", "just", "easy", "powerful", "seamless".
- Same term for the same thing everywhere, matching the code and UI.
- Descriptive link text, never "click here".
- Examples run as written, with realistic data and the output shown. Never show a sample you haven't run.
- Unambiguous dates (2026-10-18) and units. Don't pre-announce features.
- Before publishing prose, do a pass for AI-writing tells (a humanizer skill, if you have one).

## Docs carry what code can't
Code is the source of truth for behavior, signatures, data shapes and control flow; make it self-explaining and don't restate it in prose. Docs carry:
- **Why:** one short ADR per real decision, `docs/decisions/NNNN-title.md`.
- **Where:** one line per top-level directory, plus the entry points.
- **Invariants and traps** not visible locally ("never commit real customer data", "this folder is a live install").
- **How to run, test and verify:** exact commands and how to know they worked.
- **Domain language:** a short glossary of terms the code uses.
- **Outside the repo:** services, where credentials live (never values), data sources, who decides.

The in/out test for every line: would a capable agent or new engineer, reading only the code, get this wrong or waste time without it? If not, cut it. Full goes-in, stays-out and gray-zone lists: `references/in-or-out.md`.

## ADRs
- About 10-15 lines, fixed shape: Status (accepted / superseded by NNNN), Date, Decision (one present-tense sentence), Why (2-3 bullets that still apply), Rejected (one line each), Consequences.
- The decision as it stands. No "we first tried", timelines or who said what; git log and PRs hold the story.
- Only decisions an agent or newcomer would otherwise undo.
- A changed decision gets a new ADR; mark the old one superseded in its first line.

## The agent context file (AGENTS.md)
- AGENTS.md is the real file. CLAUDE.md contains only the line `@AGENTS.md`, so Claude Code imports it and other harnesses read AGENTS.md directly. No symlinks.
- Under ~100 lines; it loads into every session.
- In order: purpose paragraph; repo map; commands (setup, run, test, lint, gate); conventions that differ from defaults; hard rules and traps; pointers to deeper docs.
- Point, don't paste ("rounding rules: see `billing/rounding.py`").
- Only what an agent would get wrong untold. Skip what a linter, formatter, type checker or test enforces.
- Per-directory AGENTS.md (plus its one-line CLAUDE.md) only where a subtree has its own rules.

**Comments:** one line on why, a constraint or a non-obvious choice. Never narrate the next line.

## Budgets and bloat
- AGENTS.md ≤100 lines, README ≤150, ADR ≤15, SKILL.md ≤120 with a description ≤60 chars, how-to ≤1 screen of steps. Over budget fails the check; cut, don't raise the cap.
- Edit, don't append: rewrite the line a change supersedes.
- Net-zero by default: a PR that grows docs says what it replaced or why growth is needed.
- One home per fact; delete duplicates and link.
- Agents' session notes go in the PR or their own memory, not repo docs.
- A scheduled pruning run that may only delete: `scripts/prune_docs.sh <repo>` opens one PR, and only if net lines go down and `doc_check.py` gets no worse. Details: `references/in-or-out.md`.

## Keeping docs true
- Docs change in the same PR as the code they describe; a behavior change without its doc goes back.
- Generate reference from code (OpenAPI from FastAPI/pydantic, typed clients).
- CI checks where cheap: broken links, stale paths, README commands that run.
- Delete stale docs. Missing beats wrong.

## Review checklist
1. Each page is one Diátaxis type, and its title says what the reader gets or does.
2. The first sentence states the outcome. Steps are numbered and each one is verifiable.
3. Every command and sample was run, and its output is shown.
4. Nothing restates what the code already says. Why, where, invariants and commands are present.
5. AGENTS.md is under ~100 lines and points to detail instead of containing it; CLAUDE.md is only `@AGENTS.md`.
6. ADRs follow the fixed shape, read as the current rule, and contain no story of how it was decided.
7. Every line passes the in/out test; nothing from the stays-out list made it in.
8. Docs are within budget, and any growth in the diff is justified in the PR.
9. Terms match the code and UI. No filler words, no "click here", no future promises.
10. `make gate` calls `scripts/doc_check.py <repo>` and it prints `doc check: clean`.

Sources: `references/sources.md`.
