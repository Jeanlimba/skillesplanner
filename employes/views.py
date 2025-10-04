# employes/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employe, Departement, Competence, CompetenceEmploye
from .forms import EmployeForm, CompetenceEmployeForm, EmployeFormSimple
from formateurs.models import Formateur

@login_required
def liste_employes(request):
    employes = Employe.objects.select_related('user', 'departement').all()
    departements = Departement.objects.all()
    
    departement_id = request.GET.get('departement')
    if departement_id:
        employes = employes.filter(departement_id=departement_id)
    
    return render(request, 'employes/liste_employes.html', {
        'employes': employes,
        'departements': departements
    })

@login_required
def detail_employe(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    competences = employe.competenceemploye_set.select_related('competence')
    
    # Formulaire pour ajouter une compétence
    if request.method == 'POST':
        form = CompetenceEmployeForm(request.POST)
        if form.is_valid():
            competence_employe = form.save(commit=False)
            competence_employe.employe = employe
            competence_employe.save()
            messages.success(request, "Compétence ajoutée avec succès")
            return redirect('detail_employe', employe_id=employe.id)
    else:
        form = CompetenceEmployeForm()
    
    return render(request, 'employes/detail_employe.html', {
        'employe': employe,
        'competences': competences,
        'form': form
    })

@login_required
def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            employe = form.save()
            messages.success(request, "Employé ajouté avec succès")
            return redirect('liste_employes')
    else:
        form = EmployeForm()
    
    return render(request, 'employes/form_employe.html', {'form': form})

@login_required
def modifier_employe(request, employe_id):
    employe = get_object_or_404(Employe, id=employe_id)
    
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            employe = form.save()
            messages.success(request, "Employé modifié avec succès")
            return redirect('detail_employe', employe_id=employe.id)
    else:
        form = EmployeForm(instance=employe)
    
    return render(request, 'employes/form_employe.html', {'form': form})


@login_required
def api_employes_disponibles(request):
    """API pour récupérer les employés disponibles comme formateurs"""
    try:
        employes = Employe.objects.select_related('user', 'departement').all()
        
        # Exclure les employés qui sont déjà formateurs
        # Utiliser une gestion d'erreur au cas où la table Formateur n'existe pas encore
        try:
            formateurs_existants = Formateur.objects.filter(employe__isnull=False).values_list('employe_id', flat=True)
            employes = employes.exclude(id__in=formateurs_existants)
        except Exception:
            # Si la table Formateur n'existe pas encore, on prend tous les employés
            pass
        
        data = {
            'employes': [
                {
                    'id': emp.id,
                    'nom_complet': emp.nom_complet,
                    'poste': emp.poste,
                    'departement': emp.departement.nom if emp.departement else ''
                }
                for emp in employes
            ]
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)