from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.exceptions import ValidationError

from dinedashapp.models import User


class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        super().clean()
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        self.user = authenticate(email=email, password=password)
        if not self.user:
            raise ValidationError("Email and password are incorrect.")


class RegistrationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        """Reject emails that differ only in case."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email
