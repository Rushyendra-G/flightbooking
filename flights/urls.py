# flights/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.flight_search, name='search_flights'),
]