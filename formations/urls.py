# formations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_formations, name='liste_formations'),
]