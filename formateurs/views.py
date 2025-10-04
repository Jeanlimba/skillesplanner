# formateurs/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Formateur

@login_required
def liste_formateurs(request):
    formateurs = Formateur.objects.all()
    return render(request, 'formateurs/liste_formateurs.html', {
        'formateurs': formateurs
    })