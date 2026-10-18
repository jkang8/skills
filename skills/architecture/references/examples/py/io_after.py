"""After: functional core, imperative shell. The rule takes data and a date; the shell fetches them."""
import datetime
from collections.abc import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import InvoiceRow

REMINDER_DAYS = (1, 7, 30)


def reminders_due(unpaid: Iterable[tuple[int, datetime.date]], today: datetime.date) -> list[int]:
    return [id_ for id_, due in unpaid if (today - due).days in REMINDER_DAYS]


def run_reminders(s: Session, clock: Callable[[], datetime.date] = datetime.date.today) -> list[int]:
    rows = s.scalars(select(InvoiceRow).where(InvoiceRow.paid.is_(False))).all()
    return reminders_due(((r.id, datetime.date.fromisoformat(r.due)) for r in rows), clock())
