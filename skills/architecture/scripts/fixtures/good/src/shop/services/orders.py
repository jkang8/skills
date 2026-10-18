from dataclasses import dataclass

from shop.domain import pricing


@dataclass
class Order:
    subtotal: int


def checkout(order: Order) -> int:
    return pricing.total(order)
