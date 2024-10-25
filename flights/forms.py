# forms.py
from django import forms
from django.forms import formset_factory, BaseFormSet
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

class PassengerForm(forms.Form):
    """Form for passenger counts"""
    adult_count = forms.IntegerField(
        min_value=1, max_value=9, initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'adult_count'
        })
    )
    child_count = forms.IntegerField(
        min_value=0, max_value=8, initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'child_count'
        })
    )
    infant_count = forms.IntegerField(
        min_value=0, max_value=4, initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'infant_count'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        adult_count = cleaned_data.get('adult_count', 0)
        child_count = cleaned_data.get('child_count', 0)
        infant_count = cleaned_data.get('infant_count', 0)

        if adult_count + child_count + infant_count > 9:
            raise forms.ValidationError("Total passengers cannot exceed 9")
        
        if infant_count > adult_count:
            raise forms.ValidationError("Number of infants cannot exceed number of adults")

        return cleaned_data

class OneWayFlightForm(forms.Form):
    """Form for one-way flights"""
    origin = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'From (e.g. BOM)'
        })
    )
    destination = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'To (e.g. DEL)'
        })
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.now().date().isoformat()
        })
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        departure_date = cleaned_data.get('departure_date')

        if origin and destination and origin.upper() == destination.upper():
            raise forms.ValidationError("Origin and destination cannot be the same")

        if departure_date and departure_date < datetime.now().date():
            raise forms.ValidationError("Departure date cannot be in the past")

        return cleaned_data

class RoundTripFlightForm(forms.Form):
    """Simplified form for round-trip flights - only dates and times"""
    origin = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'From (e.g. BOM)'
        })
    )
    destination = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'To (e.g. DEL)'
        })
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.now().date().isoformat()
        })
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.now().date().isoformat()
        })
    )
    return_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')

        if origin and destination and origin.upper() == destination.upper():
            raise forms.ValidationError("Origin and destination cannot be the same")

        if departure_date and departure_date < datetime.now().date():
            raise forms.ValidationError("Departure date cannot be in the past")

        if departure_date and return_date and return_date < departure_date:
            raise forms.ValidationError("Return date must be after departure date")

        return cleaned_data

class MultiCitySegmentForm(forms.Form):
    """Form for multi-city flight segments"""
    origin = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'From (e.g. BOM)'
        })
    )
    destination = forms.CharField(
        max_length=3, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control airport-input',
            'placeholder': 'To (e.g. DEL)'
        })
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.now().date().isoformat()
        })
    )
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    flight_cabin_class = forms.ChoiceField(
        choices=CABIN_CLASSES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BaseMultiCityFormSet(BaseFormSet):
    """Base formset for multi-city segments with validation"""
    def clean(self):
        if any(self.errors):
            return

        dates = []
        for form in self.forms:
            if form.cleaned_data:
                date = form.cleaned_data.get('departure_date')
                if date:
                    if dates and date < dates[-1]:
                        raise forms.ValidationError(
                            "Flight dates must be in sequence"
                        )
                    dates.append(date)

                # Validate that segments connect
                if len(self.forms) > 1:
                    prev_dest = self.forms[self.forms.index(form) - 1].cleaned_data.get('destination') if self.forms.index(form) > 0 else None
                    curr_origin = form.cleaned_data.get('origin')
                    
                    if prev_dest and curr_origin and prev_dest.upper() != curr_origin.upper():
                        raise forms.ValidationError(
                            f"Flight segments must connect. Segment {self.forms.index(form) + 1} should depart from {prev_dest.upper()}"
                        )

class FlightSearchOptionsForm(forms.Form):
    """Form for additional flight search options"""
    direct_flight = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'direct_flight'
        })
    )
    one_stop_flight = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'one_stop_flight'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        direct_flight = cleaned_data.get('direct_flight')
        one_stop_flight = cleaned_data.get('one_stop_flight')

        if direct_flight and one_stop_flight:
            raise forms.ValidationError("Cannot select both direct and one-stop flights")

        return cleaned_data

# Create the formset for multi-city segments
MultiCityFormSet = formset_factory(
    MultiCitySegmentForm,
    formset=BaseMultiCityFormSet,
    min_num=2,
    max_num=6,
    validate_min=True,
    validate_max=True,
    extra=0
)