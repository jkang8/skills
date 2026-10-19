---
name: ui-design-system
description: "Use when building UI: tokens, closed component set, review."
version: 1.4.0
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, components, design-system, frontend, accessibility]
    related_skills: [coding-orchestration, repo-setup, demo-video]
---

# UI design system

## When to use
Any product UI the user asks for: dashboards, demos, internal tools. Put these rules in the coding agent's brief (see coding-orchestration). The builder checks screenshots against the checklist before the user sees anything. Independent review: the `review` skill. Captioned walkthrough: the `demo-video` skill.

The bar: tasteful, AI-native, no AI slop. References: Linear, Vercel, Stripe. Dense, calm, data-forward.

## Local overrides
If `ui-design-system.local.md` exists in this skill's folder or in `overrides/` at the checkout root this skill came from (resolve symlinks), read it first. It fills the `<placeholders>` and wins on conflict.

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

Pages compose these only; page files hold no styling beyond layout (flex/grid/gap/width).

Add one only when composing the set can't meet the need. First write three lines in `INVENTORY.md` in `<org>/ui`: what it is, what was tried and why it fell short, who uses it. Remove overlapping components; a variant beats a new one.

## Layout & surfaces
- Name the surface first: operate (a work queue), monitor (a dashboard) or brief (a periodic summary). Each gets its own view.
- Work queues are a list plus a detail pane, with one short summary line above the list when it opens.
- Answer first: one headline number or decision top-left. Secondary totals live in a report view; detail is one click away (Sheet or Dialog), never a separate page.
- Every data view has loading (Skeleton matching the layout), empty (what's missing + the one fixing action) and error (what failed + retry) states.
- Tables: numbers right-aligned; truncated text shows the full value on hover; filter bar above; filters in the URL.
- Keyboard: everything reachable by Tab, visible focus rings, Esc closes layers, ⌘K opens Command.
- Accessibility: WCAG AA in both themes, labels on every input, `aria-label` on icon-only buttons.
- Interaction and hierarchy details: `references/patterns.md`.

## Copy
- One idea per sentence, about 12 words. No run-ons, parentheticals or semicolons.
- Say what is, not what isn't: "You approve every draft", not "Nothing is sent without you". Explain totals with layout, not negative tags. Hide zero-states like "$0 handled".
- Labels are short, specific, sentence case ("3 invoices overdue", not "Unlock hidden revenue"). No marketing copy in the app.
- Buttons are verb phrases of up to 3 words: "Approve", "Fix notes", "Re-run". Never a sentence, never "we" or "I" ("Notify me"). If users need to know what a click does first, use a Tooltip or a one-line helper.
- A figure appears once per card. One money format everywhere. Dates drop the year when current. At most one pill per row; the rest is plain text.
- Plain wording, list items, trust statements and disclosure: `references/clarity.md`.

## AI-native patterns
AI features earn their place by doing work, not describing it: notice things before anyone asks, prepare the fix, hand a person a decision, show the source. Numbers people must audit (totals, rules, statistics) stay deterministic; AI reads, flags and drafts. Fall back to deterministic output when AI is unavailable. Patterns (footprints, citations, agent timeline, drafted artifact, inbox, offline-safe demos): `references/patterns.md`.

## Scores & tiers
For any value bucketed into levels (confidence, risk, urgency, priority, health, impact):
- **Define each scale once** in one pure, tested module with named threshold constants. UI reads tiers from it, never hardcodes cutoffs.
- **One scale per meaning.** Don't reuse a color or shape for two scales on one screen.
- **Show a tier only when it is not the default.** The default tier (for example High confidence) shows nothing; only departures get a word and a tone. Max one semantic color per row.
- **Never color alone.** Pair tone with a word or shape ("Needs review", "Due in 6 days"). AA contrast in both themes.
- **Relative bands beat fixed numbers** when users differ in scale.
- **Show the rule.** Hover or footprint states the value and the threshold it crossed ("0.91, High at 0.85"). Uncertain values show as a range, not a gauge or a falsely precise number.
- **Low-confidence AI output is held, not hidden:** labeled "Needs review" and kept out of headline totals.
- **Sort by what the user acts on** (urgency, then impact) and label the sort.

## Banned (slop indicators)
Purple/blue gradients · glassmorphism · ✨ sparkle icons · emoji in UI · "AI-powered" or "Magic" badges · robot or brain mascots · hero sections inside an app · lorem ipsum · stock illustrations · shadows on every card · rounded-2xl/3xl · centered-everything layouts · gradient text · animated blobs · typing-effect text for content · more than one accent color · labeled slots on list items · negative reassurance copy · a disclaimer repeated on every card · full sentences in buttons.

## Process
Mockup first. Before building or changing a screen, make 2-3 static HTML mockups with real data (conservative, strong-fit, divergent), screenshot them, pick one, then build. Screenshots are the review unit; record video only after the screens are approved. The design reviewer gates the visual loop.

## Review checklist (before showing the user)
1. Mockups were screenshotted and one was chosen before building.
2. Screenshot every screen in light and dark at 1440×900, and the main screen at 390px wide.
3. Grep for violations: hex colors and palette classes outside tokens, `rounded-2xl|3xl`, `bg-gradient`, `backdrop-blur`, emoji, components imported from outside `components/ui/`.
4. Layout & surfaces: the surface is named, one headline number leads, and loading, empty and error states each work when forced. A stretched grid panel leaves dead space (use `items-start`). If the headline differs from a total elsewhere, show the bridge (total -> adjustments -> headline).
5. Copy: every sentence, button and figure follows the Copy section; nothing in Banned appears.
6. Clarity: the screen passes `references/clarity.md`.
7. AI output shows its footprints and sources, and can be edited or undone.
8. Every scored or tiered value comes from one scale module, shows its rule, and doesn't rely on color alone.
9. Walk the NN/g heuristics once: system status visible, Undo available, consistent, errors prevented or explained, shortcuts for experts.
10. `make gate` calls `scripts/design_lint.py <web dir>` and it prints `design lint: clean`.

Sources and what each contributed: `references/sources.md`. Re-read it when a design call isn't covered here.
