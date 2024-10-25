# forms.py
from django import forms
from datetime import datetime

TIME_CHOICES = [
    ('00:00:00', 'Any Time'),
    ('08:00:00', 'Morning Flights'),
    ('14:00:00', 'Afternoon Flights'),
    ('19:00:00', 'Evening Flights'),
    ('01:00:00', 'Night Flights'),
]

CABIN_CLASSES = [
    (1, 'All Classes'),
    (2, 'Economy'),
    (3, 'Premium Economy'),
    (4, 'Business'),
    (5, 'Premium Business'),
    (6, 'First'),
]

class BaseFlightForm(forms.Form):
    """Base form with common fields for all journey types"""
    adult_count = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    child_count = forms.IntegerField(
        min_value=0, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    infant_count = forms.IntegerField(
        min_value=0, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    direct_flight = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    one_stop_flight = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class OneWayFlightForm(BaseFlightForm):
    """Form for one-way flights"""
    origin = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'From (e.g. BOM)'})
    )
    destination = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'To (e.g. DEL)'})
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class RoundTripFlightForm(BaseFlightForm):
    """Form for round-trip flights"""
    origin = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'From (e.g. BOM)'})
    )
    destination = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'To (e.g. DEL)'})
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    return_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class MultiCitySegmentForm(forms.Form):
    """Form for a single segment in multi-city journey"""
    origin = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'From (e.g. BOM)'})
    )
    destination = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'To (e.g. DEL)'})
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class MultiCityFlightForm(BaseFlightForm):
    """Form for multi-city flights"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.segment_forms = []
        
        # Get data from POST if available
        data = kwargs.get('data', None)
        if data:
            segment_count = int(data.get('segment_count', 2))
        else:
            segment_count = 2  # Default number of segments
            
        for i in range(segment_count):
            prefix = f'segment_{i}'
            form = MultiCitySegmentForm(
                prefix=prefix,
                data=data if data else None
            )
            self.segment_forms.append(form)
        print(f"Segment forms are: {self.segment_forms}")

    def is_valid(self):
        print("Calling is_valid on MultiCityFlightForm")
        if not super().is_valid():
            print("BaseFlightForm is not valid")
            return False
        print("BaseFlightForm is valid")
        segment_validity = all(form.is_valid() for form in self.segment_forms)
        print(f"Segment forms are valid: {segment_validity}")
        return segment_validity

    def clean(self):
        print("Calling clean on MultiCityFlightForm")
        cleaned_data = super().clean()
        print(f"Cleaned data from base form: {cleaned_data}")
        cleaned_data['segments'] = [
            form.cleaned_data 
            for form in self.segment_forms 
            if form.is_valid()
        ]
        print(f"Cleaned data for all forms: {cleaned_data}")
        return cleaned_data 
