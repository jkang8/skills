Score each item 1 (clearly met) or 0 (not met or can't tell). Judge the change the agent made to this small Python repo (app/, tests/).
1. The new or changed business logic is a pure function over plain data, with database, environment, email and clock access kept at the edges and passed in.
2. Tests of the new logic run without mocks (mocks only at true I/O edges, if at all), and the tests pass when run with `python3 -m unittest discover -s tests`.
3. The change extends or reuses the existing code (e.g. the existing discount/total logic) instead of adding a parallel version next to it.
4. No new grab-bag module (utils/helpers/misc/common) and no new code added to the existing utils grab bag without moving it to a module named for its concept.
5. No new boolean parameter that switches behavior; no interface/base class with a single implementation; no speculative options.
6. Errors are not swallowed: no new blanket `except Exception` that hides the cause; failures carry a reason.
7. Each module touched can be described in one sentence without "and".
8. No dead code, old versions or commented-out code left behind; nothing built for a future that wasn't asked for.
9. Config is read in one place, not ad hoc from `os.environ` inside logic.
10. The diff stays focused on the task: no unrelated refactors mixed in (a small tidy that the change needs is fine).
