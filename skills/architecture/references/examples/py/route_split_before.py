"""Before: one route queries, decides what's overdue, and formats the response."""
import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import InvoiceRow, seeded_session

app = FastAPI()


@app.get("/customers/{customer}/overdue")
def overdue(customer: str, s: Session = Depends(seeded_session)):
    rows = s.scalars(select(InvoiceRow).where(InvoiceRow.customer == customer)).all()
    today = datetime.date(2026, 10, 18)
    late = [r for r in rows if not r.paid and datetime.date.fromisoformat(r.due) < today]
    return {"count": len(late), "total": "$%.2f" % (sum(r.amount_cents for r in late) / 100)}
