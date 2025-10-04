# clients/urls.py
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('super-admin/', views.tableau_de_bord_super_admin, name='tableau_de_bord_super_admin'),
    path('creer-client/', views.creer_client, name='creer_client'),
    path('<int:client_id>/utilisateurs/', views.gerer_utilisateurs_client, name='gerer_utilisateurs_client'),
]