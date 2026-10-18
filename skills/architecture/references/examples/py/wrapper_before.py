"""Before: a one-caller wrapper that only renames the call."""
from sqlalchemy.orm import Session

from db import InvoiceRow


def get_invoice_by_id_from_db(s: Session, invoice_id: int) -> InvoiceRow | None:
    return s.get(InvoiceRow, invoice_id)


def mark_paid(s: Session, invoice_id: int) -> None:
    row = get_invoice_by_id_from_db(s, invoice_id)
    if row is None:
        raise KeyError(invoice_id)
    row.paid = True
