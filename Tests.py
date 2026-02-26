import unittest

from Circuit import LoisPhysiques

class TestsLois(unittest.TestCase):
    def test_ohm(self):
        lp = LoisPhysiques()
        self.assertEqual(lp.loi_ohm(4,8),32)

    def test_resistance_serie(self):
        lp = LoisPhysiques()
        self.assertEqual(lp.resistance_serie(5,8,4,9,7.5,987), 1020.5)

    def resistance_serie(self):
        lp = LoisPhysiques()
        self.assertEqual(lp.resistance_parallele(0.2,0.4,0.8,0.5), 1/10.75)
