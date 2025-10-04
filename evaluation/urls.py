# evaluation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluation_besoins, name='evaluation_besoins'),
    path('creer/', views.creer_evaluation, name='creer_evaluation'),
    path('<int:evaluation_id>/', views.detail_evaluation, name='detail_evaluation'),
]