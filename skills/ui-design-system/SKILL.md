---
name: ui-design-system
description: "Use when building UI: tokens, closed component set, review."
version: 1.3.3
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, components, design-system, frontend, accessibility]
    related_skills: [coding-orchestration, repo-setup, demo-video]
---

# UI design system

## When to use
Any product UI the user asks for: dashboards, demos, internal tools. Put these rules in the coding agent's brief (see coding-orchestration). The agent that built the UI checks screenshots against the checklist before the user sees anything. For an independent review, see the `review` skill. To record a captioned walkthrough of the UI, use the `demo-video` skill.

The bar: tasteful, AI-native, slick, no AI slop. Reference points: Linear, Vercel, Stripe dashboards. Dense, calm, data-forward.

## Local overrides
If `ui-design-system.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here; its rules add to these and win on conflict.

## Stack
Vite + React + TypeScript + Tailwind v4 + shadcn/ui (Radix underneath), pnpm. Icons from lucide only. Geist (or Inter) for text, Geist Mono for codes and IDs.

## Tokens (the only values allowed)
- **Color:** one neutral ramp (zinc), ONE accent, semantic success/warning/danger. All through CSS variables, light and dark. No hex literals or Tailwind palette classes outside the token file.
- **Type:** 12 / 13 / 14 / 16 / 20 / 24 / 32; body 14. Weights 400 and 500, 600 for figures only. `tabular-nums` for money and counts.
- **Spacing:** 4px grid (Tailwind 1, 2, 3, 4, 6, 8, 12, 16). One density per screen.
- **Radius:** 6px controls, 8px panels. Nothing rounder.
- **Elevation:** 1px border by default; shadows only on floating layers (menus, dialogs, toasts).
- **Motion:** 150–200ms ease-out, opacity and translate only, no bounce. Respect `prefers-reduced-motion`.

## The component set (closed)
Only these, from your shadcn registry `@<your-registry>` (repo `<org>/ui`; setup in repo-setup), restyled to the tokens. Fixes go to the registry first, then get re-added in apps.

Button (primary / secondary / ghost / destructive; sm, md) · Input · Textarea · Select · Checkbox · Switch · Badge (neutral + semantic) · Panel (the one card) · Stat (label, figure, delta) · DataTable (sort, filter, row click, sticky header) · Tabs · Dialog · Sheet · DropdownMenu · Popover · Tooltip · Command (⌘K) · Toast · Skeleton · EmptyState · PageHeader · AppShell (sidebar + content).

Pages compose these and nothing else; page files hold no styling beyond layout (flex/grid/gap/width).

Adding one: only when composing the set can't meet the need. First write three lines in `INVENTORY.md` in `<org>/ui`: what it is, which components were tried and why they fell short, who uses it. Overlapping components: remove one. A variant beats a new component.

## UX rules
- Answer first: the main number or decision top-left; detail one click away (Sheet or Dialog), never a separate page.
- Every data view has loading (Skeleton matching the layout), empty (what's missing + the one fixing action) and error (what failed + retry) states.
- Tables: numbers right-aligned; truncated text shows the full value on hover; filter bar above; filters in the URL.
- Keyboard: everything reachable by Tab, visible focus rings, Esc closes layers, ⌘K opens Command.
- Accessibility: WCAG AA in both themes, labels on every input, `aria-label` on icon-only buttons.
- Buttons and primary actions are **short verb phrases, up to 3 words, ideally fewer**: "Approve", "Fix notes", "Re-run". Never a full sentence in a button, never "we"/"I" ("Notify me", not "We'll email you"), never an explanation inside the control. A sentence that must be shown goes in the nearby text; if a user needs to know what clicking does first, use a Tooltip or a one-line helper under the button.
- Labels: short, specific, sentence case ("3 invoices overdue", not "Unlock hidden revenue"). No marketing copy in the app.
- Sentences: one idea each, about 12 words at most, with no parentheticals, semicolons or chained clauses.
- State what is, not what isn't: "You approve every draft", not "Nothing is sent without you". Explain totals with layout (sections), not negative tags. Hide zero-states like "$0 handled".
- Show a figure once per card, never twice. At most one pill per row; the rest is plain text.
- Don't template list items with labeled slots (Happened / Impact / Next). A list item is a specific title sentence (names, dates, numbers), one muted meta line, the amount once, and one action. Specificity replaces labels.
- Write for the least technical reader: one action leads per view, detail is one click away, and the trust guarantee is said once (more in `references/clarity.md`).
- AI features earn their place by doing work, not describing it: notice things before anyone asks, prepare the fix, hand a person a decision, and show the source. Numbers people must audit (totals, rules, statistics) stay deterministic; AI reads, flags and drafts. Fall back to deterministic output when AI is unavailable.

## Interaction, hierarchy and AI-native rules
Follow `references/patterns.md`: exact transition properties, entry from `scale(0.95)`, 24px hit targets, skeleton show delay and minimum time, optimistic updates with Undo, ellipsis labels, emphasis by weight and color before size, quiet chrome, strict alignment, and the AI patterns (footprints, inline citations, muted "Generated" label, progress against a plan, edit/accept/undo, honest limits).

## Clarity for the user
Follow `references/clarity.md`: write for the least technical user; each screen answers "what do I do next, and what is it worth?"; one headline number; counts that reconcile; one plain sentence and one named action per item; details behind a click; trust guarantees stated once; progress and a done state; role-specific views; one-story demos.

## Scores, tiers and thresholds
For any value bucketed into levels (confidence, risk, urgency, priority, health, impact):
- **Define each scale once** in one pure, tested module with named threshold constants. UI reads tiers from it, never hardcodes cutoffs.
- **One scale per meaning.** Don't reuse a color or shape for two different scales on one screen.
- **Quiet by default, loud only where action is needed.** Most tiers are neutral; only the tier that needs a decision gets a semantic tone. Max one semantic color per row.
- **Never color alone.** Pair tone with a word and/or shape ("High", a segmented meter, "Due in 6 days"). AA contrast in both themes.
- **Order by weight before hue.** Rank magnitude with weight and position; reserve color for state.
- **Relative bands beat fixed numbers** when users differ in scale (bands as a share of their own baseline).
- **Show the rule.** Hover or footprint states the value and the threshold it crossed ("0.91, High at 0.85"). Uncertain values show as a range (thin interval bar), not a gauge or a falsely precise number.
- **Low-confidence AI output is held, not hidden:** labeled "Needs review" and kept out of headline totals.
- **Sort by what the user acts on** (urgency, then impact) and label the sort.

## Banned (slop indicators)
Purple/blue gradients · glassmorphism · ✨ sparkle icons · emoji in UI · "AI-powered" or "Magic" badges · robot or brain mascots · hero sections inside an app · lorem ipsum · stock illustrations · shadows on every card · rounded-2xl/3xl · centered-everything layouts · gradient text · animated blobs · typing-effect text for content · more than one accent color.

## Review checklist (before showing the user)
1. Screenshot every screen in light and dark at 1440×900, and the main screen at 390px wide.
2. Grep for violations: hex colors and palette classes outside tokens, `rounded-2xl|3xl`, `bg-gradient`, `backdrop-blur`, emoji, components imported from outside `components/ui/`.
3. Check each screen against the banned list, the UX rules and `references/patterns.md`. Fix, then re-shoot. Watch grid rows: a panel stretched to match a taller neighbor leaves dead space at its bottom (use `items-start` or size the row to content). When a headline figure differs from a total shown elsewhere on the page, show the bridge (total -> adjustments -> headline) on the page; a reader asks about any unexplained gap.
4. Check loading, empty and error states by forcing each one.
5. Walk the NN/g heuristics once: system status visible, Undo available, consistent with the rest of the app, errors prevented or explained, shortcuts for experts.
6. Every AI output shows its footprints and its sources, and can be edited or undone.
7. Every scored or tiered value comes from one scale module, shows its rule, and doesn't rely on color alone.
8. Each screen answers "what do I do next, and what is it worth?" for the least technical user, with one headline number, counts that reconcile, and details behind a click (`references/clarity.md`).
9. `make gate` calls `scripts/design_lint.py <web dir>` and it prints `design lint: clean`.

Sources and what each contributed: `references/sources.md`. Re-read it when a design call isn't covered here.
