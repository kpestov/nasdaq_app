#!/usr/bin/env python
import os
import sys
import time
import django
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool
from nasdaqstat.models import *

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), 'nasdaqengine/')))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), 'nasdaqengine/nasdaqengine/')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()


def get_companies():
    with open('tickers.txt') as f:
        companies_list = [company.rstrip().lower() for company in f]
        return companies_list


def historical_url_generator(companies_list):

    base_url = 'https://www.nasdaq.com/symbol/'

    for company in companies_list:
        historical_url = base_url + '{}/historical'.format(company.lower())
        yield historical_url


def insider_url_generator(companies_list):

    base_url = 'https://www.nasdaq.com/symbol/'

    for company in companies_list:

        historical_url = base_url + '{}/insider-trades'.format(company.lower())
        r = requests.get(historical_url)
        time.sleep(0.5)

        if r.status_code != 200:
            print('The server is not responding!')

        html = r.text
        soup = BeautifulSoup(html, 'lxml')

        try:
            pages = soup.find('ul', class_='pager').find_all('a', class_='pagerlink')[-1].get('href')
            total_pages = pages.split('=')[1]

            if int(total_pages) < 10:
                page_quantity = int(total_pages)
            else:
                page_quantity = 10

            for page in range(1, page_quantity + 1):
                insider_url = base_url + '{}/insider-trades?page={}'.format(company.lower(), page)

                yield insider_url
                print('{} is in parsing process'.format(company.lower()))
        except:
            print('There is no <ul> tag with class=pager')
            break


def convert_data(data):
    if len(data) < 10:
        converted_data = datetime.today().strftime('%Y-%m-%d')
        return converted_data
    else:
        converted_data = datetime.strptime(data, '%m/%d/%Y').strftime('%Y-%m-%d')
        return converted_data


def historical_parser(html):
    soup = BeautifulSoup(html, 'lxml')

    try:
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
            print('-')
    except:
        print('There is no <div> tag with class=genTable')


def insider_parser(html):
    soup = BeautifulSoup(html, 'lxml')

    try:
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
            print('-')
    except:
        print('There is no <table> tag with class=certain-width')


def company_in_db(company):
    if Company.objects.filter(ticker=company).exists():
        exist_company = Company.objects.get(ticker=company)
        return exist_company.id
    else:
        new_company = Company(ticker=company)
        new_company.save()
        return new_company.id


def insider_in_db(insider_data):
    if Insider.objects.filter(name=insider_data['insider']).exists():
        exist_insider = Insider.objects.get(name=insider_data['insider'])
        return exist_insider.id
    else:
        new_insider = Insider.objects.create(name=insider_data['insider'], relation=insider_data['relation'])
        return new_insider.id


def write_historical_data(historical_urls):
    company_name = historical_urls.split('/')[4]
    company_id = company_in_db(company_name)
    historical_html = requests.get(historical_urls).text
    print('{} is in parsing process'.format(company_name))
    time.sleep(0.5)

    for historical_data in historical_parser(historical_html):
        Historical.objects.create(ticker_id=company_id, **historical_data)


def write_insider_data(insider_urls):

    company_name = insider_urls.split('/')[4]
    company_id = company_in_db(company_name)
    insider_html = requests.get(insider_urls).text
    print('{} is in parsing process'.format(company_name))
    time.sleep(0.5)

    for insider_data in insider_parser(insider_html):
        insider_id = insider_in_db(insider_data)
        InsiderTrades.objects.create(
            ticker_id=company_id,
            insider_id=insider_id,
            last_date=insider_data['last_date'],
            transaction_type=insider_data['transaction_type'],
            owner_type=insider_data['owner_type'],
            shares_traded=insider_data['shares_traded'],
            last_price=insider_data['last_price'],
            shares_held=insider_data['shares_held']
        )


def make_all():

    print('Enter the number of threads:')
    num_threads = int(input())
    print('\n')

    companies_list = get_companies()
    historical_urls = historical_url_generator(companies_list)
    insider_urls = insider_url_generator(companies_list)

    with Pool(num_threads) as p:
        p.map(write_historical_data, historical_urls)
        p.map(write_insider_data, insider_urls)


def time_logger(func):
    def wrapper():
        start = datetime.now()
        func()
        end = datetime.now()
        estimated_time = end - start
        print('Parsing is done in {}'.format(estimated_time))
    return wrapper


@time_logger
def main():
    make_all()

    num_companies = Company.objects.count()
    num_insiders = Insider.objects.count()
    num_historicals = Historical.objects.count()
    num_insidertrades = InsiderTrades.objects.count()

    print('\n{} records were created in the table "Company"\n'
          '\n{} records were created in the table "Insider"\n'
          '\n{} records were created in the table "HIstorical"\n'
          '\n{} records were created in the table "Insider Trades"\n'.format(
                                                                             num_companies,
                                                                             num_insiders,
                                                                             num_historicals,
                                                                             num_insidertrades
                                                                             ))


if __name__ == '__main__':
    main()
