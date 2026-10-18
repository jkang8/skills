---
name: repo-setup
description: "Use when starting a new repo: a default scaffold stack."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [scaffold, stack, uv, pydantic, fastapi, postgres, react, pnpm]
    related_skills: [coding-orchestration, ui-design-system, doc-writing]
---

# Repo setup (default stack)

## When to use
Any new project the user starts, unless they name a different stack. Put this in the coding agent's brief (coding-orchestration). Scaffold only what the project uses: no frontend for a CLI, no Postgres until there's data to keep.

Install the latest versions with `uv add` / `pnpm add` at scaffold time. Don't pin versions from memory.

## Local overrides
If `repo-setup.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here and its rules add to these; where they conflict, the override wins.

## Backend: `api/`
- **Python via uv:** `uv init --package`, `src/` layout, `uv add` and `uv add --dev`, commit `uv.lock`. If uv isn't on `PATH` (common in agent shells), use the full binary path from the override.
- **Pydantic v2 for every boundary:** request and response bodies, config (`pydantic-settings`, read from env), external data and anything persisted. Use frozen models for records, `StrEnum` for closed sets, and keep internal-only helpers as plain dataclasses.
- **FastAPI:** routers by domain, typed `response_model`s. OpenAPI is the API contract.
- **Postgres:** SQLAlchemy 2 (typed `Mapped[]` models) with psycopg 3 and Alembic migrations. ORM models stay separate from the Pydantic API models: map between them explicitly, don't return ORM rows from routes.
- **Local DB:** `docker compose` with a single `postgres` service and a named volume. Tests run against a real Postgres (a separate test database, or testcontainers), not SQLite.
- **Quality:** ruff (lint and format) and pyright (strict on `src/`), plus pytest. All three run in the gate.

## Frontend: `web/`, pnpm workspace
- **pnpm, Vite, React, TypeScript (strict)** in `web/`. Components come from your shared shadcn registry `@<your-registry>` (below), added with `pnpm dlx shadcn add @<your-registry>/<name>`.
- **Tailwind v4 and shadcn/ui,** restyled to the ui-design-system tokens and its closed component set.
- **TanStack Query** for server state and **TanStack Router** for typed routes and URL-backed filters. Don't add a global store until something actually needs one.
- **API types are generated from OpenAPI** (`@hey-api/openapi-ts` or `openapi-typescript`) into `web/src/api/`. Never hand-write them, and regenerate in the gate.
- **Quality:** Vitest for unit tests and Playwright for a smoke test plus screenshots. ESLint and Prettier, or Biome, whichever the template ships; pick one.

## Component library: shadcn registry `@<your-registry>` (repo `<org>/ui`)
One private repo holds your restyled shadcn components as a shadcn registry, shared by every project. Domain-free: no app content ever goes in it (a domain guard runs in its gate).
- **Registry:** `registry.json` at the repo root lists every item (the tokens/theme item, primitives, composites, with their `registryDependencies`); `shadcn build` writes `public/r/<name>.json`. A `theme` item installs the tokens into the app's CSS.
- **Apps:** `components.json` declares `"registries": {"@<your-registry>": {"url": "<raw URL>/public/r/{name}.json", "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}`; then `pnpm dlx shadcn add @<your-registry>/theme @<your-registry>/button`. Components land in `web/src/components/ui/` as app code.
- **Updates:** fix in the registry first, then re-run `shadcn add --overwrite` in each app. Local edits in an app are allowed only when truly app-specific, and noted in that app's INVENTORY.md. Tradeoff: copied components don't auto-update; switch to a published package once ~5 apps share it.
- **Its own gate:** lint, types, Vitest, `shadcn build` clean, domain guard, and Playwright screenshots of its catalog.

Modular means each piece can be used, tested and replaced on its own, and layers only depend downward.
- **Layers:** `tokens/` (CSS variables, light and dark, the only place colors and sizes are defined) -> `primitives/` (Button, Input, Badge... thin wrappers over Radix/shadcn) -> `composites/` (DataTable, Command, Stat, EmptyState, AppShell, built only from primitives). Apps import from the library, never the reverse. Composites never import app code or fetch data; they take props.
- **One folder per component:** `button/{button.tsx,button.test.tsx,index.ts}`. Variants via `cva`, class merging via `cn()`. Props are typed and documented by their types, not prose.
- **Pick what you need:** each component is its own registry item, so an app adds only what it uses.
- **Catalog:** the `<org>/ui` repo has a small Vite app rendering every component and variant in both themes. Playwright screenshots it in the gate; that's the visual regression check and the design review surface. No Storybook unless the user asks.
- **Closed set:** adding a component follows ui-design-system's INVENTORY.md rule. A new variant beats a new component; a composite beats a new primitive.
- **App-specific components** (built from library parts, used by one app) live in the app's `web/src/components/`. Promote one to the library when a second app needs it.

## Repo root
- `Makefile` (or `justfile`) with `dev` (db, api and web together), `test`, `gate` (lint, types, tests, type generation diff) and `db-migrate`.
- `.env.example` with every variable and no real values. `.env` is gitignored.
- **CI is optional.** Ask the user at scaffold time if it isn't clear. Default to no CI for prototypes, demos and solo experiments; add it once the repo has collaborators, automated agents opening PRs, or something deployed. With CI: `.github/workflows/ci.yml` runs `make gate` on PRs, and `main` gets branch protection requiring it. Without CI: agents run `make gate` locally and paste the result in the PR body. Either way, the user merges.
- Adding CI later is one step: drop in the workflow (it only calls `make gate`) and turn on branch protection. Keep all check logic in the Makefile, never in the workflow, so the switch costs nothing.
- `CLAUDE.md` (with `AGENTS.md` symlinked to it) and a README, written per the doc-writing skill.
- Private repo unless the user says otherwise. Commit with the user's GitHub noreply address (`<user>@users.noreply.github.com`, set in the override) so a personal email never lands in history.

## Layout
```
api/   src/<pkg>/{models,db,routers,services}/  tests/  alembic/  pyproject.toml
web/   src/{api,routes,components/ui,lib}/   components.json (registry @<your-registry>)

# separate repo <org>/ui (shadcn registry):
registry/{tokens,primitives,composites}/<component>/  registry.json  public/r/  catalog/
compose.yaml  Makefile  .env.example  CLAUDE.md  README.md  [.github/workflows/ci.yml if CI]
```

## Done when
`make dev` brings up db, api and web from a fresh clone. `make gate` passes locally (and in CI, if enabled). One route goes end to end (a DB row, then an API response, then a generated type, then rendered in the UI), with a test at each layer.
