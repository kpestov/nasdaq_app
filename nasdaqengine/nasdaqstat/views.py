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
