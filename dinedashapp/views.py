from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from dinedashapp.forms import (
    DeliveryContractorLogInForm,
    DeliveryContractorRegistrationForm,
    RegularAccountDetailsForm,
    RegularUserLogInForm,
    RegularUserRegistrationForm,
    RestaurantInfoForm,
    RestaurantLogInForm,
    RestaurantRegistrationForm,
)
from dinedashapp.geo import get_distance_in_miles
from dinedashapp.models import BlogPost, MenuItem, Restaurant, RestaurantReview


def check_authorization(user, target):
    return (target is None and not user.is_authenticated) or (
        (user.is_authenticated) and (target == user.user_type)
    )


def deny_if_not_target(target):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if check_authorization(request.user, target):
                return func(request, *args, **kwargs)

            raise PermissionDenied()

        return wrapper

    return decorator


def index(request):
    pricing_examples = MenuItem.objects.all()[:4]
    return render(
        request,
        "dinedashapp/index.html",
        {"pricing_examples": pricing_examples},
    )


def about_us(request):
    return render(request, "dinedashapp/about_us.html")


def contact_us(request):
    return render(request, "dinedashapp/contact_us.html")


def blog(request):
    posts = BlogPost.objects.all()
    return render(request, "dinedashapp/blog.html", {"blog_posts": posts})


@deny_if_not_target(None)
def log_in_question(request):
    return render(request, "dinedashapp/log_in_question.html")


class AnonymousUserRequiredMixin:
    target = None

    def dispatch(self, *args, **kwargs):
        if check_authorization(self.request.user, self.target):
            return super().dispatch(*args, **kwargs)
        raise PermissionDenied()


class RegularUserRequiredMixin(AnonymousUserRequiredMixin):
    target = "Reg"


class RestaurantUserRequiredMixin(AnonymousUserRequiredMixin):
    target = "Res"


class DeliveryUserRequiredMixin(AnonymousUserRequiredMixin):
    target = "Del"


class RegularLogInView(AnonymousUserRequiredMixin, FormView):
    template_name = "dinedashapp/log_in_form.html"
    form_class = RegularUserLogInForm
    extra_context = {
        "title": "Regular Customer Log In",
        "registration_url": reverse_lazy("register_regular"),
    }

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect("index")


class RestaurantLogInView(RegularLogInView):
    form_class = RestaurantLogInForm
    extra_context = {
        "title": "Restaurant Log In",
        "registration_url": reverse_lazy("register_restaurant"),
    }

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect("restaurant_info", pk=form.user.restaurant.pk)


class DeliveryLogInView(RegularLogInView):
    form_class = DeliveryContractorLogInForm
    extra_context = {
        "title": "Delivery Contractor Log In",
        "registration_url": reverse_lazy("register_delivery"),
    }


class RegularRegistrationView(AnonymousUserRequiredMixin, FormView):
    template_name = "dinedashapp/registration_form.html"
    form_class = RegularUserRegistrationForm
    extra_context = {
        "title": "Regular Customer Registration",
        "log_in_url": reverse_lazy("log_in_regular"),
    }

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        user = authenticate(email=email, password=password)

        login(self.request, user)
        return redirect("index")


class RestaurantRegistrationView(RegularRegistrationView):
    form_class = RestaurantRegistrationForm
    extra_context = {
        "title": "Restaurant Registration",
        "log_in_url": reverse_lazy("log_in_restaurant"),
    }

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        user = authenticate(email=email, password=password)

        login(self.request, user)
        return redirect("restaurant_info", pk=user.restaurant.id)


class DeliveryRegistrationView(RegularRegistrationView):
    form_class = DeliveryContractorRegistrationForm
    extra_context = {
        "title": "Delivery Contractor Registration",
        "log_in_url": reverse_lazy("log_in_delivery"),
    }

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        user = authenticate(email=email, password=password)

        login(self.request, user)
        return redirect("index")


def log_out(request):
    logout(request)
    return redirect("index")


class RestaurantSearchView(ListView):
    template_name = "dinedashapp/restaurant_search.html"
    context_object_name = "restaurants"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if query := self.request.GET.get("query"):
            kwargs["query"] = query
        if order_by := self.request.GET.get("order_by"):
            kwargs["order_by"] = order_by
        if (
            (user := self.request.user).is_authenticated
            and user.user_type == "Reg"
            and user.customer_info.location
        ):
            kwargs["user_has_location"] = True
        return kwargs

    def get_queryset(self):
        queryset = Restaurant.objects.values(
            "pk",
            "name",
            "description",
            "location_x_coordinate",
            "location_y_coordinate",
        ).annotate(average_rating=Avg("reviews__rating"))

        if query := self.request.GET.get("query"):
            query = query.strip().replace("  ", " ")
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if (order_by := self.request.GET.get("order_by")) == "name":
            queryset = queryset.order_by("name")
        elif order_by == "-name":
            queryset = queryset.order_by("-name")
        elif order_by == "highest_rating":
            # Only includes restaurants that have reviews.
            queryset = queryset.filter(average_rating__gt=0).order_by(
                "-average_rating", "name"
            )
        elif order_by == "lowest_rating":
            # Only includes restaurants that have reviews.
            queryset = queryset.filter(average_rating__gt=0).order_by(
                "average_rating", "name"
            )
        else:
            queryset = queryset.order_by("name")

        user = self.request.user
        user_has_location = (
            user.is_authenticated
            and user.user_type == "Reg"
            and user.customer_info.location
        )

        if user_has_location:
            user_coordinates = (
                user.customer_info.location_x_coordinate,
                user.customer_info.location_y_coordinate,
            )
            result = map(
                lambda r: r
                | {
                    "distance_away": get_distance_in_miles(
                        (r["location_x_coordinate"], r["location_y_coordinate"]),
                        user_coordinates,
                    )
                },
                queryset,
            )
        else:
            result = queryset

        if order_by == "lowest_distance" and user_has_location:
            result = sorted(
                result,
                key=lambda r: r["distance_away"],
            )

        return result


class RestaurantInfoView(DetailView):
    model = Restaurant
    template_name = "dinedashapp/restaurant_info.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()

        user = self.request.user
        context["is_owner"] = (
            user.is_authenticated and user.user_type == "Res" and user.restaurant == obj
        )

        context["sunday_hours"] = (
            f"{obj.open_hour_sunday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_sunday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_sunday is not None
            else "closed"
        )
        context["monday_hours"] = (
            f"{obj.open_hour_monday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_monday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_monday is not None
            else "closed"
        )
        context["tuesday_hours"] = (
            f"{obj.open_hour_tuesday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_tuesday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_tuesday is not None
            else "closed"
        )
        context["wednesday_hours"] = (
            f"{obj.open_hour_wednesday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_wednesday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_wednesday is not None
            else "closed"
        )
        context["thursday_hours"] = (
            f"{obj.open_hour_thursday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_thursday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_thursday is not None
            else "closed"
        )
        context["friday_hours"] = (
            f"{obj.open_hour_friday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_friday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_friday is not None
            else "closed"
        )
        context["saturday_hours"] = (
            f"{obj.open_hour_saturday.strftime("%I:%M %p").lstrip("0")} to {obj.close_hour_saturday.strftime("%I:%M %p").lstrip("0")}"
            if obj.open_hour_saturday is not None
            else "closed"
        )

        context["average_rating"] = obj.get_average_rating()

        return context


class CreateMenuItemView(RestaurantUserRequiredMixin, CreateView):
    model = MenuItem
    fields = ("name", "price", "description")
    template_name = "dinedashapp/menu_item_form.html"

    def form_valid(self, form):
        obj = form.save(False)
        obj.restaurant = self.request.user.restaurant
        obj.save()
        return redirect("restaurant_info", obj.restaurant.pk)


class EditMenuItemView(RestaurantUserRequiredMixin, UpdateView):
    model = MenuItem
    fields = ("name", "price", "description")
    template_name = "dinedashapp/menu_item_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(restaurant__user=self.request.user)

    def get_success_url(self):
        return reverse("restaurant_info", kwargs={"pk": self.object.restaurant.pk})


class EditRestaurantInfoView(RestaurantUserRequiredMixin, UpdateView):
    form_class = RestaurantInfoForm
    template_name = "dinedashapp/restaurant_info_form.html"

    def get_object(self, queryset=None):
        return self.request.user.restaurant

    def get_success_url(self):
        return reverse(
            "restaurant_info", kwargs={"pk": self.request.user.restaurant.id}
        )


class ListOfReviewsView(ListView):
    template_name = "dinedashapp/restaurant_reviews_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        return RestaurantReview.objects.filter(
            restaurant__pk=self.kwargs["restaurant_id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = Restaurant.objects.get(pk=self.kwargs["restaurant_id"])
        return context


class CreateReviewView(RegularUserRequiredMixin, CreateView):
    model = RestaurantReview
    fields = ("rating", "description")
    template_name = "dinedashapp/restaurant_review_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant_id"] = self.kwargs["restaurant_id"]
        return context

    def form_valid(self, form):
        obj = form.save(False)
        restaurant_id = self.kwargs["restaurant_id"]
        obj.restaurant_id = restaurant_id
        obj.user = self.request.user
        obj.save()
        return redirect("restaurant_reviews", restaurant_id)


class AbstractChangePasswordView(PasswordChangeView):
    template_name = "dinedashapp/change_password_form.html"


class ChangePasswordForRegularView(
    RegularUserRequiredMixin, AbstractChangePasswordView
):
    success_url = reverse_lazy("regular_account")


class ChangePasswordForRestaurantView(
    RestaurantUserRequiredMixin, AbstractChangePasswordView
):
    def get_success_url(self):
        return redirect("restaurant_info", pk=self.request.user.restaurant.pk)


class ChangePasswordForDeliveryView(
    DeliveryUserRequiredMixin, AbstractChangePasswordView
):
    success_url = reverse_lazy("index")


class RegularAccountView(RegularUserRequiredMixin, TemplateView):
    template_name = "dinedashapp/regular_account.html"


class EditRegularAccountDetailsView(RegularUserRequiredMixin, UpdateView):
    form_class = RegularAccountDetailsForm
    template_name = "dinedashapp/edit_regular_account_details.html"
    success_url = reverse_lazy("regular_account")

    def get_object(self, queryset=None):
        return self.request.user.customer_info
