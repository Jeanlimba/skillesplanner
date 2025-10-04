# planification/urls.py - AJOUTER CETTE URL
from django.urls import path
from . import views

urlpatterns = [
    path('', views.planification_formations, name='planification_formations'),
    path('creer/', views.creer_planification, name='creer_planification'),
    path('etape-informations/', views.etape_informations, name='etape_informations'),
    path('etape-qui/', views.etape_qui, name='etape_qui'),
    path('etape-objectifs/', views.etape_objectifs, name='etape_objectifs'),
    path('etape-par-qui/', views.etape_par_qui, name='etape_par_qui'),
    path('etape-programme/', views.etape_programme, name='etape_programme'),
    path('etape-evaluation/', views.etape_evaluation, name='etape_evaluation'),
    path('etape-cout/', views.etape_cout, name='etape_cout'),
    path('finaliser/', views.finaliser_planification, name='finaliser_planification'),
    path('<int:planification_id>/', views.detail_planification, name='detail_planification'),
    path('creer-employe-ajax/', views.creer_employe_ajax, name='creer_employe_ajax'),
    
    # AJOUTER CETTE URL
    path('creer-formateur-ajax/', views.creer_formateur_ajax, name='creer_formateur_ajax'),
    path('<int:planification_id>/soumettre/', views.soumettre_validation, name='soumettre_validation'),
    path('<int:planification_id>/valider-n1/', views.valider_planification_n1, name='valider_planification_n1'),
    path('<int:planification_id>/valider-n2/', views.valider_planification_n2, name='valider_planification_n2'),
    path('<int:planification_id>/rejeter/', views.rejeter_planification, name='rejeter_planification'),
]