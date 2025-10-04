# suivi/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.suivi_evaluations, name='suivi_evaluations'),
    path('indicateurs/', views.indicateurs_performance, name='indicateurs_performance'),
    path('rapports/', views.rapports_formations, name='rapports_formations'),
]