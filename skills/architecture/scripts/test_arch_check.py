import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from arch_check import check  # noqa: E402


class ArchCheck(unittest.TestCase):
    def test_good_tree_is_clean(self):
        self.assertEqual(check(HERE / "fixtures/good"), [])

    def test_bad_tree(self):
        self.assertEqual(sorted(check(HERE / "fixtures/bad")), sorted([
            "src/shop/big.py: 501 lines, over 500; split by concept",
            "src/shop/utils.py: grab-bag file name; name it for the concept it owns",
            "web/src/helpers.ts: grab-bag file name; name it for the concept it owns",
            "import cycle: shop.a -> shop.b -> shop.a",
            "import cycle: web/src/a.ts -> web/src/b.ts -> web/src/a.ts",
        ]))

    def test_exclude(self):
        hits = check(HERE / "fixtures/bad", ["src/shop/utils.py", "web/src/helpers.ts", "src/shop/big.py"])
        self.assertTrue(all("cycle" in h for h in hits))


if __name__ == "__main__":
    unittest.main()
