from django.urls import path
from dinedashapp.views import index, log_in_question, RegularLogInView, RestaurantLogInView, DeliveryLogInView

urlpatterns = [
    path('', index, name='index'),
    path('log_in_question', log_in_question, name= 'log_in_question'),
    path('log_in_regular', RegularLogInView.as_view(), name= 'log_in_regular'),
    path('log_in_restaurant', RestaurantLogInView.as_view(), name= 'log_in_restaurant'),
    path('log_in_delivery', DeliveryLogInView.as_view(), name= 'log_in_delivery'),
]