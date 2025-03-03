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


class AbstractUserCreationForm(BaseUserCreationForm):
    user_type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ("email", "user_type")

    def clean_email(self):
        """Reject emails that differ only in case."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def __init__(self, *args, **kwargs):
        hidden_value = kwargs.pop("user_type", "Reg")
        super().__init__(*args, **kwargs)
        self.fields["user_type"].initial = hidden_value

    def save(self, commit=True):
        user = super().save(commit=False)
        user.hidden_field = self.cleaned_data["user_type"]
        if commit:
            user.save()
        return user


class RegularUserRegistrationForm(AbstractUserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)


class RestaurantRegistrationForm(AbstractUserCreationForm):
    restaurant_name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000)


class DeliveryContractorRegistrationForm(RegularUserRegistrationForm):
    pass
