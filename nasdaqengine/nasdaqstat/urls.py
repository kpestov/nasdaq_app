from django.urls import path
from .views import *


urlpatterns = [
    path('', TickerHistorical.as_view(), name='ticker_historical_url'),
    path('insider/', TickerInsiderTrades.as_view(), name='ticker_insider_trades_url'),
    path('insider/<str:insider_name>/', InsiderOperations.as_view(), name='insider_operations_url'),
    path('analytics', Analytics.as_view(), name='analytics_url'),
    path('delta', Delta.as_view(), name='delta_url'),
]