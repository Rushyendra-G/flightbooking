from django.shortcuts import render
from django.core.paginator import Paginator
import json
from .forms import FlightSearchForm

def flight_search_view(request):
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            # Handle form data and flight search logic here
            return render(request, 'search_results.html', {'form': form})
    else:
        form = FlightSearchForm()

    return render(request, 'flight_search.html', {'form': form})

def results_view(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        
        # Check if the uploaded file is empty
        if json_file.size == 0:
            return render(request, 'upload.html', {'error': 'Uploaded file is empty.'})
        
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError as e:
            return render(request, 'upload.html', {'error': f'Invalid JSON file: {str(e)}'})
        
        # Extract results
        results = json_data['Response']['Results']
        outbound_cards = []
        return_cards = []

        print("#########################")
        print("Length of results: ", len(results))
        print("#########################")

        with open('segment.txt', 'a') as f:
            for index, result_group in enumerate(results):
                for result in result_group:
                    f.write(f"Result {index + 1}:\n")
                    card = {
                        'fare': result['Fare']['BaseFare'],
                        'publishedFare': result['Fare']['PublishedFare'],
                        'currency': result['Fare']['Currency'],
                        'Source': result['Source'],
                    }

                    segments = []
                    for segment_index, segment in enumerate(result['Segments']):
                        segment = segment[0]
                        f.write(json.dumps(segment, indent=2) + "\n")
                        f.write("--------------------------\n")

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

    return render(request, 'upload.html')