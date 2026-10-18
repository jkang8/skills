"""Each pair behaves the same before and after; the after side is testable without patching."""
import datetime
import unittest

from fastapi.testclient import TestClient

import flag_after
import flag_before
import io_after
import route_split_after
import route_split_before
import wrapper_after
import wrapper_before
from db import InvoiceRow, seeded_session
from grab_bag_after import business_days, money
from grab_bag_before import utils


class Pairs(unittest.TestCase):
    def test_route_split_same_response(self):
        before = TestClient(route_split_before.app).get("/customers/Acme/overdue").json()
        after = TestClient(route_split_after.app).get("/customers/Acme/overdue").json()
        self.assertEqual(before, after)
        self.assertEqual(after, {"count": 1, "total": "$120.00"})

    def test_route_split_rule_needs_no_db(self):
        inv = route_split_after.Invoice(amount_cents=500, due=datetime.date(2026, 1, 1), paid=False)
        out = route_split_after.overdue_summary([inv], datetime.date(2026, 1, 2))
        self.assertEqual(out.count, 1)

    def test_wrapper_inlined_same_effect(self):
        for mod in (wrapper_before, wrapper_after):
            s = seeded_session()
            mod.mark_paid(s, 1)
            self.assertTrue(s.get(InvoiceRow, 1).paid)

    def test_flag_split(self):
        self.assertEqual(flag_before.format_amount(123456), flag_after.display_amount(123456))
        self.assertEqual(flag_before.format_amount(123456, for_csv=True), flag_after.csv_amount(123456))

    def test_grab_bag_split(self):
        d = datetime.date(2026, 10, 16)  # a Friday
        self.assertEqual(utils.add_business_days(d, 1), business_days.add_business_days(d, 1))
        self.assertEqual(utils.cents_to_str(150), money.display(150))

    def test_functional_core_without_mocks(self):
        unpaid = [(1, datetime.date(2026, 10, 11)), (2, datetime.date(2026, 10, 17))]
        self.assertEqual(io_after.reminders_due(unpaid, datetime.date(2026, 10, 18)), [1, 2])
        self.assertEqual(io_after.run_reminders(seeded_session(), clock=lambda: datetime.date(2026, 10, 2)), [1])


if __name__ == "__main__":
    unittest.main()
