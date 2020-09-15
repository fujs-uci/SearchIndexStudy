from django.urls import path
from .views import *


app_name = "results"
urlpatterns = [
    path('', index, name="index")
]
