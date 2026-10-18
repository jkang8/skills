# What goes in vs. what stays out

Test for every line: would a capable agent or new engineer, reading only the code, get this wrong or waste time without it? If not, cut it.

## Goes in
- Rules that hold everywhere and aren't visible locally ("no real customer data", "never merge PRs", "this folder is live").
- Commands you'd otherwise have to guess, with how to tell they worked.
- Where things are: entry points, the one file that owns a concern.
- Decisions an agent would plausibly reverse, with the reason that still applies.
- Domain terms the code uses but doesn't define (e.g. tenant, seat, settlement, chargeback).
- Things outside the repo: services, data sources, where credentials live, who approves what.
- Known traps: the bug that looks like a feature, the test that's slow on purpose. Examples: "the held-out eval set is frozen", "this folder is a live install".

## Stays out
- Anything the code, types, tests, linter or formatter already says or enforces.
- Function-by-function descriptions, file listings deeper than the top level, restated schemas.
- History and process: who decided, what was tried first, meeting outcomes, timelines. That's what git log and PRs are for.
- Status that goes stale fast: current sprint, TODO lists, "in progress" notes, version numbers that a lockfile already holds.
- Generic advice any engineer knows ("write tests", "use meaningful names").
- Aspirations and roadmap ("we plan to add…").
- Secrets and personal data, ever.

## Gray zone, decide once
- Examples go in reference and how-tos only if they run.
- Architecture diagrams go in only when the flow spans 3+ components and isn't obvious from the entry point.
- A decision goes in only if undoing it would cost real time.

## Fighting bloat, in detail
- **Hard budgets, checked in CI** (`../scripts/doc_check.py`): over budget fails; the fix is cutting, not raising the cap.
- **Edit, don't append.** A change first looks for the existing line it supersedes and rewrites it. A new section needs a reason a current one can't hold the content.
- **Net-zero by default.** A doc diff that's only additions gets a second look in review.
- **One home per fact.** Duplicates are where drift starts.
- **Staleness checks in CI:** paths, commands and symbols named in docs must still exist.
- **A pruning pass on a schedule.** A separate agent run (monthly, or every N merged PRs) whose only job is deletion: remove what fails the in/out test, merge near-duplicates, collapse superseded ADRs to their one-line pointer. Measured by lines removed; it may not add content.
- **Agents' notes go elsewhere.** Session learnings, task logs and "I discovered that…" belong in the PR description or the agent's own memory unless they pass the in/out test.
