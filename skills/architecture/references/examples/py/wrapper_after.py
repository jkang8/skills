"""After: the wrapper is inlined; the one caller reads top to bottom."""
from sqlalchemy.orm import Session

from db import InvoiceRow


def mark_paid(s: Session, invoice_id: int) -> None:
    row = s.get(InvoiceRow, invoice_id)
    if row is None:
        raise KeyError(invoice_id)
    row.paid = True
