# hotels/forms.py

from django import forms

class CountryForm(forms.Form):
    country = forms.ChoiceField(label='Select Country', required=True)

class CityForm(forms.Form):
    city = forms.ChoiceField(label='Select City', required=True)
