# Before/after examples

Six small refactors, each a pair of files in `examples/`. Every pair runs: `examples/check.sh` runs the Python pairs under one test (before and after give the same result) and type-checks the TypeScript pair. Open the files; this page only says what changed and which rule it follows.

| Pair | Smell in the before file | What the after file does | Rule |
|---|---|---|---|
| `examples/py/route_split_before.py` → `examples/py/route_split_after.py` | A FastAPI route queries, decides what's overdue and formats money | `overdue_summary()` is a pure function over frozen Pydantic records; the route fetches, maps ORM rows to models, and returns a typed `response_model`; the clock is a dependency | Separation of concerns; functional core; types are the contract |
| `examples/ts/src/invoices_before.tsx` → `examples/ts/src/invoices_after.tsx` | A component fetches, tracks loading/error, filters and renders | `useInvoices()` owns the I/O and returns a discriminated union; `UnpaidList` is pure over props; the fetch goes through the API client | One reason to change per module; invalid states unrepresentable |
| `examples/py/wrapper_before.py` → `examples/py/wrapper_after.py` | `get_invoice_by_id_from_db()` has one caller and only renames `Session.get` | Inlined | Inline a one-caller wrapper whose name restates its body |
| `examples/py/flag_before.py` → `examples/py/flag_after.py` | `format_amount(cents, for_csv=False)` switches behavior on a boolean | Two functions, `display_amount()` and `csv_amount()` | Boolean parameters that switch behavior are a smell |
| `examples/py/grab_bag_before/utils.py` → `examples/py/grab_bag_after/` | Money, dates and strings share `utils.py`; `slug()` has no callers | `money.py` and `business_days.py`, each owning one concept; `slug()` deleted rather than moved | No grab bags; shared code lives in the module that owns the concept; delete dead code |
| `examples/py/io_before.py` → `examples/py/io_after.py` | The reminder rule reads `date.today()` and the DB itself, so tests must patch both | `reminders_due(unpaid, today)` is pure; `run_reminders(s, clock)` is the thin shell | Functional core, imperative shell; side effects visible in the signature |

`examples/py/db.py` is the shared SQLAlchemy model and seeded in-memory database the pairs run against.
