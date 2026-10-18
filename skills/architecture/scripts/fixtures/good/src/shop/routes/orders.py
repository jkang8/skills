from shop.services.orders import Order, checkout


def post_order(subtotal: int) -> dict:
    return {"total": checkout(Order(subtotal))}
