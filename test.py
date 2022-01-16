import unittest
import utils


class TestUtils(unittest.TestCase):
    def test_signed_bin_to_dec(self):
        self.assertEqual(utils.signed_bin_to_dec(0x800, 12), -2048)
        self.assertEqual(utils.signed_bin_to_dec(0xFF4, 12), -12)

    def test_logical_rshift(self):
        self.assertEqual(utils.logical_rshift(-1, 1), 0x7FFFFFFF)
        self.assertEqual(utils.logical_rshift(-1, 0), -1)


if __name__ == "__main__":
    unittest.main()
