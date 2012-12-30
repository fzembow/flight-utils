# About
United Airlines doesn't provide an API or export of your frequent flier information, 
such as the flights which you have taken on United or any of their Star Alliance partners. 
This is a script that allows you to export your flight data from the United website, including
dates, airports, and miles.

It works by scraping a United MileagePlus account, given a username and password. This means that
the script can break any time that United decides to update its page structure or URLs. Since
United doesn't use HTTPS, running this script is just as secure as accessing United directly
in your browser. The credentials aren't stored anywhere by the script.

# Dependencies
- [mechanize](http://wwwsearch.sourceforge.net/mechanize/) allows for programmatic navigation of web pages. Install it with `easy_install mechanize`.
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) makes parsing HTML easy. Install it with either: `easy_install BeautifulSoup` or `pip install BeautifulSoup`.
- [soupselect](http://code.google.com/p/soupselect/) makes working with BeautifulSoup easier. It's bundled in the code.

# Usage

```
united.py [-h] [--include_non_flights] USERNAME PASSWORD

Fetch United MileagePlus flight history

positional arguments:
  USERNAME              MileagePlus Number or Username.
  PASSWORD              PIN or password.

optional arguments:
  -h, --help            show this help message and exit
  --include_non_flights
                        Whether to include non-flight entries, like mile
                        transfers or car rentals.
```
