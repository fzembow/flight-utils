import csv, json, os, subprocess

"""
  Transforms Openflights data to make it a little bit more useful.
  For example, it adds a num_flights fields to each airport which is useful in ranking importance.

  Depends on:
  airports.dat: http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/airports.dat
  routes.dat: http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/routes.dat

  It will fetch them if they are not found in the script's directory.
"""

AIRPORT_DATA_URL = 'http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/airports.dat'
ROUTE_DATA_URL = 'http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/routes.dat'

AIRPORT_FIELDNAMES = (
  'openflights_airport_id',
  'name',
  'city',
  'country',
  'iata',
  'icao',
  'lat',
  'lng',
  'altitude_ft',
  'timezone',
  'dst',
)

ROUTE_FIELDNAMES = (
  'airline',
  'openflights_airline_id',
  'source',
  'source_openflights_airport_id',
  'destination',
  'destination_openflights_airport_id',
  'codeshare',
  'stops',
  'equipment',
)


def main():
  airport_list = get_airports_data()

  # Dump the airports as JSON, removing any "airports" without iata codes.
  # Openflights has some rail stations and things like that which fall into that category.
  final_airports = []
  for airport in airport_list:
    if not airport['iata']:
      continue

    # Flatten the dictionary in the order of the schema, adding 
    flat_airport = []
    for fieldname in AIRPORT_FIELDNAMES:
      if fieldname in airport:
        flat_airport.append(airport[fieldname])

    flat_airport.append(airport['num_flights'])
    final_airports.append(flat_airport)

  print json.dumps(final_airports, separators=(',',':'))


def get_airports_data():
  """Returns an array of dicts, each representing an airport.

  The fieldnames are the ones from AIRPORT_FIELDNAMES.
  """

  airports_file = os.path.join(os.getcwd(), "airports.dat")
  routes_file = os.path.join(os.getcwd(), "routes.dat")

  # Fetch the data files from openflights if they don't exist.
  if not os.path.exists(airports_file):
    f = open(airports_file, "w")
    subprocess.call(['curl', '-s', AIRPORT_DATA_URL, '>', airports_file], stdout=f)
    f.close()
  if not os.path.exists(routes_file):
    f = open(routes_file, "w")
    subprocess.call(['curl', '-s', ROUTE_DATA_URL, '>', routes_file], stdout=f)
    f.close()

  airports = get_airports(airports_file)
  routes = get_routes(routes_file)

  # Count how many flights start or end in each airport.
  for route in routes:
    try:
      source_airport = airports[route['source_openflights_airport_id']]
      source_airport['num_flights'] += 1
    except KeyError:
      pass
    try:
      destination_airport = airports[route['destination_openflights_airport_id']]
      destination_airport['num_flights'] += 1
    except KeyError:
      pass

  airport_list = airports.values()
  airport_list.sort(key=lambda x: x['num_flights'], reverse=True)
  return airport_list


def get_airports(airports_file):
  """Returns a dictionary of airports, keyed by openflights id."""
  reader = csv.DictReader(open(airports_file, 'rb'),
                          fieldnames=AIRPORT_FIELDNAMES)
  airports = {}
  for airport in reader:
    airport_id = airport['openflights_airport_id']
    del airport['openflights_airport_id']

    # Remove strange '\\N' characters.
    for k, v in airport.iteritems():
      if v == '\\N':
        airport[k] = ''
    airports[airport_id] = airport

    # Add a counter for the number of flights.
    airport['num_flights'] = 0
  return airports


def get_routes(routes_file):
  """Returns a list of flights."""
  reader = csv.DictReader(open(routes_file, 'rb'),
                          fieldnames=ROUTE_FIELDNAMES)

  routes = []
  for route in reader:
    for k, v in route.iteritems():
      if v == '\\N':
        route[k] = ''
    routes.append(route)
  return routes

if __name__ == "__main__":
  main()
