from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from dinedashapp.forms import LogInForm, RegistrationForm
from dinedashapp.models import BlogPost


def index(request):
    return render(request, "dinedashapp/index.html")


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
