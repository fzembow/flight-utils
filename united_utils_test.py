import unittest
import united_utils

class TestUnitedUtils(unittest.TestCase):

  def setUp(self):
    self.parser = united_utils.UnitedAirportParser()

  def test_old_style(self):
    start, end = self.parser.get_iata_codes(u"MUNICH/NEWARK")
    self.assertEqual(start, "MUC")
    self.assertEqual(end, "EWR")

  def test_old_style_with_parens(self):
    start, end = self.parser.get_iata_codes(u"SAN FRANCISCO/NEW YORK (JFK)")
    self.assertEqual(start, "SFO")
    self.assertEqual(end, "JFK")

  def test_new_style(self):
    start, end = self.parser.get_iata_codes(u"Tokyo-Jakarta")
    self.assertEqual(start, "NRT")
    self.assertEqual(end, "CGK")

  def test_new_style_with_parens(self):
    start, end = self.parser.get_iata_codes(u"New York (JFK)-Los Angeles")
    self.assertEqual(start, "JFK")
    self.assertEqual(end, "LAX")

  def test_new_style_with_slash(self):
    start, end = self.parser.get_iata_codes(u"New York/Newark-Austin")
    self.assertEqual(start, "EWR")
    self.assertEqual(end, "AUS")

  def test_bogus_cities(self):
    self.assertRaises(ValueError, self.parser.get_iata_codes, u"Alakhakhfsa/Jasihfas Mas")

  def test_bogus_input(self):
    self.assertRaises(ValueError, self.parser.get_iata_codes, u"New York")

if __name__ == '__main__':
    unittest.main()
