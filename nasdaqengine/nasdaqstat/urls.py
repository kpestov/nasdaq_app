from django.urls import path
from .views import *


urlpatterns = [
    path('', TickerList.as_view(), name='ticker_list_url'),
    path('<str:ticker>/', TickerHistorical.as_view(), name='ticker_historical_url')
]
