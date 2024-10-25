import json
from django.shortcuts import render
from django.http import JsonResponse
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

        if form.is_valid():
            # Initialize API and search flights
            api = FlightAPI(request.META.get('REMOTE_ADDR', '127.0.0.1'))
            try:
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
                
                with open('results.json', 'w') as f:
                    f.write(json.dumps(results, indent=4))
                
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
                            segment = segment[0]
                            segments.append({
                                f'Segment{segment_index + 1}': {
                                    'AirlineCode': segment['Airline']['AirlineCode'],
                                    'AirlineName': segment['Airline']['AirlineName'],
                                    'FlightNumber': segment['Airline']['FlightNumber'],
                                    'Baggage': segment['Baggage'],
                                    'CabinBaggage': segment['CabinBaggage'],
                                    'CabinClass': segment['CabinClass'],
                                    'Duration': segment['Duration'],
                                    'OriginAirportCode': segment['Origin']['Airport']['AirportCode'],
                                    'OriginAirportName': segment['Origin']['Airport']['AirportName'],
                                    'OriginTerminal': segment['Origin']['Airport']['Terminal'],
                                    'OriginCityCode': segment['Origin']['Airport']['CityCode'],
                                    'OriginCityName': segment['Origin']['Airport']['CityName'],
                                    'DestinationAirportCode': segment['Destination']['Airport']['AirportCode'],
                                    'DestinationAirportName': segment['Destination']['Airport']['AirportName'],
                                    'DestinationTerminal': segment['Destination']['Airport']['Terminal'],
                                    'DestinationCityCode': segment['Destination']['Airport']['CityCode'],
                                    'DestinationCityName': segment['Destination']['Airport']['CityName'],
                                    'DepartureTime': segment['Origin']['DepTime'],
                                    'ArrivalTime': segment['Destination']['ArrTime'],
                                }
                            })

                        card['Segments'] = segments
                        if index == 0:  # Outbound flight
                            outbound_cards.append(card)
                        else:  # Return flight
                            return_cards.append(card)

                return render(request, 'results.html', {'outbound_cards': outbound_cards, 'return_cards': return_cards})

            except Exception as e:
                return render(request, 'results.html', {'error': str(e)})
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

