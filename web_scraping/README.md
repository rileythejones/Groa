# Web Scraping

General overview of our process, why we made certain choices, and what data is ultimately being fed into our DB.


## Quick Rundown of the Scraper
This scraper uses a list of IMDB movie IDs pulled from their publicly available tarball files at https://datasets.imdbws.com/ to return movie review and ratings. It can use this list of IDs to scrape not only IMDB.com itself, but also letterboxd.com. In addition, it can scrape a complete list of all movies on Netflix and their URLs from finder.com. The scraper can also insert the data it scrapes into a table on AWS RDS or be configured to insert into some other SQL database.

## Blockers
As of 02/03/2020 IMDB, Letterboxd, and Finder scraping are supported. Currently, only IMDB supports the capability to compare inputs to the existing database and reject duplicates.

## Installing
The accompanying pipfile contains all of the necessary dependencies:
Beautiful Soup 4.8.2
python-decouple 3.3
pandas 0.25.0
psycopg2 2.8.4
requests 2.22.0

As of 02/03/2020 these are all the most recent versions of these modules. It is possible, but unlikely, that future versions may break the scraper.

## Deployment

### Development
To run the scraper locally, make a .env file with environment variables HOST, PORT, PASSWORD, and FILENAME. HOST, PORT, and PASSWORD should be the associated values for the database you are inserting into. FILENAME should be the path to the .csv file you will be reading the IMDB movie IDs from. You can run scraper.py directly and answer a few questions to configure the scraper.
Start at which row? This is the index number in the .csv that the scraper will start from. Note that this starts at zero. Inclusive.
End at which row? Last index number to read. Inclusive.
Maximum iterations? Maximum number of webpages the scraper will read before inserting into the database. Increasing this number will slightly increase speed at a slight cost to stability. From experience 100-500 are good values.
Which scraper instance is this? If you have logging features (explained below) enabled and are running multiple instances of scraper.py running at once, you need to give each instance a unique value in this field. Does not have to be a number.
Are you scraping IMDB? Answer yes if you are scraping IMBD.
Do you want to reject reviews already in the database? Answer yes for the update route, no for the scrape route. More on these below.



## Built With

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Python Library for pulling HTML data
* [psycopg2](https://pypi.org/project/psycopg2/) - PostgresSQL database adapter
* [Amazon RDS](https://aws.amazon.com/rds/?nc2=h_ql_prod_fs_rds) - The scraper outputs into two RDS DB tables
