import unittest
import utils


class TestUtils(unittest.TestCase):
    def test_signed_bin_to_dec(self):
        self.assertEqual(utils.signed_bin_to_dec(0x800, 12), -2048)


if __name__ == "__main__":
    unittest.main()
