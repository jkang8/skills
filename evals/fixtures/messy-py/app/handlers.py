import os

from app import utils


def handle_order(request, conn):
    try:
        customer = conn.execute("select * from customers where id = ?", (request["customer_id"],)).fetchone()
        subtotal = sum(item["price_cents"] * item["qty"] for item in request["items"])
        tax = float(os.environ.get("TAX_RATE", "0.08"))
        total = utils.compute_total(subtotal, bool(customer["vip"]), tax)
        conn.execute(
            "insert into orders (customer_id, subtotal_cents, created) values (?, ?, ?)",
            (customer["id"], subtotal, request["date"]),
        )
        utils.send_email(customer["email"], "Your total is " + utils.format_money(total))
        return {"status": "ok", "total": utils.format_money(total)}
    except Exception:
        return {"status": "error"}
