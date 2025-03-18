from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.exceptions import ValidationError
from geopy.exc import GeopyError

from dinedashapp.geo import get_coordinates
from dinedashapp.models import CustomerInfo, DeliveryContractorInfo, Restaurant, User


class AbstractLogInForm(forms.Form):
    user_type: str
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
        if self.user.user_type != self.user_type:
            raise ValidationError(
                "This form is not intended for the type of account associated with the credentials you provided."
            )


class RegularUserLogInForm(AbstractLogInForm):
    user_type = "Reg"


class RestaurantLogInForm(AbstractLogInForm):
    user_type = "Res"


class DeliveryContractorLogInForm(AbstractLogInForm):
    user_type = "Del"


class AbstractUserCreationForm(BaseUserCreationForm):
    user_type: str

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        """Reject emails that differ only in case."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.user_type
        if commit:
            user.save()
        return user


class RegularUserRegistrationForm(AbstractUserCreationForm):
    user_type = "Reg"
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    location = forms.CharField(label="Your location", max_length=300, required=False)

    def clean(self):
        location = self.cleaned_data.get("location", "").strip()
        if location:
            try:
                [x, y] = get_coordinates(location)
                self.cleaned_data["location_x_coordinate"] = x
                self.cleaned_data["location_y_coordinate"] = y
            except GeopyError as e:
                raise ValidationError("Could not find location.") from e

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            CustomerInfo.objects.create(
                user=user,
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                location=(location := self.cleaned_data.get("location")),
                location_x_coordinate=(
                    self.cleaned_data["location_x_coordinate"] if location else None
                ),
                location_y_coordinate=(
                    self.cleaned_data["location_y_coordinate"] if location else None
                ),
            )
        return user


class RestaurantRegistrationForm(AbstractUserCreationForm):
    user_type = "Res"
    restaurant_name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000)
    location = forms.CharField(max_length=300)

    def clean(self):
        location = self.cleaned_data.get("location", "").strip()
        if location:
            try:
                [x, y] = get_coordinates(location)
                self.cleaned_data["location_x_coordinate"] = x
                self.cleaned_data["location_y_coordinate"] = y
            except GeopyError as e:
                raise ValidationError("Could not find location.") from e
        else:
            raise ValidationError("You need to include a valid location.")

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            Restaurant.objects.create(
                user=user,
                name=self.cleaned_data["restaurant_name"],
                description=self.cleaned_data["description"],
                location=(location := self.cleaned_data["location"]),
                location_x_coordinate=(
                    self.cleaned_data["location_x_coordinate"] if location else None
                ),
                location_y_coordinate=(
                    self.cleaned_data["location_y_coordinate"] if location else None
                ),
            )
        return user


class DeliveryContractorRegistrationForm(AbstractUserCreationForm):
    user_type = "Del"
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            DeliveryContractorInfo.objects.create(
                user=user,
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
            )
        return user


class RestaurantInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if "_hour_" in field_name:
                field.required = False

    def clean(self):
        super().clean()

        for day in (
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ):
            if "open_hour_" + day not in self.cleaned_data:
                raise ValidationError(
                    f"The format of the opening hour for {day.capitalize()} is invalid."
                )

            if "close_hour_" + day not in self.cleaned_data:
                raise ValidationError(
                    f"The format of the closing hour for {day.capitalize()} is invalid."
                )

            if bool(self.cleaned_data["open_hour_" + day]) != bool(
                self.cleaned_data["close_hour_" + day]
            ):
                raise ValidationError(
                    "If you entered an opening time for a day of the week, make sure to also specify a closing time for said day."
                )

        location = self.cleaned_data["location"]
        if location != self.initial["location"]:
            try:
                [x, y] = get_coordinates(location)
                self.cleaned_data["location_x_coordinate"] = x
                self.cleaned_data["location_y_coordinate"] = y
            except GeopyError as e:
                raise ValidationError("Could not find location.") from e

    class Meta:
        model = Restaurant
        fields = (
            "description",
            "location",
            "open_hour_sunday",
            "close_hour_sunday",
            "open_hour_monday",
            "close_hour_monday",
            "open_hour_tuesday",
            "close_hour_tuesday",
            "open_hour_wednesday",
            "close_hour_wednesday",
            "open_hour_thursday",
            "close_hour_thursday",
            "open_hour_friday",
            "close_hour_friday",
            "open_hour_saturday",
            "close_hour_saturday",
        )
