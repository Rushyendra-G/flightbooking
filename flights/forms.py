from django import forms

class FlightSearchForm(forms.Form):
    adult_count = forms.IntegerField(min_value=1, initial=1, label='Adults (12+ years)', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    child_count = forms.IntegerField(min_value=0, initial=0, required=False, label='Children (2-11 years)', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    infant_count = forms.IntegerField(min_value=0, initial=0, required=False, label='Infants (0-2 years)', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    JOURNEY_TYPE_CHOICES = [
        (1, 'One Way'),
        (2, 'Round Trip'),
        (3, 'Multi-City'),
    ]
    
    journey_type = forms.ChoiceField(choices=JOURNEY_TYPE_CHOICES, label='Journey Type', widget=forms.Select(attrs={'class': 'form-select'}))
    
    # Flight segment fields can be dynamic based on the journey type
    origin1 = forms.CharField(label='From')
    destination1 = forms.CharField(label='To')
    flight_cabin_class1 = forms.ChoiceField(choices=[
        (1, 'All'), (2, 'Economy'), (3, 'Premium Economy'), 
        (4, 'Business'), (5, 'Premium Business'), (6, 'First')
    ], label='Cabin Class')
    departure_date1 = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}), label='Departure Date')
    departure_time1 = forms.ChoiceField(choices=[
        ('00:00:00', 'Any Time'), ('08:00:00', 'Morning Flight'),
        ('14:00:00', 'Afternoon Flight'), ('19:00:00', 'Evening Flight'),
        ('01:00:00', 'Night Flight'),
    ], label='Departure Time')

    direct_flight = forms.BooleanField(required=False, label='Direct Flights Only')
    one_stop_flight = forms.BooleanField(required=False, label='Include One Stop Flights')
    preferred_airlines = forms.CharField(required=False, label='Preferred Airlines (comma-separated)', widget=forms.TextInput(attrs={'class': 'form-control'}))
