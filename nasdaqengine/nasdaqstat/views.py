from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import get_object_or_404

from .models import *


class TickerList(View):
    def get(self, request):
        tickers = Company.objects.all()
        return render(request, 'nasdaqstat/index.html', context={'tickers': tickers})


class TickerHistorical(View):
    def get(self, request, ticker):
        ticker_obj = get_object_or_404(Company, ticker__iexact=ticker)
        ticker_historical = Historical.objects.filter(ticker=ticker_obj)

        return render(request, 'nasdaqstat/historical.html', context={'ticker': ticker,
                                                                      'ticker_historical': ticker_historical})


class TickerInsiderTrades(View):
    def get(self, request, ticker):

        ticker_obj = Company.objects.get(ticker=ticker)

        ticker_insider_trades = InsiderTrades.objects.filter(ticker=ticker_obj)

        return render(request, 'nasdaqstat/insider_trades.html', context={'ticker': ticker,
                                                                          'ticker_insider_trades': ticker_insider_trades})


class InsiderOperations(View):
    def get(self, request, ticker, insider_name):
        ticker_obj = Company.objects.get(ticker=ticker)
        insider_obj = Insider.objects.get(name=insider_name)
        insider_operations = InsiderTrades.objects.filter(ticker=ticker_obj).filter(insider=insider_obj.id)

        context = {'ticker': ticker,
                   'insider_operations': insider_operations,
                   'insider_name': insider_name,
                   }

        return render(request, 'nasdaqstat/insider_operations.html', context)


class Analytics(View):
    def get(self, request, ticker):
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

            return render(request, 'nasdaqstat/analytics.html', context)







