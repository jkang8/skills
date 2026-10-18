# Build defaults (paste into briefs)

## Stack
- Python: **uv** project (`uv init`, `uv add`), **pydantic v2** models for every record crossing a boundary, FastAPI for HTTP.
- Frontend: current mainstream stack managed with **pnpm**: Vite + React + TypeScript + Tailwind v4 + shadcn/ui. Ask the agent to argue for Next.js first if it thinks SSR/routing needs it.
- Generate frontend API types from the backend's OpenAPI schema, never hand-copied, so the two can't drift.
- One command runs everything (`make dev` or a script); README setup in about 5 lines.
- Tests first for logic (checks, parsers, generators); seeded synthetic data with known cases both ways so a test proves "finds exactly these".

## Design bar: tasteful, AI-native, slick, no slop
- References: Linear, Vercel, Stripe dashboards. Dense, calm, data-forward.
- One neutral palette plus one accent; a real type scale (Geist/Inter); tabular numerals for money; consistent spacing; dark and light both correct.
- Motion 150–250ms, no bounce.
- **Banned:** purple/blue gradients, glassmorphism, sparkle/✨ icons, emoji, "AI-powered" badges, robot mascots, marketing hero sections, lorem ipsum, stock illustrations, shadows on everything, centered-everything layouts, rounded-3xl cards everywhere.
- Copy short and specific ("3 invoices overdue", not "Unlock hidden revenue").
- AI-native features must earn their place (per-item plain-English explanation, ⌘K command bar, a visible run/step view) and work offline with a deterministic fallback so a live demo can't break.
- Gate: the agent screenshots every screen in both themes and reviews them against the banned list before calling it done.

The full rules are in the `ui-design-system` skill; this is the short version for briefs.

## Recorded demo
- Playwright script kept in the repo (`demo/record.ts`) so it can be rerun: 1440×900, 60–90s, human pacing (cursor moves, short pauses, no jump cuts), scripted flow through the key screens and one theme toggle.
- Convert to H.264 mp4 with ffmpeg; save to `demo/demo.mp4`; report path and length.
