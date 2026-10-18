"""Money formatting. The one place that knows how cents become text."""


def display(cents: int) -> str:
    return f"${cents / 100:,.2f}"
