import json

from django.core import serializers
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import connection

from .models import *


class TickerList(View):
    def get(self, request, api=False):
        tickers = Company.objects.all()

        if api:
            context_api = serializers.serialize('json', tickers, indent=4)
            return HttpResponse(context_api, content_type='application/json')

        return render(request, 'nasdaqstat/index.html', context={'tickers': tickers})


class TickerHistorical(View):
    def get(self, request, ticker, api=False):
        ticker_obj = get_object_or_404(Company, ticker__iexact=ticker)
        ticker_historical = Historical.objects.filter(ticker=ticker_obj)

        if api:
            context_api = serializers.serialize('json', ticker_historical, indent=4)
            return HttpResponse(context_api, content_type='application/json')

        return render(request, 'nasdaqstat/historical.html', context={'ticker': ticker,
                                                                      'ticker_historical': ticker_historical})


class TickerInsiderTrades(View):
    def get(self, request, ticker, api=False):

        ticker_obj = Company.objects.get(ticker=ticker)

        ticker_insider_trades = InsiderTrades.objects.filter(ticker=ticker_obj)

        if api:
            context_api = serializers.serialize('json', ticker_insider_trades, indent=4)
            return HttpResponse(context_api, content_type='application/json')

        return render(request, 'nasdaqstat/insider_trades.html', context={'ticker': ticker,
                                                                          'ticker_insider_trades': ticker_insider_trades})


class InsiderOperations(View):
    def get(self, request, ticker, insider_name, api=False):
        ticker_obj = Company.objects.get(ticker=ticker)
        insider_obj = Insider.objects.get(name=insider_name)
        insider_operations = InsiderTrades.objects.filter(ticker=ticker_obj).filter(insider=insider_obj.id)

        context = {'ticker': ticker,
                   'insider_operations': insider_operations,
                   'insider_name': insider_name,
                   }

        if api:
            context_api = serializers.serialize('json', insider_operations, indent=4)
            return HttpResponse(context_api, content_type='application/json')

        return render(request, 'nasdaqstat/insider_operations.html', context)


class Analytics(View):
    def get(self, request, ticker, api=False):
        analytics_query = request.GET
        if analytics_query['date_from'] and analytics_query['date_to']:
            ticker_obj = Company.objects.get(ticker=ticker)
            date_from_obj = Historical.objects.filter(ticker=ticker_obj).get(date=analytics_query['date_from'])
            date_to_obj = Historical.objects.filter(ticker=ticker_obj).get(date=analytics_query['date_to'])
            difference = dict(open=round(date_to_obj.open - date_from_obj.open, 3),
                              high=round(date_to_obj.high - date_from_obj.high, 3),
                              low=round(date_to_obj.low - date_from_obj.low, 3),
                              close=round(date_to_obj.close - date_from_obj.close, 3))

            context = {'ticker': ticker,
                       'date_from': date_from_obj,
                       'date_to': date_to_obj,
                       'difference': difference,
                       }

            if api:
                dump = json.dumps(difference, indent=4)
                return HttpResponse(dump, content_type='application/json')

            return render(request, 'nasdaqstat/analytics.html', context)


class Delta(View):
    def get(self, request, ticker, api=False):
        ticker_obj = Company.objects.get(ticker=ticker).id
        delta_query = request.GET

        if int(delta_query['value']) and delta_query['type'] in ['open', 'high', 'low', 'close']:
            query = (" SELECT MAX( select1.date ), date2 {up} FROM ("
                     " SELECT t1.date, t1.{type}, "
                     " MIN(t2.date) as date2 "
                     " FROM nasdaqstat_historical t1 "
                     " INNER JOIN nasdaqstat_historical t2 "
                     " ON (t2.{type} >= t1.{type} + {value} ) "
                     " AND t1.date < t2.date "
                     " AND t1.ticker_id = t2.ticker_id "
                     " WHERE t1.ticker_id = {ticker_id} "
                     " GROUP BY t1.id "
                     " ORDER BY t1.date ) select1 "
                     " GROUP BY date2 "
                     " UNION "
                     " SELECT MAX( select2.date ), date2{down} FROM ( "
                     " SELECT t1.date, t1.{type}, "
                     " MIN(t2.date) as date2 "
                     " FROM nasdaqstat_historical t1 "
                     " INNER JOIN nasdaqstat_historical t2 "
                     " ON (t2.{type} <= t1.{type} - {value} ) "
                     " AND t1.date < t2.date "
                     " AND t1.ticker_id = t2.ticker_id "
                     " WHERE t1.ticker_id = {ticker_id} "
                     " GROUP BY t1.id "
                     " ORDER BY t1.date ) select2 "
                     " GROUP BY date2 "
                     " ORDER BY date2; ".format(ticker_id=ticker_obj,
                                                value=delta_query['value'],
                                                type=delta_query['type'],
                                                up=", 'UP' direction",
                                                down=", 'DOWN' as direction")
                     )

            cursor = connection.cursor()
            cursor.execute(query)
            row = cursor.fetchall()

            context = {'ticker': ticker, 'row': row, 'type': delta_query['type'], 'value': delta_query['value']}

            if api:
                times = []
                for record in row:
                    start, finish = record[0], record[1]
                    answer = {'start': start.strftime('%m/%d/%Y'), 'finish': finish.strftime('%m/%d/%Y'),
                              'status': record[2]}
                    times.append(answer)

                return HttpResponse(json.dumps(times), content_type='application/json')

            return render(request, 'nasdaqstat/delta.html', context)







