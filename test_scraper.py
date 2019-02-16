#!/usr/bin/env python
import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime


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


def url_generator(companies_list):
    base_url = 'https://www.nasdaq.com/symbol/'
    for company in companies_list:
        historical_url = base_url + '{}/historical'.format(company.lower())
        insider_url = base_url + '{}/insider-trades'.format(company.lower())

        yield historical_url, insider_url


# def insider_url_generator(companies_list):
#     for company in companies_list:
#         insider_url = 'https://www.nasdaq.com/symbol/{}/insider-trades'.format(company.lower())
#         # insider_html = requests.get(insider_url).text
#         yield insider_url


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

    table_lines = soup.find('div', class_='genTable').find_all('tr')[2:]

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


def insider_parser(html):
    soup = BeautifulSoup(html, 'lxml')

    table_lines = soup.find('table', class_='certain-width').find_all('tr')[1:]

    for line in table_lines:
        last_price_value = line.find_all('td')[6].get_text()

        if not last_price_value:
            last_price_value = None
        else:
            last_price_value = float(last_price_value.replace(',', ''))

        insider_data = dict(
            insider=line.find_all('td')[0].get_text(),
            relation=line.find_all('td')[1].get_text(),
            last_date=convert_data(line.find_all('td')[2].get_text()),
            transaction_type=line.find_all('td')[3].get_text(),
            owner_type=line.find_all('td')[4].get_text(),
            shares_traded=float(line.find_all('td')[5].get_text().replace(',', '')),
            last_price=last_price_value,
            shares_held=float(line.find_all('td')[7].get_text().replace(',', '')),
        )

        yield insider_data


def write_historical_data():
    companies_list = get_companies()
    for url in url_generator(companies_list):
        historical_url = url[0]
        company = Company.objects.create(ticker=historical_url.split('/')[4])
        historical_html = requests.get(historical_url).text
        for data in historical_parser(historical_html):
            Historical.objects.create(ticker=company, **data)


def write_insider_data():
    companies_list = get_companies()
    for url in url_generator(companies_list):
        insider_url = url[1]
        company = Company.objects.create(ticker=insider_url.split('/')[4])
        insider_html = requests.get(insider_url).text
        for data in insider_parser(insider_html):
            insider = Insider.objects.create(name=data['insider'], relation=data['relation'])
            InsiderTrades.objects.create(
                ticker=company,
                insider=insider,
                last_date=data['last_date'],
                transaction_type=data['transaction_type'],
                owner_type=data['owner_type'],
                shares_traded=data['shares_traded'],
                last_price=data['last_price'],
                shares_held=data['shares_held']
            )


def write_data():
    companies_list = get_companies()
    for url in url_generator(companies_list):
        historical_url = url[0]
        insider_url = url[1]
        company_name = Company.objects.create(ticker=historical_url.split('/')[4])
        historical_html = requests.get(historical_url).text
        insider_html = requests.get(insider_url).text

        for historical_data in historical_parser(historical_html):
            Historical.objects.create(ticker=company_name, **historical_data)

        for insider_data in insider_parser(insider_html):
            insider = Insider.objects.create(name=insider_data['insider'], relation=insider_data['relation'])
            InsiderTrades.objects.create(
                ticker=company_name,
                insider=insider,
                last_date=insider_data['last_date'],
                transaction_type=insider_data['transaction_type'],
                owner_type=insider_data['owner_type'],
                shares_traded=insider_data['shares_traded'],
                last_price=insider_data['last_price'],
                shares_held=insider_data['shares_held']
            )


if __name__ == '__main__':
    write_data()
    # write_historical_data()
    # write_insider_data()

