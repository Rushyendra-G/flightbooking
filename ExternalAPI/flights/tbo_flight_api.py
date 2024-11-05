# ExternalAPI/flights/tbo_flight_api.py

import requests
import json
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from external_api.models import ExternalTBOFlightToken  # Import from main file

class AuthRequest:
    def __init__(self, client_id, username, password, end_user_ip):
        self.ClientId = client_id
        self.UserName = username
        self.Password = password
        self.EndUserIp = end_user_ip

    def to_dict(self):
        return {
            "ClientId": self.ClientId,
            "UserName": self.UserName,
            "Password": self.Password,
            "EndUserIp": self.EndUserIp
        }

class Segment:
    def __init__(self, origin, destination, cabin_class, departure_time, arrival_time):
        self.Origin = origin
        self.Destination = destination
        self.FlightCabinClass = cabin_class
        self.PreferredDepartureTime = departure_time
        self.PreferredArrivalTime = arrival_time

    def to_dict(self):
        return {
            "Origin": self.Origin,
            "Destination": self.Destination,
            "FlightCabinClass": self.FlightCabinClass,
            "PreferredDepartureTime": self.PreferredDepartureTime,
            "PreferredArrivalTime": self.PreferredArrivalTime,
        }

class SearchRequest:
    def __init__(self, end_user_ip, token_id, adult_count, child_count, infant_count, journey_type, segments, direct_flight=False, one_stop_flight=False, preferred_airlines=None):
        self.EndUserIp = end_user_ip
        self.TokenId = token_id
        self.AdultCount = adult_count
        self.ChildCount = child_count
        self.InfantCount = infant_count
        self.DirectFlight = direct_flight
        self.OneStopFlight = one_stop_flight
        self.JourneyType = journey_type
        self.PreferredAirlines = preferred_airlines
        self.Segments = [segment.to_dict() for segment in segments]

    def to_dict(self):
        return {
            "EndUserIp": self.EndUserIp,
            "TokenId": self.TokenId,
            "AdultCount": self.AdultCount,
            "ChildCount": self.ChildCount,
            "InfantCount": self.InfantCount,
            "DirectFlight": self.DirectFlight,
            "OneStopFlight": self.OneStopFlight,
            "JourneyType": self.JourneyType,
            "PreferredAirlines": self.PreferredAirlines,
            "Segments": self.Segments,
        }

class FlightAPI:
    BASE_URL = "http://api.tektravels.com"
    AUTH_URL = f"{BASE_URL}/SharedServices/SharedData.svc/rest/Authenticate"
    SEARCH_URL = f"{BASE_URL}/BookingEngineService_Air/AirService.svc/rest/Search"

    def __init__(self, end_user_ip):
        self.end_user_ip = end_user_ip
        self.token_id = None
        self.load_token()

    def authenticate(self, auth_request):
        """Only performs authentication, doesn't store token"""
        response = requests.post(self.AUTH_URL, json=auth_request.to_dict())
        if response.status_code == 200:
            data = response.json()
            if data['Status'] == 1:
                return data['TokenId']
            else:
                raise Exception("Authentication failed: " + data['Error']['ErrorMessage'])
        else:
            raise Exception(f"HTTP Error: {response.status_code}")

    def is_token_valid(self):
        return self.token_id is not None

    def load_token(self):
        """Reads token from database"""
        try:
            latest_token = ExternalTBOFlightToken.objects.filter(
                provider='tbo',
                is_active=True
            ).latest('created_at')
            self.token_id = latest_token.token_id
        except ObjectDoesNotExist:
            self.token_id = None

    def search_flights(self, adult_count, child_count, infant_count, journey_type, segments, 
                      direct_flight=False, one_stop_flight=False, preferred_airlines=None):
        if not self.is_token_valid():
            raise Exception("Token is not valid. Please authenticate.")

        search_request = SearchRequest(self.end_user_ip, self.token_id, adult_count, 
                                    child_count, infant_count, journey_type, segments,
                                    direct_flight, one_stop_flight, preferred_airlines)
        response = requests.post(self.SEARCH_URL, json=search_request.to_dict())
        return response.json()
