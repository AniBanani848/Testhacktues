from django import forms
from .models import Profile, Resource, Supply

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'subject', 'file']