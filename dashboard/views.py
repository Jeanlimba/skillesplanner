from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from formations.models import SessionFormation, Inscription
from finances.models import BudgetFormation, DepenseFormation
from employes.models import Employe, CompetenceEmploye
from evaluation.models import EvaluationBesoin, BesoinFormation

@login_required
@login_required
def tableau_de_bord(request):
    # KPIs principaux
    sessions_total = SessionFormation.objects.count()
    employes_formes = Inscription.objects.values('employe').distinct().count()
    cout_total = DepenseFormation.objects.aggregate(total=Sum('montant'))['total'] or 0
    total_employes = Employe.objects.count()
    
    # Évaluations des besoins
    evaluations_total = EvaluationBesoin.objects.count()
    besoins_identifies = BesoinFormation.objects.count()
    besoins_critiques = BesoinFormation.objects.filter(priorite=4).count()
    
    # Statistiques par statut des sessions
    stats_sessions = SessionFormation.objects.values('statut').annotate(
        count=Count('id')
    )
    
    # Budget vs Dépenses
    budgets = BudgetFormation.objects.all()
    
    # Compétences les plus demandées
    competences_populaires = CompetenceEmploye.objects.values(
        'competence__nom'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Sessions à venir
    sessions_prochaines = SessionFormation.objects.filter(
        statut__in=['P', 'C']
    ).order_by('date_debut')[:5]
    
    context = {
        'sessions_total': sessions_total,
        'employes_formes': employes_formes,
        'evaluations_total': evaluations_total,
        'besoins_identifies': besoins_identifies,
        'besoins_critiques': besoins_critiques,
        'cout_total': cout_total,
        'total_employes': total_employes,
        'stats_sessions': stats_sessions,
        'budgets': budgets,
        'competences_populaires': competences_populaires,
        'sessions_prochaines': sessions_prochaines,
    }
    
    return render(request, 'dashboard/tableau_de_bord.html', context)