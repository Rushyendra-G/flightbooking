# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import (
    PassengerForm,
    OneWayFlightForm,
    RoundTripFlightForm,
    MultiCityFormSet,
    FlightSearchOptionsForm
)
from ExternalAPI.flights.tbo_flight_api import FlightAPI, Segment

def format_datetime(date, time):
    return f"{date}T{time}"

def create_segment(origin, destination, date, time, cabin_class):
    datetime_str = format_datetime(date, time)
    return Segment(
        origin=origin.upper(),
        destination=destination.upper(),
        cabin_class=cabin_class,
        departure_time=datetime_str,
        arrival_time=datetime_str
    )

def flight_search(request):
    journey_type = request.GET.get('type', '1')
    error = None
    passenger_form = PassengerForm(request.POST or None)
    options_form = FlightSearchOptionsForm(request.POST or None)
    
    if request.method == 'POST':
        journey_type = request.POST.get('journey_type', '1')
        forms_valid = passenger_form.is_valid() and options_form.is_valid()
        segments = []

        try:
            if journey_type == '1':
                flight_form = OneWayFlightForm(request.POST)
                if flight_form.is_valid() and forms_valid:
                    segments = [
                        create_segment(
                            flight_form.cleaned_data['origin'],
                            flight_form.cleaned_data['destination'],
                            flight_form.cleaned_data['departure_date'],
                            flight_form.cleaned_data['departure_time'],
                            flight_form.cleaned_data['flight_cabin_class']
                        )
                    ]
                else:
                    error = "Please check your flight details"

            elif journey_type == '2':
                flight_form = RoundTripFlightForm(request.POST)
                if flight_form.is_valid() and forms_valid:
                    segments = [
                        create_segment(
                            flight_form.cleaned_data['origin'],
                            flight_form.cleaned_data['destination'],
                            flight_form.cleaned_data['departure_date'],
                            flight_form.cleaned_data['departure_time'],
                            flight_form.cleaned_data['flight_cabin_class']
                        ),
                        create_segment(
                            flight_form.cleaned_data['destination'],
                            flight_form.cleaned_data['origin'],
                            flight_form.cleaned_data['return_date'],
                            flight_form.cleaned_data['return_time'],
                            flight_form.cleaned_data['flight_cabin_class']
                        )
                    ]
                else:
                    error = "Please check your flight details"

            else:  # Multi-city
                formset = MultiCityFormSet(request.POST)
                if formset.is_valid() and forms_valid:
                    for form in formset:
                        segments.append(
                            create_segment(
                                form.cleaned_data['origin'],
                                form.cleaned_data['destination'],
                                form.cleaned_data['departure_date'],
                                form.cleaned_data['departure_time'],
                                form.cleaned_data['flight_cabin_class']
                            )
                        )
                else:
                    error = "Please check your flight details"

            if segments and not error:
                api = FlightAPI(request.META.get('REMOTE_ADDR', '127.0.0.1'))
                results = api.search_flights(
                    adult_count=passenger_form.cleaned_data['adult_count'],
                    child_count=passenger_form.cleaned_data['child_count'],
                    infant_count=passenger_form.cleaned_data['infant_count'],
                    journey_type=int(journey_type),
                    segments=segments,
                    direct_flight=options_form.cleaned_data['direct_flight'],
                    one_stop_flight=options_form.cleaned_data['one_stop_flight']
                )

                if results is None:
                    return render(request, 'results.html', {'error': 'No flights found for your search criteria'})
                
                if results['Response']['ResponseStatus'] != 1:
                    return render(request, 'results.html', {
                        'error': results['Response']['Error']['ErrorMessage']
                    })

                results = results['Response']['Results']
                outbound_cards = []
                return_cards = []

                for index, result_group in enumerate(results):
                    for result in result_group:
                        card = {
                            'fare': result['Fare']['BaseFare'],
                            'publishedFare': result['Fare']['PublishedFare'],
                            'currency': result['Fare']['Currency'],
                            'Source': result['Source'],
                        }

                        segments = []
                        for segment_index, segment in enumerate(result['Segments']):
                            for i, subsegment in enumerate(segment):
                                segments.append({
                                    f'Segment{segment_index + 1}-{i + 1}': {
                                        'AirlineCode': subsegment['Airline']['AirlineCode'],
                                        'AirlineName': subsegment['Airline']['AirlineName'],
                                        'FlightNumber': subsegment['Airline']['FlightNumber'],
                                        'Baggage': subsegment['Baggage'],
                                        'CabinBaggage': subsegment['CabinBaggage'],
                                        'CabinClass': subsegment['CabinClass'],
                                        'Duration': subsegment['Duration'],
                                        'OriginAirportCode': subsegment['Origin']['Airport']['AirportCode'],
                                        'OriginAirportName': subsegment['Origin']['Airport']['AirportName'],
                                        'OriginTerminal': subsegment['Origin']['Airport']['Terminal'],
                                        'OriginCityCode': subsegment['Origin']['Airport']['CityCode'],
                                        'OriginCityName': subsegment['Origin']['Airport']['CityName'],
                                        'DestinationAirportCode': subsegment['Destination']['Airport']['AirportCode'],
                                        'DestinationAirportName': subsegment['Destination']['Airport']['AirportName'],
                                        'DestinationTerminal': subsegment['Destination']['Airport']['Terminal'],
                                        'DestinationCityCode': subsegment['Destination']['Airport']['CityCode'],
                                        'DestinationCityName': subsegment['Destination']['Airport']['CityName'],
                                        'DepartureTime': subsegment['Origin']['DepTime'],
                                        'ArrivalTime': subsegment['Destination']['ArrTime'],
                                    }
                                })
                        
                        card['Segments'] = segments
                        if index == 0:
                            outbound_cards.append(card)
                        else:
                            return_cards.append(card)

                return render(request, 'results.html', {
                    'outbound_cards': outbound_cards,
                    'return_cards': return_cards
                })

        except Exception as e:
            error = f"An error occurred while processing your request: {str(e)}"

    # Initialize forms for GET request
    if journey_type == '1':
        flight_form = OneWayFlightForm()
    elif journey_type == '2':
        flight_form = RoundTripFlightForm()
    else:
        flight_form = MultiCityFormSet()

    return render(request, 'flight_search.html', {
        'passenger_form': passenger_form,
        'flight_form': flight_form,
        'options_form': options_form,
        'journey_type': journey_type,
        'error': error
    })