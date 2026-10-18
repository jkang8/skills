---
name: architecture
description: "Use when structuring code: modules, helpers, boundaries."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [architecture, design, modularity, abstraction, refactoring, review]
    related_skills: [coding-orchestration, repo-setup, doc-writing]
---

# Architecture: engineering taste

## When to use
Any code an agent writes or reviews in your repos: new features, refactors, reviews. Put it in the coding agent's brief (coding-orchestration). Taste here means code a new reader can change safely in one sitting.

## Local overrides
If `architecture.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its rules add to these and win on conflict.

## Core rules
1. **Deep modules over shallow ones.** A module earns its place by hiding a lot behind a small interface (Ousterhout). A wrapper that forwards arguments and adds a name is cost, not structure.
2. **Hide decisions, not just code.** Split along things likely to change independently: a data source, a rule set, a vendor API, the UI (Parnas). Each decision lives in exactly one module.
3. **Functional core, imperative shell.** Business logic is pure functions over typed data (Pydantic models, TS types). I/O (DB, HTTP, files, clock, randomness) sits at the edges and is passed in. Pure code gets the tests; the shell stays thin.
4. **Dependencies point one way.** routes -> services -> domain; UI -> API client -> generated types. Domain code never imports frameworks, routers or ORM sessions. No cycles.
5. **Types are the contract.** Validate at the boundary once, then trust the types inside. Make invalid states unrepresentable (enums, discriminated unions, frozen models) instead of checking flags everywhere.

## Helpers vs. locality
Default to locality: keep behavior where it's used, so a reader sees what a thing does without jumping files (locality of behavior).
- **Extract a helper when** it's used in 3+ places with the same meaning (rule of three), OR it names a real domain concept (`business_days_between`), OR it isolates something hard (date math, money, parsing) worth its own tests.
- **Don't extract when** it's used once, the name just restates the body (`get_user_by_id_from_db`), or callers would need flags to vary it. Two similar blocks that may diverge stay duplicated: duplication is cheaper than the wrong abstraction (Metz).
- **Inline a helper when** it has one caller, or its callers keep adding parameters to bend it.
- A function fits on one screen and stays at one level of abstraction. Long is fine if it reads top to bottom; deeply nested is not.
- Private helpers sit next to their caller, below it. Shared ones go in the module that owns the concept, never in `utils.py` / `helpers.ts` grab bags.

## Reuse
- Reuse what exists first: the codebase's own helpers, then the stdlib, then installed deps.
- Design for reuse only on the second real use. The first version is concrete.
- Reusable means a stable interface and no knowledge of callers. If it imports from its caller's layer, it isn't reusable, it's tangled.
- Share across repos only when two live projects need it (same rule as the UI registry).

## Separation of concerns
- One reason to change per module. Signs it's mixed: a function that queries, decides and formats; a component that fetches and renders; a model with HTTP code.
- Config, secrets and environment come in through one settings object, never read ad hoc.
- Errors: raise typed errors in the core, translate them to HTTP/UI messages in the shell. Never swallow them.
- Side effects are visible in the signature (it takes a `db`, `client`, `now`).

## Layout
- Group by feature, then by layer inside it, once a repo has more than ~3 features (`notes/{models,service,routes}.py`). Small repos stay flat.
- File names say what's in them. No `misc`, `common`, `core2`, `new_`.
- Tests mirror source paths. A test that needs heavy mocking means the code mixes I/O and logic: fix the code.

## Smells (fix or justify)
Speculative generality (options, plugins, base classes with one subclass) · pass-through layers · manager/handler/processor names · boolean parameters that switch behavior · god files over ~500 lines · global mutable state · the same constant in two places · `utils` grab bags · circular imports · DTO-to-DTO mapping chains with no logic · comments explaining what instead of why.

## Review checklist
1. Can each module be described in one sentence without "and"?
2. Does every helper pass the extract test above? Any one-caller wrappers to inline?
3. Is business logic pure and tested without mocks, with I/O at the edges?
4. Do imports point one way, with no domain code importing frameworks?
5. Could a new reader change one feature by reading one folder?
6. Is anything built for a future nobody requested? Remove it.
7. Did the change reuse existing code instead of adding a parallel version?

Sources: `references/sources.md`.
