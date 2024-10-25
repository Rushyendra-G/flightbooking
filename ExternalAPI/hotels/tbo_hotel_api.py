import json
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class TBOApiWrapper:
    BASE_URL = "http://api.tbotechnology.in/TBOHolidays_HotelAPI"

    def __init__(self):
        self.tbo_username = os.getenv("TBO_USERNAME")
        self.tbo_password = os.getenv("TBO_PASSWORD")
        self.travellyke_username = os.getenv("TRAVELLYKE_USERNAME")
        self.travellyke_password = os.getenv("TRAVELLYKE_PASSWORD")

    def _get(self, endpoint, auth_type='tbo', params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        if auth_type == 'tbo':
            auth = HTTPBasicAuth(self.tbo_username, self.tbo_password)
        else:
            auth = HTTPBasicAuth(self.travellyke_username, self.travellyke_password)
        
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def _post(self, endpoint, auth_type='tbo', data=None):
        url = f"{self.BASE_URL}/{endpoint}"
        if auth_type == 'tbo':
            auth = HTTPBasicAuth(self.tbo_username, self.tbo_password)
        else:
            auth = HTTPBasicAuth(self.travellyke_username, self.travellyke_password)
        
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()  # Raise an error for bad responses
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


