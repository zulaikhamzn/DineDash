from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from dinedashapp.forms import (
    LogInForm,
    RegularUserRegistrationForm,
    RestaurantRegistrationForm,
)
from dinedashapp.models import BlogPost, CustomerInfo, MenuItem, Restaurant


def redirect_if_not_target(target=None):
    def decorator(func):
        @wraps
        def wrapper(request, *args, **kwargs):
            user = request.user
            if (target is None and user.is_authenticated) or (
                target is not None
                and ((not user.is_authenticated) or (target != user.user_type))
            ):
                return redirect("index")
            return func(request, *args, **kwargs)

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


def log_in_question(request):
    return render(request, "dinedashapp/log_in_question.html")


class RegularLogInView(FormView):
    template_name = "dinedashapp/log_in_form.html"
    form_class = LogInForm
    extra_context = {
        "title": "Regular Customer Log In",
        "registration_url": reverse_lazy("register_regular"),
    }

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect("index")


class RestaurantLogInView(RegularLogInView):
    extra_context = {
        "title": "Restaurant Log In",
        "registration_url": reverse_lazy("register_restaurant"),
    }

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect("restaurant_info", pk=form.user.restaurant.pk)


class DeliveryLogInView(RegularLogInView):
    extra_context = {
        "title": "Delivery Log In",
        "registration_url": reverse_lazy("register_delivery"),
    }


class RegularRegistrationView(FormView):
    template_name = "dinedashapp/registration_form.html"
    form_class = RegularUserRegistrationForm
    extra_context = {
        "title": "Regular Customer Registration",
        "log_in_url": reverse_lazy("log_in_regular"),
    }
    initial = {"user_type": "Reg"}

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]

        user = authenticate(email=email, password=password)

        CustomerInfo.objects.create(
            user=user, first_name=first_name, last_name=last_name
        )

        login(self.request, user)
        return redirect("index")


class RestaurantRegistrationView(RegularRegistrationView):
    form_class = RestaurantRegistrationForm
    extra_context = {
        "title": "Restaurant Registration",
        "log_in_url": reverse_lazy("log_in_restaurant"),
    }
    initial = {"user_type": "Res"}

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        restaurant_name = form.cleaned_data["restaurant_name"]
        description = form.cleaned_data["description"]

        user = authenticate(email=email, password=password)

        restaurant = Restaurant.objects.create(
            user=user, name=restaurant_name, description=description
        )

        login(self.request, user)
        return redirect("restaurant_info", pk=restaurant.pk)


class DeliveryRegistrationView(RegularRegistrationView):
    extra_context = {
        "title": "Delivery Registration",
        "log_in_url": reverse_lazy("log_in_delivery"),
    }
    initial = {"user_type": "Del"}


def log_out(request):
    logout(request)
    return redirect("index")


class RestaurantSearchView(ListView):
    template_name = "dinedashapp/restaurant_search.html"
    context_object_name = "restaurants"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if query := self.request.GET.get("query"):
            kwargs.update({"query": query})
        return kwargs

    def get_queryset(self):
        if query := self.request.GET.get("query"):
            query = query.strip().replace("  ", " ")
            return Restaurant.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            return []


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
        print(user.is_authenticated and user.user_type == "Res")

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

        return context


class CreateMenuItemView(CreateView):
    model = MenuItem
    fields = ("name", "price", "description")
    template_name = "dinedashapp/menu_item_form.html"

    def form_valid(self, form):
        obj = form.save(False)
        obj.restaurant = self.request.user.restaurant
        obj.save()
        return redirect("restaurant_info", obj.restaurant.pk)


class EditMenuItemView(UpdateView):
    model = MenuItem
    fields = ("name", "price", "description")
    template_name = "dinedashapp/menu_item_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(restaurant__user=self.request.user)

    def get_success_url(self):
        return reverse("restaurant_info", kwargs={"pk": self.object.restaurant.pk})


class EditRestaurantInfoView(UpdateView):
    model = Restaurant
    fields = (
        "description",
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
    template_name = "dinedashapp/restaurant_hours_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields.values():
            field.required = False

        return form

    def get_success_url(self):
        return reverse("restaurant_info", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            if "_both_null_or_neither_null" in repr(e):
                form.add_error(
                    None,
                    "Could not process data. If you entered an opening time for a day of the week, make sure to also specify a closing time for said day.",
                )
                return self.form_invalid(form)
            raise e
