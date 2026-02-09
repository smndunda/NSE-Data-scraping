[![Daily NSE Download](https://github.com/smndunda/NSE-Data-scraping/actions/workflows/daily_run.yml/badge.svg)](https://github.com/smndunda/NSE-Data-scraping/actions/workflows/daily_run.yml)
# Nairobi Securities Exchange (NSE) Daily Scraper

This project automatically scrapes the Daily Equity/Bond/Derivative Price List from the NSE website 
every weekday at 3:15 PM EAT.

## How it works
- **Language:** Python
- **Automation:** GitHub Actions
- **Libraries:** BeautifulSoup, Requests

The data is stored as PDFs in the `NSE_Daily_Reports` folder, organized by date.
