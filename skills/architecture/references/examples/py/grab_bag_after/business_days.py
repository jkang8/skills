"""Business-day arithmetic, kept apart because it's easy to get wrong and has its own tests."""
import datetime


def add_business_days(d: datetime.date, n: int) -> datetime.date:
    while n:
        d += datetime.timedelta(days=1)
        n -= d.weekday() < 5
    return d
