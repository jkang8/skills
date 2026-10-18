# Component library: shadcn registry `@<your-registry>` (repo `<org>/ui`)

One private repo holds your restyled shadcn components as a shadcn registry, shared by every project. Domain-free: no app content ever goes in it (a domain guard runs in its gate).

## Registry
- `registry.json` at the repo root lists every item (the tokens/theme item, primitives, composites, with their `registryDependencies`); `shadcn build` writes `public/r/<name>.json`. A `theme` item installs the tokens into the app's CSS.
- **Apps:** `components.json` declares `"registries": {"@<your-registry>": {"url": "<raw URL>/public/r/{name}.json", "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}`; then `pnpm dlx shadcn add @<your-registry>/theme @<your-registry>/button`. Components land in `web/src/components/ui/` as app code.
- **Updates:** fix in the registry first, then re-run `shadcn add --overwrite` in each app. Local edits in an app are allowed only when truly app-specific, and noted in that app's INVENTORY.md. Tradeoff: copied components don't auto-update; switch to a published package once ~5 apps share it.
- **Its own gate:** lint, types, Vitest, `shadcn build` clean, domain guard, and Playwright screenshots of its catalog.

## Modular
Each piece can be used, tested and replaced on its own, and layers only depend downward.
- **Layers:** `tokens/` (CSS variables, light and dark, the only place colors and sizes are defined) -> `primitives/` (Button, Input, Badge... thin wrappers over Radix/shadcn) -> `composites/` (DataTable, Command, Stat, EmptyState, AppShell, built only from primitives). Apps import from the library, never the reverse. Composites never import app code or fetch data; they take props.
- **One folder per component:** `button/{button.tsx,button.test.tsx,index.ts}`. Variants via `cva`, class merging via `cn()`. Props are typed and documented by their types, not prose.
- **Pick what you need:** each component is its own registry item, so an app adds only what it uses.
- **Catalog:** a small Vite app in `<org>/ui` renders every component and variant in both themes. Playwright screenshots it in the gate; that's the visual regression check and the design review surface. No Storybook unless the user asks.
- **Closed set:** adding a component follows ui-design-system's INVENTORY.md rule. A new variant beats a new component; a composite beats a new primitive.
- **App-specific components** (built from library parts, used by one app) live in the app's `web/src/components/`. Promote one to the library when a second app needs it.
