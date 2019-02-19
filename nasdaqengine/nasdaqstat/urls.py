from django.urls import path
from .views import *


urlpatterns = [
    path('', TickerList.as_view(), name='ticker_list_url'),
    path('<str:ticker>/', TickerHistorical.as_view(), name='ticker_historical_url'),
    path('<str:ticker>/insider/', TickerInsiderTrades.as_view(), name='ticker_insider_trades_url'),
    path('<str:ticker>/insider/<str:insider_name>/', InsiderOperations.as_view(), name='insider_operations_url'),
    path('<str:ticker>/analytics', Analytics.as_view(), name='analytics_url'),
]


# http://127.0.0.1:8000/goog/analytics?date_from=2019-02-15&date_to=2019-02-14