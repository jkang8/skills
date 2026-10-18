"""After: two functions, each named for what it does. Callers say which one they mean."""


def display_amount(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def csv_amount(cents: int) -> str:
    return f"{cents / 100:.2f}"
