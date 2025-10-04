# formations/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CatalogueFormation, SessionFormation

@login_required
def liste_formations(request):
    formations = CatalogueFormation.objects.all()
    sessions = SessionFormation.objects.select_related('formation', 'formateur')
    
    return render(request, 'formations/liste_formations.html', {
        'formations': formations,
        'sessions': sessions
    })