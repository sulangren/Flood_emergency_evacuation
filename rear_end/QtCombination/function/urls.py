"""
URL configuration for QtCombination project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from function.views import NearbySheltersAPIView, RescuePathAPIView, ShelterListAPIView,RescuePriorityDispatchAPIView

urlpatterns = [
    path("nearby_shelters/",NearbySheltersAPIView.as_view(), name='query-latest-weather'),
    path('rescue_path/', RescuePathAPIView.as_view(), name='rescue-path'),
    path('rescue_stations/', ShelterListAPIView.as_view(), name='rescue-stations'),
    path('calculate_rescue_distance/',RescuePriorityDispatchAPIView.as_view(), name='collective-relief')
]
