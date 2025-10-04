# finances/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import BudgetFormation, DepenseFormation

@login_required
def tableau_finances(request):
    budgets = BudgetFormation.objects.select_related('departement')
    depenses = DepenseFormation.objects.select_related('session')
    
    total_budget = budgets.aggregate(total=Sum('montant_alloue'))['total'] or 0
    total_depenses = depenses.aggregate(total=Sum('montant'))['total'] or 0
    
    return render(request, 'finances/tableau_finances.html', {
        'budgets': budgets,
        'depenses': depenses,
        'total_budget': total_budget,
        'total_depenses': total_depenses,
        'solde': total_budget - total_depenses
    })