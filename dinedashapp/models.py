from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """Creates a new user."""
        email = self.normalize_email(email)
        user = User(email=email, user_type=self.model.default_user_type, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """Creates a new super user."""
        email = self.normalize_email(email)
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        user = User(
            email=email,
            **kwargs,
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    USER_TYPES = (("Reg", "Regular"), ("Res", "Restaurant"), ("Del", "Delivery"))

    email = models.EmailField("email address", unique=True)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    USERNAME_FIELD = "email"

    user_type = models.CharField(max_length=3, choices=USER_TYPES, default="Regular")


class CustomerInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_info"
    )

    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    location = models.CharField("defaultlocation", max_length=300, null=True)
    location_x_coordinate = models.DecimalField(
        max_digits=9, decimal_places=6, null=True
    )
    location_y_coordinate = models.DecimalField(
        max_digits=9, decimal_places=6, null=True
    )

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name} {self.last_name}".strip()


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField("Date posted", default=timezone.now)
    content = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ["-date"]


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    open_hour_sunday = models.TimeField(null=True)
    open_hour_monday = models.TimeField(null=True)
    open_hour_tuesday = models.TimeField(null=True)
    open_hour_wednesday = models.TimeField(null=True)
    open_hour_thursday = models.TimeField(null=True)
    open_hour_friday = models.TimeField(null=True)
    open_hour_saturday = models.TimeField(null=True)
    close_hour_sunday = models.TimeField(null=True)
    close_hour_monday = models.TimeField(null=True)
    close_hour_tuesday = models.TimeField(null=True)
    close_hour_wednesday = models.TimeField(null=True)
    close_hour_thursday = models.TimeField(null=True)
    close_hour_friday = models.TimeField(null=True)
    close_hour_saturday = models.TimeField(null=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="restaurant"
    )
    location = models.CharField("location", max_length=300)
    location_x_coordinate = models.DecimalField(max_digits=10, decimal_places=7)
    location_y_coordinate = models.DecimalField(max_digits=10, decimal_places=7)

    def __str__(self):
        return str(self.name)

    def get_average_rating(self):
        return self.reviews.aggregate(Avg("rating")).get("rating__avg")

    class Meta:
        ordering = ["name"]

        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    open_hour_sunday__isnull=True, close_hour_sunday__isnull=True
                )
                | models.Q(
                    open_hour_sunday__isnull=False, close_hour_sunday__isnull=False
                ),
                name="sunday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_monday__isnull=True, close_hour_monday__isnull=True
                )
                | models.Q(
                    open_hour_monday__isnull=False, close_hour_monday__isnull=False
                ),
                name="monday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_tuesday__isnull=True, close_hour_tuesday__isnull=True
                )
                | models.Q(
                    open_hour_tuesday__isnull=False, close_hour_tuesday__isnull=False
                ),
                name="tuesday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_wednesday__isnull=True, close_hour_wednesday__isnull=True
                )
                | models.Q(
                    open_hour_wednesday__isnull=False,
                    close_hour_wednesday__isnull=False,
                ),
                name="wednesday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_thursday__isnull=True, close_hour_thursday__isnull=True
                )
                | models.Q(
                    open_hour_thursday__isnull=False, close_hour_thursday__isnull=False
                ),
                name="thursday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_friday__isnull=True, close_hour_friday__isnull=True
                )
                | models.Q(
                    open_hour_friday__isnull=False, close_hour_friday__isnull=False
                ),
                name="friday_both_null_or_neither_null",
            ),
            models.CheckConstraint(
                check=models.Q(
                    open_hour_saturday__isnull=True, close_hour_saturday__isnull=True
                )
                | models.Q(
                    open_hour_saturday__isnull=False, close_hour_saturday__isnull=False
                ),
                name="saturday_both_null_or_neither_null",
            ),
        ]


class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menu_items"
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]


class RestaurantReview(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="restaurant_reviews"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(
        "rating out of 5", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.CharField(max_length=200)
    date_created = models.DateTimeField("date created", default=timezone.now)

    class Meta:
        ordering = ["-date_created"]


class DeliveryContractorInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="delivery_contractor_info"
    )

    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name} {self.last_name}".strip()
