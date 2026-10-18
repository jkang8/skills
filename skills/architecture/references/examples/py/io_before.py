"""Before: the reminder rule reads the clock and the database itself, so tests must patch both."""
import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import InvoiceRow


def reminders_due(s: Session) -> list[int]:
    today = datetime.date.today()
    rows = s.scalars(select(InvoiceRow).where(InvoiceRow.paid.is_(False))).all()
    return [r.id for r in rows if (today - datetime.date.fromisoformat(r.due)).days in (1, 7, 30)]
