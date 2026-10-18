# Sources and what each one taught

**Read** means the source was read when the rules were written (2026-10-18). **Known** means it was written from general knowledge of the source, not a fresh reading; check the source before relying on a specific claim. Each line summarizes; follow the link for the original.

## Interaction details
- **Vercel, Web Interface Guidelines** (read; [vercel.com/design/guidelines](https://vercel.com/design/guidelines)): keyboard everywhere; `:focus-visible` rings never covered by sticky chrome; hit target at least 24px (44px on mobile); mobile inputs at least 16px so iOS doesn't zoom; never block paste or zoom; loading buttons keep their label; skeletons get a short show delay and a minimum display time so they don't flicker; URL as state; optimistic updates with rollback or Undo; ellipsis on follow-up labels; confirm or Undo destructive actions; tooltip delay only on the first in a group; `overscroll-behavior: contain` in modals; scroll position restores on Back.
- **Emil Kowalski, design engineering** (read; [github.com/emilkowalski/skills](https://github.com/emilkowalski/skills)): unseen details compound; name exact transition properties; nothing appears from nothing (scale 0.95 plus opacity, not scale 0); ease-out for entering UI; buttons press to `scale(0.97)`; popovers scale from their trigger, modals stay centered.
- **Rauno Freiberg, Invisible Details of Interaction Design** (known): interactions follow learned physical metaphors; respond to input immediately; the best detail is the one users never notice.

## Product design practice
- **Linear, "How we redesigned the Linear UI"** (read; [linear.app/now](https://linear.app/now)): reduce visual noise in chrome, keep alignment strict, raise hierarchy and density of navigation; a redesign evolves the product instead of taking it apart.
- **Stripe dashboard** (known): trust through clarity; money is precise, labeled and tabular; status uses words plus color, never color alone.
- **Vercel Geist, GitHub Primer, Apple HIG** (known): small token sets, system-consistent components, content before chrome, platform conventions over novelty.

## UX research
- **Nielsen Norman Group, 10 usability heuristics** (known; [nngroup.com/articles/ten-usability-heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)): system status, real-world match, user control (Undo), consistency, error prevention, recognition over recall, shortcuts for experts, minimalist design, helpful errors, help in context.
- **Laws of UX, Jon Yablonski** (known; [lawsofux.com](https://lawsofux.com)): Fitts, Hick, Jakob, Miller and chunking, Doherty threshold (respond in under 400ms), aesthetic-usability effect (polish buys patience, so it can't hide broken flows).
- **Refactoring UI, Wathan and Schoger** (known): hierarchy from weight and color before size; de-emphasize secondary text; start with too much whitespace; fixed type and spacing scales; spacing and background shifts before borders.

## AI-native patterns
- **The Shape of AI, Emily Campbell** (read; [shapeof.ai](https://www.shapeof.ai)): footprints, prompt details, disclosure, caveats, follow-up, suggestions and templates, data ownership.
- **Brent Haskins, agent interface contract and streaming UX** (read; [brenthaskins.com](https://brenthaskins.com)): citations placed inline and always shown; streaming must advance understanding; show progress against a known plan instead of a spinner.
- **Linear, agents developer guide** (read; [linear.app/developers/agents](https://linear.app/developers/agents)): agents act inside existing workflows and objects rather than in a separate chat surface.
