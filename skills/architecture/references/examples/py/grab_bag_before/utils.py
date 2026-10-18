"""Before: a utils grab bag. Money, dates and strings share a file and nothing owns them."""
import datetime


def cents_to_str(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def add_business_days(d: datetime.date, n: int) -> datetime.date:
    while n:
        d += datetime.timedelta(days=1)
        n -= d.weekday() < 5
    return d


def slug(s: str) -> str:
    return "-".join(s.lower().split())
