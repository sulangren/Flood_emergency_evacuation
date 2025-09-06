# urls.py
from django.contrib import admin
from django.urls import path, include

from query_api.views import QuerySortedListView, QuerySearchView,LatestWeatherAPIView

urlpatterns = [
    path("list/", QuerySortedListView.as_view(), name='query-sorted-list'),
    path("query/",QuerySearchView.as_view(), name='query-search'),
    path("weather/",LatestWeatherAPIView.as_view(), name='query-latest-weather'),
]
