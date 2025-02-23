from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
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

    USER_TYPES = [("Reg", "Regular"), ("Res", "Restaurant"), ("Del", "Delivery")]

    email = models.EmailField("email address", blank=False, unique=True)
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)
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
