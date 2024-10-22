from django.shortcuts import render
from .forms import FlightSearchForm

def flight_search_view(request):
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            # Handle form data
            # (You would process the flight search data here)
            return render(request, 'search_results.html', {'form': form, 'results': results})
    else:
        form = FlightSearchForm()

    return render(request, 'flight_search.html', {'form': form})
