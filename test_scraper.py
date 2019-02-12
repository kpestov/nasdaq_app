#!/usr/bin/env python
import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
import json


sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), 'nasdaqengine/')))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), 'nasdaqengine/nasdaqengine/')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from nasdaqstat.models import *


url = 'https://www.nasdaq.com/symbol/goog/historical'


def get_companies():
    with open('tickers.txt') as f:
        companies_list = [company.rstrip().lower() for company in f]
        return companies_list


def html_generator(companies_list):
    for company in companies_list:
        historical_url = 'https://www.nasdaq.com/symbol/{}/historical'.format(company.lower())
        yield requests.get(historical_url).text, company


# def get_html(url):
#     response = requests.get(url)
#     return response.text


def convert_data(data):
    if len(data) < 10:
        converted_data = datetime.today().strftime('%Y-%m-%d')
        return converted_data
    else:
        converted_data = datetime.strptime(data, '%m/%d/%Y').strftime('%Y-%m-%d')
        return converted_data


def historical_parser(html):
    soup = BeautifulSoup(html, 'lxml')

    table_lines = soup.find('div', class_='genTable').find_all('tr')[1:]

    for line in table_lines:

        historical_data = dict(
            date=convert_data(line.find_all('td')[0].get_text().strip()),
            open=float(line.find_all('td')[1].get_text().replace(',', '')),
            high=float(line.find_all('td')[2].get_text().replace(',', '')),
            low=float(line.find_all('td')[3].get_text().replace(',', '')),
            close=float(line.find_all('td')[4].get_text().replace(',', '')),
            volume=float(line.find_all('td')[5].get_text().replace(',', '')),
        )

        yield historical_data


def main():
    companies_list = get_companies()
    for page_and_company in html_generator(companies_list):
        company = Company.objects.create(ticker=page_and_company[1])
        print(company)
        for data in historical_parser(page_and_company[0]):
            Historical.objects.create(ticker=company, **data)



if __name__ == '__main__':
    main()

