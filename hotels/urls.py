# urls.py
from django.urls import path
from .views import HomeView, CitySelectionView, HotelSearchView, HotelDetailView

app_name = 'hotels'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('cities/', CitySelectionView.as_view(), name='city_selection'),
    path('search/', HotelSearchView.as_view(), name='hotel_search'),
    path('hotel/<str:hotel_code>/', HotelDetailView.as_view(), name='hotel_detail'),
]