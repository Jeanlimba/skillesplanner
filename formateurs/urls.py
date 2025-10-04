# formateurs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_formateurs, name='liste_formateurs'),
]