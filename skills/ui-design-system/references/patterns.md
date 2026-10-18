# Interaction, hierarchy and AI-native patterns

Part of the ui-design-system rules; the checklist checks against this file.

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
