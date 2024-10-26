# forms.py
from django import forms
from datetime import date

class HotelSearchBaseForm(forms.Form):
    def __init__(self, choices=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if choices and hasattr(self, 'update_choices'):
            self.update_choices(choices)

class CountrySelectForm(HotelSearchBaseForm):
    country = forms.ChoiceField(
        label='Select Country',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def update_choices(self, choices):
        self.fields['country'].choices = [(c['Code'], c['Name']) for c in choices]

class CitySelectForm(HotelSearchBaseForm):
    city = forms.ChoiceField(
        label='Select City',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def update_choices(self, choices):
        self.fields['city'].choices = [(c['Code'], c['Name']) for c in choices]

class RoomConfigurationForm(forms.Form):
    adults = forms.IntegerField(
        min_value=1,
        max_value=4,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    children = forms.IntegerField(
        min_value=0,
        max_value=3,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class SearchDetailsForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    nationality = forms.ChoiceField(
        choices=[('IN', 'India'), ('US', 'United States'), ('GB', 'United Kingdom')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    room_count = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )