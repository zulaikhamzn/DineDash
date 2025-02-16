from django.shortcuts import render
from django.views.generic import FormView

from dinedashapp.forms import LogInForm


def index(request):
    return render(request, "dinedashapp/index.html")


def log_in_question(request):
    return render(request, "dinedashapp/log_in_question.html")


class RegularLogInView(FormView):
    template_name = "dinedashapp/log_in_form.html"
    form_class = LogInForm
    extra_context = {"title": "Regular Customer Log In"}


class RestaurantLogInView(RegularLogInView):
    extra_context = {"title": "Restaurant Log In"}


class DeliveryLogInView(RegularLogInView):
    extra_context = {"title": "Delivery Log In"}
