from django import forms
from .models import PetFriendlyPlace

class PetFriendlyPlaceForm(forms.ModelForm):
    class Meta:
        model = PetFriendlyPlace
        fields = ['name', 'description', 'latitude', 'longitude', 'address']