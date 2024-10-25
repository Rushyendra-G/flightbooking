from django.urls import path
from . import views

urlpatterns = [
    path('hotel-search', views.home, name='home'),
    path('city-search/', views.city_search, name='city_search'),
    path('hotels/<str:city_code>/', views.hotel_search, name='hotel_search'),
    path('hotel/<str:hotel_code>/', views.hotel_details, name='hotel_details'),
]
