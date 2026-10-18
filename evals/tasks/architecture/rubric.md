Score each item 1 (clearly met) or 0 (not met or can't tell). Judge the change in `.changes.diff`, not code that was already there.
1. The new or changed business logic is a pure function over plain values, with database, environment, email and clock access kept at the edges.
2. Tests of the new logic use real data without mocks (mocks only at true I/O edges, if at all), test the behavior the task asked for, and pass: `.tests.txt` ends with `OK` and `(exit 0)`.
3. The change extends or reuses the existing code (e.g. the existing discount/total logic) instead of adding a parallel version next to it.
4. The change adds no new grab-bag module (utils/helpers/misc/common); new code it adds lives in a module named for its concept, or next to its only caller.
5. The change adds no boolean parameter that switches behavior, no interface/base class with a single implementation, no speculative options.
6. Errors are not swallowed: the change adds no blanket `except Exception` that hides the cause, and failures it touches carry a reason.
7. Each module the change adds can be described in one sentence without "and".
8. No dead code, old versions or commented-out code left behind by the change; nothing built for a future that wasn't asked for.
9. The change adds no new ad-hoc `os.environ` reads inside logic.
10. The diff stays focused on the task: no unrelated refactors mixed in (a small tidy that the change needs is fine).
