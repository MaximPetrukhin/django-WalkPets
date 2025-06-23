from django import forms
from .models import Walker

class WalkerApplicationForm(forms.ModelForm):
    class Meta:
        model = Walker
        fields = ['name', 'phone', 'image', 'description', 'experience']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }