"""Before: a boolean parameter switches between two behaviors."""


def format_amount(cents: int, for_csv: bool = False) -> str:
    if for_csv:
        return f"{cents / 100:.2f}"
    return f"${cents / 100:,.2f}"
