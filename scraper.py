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

# url = https://www.nasdaq.com/symbol/goog/insider-trades?page=2


def get_companies():
    with open('tickers.txt') as f:
        companies_list = [company.rstrip().lower() for company in f]
        return companies_list


def get_html(url):
    response = requests.get(url)
    return response.text


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')

    pages = soup.find('ul', class_='pager').find_all('a', class_='pagerlink')[-1].get('href')
    total_pages = pages.split('=')[1]
    return int(total_pages)


def get_ten_pages(total_pages):
    if total_pages < 10:
        return total_pages
    return 10


def convert_data(data):
    if len(data) < 10:
        converted_data = datetime.today().strftime('%Y-%m-%d')
        return converted_data
    else:
        converted_data = datetime.strptime(data, '%m/%d/%Y').strftime('%Y-%m-%d')
        return converted_data


def get_insiders_info(html, ticker):
    insiders_info = []
    companies_insiders = dict()

    soup = BeautifulSoup(html, 'lxml')

    table_lines = soup.find('table', class_='certain-width').find_all('tr')[1:]

    for line in table_lines:
        insiders_info.append(dict(
            insider=line.find_all('td')[0].get_text(),
            relation=line.find_all('td')[1].get_text(),

            last_date=convert_data(line.find_all('td')[2].get_text()),

            transaction_type=line.find_all('td')[3].get_text(),
            owner_type=line.find_all('td')[4].get_text(),
            shares_traded=line.find_all('td')[5].get_text().replace(',', ''),
            last_price=line.find_all('td')[6].get_text(),
            shares_held=line.find_all('td')[7].get_text().replace(',', '')
        ))
    #
    # companies_insiders = dict(company=dict(ticker=dict(
    #                                        type='insider_trades',
    #                                        table_info=insiders_info
    #                                        )))

    companies_insiders[ticker] = dict(type='insider_trades', table_info=insiders_info)

    return json.dumps(companies_insiders, indent=4)
    # print(json.dumps(companies_insiders, indent=4))
    # print(companies_insiders)


def main():
    # url = 'https://www.nasdaq.com/symbol/goog/insider-trades'
    base_url = 'https://www.nasdaq.com/symbol/'
    info_list = ['/historical', '/insider-trades']
    page_part = '?page='

    tickers_list = get_companies()

    for ticker in tickers_list:

        url_gen = '{}{}{}'.format(base_url, ticker, info_list[1])

        total_pages = get_total_pages(get_html(url_gen))
        ten_pages = get_ten_pages(total_pages)

        for i in range(1, 2):
            url_gen = '{}{}{}{}'.format(base_url, ticker, info_list[1], page_part + str(i))

            html = get_html(url_gen)

            get_insiders_info(html, ticker)


if __name__ == '__main__':
    print(main())


