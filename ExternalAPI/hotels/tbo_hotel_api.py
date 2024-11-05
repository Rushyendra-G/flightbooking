# ExternalAPI/hotels/tbo_hotel_api.py

import json
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class TBOApiWrapper:
    BASE_URL = "http://api.tbotechnology.in/TBOHolidays_HotelAPI"
    SEARCH_URL = "https://affiliate.tektravels.com/HotelAPI/Search"

    def __init__(self):
        self.tbo_username = os.getenv("TBO_USERNAME")
        self.tbo_password = os.getenv("TBO_PASSWORD")
        self.travellyke_username = os.getenv("TRAVELLYKE_TBO_USERNAME")
        self.travellyke_password = os.getenv("TRAVELLYKE_TBO_PASSWORD")

    def _get(self, endpoint, auth_type='tbo', params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        if auth_type == 'tbo':
            auth = HTTPBasicAuth(self.tbo_username, self.tbo_password)
        else:
            auth = HTTPBasicAuth(self.travellyke_username, self.travellyke_password)
        
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, auth_type='tbo', data=None):
        url = f"{self.BASE_URL}/{endpoint}"
        if auth_type == 'tbo':
            auth = HTTPBasicAuth(self.tbo_username, self.tbo_password)
        else:
            auth = HTTPBasicAuth(self.travellyke_username, self.travellyke_password)
        
        response = requests.post(url, auth=auth, json=data)
        response.raise_for_status()
        return response.json()

    def _search_post(self, data):
        """Special post method for the search endpoint which uses a different base URL"""
        auth = HTTPBasicAuth(self.travellyke_username, self.travellyke_password)
        response = requests.post(self.SEARCH_URL, auth=auth, json=data)
        response.raise_for_status()
        return response.json()

    def get_country_list(self):
        return self._get("CountryList")

    def get_city_list(self, country_code):
        data = {'CountryCode': country_code}
        return self._post("CityList", data=data)

    def get_hotel_code_list(self, city_code, detailed_response=True):
        data = {
            'CityCode': city_code,
            'IsDetailedResponse': str(detailed_response).lower()
        }
        return self._post("TBOHotelCodeList", data=data)

    def get_hotel_details(self, hotel_code, language="EN"):
        data = {
            'HotelCodes': hotel_code,
            'Language': language
        }
        return self._post("Hoteldetails", data=data)

    def search_hotels(self, check_in, check_out, hotel_codes, guest_nationality, pax_rooms, 
                     response_time=23.0, is_detailed_response=True, filters=None):
        """
        Search for hotel availability.
        
        Args:
            check_in (str): Check-in date (YYYY-MM-DD)
            check_out (str): Check-out date (YYYY-MM-DD)
            hotel_codes (str): Comma-separated hotel codes or single code
            guest_nationality (str): ISO 3166-1 alpha-2 country code
            pax_rooms (list): List of room occupancy dictionaries, 
                              each of form {"Adult": 1, "Children": 0, "ChildrenAges": null}
            response_time (float): Expected response time in seconds
            is_detailed_response (bool): Include detailed information
            filters (dict): Optional search filters
        """
        data = {
            "CheckIn": check_in,
            "CheckOut": check_out,
            "HotelCodes": hotel_codes,
            "GuestNationality": guest_nationality,
            "PaxRooms": pax_rooms,
            "ResponseTime": response_time,
            "IsDetailedResponse": is_detailed_response,
            "Filters": filters or {
                "Refundable": False,
                "NoOfRooms": len(pax_rooms),
                "MealType": 0,     # 0 = All, 1 = With Meal, 2 = Room Only
                "OrderBy": 0,
                "StarRating": 0,
                "HotelName": None
            }
        }

        print(f"Searching for hotels: {json.dumps(data, indent=4)}")
        
        return self._search_post(data)
