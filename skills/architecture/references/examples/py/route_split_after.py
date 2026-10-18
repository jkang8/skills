"""After: the rule is a pure function over typed records; the route only does I/O and mapping."""
import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import InvoiceRow, seeded_session


class Invoice(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    amount_cents: int
    due: datetime.date
    paid: bool


class OverdueSummary(BaseModel):
    count: int
    total: str


def overdue_summary(invoices: list[Invoice], today: datetime.date) -> OverdueSummary:
    late = [i for i in invoices if not i.paid and i.due < today]
    return OverdueSummary(count=len(late), total=f"${sum(i.amount_cents for i in late) / 100:.2f}")


def today() -> datetime.date:
    return datetime.date(2026, 10, 18)  # a real app returns datetime.date.today()


app = FastAPI()


@app.get("/customers/{customer}/overdue", response_model=OverdueSummary)
def overdue(customer: str, s: Session = Depends(seeded_session), now: datetime.date = Depends(today)):
    rows = s.scalars(select(InvoiceRow).where(InvoiceRow.customer == customer)).all()
    return overdue_summary([Invoice.model_validate(r) for r in rows], now)
