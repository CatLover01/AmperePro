import unittest

from lois import loi_ohm, resistance_parallele, resistance_serie


class TestLois(unittest.TestCase):
    def test_ohm(self):
        self.assertEqual(loi_ohm(10, 25), 2.5)
        self.assertEqual(loi_ohm(5, 10), 2)
        self.assertEqual(loi_ohm(1, 1), 1)
        self.assertEqual(loi_ohm(10, 0), 0)
        self.assertEqual(loi_ohm(0.5, 1), 2)

    def test_resistance_serie(self):
        self.assertEqual(resistance_serie(5, 8, 4, 9, 7.5, 987), 1020.5)
        self.assertEqual(resistance_serie(5), 5)
        self.assertEqual(resistance_serie(), 0)
        self.assertEqual(resistance_serie(0, 5), 5)
        self.assertEqual(resistance_serie(0.5, 0.5), 1.0)

    def test_resistance_parallele(self):
        self.assertEqual(resistance_parallele(0.2, 0.4, 0.8, 0.5), 1 / 10.75)
        self.assertEqual(resistance_parallele(5), 5)
        self.assertEqual(resistance_parallele(10, 10), 5)
        self.assertEqual(resistance_parallele(2, 2), 1)
