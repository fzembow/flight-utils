
# About
United doesn't provide an API or export of your frequent flier information, such as the flights which you have taken on United or any of their Star Alliance partners. This is a script that allows you to export your flight data from the United website.

# Dependencies
[mechanize](http://wwwsearch.sourceforge.net/mechanize/) allows for programmatic navigation of web pages. Install it with `easy_install mechanize`.
[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) makes parsing HTML easy. Install it with either: `easy_install BeautifulSoup` or `pip install BeautifulSoup`.
[soupselect](http://code.google.com/p/soupselect/) makes working with BeautifulSoup easier. It's bundled in the code.

# Usage
python united.py [UNITED USERNAME] [password]

Prints out all of your flight history in CSV format.
