import json
from django.shortcuts import render
from django.http import JsonResponse
import requests
from .forms import OneWayFlightForm, RoundTripFlightForm, MultiCityFlightForm
from ExternalAPI.flights.tbo_flight_api import FlightAPI, Segment

def format_datetime(date, time):
    return f"{date}T{time}"

def create_segment(origin, destination, date, time, cabin_class):
    datetime_str = format_datetime(date, time)
    return Segment(
        origin=origin,
        destination=destination,
        cabin_class=cabin_class,
        departure_time=datetime_str,
        arrival_time=datetime_str
    )

def flight_search(request):
    journey_type = request.GET.get('type', '1')
    
    if request.method == 'POST':
        journey_type = request.POST.get('journey_type', '1')
        
        if journey_type == '1':
            form = OneWayFlightForm(request.POST)
            if form.is_valid():
                segments = [
                    create_segment(
                        form.cleaned_data['origin'],
                        form.cleaned_data['destination'],
                        form.cleaned_data['departure_date'],
                        form.cleaned_data['departure_time'],
                        form.cleaned_data['flight_cabin_class']
                    )
                ]
                
        elif journey_type == '2':
            form = RoundTripFlightForm(request.POST)
            if form.is_valid():
                segments = [
                    create_segment(
                        form.cleaned_data['origin'],
                        form.cleaned_data['destination'],
                        form.cleaned_data['departure_date'],
                        form.cleaned_data['departure_time'],
                        form.cleaned_data['flight_cabin_class']
                    ),
                    create_segment(
                        form.cleaned_data['destination'],  # Swapped for return
                        form.cleaned_data['origin'],
                        form.cleaned_data['return_date'],
                        form.cleaned_data['return_time'],
                        form.cleaned_data['flight_cabin_class']
                    )
                ]
                
        else:  # Multi-city
            form = MultiCityFlightForm(request.POST)
            if form.is_valid():
                segments = []
                for segment_data in form.cleaned_data['segments']:
                    segments.append(
                        create_segment(
                            segment_data['origin'],
                            segment_data['destination'],
                            segment_data['departure_date'],
                            segment_data['departure_time'],
                            segment_data['flight_cabin_class']
                        )
                    )
            else:
                print(form.errors)

        if form.is_valid():
            # Initialize API and search flights
            api = FlightAPI(request.META.get('REMOTE_ADDR', '127.0.0.1'))
            results = api.search_flights(
                adult_count=form.cleaned_data['adult_count'],
                child_count=form.cleaned_data['child_count'],
                infant_count=form.cleaned_data['infant_count'],
                journey_type=int(journey_type),
                segments=segments,
                direct_flight=form.cleaned_data['direct_flight'],
                one_stop_flight=form.cleaned_data['one_stop_flight']
            )
            
            if results is None:
                return render(request, 'results.html', {'error': 'No results found'})
            if results['Response']['ResponseStatus'] != 1:
                return render(request, 'results.html', {'error': results['Response']['Error']['ErrorMessage']})

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
                    if index == 0:  # Outbound flight
                        outbound_cards.append(card)
                    else:  # Return flight
                        return_cards.append(card)
                        
            return render(request, 'results.html', {'outbound_cards': outbound_cards, 'return_cards': return_cards})
    else:
        if journey_type == '1':
            form = OneWayFlightForm()
        elif journey_type == '2':
            form = RoundTripFlightForm()
        else:
            form = MultiCityFlightForm()

    return render(request, 'flight_search.html', {
        'form': form,
        'journey_type': journey_type
    })

