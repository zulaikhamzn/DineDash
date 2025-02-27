from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from dinedashapp.forms import LogInForm, RegistrationForm
from dinedashapp.models import BlogPost, MenuItem, Restaurant


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


class DeliveryLogInView(RegularLogInView):
    extra_context = {
        "title": "Delivery Log In",
        "registration_url": reverse_lazy("register_delivery"),
    }


class RegularRegistrationView(FormView):
    template_name = "dinedashapp/registration_form.html"
    form_class = RegistrationForm
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
    extra_context = {
        "title": "Restaurant Registration",
        "log_in_url": reverse_lazy("log_in_restaurant"),
    }


class DeliveryRegistrationView(RegularRegistrationView):
    extra_context = {
        "title": "Delivery Registration",
        "log_in_url": reverse_lazy("log_in_delivery"),
    }


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
