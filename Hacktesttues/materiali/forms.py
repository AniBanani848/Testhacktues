from django import forms
from django.contrib.auth.models import User

from .models import Profile, Resource, Supply


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm password',
    )
    current_major = forms.CharField(
        max_length=100,
        label='What are you studying?',
        help_text='e.g. Computer Science, Mechanical Engineering',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    learning_focus = forms.CharField(
        max_length=200,
        required=False,
        label='Current focus (optional)',
        help_text='Course, lab, or topic you care about right now.',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise forms.ValidationError('Email is required so we can send your verification code.')
        return email


class VerifyEmailForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Verification code',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control text-center fs-4 tracking-wider',
                'placeholder': '000000',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6}',
                'autocomplete': 'one-time-code',
            },
        ),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['current_major', 'learning_focus', 'bio', 'profile_picture']
        widgets = {
            'current_major': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_focus': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'subject', 'course_code', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'course_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS101'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ['item_name', 'description', 'subject_area']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Same as your field of study'}),
        }
