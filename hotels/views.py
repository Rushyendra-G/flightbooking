from django.shortcuts import render
from ExternalAPI.hotels.tbo_hotel_api import TBOApiWrapper

def home(request):
    api = TBOApiWrapper()
    countries = api.get_country_list()
    return render(request, 'hotels/home.html', {'countries': countries.get('CountryList', [])})

def city_search(request):
    if request.method == 'POST':
        country_code = request.POST.get('country_code')
        api = TBOApiWrapper()
        cities = api.get_city_list(country_code)
        return render(request, 'hotels/city_search.html', {'cities': cities.get('CityList', []), 'country_code': country_code})

def hotel_search(request, city_code):
    api = TBOApiWrapper()
    hotels = api.get_hotel_code_list(city_code)
    return render(request, 'hotels/hotel_search.html', {'hotels': hotels.get('Hotels', []), })

def hotel_details(request, hotel_code):
    api = TBOApiWrapper()
    hotel_details = api.get_hotel_details(hotel_code)
    return render(request, 'hotels/hotel_details.html', {'hotel': hotel_details.get('HotelDetails', [{}])[0]})
