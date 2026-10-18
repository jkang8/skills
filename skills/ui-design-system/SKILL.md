---
name: ui-design-system
description: "Use when building UI: tokens, closed component set, review."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, components, design-system, frontend, accessibility]
    related_skills: [coding-orchestration, repo-setup]
---

# UI design system

## When to use
Any product UI the user asks for: dashboards, demos, internal tools. Put the rules below into the coding agent's brief (see coding-orchestration). The orchestrator (or you, working alone) reviews screenshots against the checklist before showing the user anything.

The bar: tasteful, AI-native, slick, and nothing that looks like AI slop. Reference points: Linear, Vercel, Stripe dashboards. Dense, calm and data-forward.

## Local overrides
If `ui-design-system.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here and its rules add to these; where they conflict, the override wins.

## Stack default
Vite + React + TypeScript + Tailwind v4 + shadcn/ui (Radix underneath), with pnpm. Icons come from lucide only. Fonts: Geist (or Inter) for text, Geist Mono for codes and IDs.

## Tokens (the only values allowed)
- **Color:** one neutral ramp (zinc) plus ONE accent and semantic success/warning/danger. Everything goes through CSS variables in light and dark. Hex literals and Tailwind palette classes outside the token file are banned.
- **Type scale:** 12 / 13 / 14 / 16 / 20 / 24 / 32. Body text is 14. Use two weights (400, 500), plus 600 for figures only. Money and counts use `tabular-nums`.
- **Spacing:** a 4px grid (1, 2, 3, 4, 6, 8, 12, 16 in Tailwind units). Pick density once per screen.
- **Radius:** 6px for controls and 8px for panels. Nothing rounder.
- **Elevation:** a 1px border by default. Use a shadow only on floating layers (menus, dialogs, toasts).
- **Motion:** 150–200ms ease-out, opacity and translate only, no bounce. Respect `prefers-reduced-motion`.

## The component set (closed)
The app may use only these. They come from your shared shadcn registry `@<your-registry>` (repo `<org>/ui`; setup in the repo-setup skill), restyled to the tokens. Fixes go to the registry first, then get re-added in apps:

Button (primary / secondary / ghost / destructive; sm and md) · Input · Textarea · Select · Checkbox · Switch · Badge (neutral + semantic) · Panel (the one card) · Stat (label, figure, delta) · DataTable (sort, filter, row click, sticky header) · Tabs · Dialog · Sheet (side panel for detail) · DropdownMenu · Popover · Tooltip · Command (⌘K) · Toast · Skeleton · EmptyState · PageHeader · AppShell (sidebar + content).

Pages compose these and nothing else. Page files hold no one-off styling beyond layout (flex/grid/gap/width).

### Adding a component
Do it only when the need can't be met by composing the set. Before adding one, the agent writes three lines in `INVENTORY.md` in the `<org>/ui` repo: what it is, which existing components were tried and why they fell short, and who uses it. If two components overlap, remove one. A variant on an existing component beats a new component.

## UX rules
- Answer first: the screen's main number or decision goes top-left, and detail sits one click away (Sheet or Dialog), never on a separate page.
- Every data view has a loading state (Skeleton matching the final layout), an empty state (what's missing and the one action that fixes it) and an error state (what failed and a retry).
- Tables: right-align numbers; truncate text and show the full value on hover; keep the filter bar above the table; persist filters in the URL.
- Keyboard: everything is reachable by Tab, focus rings stay visible (never remove the outline), Esc closes layers, ⌘K opens Command.
- Accessibility: WCAG AA contrast in both themes, labels on every input, icon-only buttons get `aria-label`.
- Copy: short and specific, using sentence case. "3 invoices overdue", not "Unlock hidden revenue". Write no marketing copy inside the app.
- AI features must earn their place. They explain, summarize or speed up a task, and they show their source. If an AI feature isn't available, the app falls back to deterministic output.

## Interaction details (Vercel guidelines, Emil Kowalski)
- Name exact transition properties, never `transition: all`. Entering UI starts from `scale(0.95)` plus opacity and eases out. Popovers grow from their trigger; modals stay centered. Buttons press to `scale(0.97)` on `:active`.
- Hit targets are at least 24px (44px on touch). Mobile inputs use at least 16px text. Never block paste or zoom.
- Skeletons and spinners wait ~200ms before appearing and stay at least ~400ms so they don't flicker. Loading buttons keep their label and add a spinner.
- Use optimistic updates with rollback. Destructive actions get a confirm or a timed Undo. Labels that open a follow-up step or show progress end in an ellipsis ("Rename…", "Saving…").
- Only the first tooltip in a group is delayed. Modals and sheets use `overscroll-behavior: contain`. Back restores scroll position and filters.
- Respond to input within 100ms and finish a view change within 400ms (Doherty threshold).

## Hierarchy (Refactoring UI, Linear)
- Build emphasis with weight and color before size. Mute secondary text instead of shouting the primary.
- Use spacing and a background shift before adding a border. Chrome (sidebar, headers, tabs) stays quieter than content.
- Strict alignment: every edge lines up with something. Use one density per screen.

## AI-native patterns (Shape of AI, agent UX)
AI belongs inside the work, not in a separate chat page or a decoration.
- **Footprints:** every AI result can open the steps that produced it, with the inputs, rules or prompt used and the time.
- **Inline citations:** each claim links to its source record. A claim with no source is shown as unverified.
- **Disclosure without decoration:** a small "Generated" label in muted text, never a sparkle or a gradient.
- **Progress against a plan:** long runs list their steps and tick them off with real counts ("Checked 1,204 records"). No idle "Thinking…", no fake typing.
- **Follow-up over guessing:** an unclear request gets one short clarifying question with suggested answers.
- **Suggestions in empty inputs:** 3-4 concrete examples drawn from the user's data, never generic prompts.
- **Edit, accept, undo:** AI output is a draft the user can change, accept or revert. Nothing irreversible happens without a confirm.
- **Honest limits:** state a caveat once, where it applies, in plain words.

## Banned (slop indicators)
Purple/blue gradients · glassmorphism · ✨ sparkle icons · emoji in UI · "AI-powered" or "Magic" badges · robot or brain mascots · hero sections inside an app · lorem ipsum · stock illustrations · shadows on every card · rounded-2xl/3xl · centered-everything layouts · gradient text · animated blobs · typing-effect text for content · more than one accent color.

Sources and what each contributed: `references/sources.md` (Vercel, Emil Kowalski, Linear, Stripe, NN/g, Laws of UX, Refactoring UI, Shape of AI). Re-read it when a design call isn't covered here.

## Review checklist (before showing the user)
1. Screenshot every screen in light and dark at 1440×900, and the main screen at 390px wide.
2. Grep for violations: hex colors and palette classes outside tokens, `rounded-2xl|3xl`, `bg-gradient`, `backdrop-blur`, emoji, components imported from outside `components/ui/`.
3. Check each screen against the banned list and the UX rules. Fix it, then re-shoot.
4. Check loading, empty and error states by forcing each one.
5. Walk the NN/g heuristics once: system status visible, Undo available, consistent with the rest of the app, errors prevented or explained, shortcuts for experts.
6. Every AI output shows its footprints and its sources, and can be edited or undone.
