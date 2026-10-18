"""Shared fixture for the examples: one SQLAlchemy model and an in-memory database."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class InvoiceRow(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    amount_cents: Mapped[int]
    due: Mapped[str]  # ISO date
    paid: Mapped[bool] = mapped_column(default=False)


def seeded_session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    s = Session(engine)
    s.add_all([
        InvoiceRow(id=1, customer="Acme", amount_cents=120_00, due="2026-10-01"),
        InvoiceRow(id=2, customer="Acme", amount_cents=80_00, due="2026-11-01"),
        InvoiceRow(id=3, customer="Birch", amount_cents=50_00, due="2026-09-15", paid=True),
    ])
    s.commit()
    return s
