# task_external_api.py

import os
import json
from typing import Dict, Any
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flightbooking.settings')
import django
django.setup()
from django.db import transaction
from django.utils import timezone
from dotenv import load_dotenv

from ExternalAPI.hotels.tbo_hotel_api import TBOApiWrapper
from ExternalAPI.flights.tbo_flight_api import FlightAPI, AuthRequest

from external_api.models import (
    ExternalAPISync,
    ExternalTBOCountry,
    ExternalTBOCity,
    ExternalTBOHotel,
    ExternalTBOFlightToken
)

load_dotenv()

class TravelAPISync:
    def __init__(self):
        pass

    def sync_tbo_hotels(self):
        """Synchronize TBO Hotels data"""
        api = TBOApiWrapper()

        try:
            # 1. Sync Countries
            print("Starting synchronization of countries.")
            self.log_sync('tbo', 'hotels', 'IN_PROGRESS', {'step': 'countries'})
            countries = api.get_country_list()
            print(f"Retrieved {len(countries['CountryList'])} countries.")
            self.sync_countries('tbo', countries['CountryList'])
            print("Finished synchronization of countries.")

            # 2. Sync Cities for each country
            for i, country in enumerate(countries['CountryList'], start=1):
                print(f"({i}/{len(countries['CountryList'])}) Starting synchronization of cities for country: {country['Name']} ({country['Code']}).")
                self.log_sync('tbo', 'hotels', 'IN_PROGRESS', {
                    'step': 'cities',
                    'country': country['Code']
                })
                cities = api.get_city_list(country['Code'])
                print(f"Retrieved {len(cities['CityList'])} cities for country {country['Code']}.")
                self.sync_cities('tbo', country['Code'], cities['CityList'])
                print(f"Finished synchronization of cities for country {country['Code']}.")

                # 3. Sync Hotels for each city
                for j, city in enumerate(cities['CityList'], start=1):
                    print(f"({i}/{len(countries['CountryList'])}) ({j}/{len(cities['CityList'])}) Starting synchronization of hotels for city: {city['Name']} ({city['Code']}).")
                    self.log_sync('tbo', 'hotels', 'IN_PROGRESS', {
                        'step': 'hotels',
                        'country': country['Code'],
                        'city': city['Code']
                    })
                    hotels = api.get_hotel_code_list(city['Code'], True)
                    print(f"Retrieved {len(hotels.get('Hotels', []))} hotels for city {city['Code']}.")
                    self.sync_hotels('tbo', city['Code'], hotels.get('Hotels', []))
                    print(f"Finished synchronization of hotels for city {city['Code']}.")

            self.log_sync('tbo', 'hotels', 'SUCCESS')
            print("Synchronization of TBO Hotels data completed successfully.")

        except Exception as e:
            self.log_sync('tbo', 'hotels', 'ERROR', {'error': str(e)})
            print(f"Error during synchronization: {str(e)}")
            raise

    @transaction.atomic
    def sync_countries(self, provider: str, countries: Dict[str, Any]):
        """Sync countries to the database"""
        print("Syncing countries to the database.")
        for i, country in enumerate(countries, start=1):
            print(f"({i}/{len(countries)}) Syncing country: {country['Name']} ({country['Code']}).")
            country_obj, created = ExternalTBOCountry.objects.update_or_create(
                provider=provider,
                provider_country_code=country['Code'],
                defaults={
                    'name': country['Name'],
                    'details': json.dumps(country)
                }
            )
            if created:
                print(f"Added new country to database: {country['Name']} ({country['Code']}).")
                country_obj.save()

    @transaction.atomic
    def sync_cities(self, provider: str, country_code: str, cities: Dict[str, Any]):
        """Sync cities to the database"""
        print(f"Syncing cities to the database for country code: {country_code}.")
        for i, city in enumerate(cities, start=1):
            print(f"({i}/{len(cities)}) Syncing city: {city['Name']} ({city['Code']}).")
            country_obj = ExternalTBOCountry.objects.get(provider=provider, provider_country_code=country_code)
            city_obj, created = ExternalTBOCity.objects.update_or_create(
                provider=provider,
                provider_city_code=city['Code'],
                defaults={
                    'country': country_obj,
                    'name': city['Name'],
                    'details': json.dumps(city)
                }
            )
            if created:
                print(f"Added new city to database: {city['Name']} ({city['Code']}).")
                city_obj.save()

    @transaction.atomic
    def sync_hotels(self, provider: str, city_code: str, hotels: Dict[str, Any]):
        """Sync hotels to the database"""
        print(f"Syncing hotels to the database for city code: {city_code}.")
        for index, hotel in enumerate(hotels):
            print(f"Syncing hotel({index + 1}/{len(hotels)}): {hotel['HotelName']} ({hotel['HotelCode']}).")
            city_obj = ExternalTBOCity.objects.get(provider=provider, provider_city_code=city_code)
            hotel_obj, created = ExternalTBOHotel.objects.update_or_create(
                provider=provider,
                provider_hotel_code=hotel['HotelCode'],
                defaults={
                    'city': city_obj,
                    'name': hotel['HotelName'],
                    'rating': hotel['HotelRating'].replace('Star', ''),
                    'address': hotel['Address'],
                    'latitude': float(hotel['Map'].split('|')[0]),
                    'longitude': float(hotel['Map'].split('|')[1]),
                    'facilities': json.dumps(hotel.get('HotelFacilities', [])),
                    'attractions': json.dumps(hotel.get('Attractions', [])),
                    'description': hotel.get('Description', ''),
                    'details': json.dumps(hotel)
                }
            )
            if created:
                print(f"Added new hotel to database: {hotel['HotelName']} ({hotel['HotelCode']}).")
                hotel_obj.save()

    def log_sync(self, provider: str, api_type: str, status: str, details: Dict[str, Any] = None):
        """Log synchronization status"""
        ExternalAPISync.objects.create(
            provider=provider,
            api_type=api_type,
            last_sync=timezone.now(),
            status=status,
            details=json.dumps(details or {})
        )

    def sync_flight_token(self):
        """Synchronize TBO Flight API token"""
        try:
            self.log_sync('tbo', 'flight', 'IN_PROGRESS', {'step': 'authentication'})
            
            # Create auth request
            auth_request = AuthRequest(
                client_id=os.getenv("TBO_CLIENT_ID"),
                username=os.getenv("TRAVELLYKE_TBO_USERNAME"),
                password=os.getenv("TRAVELLYKE_TBO_PASSWORD"),
                end_user_ip=os.getenv("TBO_END_USER_IP")
            )
            
            # Get new token
            api = FlightAPI(os.getenv("TBO_END_USER_IP"))
            new_token = api.authenticate(auth_request)

            print("Synchronization of TBO Flight API token completed successfully.")
            print("New token: " + new_token)
            
            with transaction.atomic():
                # Deactivate all existing tokens
                ExternalTBOFlightToken.objects.filter(
                    provider='tbo',
                    is_active=True
                ).update(is_active=False)
                
                # Create new token entry
                ExternalTBOFlightToken.objects.create(
                    provider='tbo',
                    token_id=new_token,
                    is_active=True
                )
            
            self.log_sync('tbo', 'flight', 'SUCCESS')
            
        except Exception as e:
            self.log_sync('tbo', 'flight', 'ERROR', {'error': str(e)})
            raise

def main():
    sync = TravelAPISync()
    sync.sync_flight_token()
    sync.sync_tbo_hotels()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'flight-token':
        sync = TravelAPISync()
        sync.sync_flight_token()
    else:
        main()
