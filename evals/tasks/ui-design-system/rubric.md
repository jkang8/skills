Score each item 1 (clearly met) or 0 (not met or can't tell). The app is a React + Tailwind frontend under web/.
1. Colors come only from theme tokens/CSS variables (no hex, rgb or Tailwind palette classes like blue-500 outside the tokens file).
2. No slop: no gradients, glassmorphism/backdrop blur, sparkle or emoji, "AI-powered"/"Magic" badges, rounded-2xl/3xl, shadows on every card.
3. Every data view has a loading state that matches the final layout (skeleton, not just a spinner or "Loading...").
4. Every data view has an empty state that says what's missing and offers the one action that fixes it.
5. Every data view has an error state that says what failed and offers a retry.
6. Copy is short, specific and sentence case; no marketing copy.
7. Accessibility: every input has a label, icon-only buttons have aria-label, focus outlines are not removed.
8. Numbers: amounts/counts use tabular numerals, and numbers in tables are right-aligned (or there are no numeric tables).
9. Destructive or irreversible actions have a confirm step or an Undo.
10. Page code uses the shared components in components/ui (adding new ones there is fine) and holds no one-off styling beyond layout.
11. If the task has an AI feature: the output shows its source (citations link to the source item), is marked as generated without decoration, and the page works when the AI call fails. Otherwise score 1.
12. Interactions: no `transition-all`; motion is short and limited to opacity/transform; hit targets look at least 24px.
