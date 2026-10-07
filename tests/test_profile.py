import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from validate_profile import validate


class ProfileTests(unittest.TestCase):
    def test_live_profile_validates(self):
        data = validate(ROOT / "data/gateways.yaml")
        self.assertEqual(data["schema"], 2)
        self.assertEqual(data["gateways"][0]["id"], "argolink")

    def test_exactly_one_verified_route(self):
        data = validate(ROOT / "data/gateways.yaml")
        verified = [row for row in data["gateways"] if row["status"] == "verified"]
        self.assertEqual([row["id"] for row in verified], ["argolink"])


if __name__ == "__main__":
    unittest.main()
