import os
from ExternalAPI.hotels.tbo_hotel_api import TBOApiWrapper  # Adjust the import based on your file structure

def test_api():
    api = TBOApiWrapper()

    # Test get_country_list
    print("Testing get_country_list...")
    try:
        countries = api.get_country_list()
        print("Countries retrieved successfully:")
        for country in countries.get('CountryList', []):
            print(f"- {country['Name']} (Code: {country['Code']})")
    except Exception as e:
        print(f"Error retrieving countries: {e}")

    # Test get_city_list
    if countries and 'CountryList' in countries:
        country_code = countries['CountryList'][0]['Code']  # Get the first country code
        print("\nTesting get_city_list...")
        try:
            cities = api.get_city_list(country_code)
            print("Cities retrieved successfully:")
            for city in cities.get('CityList', []):
                print(f"- {city['Name']} (Code: {city['Code']})")
        except Exception as e:
            print(f"Error retrieving cities: {e}")

        last_hotel_code_for_test = None

        # Test get_hotel_code_list
        if cities and 'CityList' in cities:
            city_code = cities['CityList'][0]['Code']  # Get the first city code
            print("\nTesting get_hotel_code_list...")
            try:
                hotels = api.get_hotel_code_list(city_code)
                print("Hotels retrieved successfully:")
                for hotel in hotels.get('Hotels', []):
                    print(f"- {hotel['HotelName']} (Code: {hotel['HotelCode']})")
                    last_hotel_code_for_test = hotel['HotelCode']
            except Exception as e:
                print(f"Error retrieving hotels: {e}")

            # Test get_hotel_details
            if hotels and 'Hotels' in hotels:
                hotel_code = last_hotel_code_for_test
                print(f"\nTesting get_hotel_details for hotel code {hotel_code}...")
                print("\nTesting get_hotel_details...")
                try:
                    hotel_details = api.get_hotel_details(hotel_code)
                    print("Hotel details retrieved successfully:")
                    print(hotel_details)
                except Exception as e:
                    print(f"Error retrieving hotel details: {e}")

if __name__ == "__main__":
    test_api()
