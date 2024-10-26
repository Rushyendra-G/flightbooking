# views.py
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from .forms import (
    CountrySelectForm, CitySelectForm, SearchDetailsForm,
    RoomConfigurationForm
)
from ExternalAPI.hotels.tbo_hotel_api import TBOApiWrapper
from datetime import datetime
import json

class BaseHotelView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = TBOApiWrapper()

class HomeView(BaseHotelView):
    def get(self, request):
        try:
            countries = self.api.get_country_list()
            form = CountrySelectForm(choices=countries.get('CountryList', []))
            return render(request, 'hotels/home.html', {'form': form})
        except Exception as e:
            messages.error(request, f"Unable to fetch countries: {str(e)}")
            return render(request, 'hotels/error.html')

class CitySelectionView(BaseHotelView):
    def post(self, request):
        country_code = request.POST.get('country')
        try:
            cities = self.api.get_city_list(country_code)
            form = CitySelectForm(choices=cities.get('CityList', []))
            search_form = SearchDetailsForm()
            room_form = RoomConfigurationForm()
            
            context = {
                'form': form,
                'search_form': search_form,
                'room_form': room_form,
                'country_code': country_code
            }
            return render(request, 'hotels/city_selection.html', context)
        except Exception as e:
            messages.error(request, f"Unable to fetch cities: {str(e)}")
            return redirect('home')

class HotelSearchView(BaseHotelView):
    def post(self, request):
        try:
            # Get the city code from the request
            city_code = request.POST.get('city')
            hotel_codes_response = self.api.get_hotel_code_list(city_code, detailed_response=True)

            print(f"Searching for hotels in {city_code}...")
            
            # Check if the API response was successful and contains hotels
            if hotel_codes_response['Status']['Code'] != 200 or not hotel_codes_response.get('Hotels'):
                messages.warning(request, "No hotels found in the selected city.")
                return redirect('hotels:city_selection')
            
            # Save all hotels
            all_hotels = hotel_codes_response['Hotels']
            
            # Extract hotel codes
            hotel_codes = ','.join([hotel['HotelCode'] for hotel in hotel_codes_response['Hotels']])
            
            # Process search parameters and check availability
            search_data = self.process_search_data(request.POST)
            search_data['hotel_codes'] = hotel_codes
            
            hotels = self.api.search_hotels(**search_data)
            print(f"Search results: {json.dumps(hotels, indent=4)}")
            
            # Store search parameters in session for pagination/filtering
            request.session['search_params'] = search_data
            
            # Create a map of hotel details
            hotel_details_map = {hotel['HotelCode']: hotel for hotel in hotel_codes_response['Hotels']}
            
            available_hotels = []
            if hotels.get("Hotels"):
                for hotel in hotels["Hotels"]:
                    hotel_code = hotel['HotelCode']
                    if hotel_code in hotel_details_map:
                        # Merge basic hotel info with availability data
                        hotel_info = hotel_details_map[hotel_code].copy()
                        hotel_info.update(hotel)
                        available_hotels.append(hotel_info)
                
            print(f"Available hotels: {len(available_hotels)}")
            
            return render(request, 'hotels/hotel_list.html', {
                'hotels': available_hotels,
                'search_params': search_data,
                'total_hotels': len(hotel_codes_response['Hotels']),
                'available_hotels': len(available_hotels),
                'all_hotels': all_hotels
            })
        except Exception as e:
            print(f"Search failed: {str(e)}")
            messages.error(request, f"Search failed: {str(e)}")
            return redirect('home')
    
    def process_search_data(self, post_data):
        check_in = datetime.strptime(post_data['check_in'], '%Y-%m-%d')
        check_out = datetime.strptime(post_data['check_out'], '%Y-%m-%d')
        
        # Process room configuration
        pax_rooms = []
        room_count = int(post_data.get('room_count', 1))
        
        for i in range(room_count):
            room = {
                "Adult": int(post_data.get(f'adults_{i}', 1)),
                "Children": int(post_data.get(f'children_{i}', 0)),
                "ChildrenAges": []  # Could be enhanced to handle children ages
            }
            pax_rooms.append(room)
        
        return {
            'check_in': check_in.strftime('%Y-%m-%d'),
            'check_out': check_out.strftime('%Y-%m-%d'),
            'hotel_codes': '',  # This will be populated with the hotel codes
            'guest_nationality': post_data.get('nationality'),
            'pax_rooms': pax_rooms,
            'is_detailed_response': True,
            'filters': {
                'Refundable': False,
                'NoOfRooms': room_count,
                'MealType': 0,
                'OrderBy': 0,
                'StarRating': int(post_data.get('star_rating', 0)),
                'HotelName': None
            }
        }
    
class HotelDetailView(BaseHotelView):
    def get(self, request, hotel_code):
        try:
            hotel_details = self.api.get_hotel_details(hotel_code)
            return render(request, 'hotels/hotel_detail.html', {
                'hotel': hotel_details.get('HotelDetails', [{}])[0],
                'search_params': request.session.get('search_params')
            })
        except Exception as e:
            messages.error(request, f"Unable to fetch hotel details: {str(e)}")
            return redirect('home')