Score each item 1 (clearly met) or 0 (not met or can't tell).
1. Python uses uv conventions (pyproject with a src/ layout; no requirements.txt as the source of truth).
2. Pydantic models at the API boundary and for config (settings read from env).
3. ORM models are separate from API models, and routes don't return ORM rows.
4. Postgres via SQLAlchemy 2 typed models and Alembic migrations, with a docker compose file for local Postgres (or no DB when the task needs none).
5. Tests target a real Postgres, not SQLite (or no DB when the task needs none).
6. Frontend (when present): pnpm, Vite, React, strict TypeScript, Tailwind; API types generated from OpenAPI rather than hand-written.
7. A Makefile (or justfile) with dev, test and gate targets, and the gate runs lint, types and tests.
8. .env.example lists the variables with no real values, and .env is gitignored.
9. CLAUDE.md exists with commands and rules (AGENTS.md pointing at it is a plus), plus a short README.
10. Scaffolds only what the task needs (no frontend for an API-only task, no extra services).
