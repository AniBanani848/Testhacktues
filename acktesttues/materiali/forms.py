from django import forms
from .models import Profile, Resource, Supply
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    learning_focus = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ['item_name', 'description']
class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'subject', 'file']