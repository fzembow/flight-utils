import csv, re
import process_openflights


class UnitedAirportParser:
  """Singleton class that helps extract airport codes from strings found in MileagePlus statements."""

  _instance = None
  def __new__(self, *args, **kwargs):
    if not self._instance:
      self._instance = super(UnitedAirportParser, self).__new__(self, *args, **kwargs)
    return self._instance

  airports = process_openflights.get_airports_data()

  def get_iata_codes(self, string):
    """Gets the IATA codes corresponding to a string with two city names.

    The format of the string changed on March 3, 2011, but this script can handle both.
    """

    # Infer from the presence of capitalization and slashes vs. dashes
    # what style the string is.
    all_uppercase = re.search(r'[a-z]', string) is None
    dashes = string.count('-')
    slashes = string.count('/')
    
    if not all_uppercase and dashes > 0:
      return self._parse_new_style(string)
    elif slashes > 0:
      return self._parse_old_style(string)
    else:
      raise ValueError("Couldn't recognize airport string: %s" % string)


  def _parse_iata_in_paren(self, string):
    search = re.search(r'\(([A-Z]{3,4})\)', string)
    if search:
      return search.group(1)
    return None


  def _find_iata_by_city(self, string):
    city = str(string.lower())

    candidate_airports = filter(lambda x: x['city'].lower().find(city) != -1,
        self.airports)

    if len(candidate_airports) == 0:
      raise ValueError("Didn't find any airports in the city of %s", string)

    # The airports are ordered by number of flights, so the first airport
    # is the most likely candidate.
    return candidate_airports[0]['iata']


  def _parse_old_style(self, string):
    """Parses airport codes from before 3/3/2011."""

    def parse_old_fragment(fragment):
      # Check for parens with an IATA code.
      iata = self._parse_iata_in_paren(fragment)
      if iata:
        return iata

      # Look up the airport by city name.
      iata = self._find_iata_by_city(fragment)
      if iata:
        return iata
      
      raise ValueError("Couldn't find an airport code for the city of %s", string)

    # Check that there's a slash, which splits the start and end cities.
    return map(parse_old_fragment, string.split('/'))
  


  def _parse_new_style(self, string):
    """Parses airport codes from after 3/3/2011."""

    def parse_new_fragment(fragment):
      # Check for parens with an IATA code.
      iata = self._parse_iata_in_paren(fragment)
      if iata:
        return iata

      # If the fragment has a slash, it's a compound city
      # like New York/Newark. In this case, look for the city
      # after the slash.
      if fragment.find('/') != -1:
        iata = self._find_iata_by_city(fragment.split('/')[1])
        if iata:
          return iata

      # Look up the airport by city name.
      iata = self._find_iata_by_city(fragment)
      if iata:
        return iata
      
      raise ValueError("Couldn't find an airport code for the city of %s", string)

    # Check that there's a slash, which splits the start and end cities.
    return map(parse_new_fragment, string.split('-'))
