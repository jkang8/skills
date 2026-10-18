from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # type-only, not a runtime cycle
    from shop.services.orders import Order


def total(order: Order) -> int:
    return order.subtotal
