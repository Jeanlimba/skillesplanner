# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tableau_finances, name='tableau_finances'),
]