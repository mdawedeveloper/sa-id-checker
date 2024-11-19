from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This will map the home view to the root URL
]
