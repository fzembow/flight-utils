from BeautifulSoup import BeautifulSoup
from soupselect import select
import mechanize

import sys, time, urllib, os, csv, datetime

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.45 Safari/537.17'
ACCOUNT_URL = 'http://www.united.com/web/en-US/apps/account/account.aspx'
OLD_URL_BASE = 'http://www.united.com/web/en-US/apps/mileageplus/statement/statement.aspx?MP=1'
OLD_URL_STATEMENT = 'http://www.united.com/web/en-US/apps/mileageplus/statement/statement.aspx?MP=1&SD=%s'
NEW_URL_BASE = 'http://www.united.com/web/en-US/apps/mileageplus/statement/statement.aspx'
NEW_URL_STATEMENT = 'http://www.united.com/web/en-US/apps/mileageplus/statement/statement.aspx?SD=%s'
CRAWL_DELAY = 1 # Seconds to wait between HTTP requests.


def main(argv):
  """If the script is run from the command line, it takes a username and password."""
  if len(argv) != 3:
    print "Usage: python %s [USERNAME] [PASSWORD]" % argv[0]
    sys.exit(1)

  username = argv[1]
  password = argv[2]

  flights = fetch_united_history(username, password)
  dump_csv(flights)


def fetch_united_history(username, password):
  """Retrieves a given user's United history."""

  # Set up browser
  browser = setup_browser()
  login(browser, username, password)

  # Find the URLs for eall of the statements.
  statement_urls = get_statement_urls(browser, OLD_URL_BASE, True)
  statement_urls.extend(get_statement_urls(browser, NEW_URL_BASE, False))

  # Get flights from each statement.
  flights = []
  for statement_url in statement_urls:
    flights.extend(get_statement_flights(browser, statement_url))

  # Sort the flights by date.
  flights.sort(key=lambda x: datetime.datetime.strptime(x[0], '%m/%d/%Y'))

  browser.close()
  return flights


def login(browser, username, password):
  """Logs a user into their United account, setting the appropriate cookies."""
  browser.open(ACCOUNT_URL)
  time.sleep(CRAWL_DELAY)

  browser.select_form(nr=0)

  USERNAME_ID = 'ctl00$ContentInfo$SignIn$onepass$txtField'
  PASSWORD_ID = 'ctl00$ContentInfo$SignIn$password$txtPassword'
  SUBMIT_ID = 'ctl00$ContentInfo$SignInSecure'

  browser.form[USERNAME_ID] = username
  browser.form[PASSWORD_ID] = password
  response = browser.submit(name=SUBMIT_ID)

  result = response.read()
  if 'We could not process your request.' in result:
    print "Incorrect username or password"
    sys.exit(1)

  time.sleep(CRAWL_DELAY)


def get_statement_urls(browser, base_url, is_old_statement=False):
  """Finds the URLs for each other statement, given a base URL for a statement."""

  STATEMENT_SELECT_ID = '#ctl00_ContentInfo_drpStatementDates option'

  # There is a <select> on the page with the other statements linked.
  response = browser.open(base_url)
  soup = BeautifulSoup(response.read())
  statement_dates = select(soup, STATEMENT_SELECT_ID)
  if len(statement_dates) == 0:
    print "Couldn't find statement selector at %s" % base_url
    sys.exit(1)

  statement_urls = []
  if is_old_statement:
    statement_base_url = OLD_URL_STATEMENT
  else:
    statement_base_url = NEW_URL_STATEMENT

  for statement_date in statement_dates:
    url = statement_base_url % urllib.quote(statement_date['value'].split(' ')[0], '')
    statement_urls.append(url)

  time.sleep(CRAWL_DELAY)
  return statement_urls


def get_statement_flights(browser, statement_url):
  """Returns each flight found at a given statement URL.""" 

  html = browser.open(statement_url).read()
  flights = parse_statement_flights(BeautifulSoup(html))
  time.sleep(CRAWL_DELAY)
  return flights


def parse_statement_flights(soup):
  """Takes a BeautifulSoup instance and finds what flights, if any, it contains."""

  notes = select(soup, "span.Notes")
  if len(notes) % 10 != 0:
    print "Unexpected number of span.notes in page!"
    sys.exit(1)

  # Every 10 "Notes" is one entry
  entries = [notes[i:i+10] for i in range(0, len(notes), 10)]

  trips = []
  for entry in entries:
    values = map(lambda x: x.text.strip(), entry)
    num_empty_values = values.count('')
    # Some entries, like car rentals or miles transfers, don't have all the fields.
    if num_empty_values < 4:
      trips.append(values)
  return trips


def dump_csv(flights):
  """Writes the flights as a CSV to stdout."""

  writer = csv.writer(sys.stdout)
  writer.writerow([
    'date',
    'flight', 
    'airports',
    'booking_class',
    'miles',
    'bonus_miles',
    'total_miles',
    'premier_miles',
    'premier_segments',
  ])
  writer.writerows(flights)


def setup_browser():
  """Sets up a browser that will store cookies and state."""
  browser = mechanize.Browser()
  browser.set_handle_equiv(True)
  browser.set_handle_gzip(True)
  browser.set_handle_redirect(True)
  browser.set_handle_referer(True)
  browser.set_handle_robots(False)
  # Follows refresh 0 but not hangs on refresh > 0    
  browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
  # User-Agent (this is cheating, ok?)
  browser.addheaders = [('User-agent', USER_AGENT)]
  return browser


if __name__ == "__main__":
  main(sys.argv)
