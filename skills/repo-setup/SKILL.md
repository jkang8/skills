---
name: repo-setup
description: "Use when starting a new repo: a default scaffold stack."
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [scaffold, stack, uv, pydantic, fastapi, postgres, react, pnpm]
    related_skills: [coding-orchestration, ui-design-system, doc-writing]
---

# Repo setup (default stack)

## When to use
Any new project the user starts, unless they name a different stack. Put this in the coding agent's brief (coding-orchestration). Scaffold only what the project uses: no frontend for a CLI, no Postgres until there's data to keep. Install latest versions with `uv add` / `pnpm add` at scaffold time; don't pin versions from memory.

## Local overrides
If `repo-setup.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here; its rules add to these and win on conflict.

## Backend: `api/`
- **uv:** `uv init --package`, `src/` layout, `uv add` / `uv add --dev`, commit `uv.lock`. If uv isn't on `PATH`, use the full path from the override.
- **Pydantic v2 at every boundary:** request/response bodies, config (`pydantic-settings` from env), external data, anything persisted. Frozen models for records, `StrEnum` for closed sets, plain dataclasses for internal helpers.
- **FastAPI:** routers by domain, typed `response_model`s. OpenAPI is the contract.
- **Postgres:** SQLAlchemy 2 (typed `Mapped[]`), psycopg 3, Alembic. ORM models stay separate from API models; map explicitly, never return ORM rows from routes.
- **Local DB:** `docker compose` with one `postgres` service and a named volume. Tests use a real Postgres (test database or testcontainers), not SQLite.
- **Quality:** ruff (lint + format), pyright (strict on `src/`), pytest. All in the gate.

## Frontend: `web/`, pnpm workspace
- **pnpm, Vite, React, TypeScript (strict).** Components from your shadcn registry: `pnpm dlx shadcn add @<your-registry>/<name>`.
- **Tailwind v4 + shadcn/ui,** restyled to the ui-design-system tokens and closed set.
- **TanStack Query** for server state, **TanStack Router** for typed routes and URL-backed filters. No global store until something needs one.
- **API types generated from OpenAPI** (`@hey-api/openapi-ts` or `openapi-typescript`) into `web/src/api/`. Never hand-written; regenerated in the gate.
- **Quality:** Vitest, Playwright smoke test + screenshots, and one of ESLint + Prettier or Biome (whichever the template ships).

## Component library
One private repo `<org>/ui` holds the restyled components as a shadcn registry `@<your-registry>`, shared by every app and domain-free. Rules: fix in the registry first, then `shadcn add --overwrite` in apps; layers depend downward only (tokens -> primitives -> composites); one folder per component; a variant beats a new component; promote an app component when a second app needs it. Full setup: `references/component-library.md`.

## Repo root
- `Makefile` (or `justfile`): `dev` (db, api, web together), `test`, `gate` (lint, types, tests, type-generation diff), `db-migrate`.
- `.env.example` with every variable and no values; `.env` gitignored.
- **CI is optional.** Ask the user if it isn't clear. No CI for prototypes, demos and solo experiments; add it with collaborators, PR-opening agents or a deployment. With CI: `.github/workflows/ci.yml` runs `make gate` on PRs and `main` requires it. Without: agents run `make gate` and paste the output in the PR. Either way, the user merges.
- All check logic lives in the Makefile, never the workflow, so adding CI later is one file plus branch protection.
- `AGENTS.md` (the agent context file), `CLAUDE.md` containing only `@AGENTS.md`, and a README, per doc-writing.
- Private repo unless the user says otherwise. Commit with the user's GitHub noreply address (`<user>@users.noreply.github.com`, from the override) so no personal email lands in history.

## Layout
```
api/   src/<pkg>/{models,db,routers,services}/  tests/  alembic/  pyproject.toml
web/   src/{api,routes,components/ui,lib}/   components.json (registry @<your-registry>)

# separate repo <org>/ui (shadcn registry):
registry/{tokens,primitives,composites}/<component>/  registry.json  public/r/  catalog/
compose.yaml  Makefile  .env.example  AGENTS.md  CLAUDE.md  README.md  [.github/workflows/ci.yml if CI]
```

## Done when
1. `make dev` brings up db, api and web from a fresh clone.
2. `make gate` passes locally (and in CI, if enabled), and it calls `scripts/stack_check.py <repo>`, which prints `stack check: clean`.
3. One route goes end to end (DB row, API response, generated type, rendered in the UI) with a test at each layer.
