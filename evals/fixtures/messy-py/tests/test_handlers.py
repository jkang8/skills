import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1]))
from app import db, handlers  # noqa: E402


class HandleOrder(unittest.TestCase):
    @mock.patch("app.utils.send_email")
    def test_vip_gets_ten_percent_off_before_tax(self, send):
        conn = db.connect()
        conn.execute("insert into customers (id, email, vip) values (1, 'a@example.com', 1)")
        out = handlers.handle_order({"customer_id": 1, "items": [{"price_cents": 1000, "qty": 2}], "date": "2026-01-02"}, conn)
        self.assertEqual(out, {"status": "ok", "total": "$19.44"})
        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
