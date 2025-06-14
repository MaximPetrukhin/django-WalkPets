from django import forms
from .models import Region, PetFriendlyPlaceSubmission

class RegionSelectForm(forms.Form):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Выберите регион",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PetFriendlyPlaceSubmissionForm(forms.ModelForm):
    class Meta:
        model = PetFriendlyPlaceSubmission
        fields = ['name', 'description', 'address', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название места',
            'description': 'Описание',
            'address': 'Адрес',
            'photo': 'Фото места',
        }