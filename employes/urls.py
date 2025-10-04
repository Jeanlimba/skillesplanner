# employes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_employes, name='liste_employes'),
    path('ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('<int:employe_id>/', views.detail_employe, name='detail_employe'),
    path('<int:employe_id>/modifier/', views.modifier_employe, name='modifier_employe'),
    path('api/employes-disponibles/', views.api_employes_disponibles, name='api_employes_disponibles'),
]