---
name: ui-design-system
description: "Use when building UI: tokens, closed component set, review."
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, components, design-system, frontend, accessibility]
    related_skills: [coding-orchestration, repo-setup]
---

# UI design system

## When to use
Any product UI the user asks for: dashboards, demos, internal tools. Put these rules in the coding agent's brief (see coding-orchestration). Review screenshots against the checklist before showing the user anything.

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
- Copy: short, specific, sentence case ("3 invoices overdue", not "Unlock hidden revenue"). No marketing copy in the app.
- AI features explain, summarize or speed up a task, show their source, and fall back to deterministic output when AI is unavailable.

## Interaction, hierarchy and AI-native rules
Follow `references/patterns.md`: exact transition properties, entry from `scale(0.95)`, 24px hit targets, skeleton show delay and minimum time, optimistic updates with Undo, ellipsis labels, emphasis by weight and color before size, quiet chrome, strict alignment, and the AI patterns (footprints, inline citations, muted "Generated" label, progress against a plan, edit/accept/undo, honest limits).

## Banned (slop indicators)
Purple/blue gradients · glassmorphism · ✨ sparkle icons · emoji in UI · "AI-powered" or "Magic" badges · robot or brain mascots · hero sections inside an app · lorem ipsum · stock illustrations · shadows on every card · rounded-2xl/3xl · centered-everything layouts · gradient text · animated blobs · typing-effect text for content · more than one accent color.

## Review checklist (before showing the user)
1. Screenshot every screen in light and dark at 1440×900, and the main screen at 390px wide.
2. Grep for violations: hex colors and palette classes outside tokens, `rounded-2xl|3xl`, `bg-gradient`, `backdrop-blur`, emoji, components imported from outside `components/ui/`.
3. Check each screen against the banned list, the UX rules and `references/patterns.md`. Fix, then re-shoot.
4. Check loading, empty and error states by forcing each one.
5. Walk the NN/g heuristics once: system status visible, Undo available, consistent with the rest of the app, errors prevented or explained, shortcuts for experts.
6. Every AI output shows its footprints and its sources, and can be edited or undone.
7. `make gate` calls `scripts/design_lint.py <web dir>` and it prints `design lint: clean`.

Sources and what each contributed: `references/sources.md`. Re-read it when a design call isn't covered here.
