from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email'] # Password fields are included by default


class AdminUserCreateForm(UserCreationForm):
    """Form for admin to create users (includes staff/superuser flags)."""
    email = forms.EmailField(required=False)
    is_staff = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active', 'is_superuser']


class AdminUserUpdateForm(forms.ModelForm):
    """Form for admin to update existing users (password not changed here)."""
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active', 'is_superuser']


class UserUpdateForm(forms.ModelForm):
    """Simple form for regular users to update their own info."""
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

        