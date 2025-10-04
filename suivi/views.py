# suivi/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def suivi_evaluations(request):
    return render(request, 'suivi/suivi_evaluations.html')

@login_required
def indicateurs_performance(request):
    return render(request, 'suivi/indicateurs_performance.html')

@login_required
def rapports_formations(request):
    return render(request, 'suivi/rapports_formations.html')