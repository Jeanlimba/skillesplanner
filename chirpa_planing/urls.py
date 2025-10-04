# chirpa_planing/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),
    path('dashboard/', include('dashboard.urls')),
    path('employes/', include('employes.urls')),
    path('formations/', include('formations.urls')),
    path('formateurs/', include('formateurs.urls')),
    path('finances/', include('finances.urls')),
    path('evaluation/', include('evaluation.urls')), 
    path('planification/', include('planification.urls')),  # Nouveau
    path('suivi/', include('suivi.urls')),  # Nouveau # Nouvelle application
    path('clients/', include('clients.urls')),
    
    # URLs d'authentification
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html',
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='/accounts/login/'
    ), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)