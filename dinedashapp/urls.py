from django.urls import path

from dinedashapp.views import (
    DeliveryLogInView,
    DeliveryRegistrationView,
    RegularLogInView,
    RegularRegistrationView,
    RestaurantInfoView,
    RestaurantLogInView,
    RestaurantRegistrationView,
    RestaurantSearchView,
    about_us,
    blog,
    contact_us,
    index,
    log_in_question,
    log_out,
)

urlpatterns = [
    path("", index, name="index"),
    path("about_us", about_us, name="about_us"),
    path("contact_us", contact_us, name="contact_us"),
    path("blog", blog, name="blog"),
    path("log_in_question", log_in_question, name="log_in_question"),
    path("log_in_regular", RegularLogInView.as_view(), name="log_in_regular"),
    path("log_in_restaurant", RestaurantLogInView.as_view(), name="log_in_restaurant"),
    path("log_in_delivery", DeliveryLogInView.as_view(), name="log_in_delivery"),
    path(
        "register_regular", RegularRegistrationView.as_view(), name="register_regular"
    ),
    path(
        "register_restaurant",
        RestaurantRegistrationView.as_view(),
        name="register_restaurant",
    ),
    path(
        "register_delivery",
        DeliveryRegistrationView.as_view(),
        name="register_delivery",
    ),
    path("log_out", log_out, name="log_out"),
    path("order", RestaurantSearchView.as_view(), name="restaurant_search"),
    path("restaurant/<int:pk>", RestaurantInfoView.as_view(), name="restaurant_info"),
]
