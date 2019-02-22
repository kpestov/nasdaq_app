# nasdaq_app
Web service that parses quotes of companies from https://www.nasdaq.com/

**Before running the django application you must run the scraper.py to fill the database with a data from Nasdaq!**

# Functionality
- grabs the data from:
  - http://www.nasdaq.com/symbol/cvx/historical
  - http://www.nasdaq.com/symbol/cvx/insider-trades
- writes historical stock and insider trades to postgresql
- displays parsed data and analytics in web pages 

# How to run scraper
```
python manage.py scraper -th 10
```
where "-th 10" - number of threads 

# How to run django app
```
python manage.py runserver
```
