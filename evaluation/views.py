# evaluation/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import EvaluationBesoin, BesoinFormation
from employes.models import Employe, Competence

@login_required
def evaluation_besoins(request):
    evaluations = EvaluationBesoin.objects.all().order_by('-date_creation')
    
    # Statistiques
    stats = {
        'total': evaluations.count(),
        'en_cours': evaluations.filter(statut='E').count(),
        'terminees': evaluations.filter(statut='T').count(),
    }
    
    return render(request, 'evaluation/evaluation_besoins.html', {
        'evaluations': evaluations,
        'stats': stats
    })

@login_required
def creer_evaluation(request):
    if request.method == 'POST':
        # Logique de création d'évaluation
        pass
    
    employes = Employe.objects.select_related('user', 'departement')
    competences = Competence.objects.all()
    
    return render(request, 'evaluation/creer_evaluation.html', {
        'employes': employes,
        'competences': competences
    })

@login_required
def detail_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(EvaluationBesoin, id=evaluation_id)
    besoins = BesoinFormation.objects.filter(evaluation=evaluation).select_related('employe', 'competence_requise')
    
    # Analyse des besoins par priorité
    analyse_priorite = besoins.values('priorite').annotate(
        count=Count('id')
    ).order_by('priorite')
    
    return render(request, 'evaluation/detail_evaluation.html', {
        'evaluation': evaluation,
        'besoins': besoins,
        'analyse_priorite': analyse_priorite
    })