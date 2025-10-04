# planification/views.py
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, F
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User  # Ajouter cet import
import json

from .models import ParticipantFormation, PlanificationFormation, EtapePlanification, SequenceFormation, CompetenceVisee
from .models import PlanificationFormation, EtapePlanification
from employes.models import Competence, Employe, Departement
from employes.forms import EmployeFormSimple
from formations.models import CatalogueFormation
from formateurs.models import Formateur, OrganismeFormateur

# planification/views.py
@login_required
def planification_formations(request):
    # CORRIGER la requête - enlever select_related('employe') et utiliser prefetch_related
    planifications = PlanificationFormation.objects.select_related(
        'formation_existante', 'formateur_interne'
    ).prefetch_related(
        'employes'  # Utiliser prefetch_related pour ManyToMany
    ).all().order_by('-date_creation')
    
    # Calcul manuel du coût total
    cout_total = 0
    for planif in planifications:
        cout_total += planif.cout_total
    
    # Statistiques
    stats = {
        'total': planifications.count(),
        'brouillons': planifications.filter(statut='B').count(),
        'validees': planifications.filter(statut='V').count(),
        'confirmees': planifications.filter(statut='C').count(),
        'cout_total': cout_total,
    }
    
    # Planifications récentes
    recentes = planifications[:5]
    
    return render(request, 'planification/planification_formations.html', {
        'planifications': planifications,
        'stats': stats,
        'recentes': recentes,
    })

@login_required
def creer_planification(request):
    """Rediriger vers la première étape (informations générales)"""
    # Nettoyer toute session précédente
    for key in list(request.session.keys()):
        if key.startswith('planification_'):
            del request.session[key]
    
    return redirect('etape_informations')

# planification/views.py
@login_required
def etape_qui(request):
    """Étape 2: Sélection des participants"""
    if not request.session.get('planification_infos'):
        messages.error(request, "Veuillez d'abord compléter les informations générales.")
        return redirect('etape_informations')
    
    employes = Employe.objects.select_related('user', 'departement').all()
    
    # Récupérer les employés déjà sélectionnés (initialiser si vide)
    employes_selectionnes = request.session.get('planification_employes', [])
    
    print(f"DEBUG: Employés sélectionnés en session: {employes_selectionnes}")  # Debug
    
    if request.method == 'POST':
        print(f"DEBUG: Action POST: {request.POST}")  # Debug
        
        # Vérifier si c'est une requête AJAX pour créer un employé
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return creer_employe_ajax(request)
        
        # Traitement de l'ajout/suppression d'employés
        action = request.POST.get('action')
        
        if action == 'ajouter_employe':
            employe_id = request.POST.get('employe')
            if employe_id and employe_id not in employes_selectionnes:
                employes_selectionnes.append(employe_id)
                request.session['planification_employes'] = employes_selectionnes
                request.session.modified = True  # Important: forcer la sauvegarde
                messages.success(request, "Employé ajouté à la planification")
                print(f"DEBUG: Employé {employe_id} ajouté")  # Debug
        
        elif action == 'supprimer_employe':
            employe_id = request.POST.get('employe_id')
            if employe_id in employes_selectionnes:
                employes_selectionnes.remove(employe_id)
                request.session['planification_employes'] = employes_selectionnes
                request.session.modified = True  # Important: forcer la sauvegarde
                messages.success(request, "Employé retiré de la planification")
                print(f"DEBUG: Employé {employe_id} retiré")  # Debug
        
        elif action == 'continuer':
            if employes_selectionnes:
                request.session['planification_employes'] = employes_selectionnes
                request.session.modified = True
                # REDIRIGER VERS OBJECTIFS AU LIEU DE etape_en_quoi
                return redirect('etape_objectifs')  # CHANGEMENT ICI
            else:
                messages.error(request, "Veuillez sélectionner au moins un employé")
        
        # Recharger la page après ajout/suppression
        return redirect('etape_qui')
    
    # Récupérer les objets employés sélectionnés
    employes_objets = Employe.objects.filter(id__in=employes_selectionnes)
    
    form = EmployeFormSimple()
    
    return render(request, 'planification/etape_qui.html', {
        'employes': employes,
        'form': form,
        'employes_selectionnes': employes_objets,
        'nombre_employes': len(employes_selectionnes)
    })

@login_required
@csrf_exempt
def creer_employe_ajax(request):
    """Créer un employé via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Vérifier si le matricule existe déjà
            if Employe.objects.filter(matricule=data.get('matricule')).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Un employé avec ce matricule existe déjà.'
                })
            
            # Vérifier les champs obligatoires
            required_fields = ['nom', 'prenom', 'email', 'matricule', 'poste']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': f'Le champ {field} est obligatoire.'
                    })
            
            # Créer l'utilisateur Django
            user = User.objects.create_user(
                username=data.get('matricule'),
                email=data.get('email'),
                password='temp_password123',
                first_name=data.get('prenom'),
                last_name=data.get('nom')
            )
            
            # Créer l'employé (sans date_embauche pour l'instant)
            employe = Employe(
                user=user,
                matricule=data.get('matricule'),
                poste=data.get('poste')
                # date_embauche est optionnel, donc pas besoin de le spécifier
            )
            employe.save()
            
            return JsonResponse({
                'success': True,
                'employe_id': employe.id,
                'employe_nom': f"{employe.user.get_full_name()} - {employe.poste}"
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})


@login_required
def etape_en_quoi(request):
    """Étape 3: Objectifs de la formation"""
    # Vérifier que les étapes précédentes sont complétées
    if not request.session.get('planification_infos'):
        messages.error(request, "Veuillez d'abord compléter les informations générales.")
        return redirect('etape_informations')
    
    if not request.session.get('planification_employes'):
        messages.error(request, "Veuillez d'abord sélectionner des participants.")
        return redirect('etape_qui')
    
    employes_ids = request.session.get('planification_employes', [])
    employes = Employe.objects.filter(id__in=employes_ids)
    formations = CatalogueFormation.objects.all()
    
    if request.method == 'POST':
        # Sauvegarder les données de l'étape
        request.session['planification_etape2'] = request.POST.dict()
        request.session.modified = True
        return redirect('etape_par_qui')
    
    return render(request, 'planification/etape_en_quoi.html', {
        'employes': employes,
        'formations': formations,
        'nombre_participants': len(employes_ids)
    })

# planification/views.py - CORRECTION
@login_required
def etape_par_qui(request):
    """Étape 4: Sélection du formateur - Version simplifiée"""
    # Vérifier que les étapes précédentes sont complétées
    if not request.session.get('planification_objectifs'):
        messages.error(request, "Veuillez d'abord définir les objectifs de la formation.")
        return redirect('etape_objectifs')
    
    # Récupérer les formateurs et organismes avec gestion d'erreur
    try:
        formateurs_internes = Formateur.objects.filter(type_formateur='I', actif=True)
        organismes_externes = OrganismeFormateur.objects.filter(actif=True)
    except Exception as e:
        # Si les tables n'existent pas encore
        formateurs_internes = Formateur.objects.none()
        organismes_externes = OrganismeFormateur.objects.none()
        print(f"Attention: Tables non créées - {e}")
    
    if request.method == 'POST':
        # Vérifier si c'est une requête AJAX pour créer un formateur/organisme
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return creer_formateur_ajax(request)
        
        # Traitement normal de l'étape (CHAMPS SIMPLIFIÉS)
        formateur_data = {
            'formateur_id': request.POST.get('formateur_id'),
            'organisme_id': request.POST.get('organisme_id'),
            'type_formateur': request.POST.get('type_formateur', 'interne'),
            'commentaires_formateur': request.POST.get('commentaires_formateur', ''),
        }
        
        request.session['planification_formateur'] = formateur_data
        request.session.modified = True
        
        messages.success(request, "Formateur sélectionné avec succès !")
        return redirect('etape_programme')
    
    # Charger les données existantes si disponibles
    formateur_data = request.session.get('planification_formateur', {})
    
    return render(request, 'planification/etape_par_qui.html', {
        'formateurs_internes': formateurs_internes,
        'organismes_externes': organismes_externes,
        'formateur_data': formateur_data
    })

@login_required
@csrf_exempt
def creer_formateur_ajax(request):
    """Créer un formateur ou organisme via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_creation = data.get('type_creation')  # 'formateur_interne' ou 'organisme_externe'
            
            if type_creation == 'formateur_interne':
                # Créer un formateur interne (agent)
                employe_id = data.get('employe_id')
                specialite = data.get('specialite', '')
                
                if not employe_id or not specialite:
                    return JsonResponse({
                        'success': False,
                        'error': 'L\'employé et la spécialité sont obligatoires.'
                    })
                
                employe = Employe.objects.get(id=employe_id)
                
                # Vérifier si l'employé est déjà formateur
                if Formateur.objects.filter(employe=employe).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Cet employé est déjà formateur.'
                    })
                
                # Créer le formateur
                formateur = Formateur(
                    nom=employe.user.last_name,
                    prenom=employe.user.first_name,
                    email=employe.user.email,
                    telephone='',  # À compléter
                    type_formateur='I',
                    employe=employe,
                    specialite=specialite,
                    tarif_horaire=0  # Par défaut
                )
                formateur.save()
                
                return JsonResponse({
                    'success': True,
                    'formateur_id': formateur.id,
                    'formateur_nom': f"{formateur.nom_complet} - {specialite}"
                })
                
            elif type_creation == 'organisme_externe':
                # Créer un organisme formateur
                nom = data.get('nom')
                siret = data.get('siret')
                contact_principal = data.get('contact_principal')
                specialites = data.get('specialites', '')
                
                if not nom or not siret:
                    return JsonResponse({
                        'success': False,
                        'error': 'Le nom et le SIRET sont obligatoires.'
                    })
                
                # Vérifier si le SIRET existe déjà
                if OrganismeFormateur.objects.filter(siret=siret).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Un organisme avec ce SIRET existe déjà.'
                    })
                
                organisme = OrganismeFormateur(
                    nom=nom,
                    siret=siret,
                    adresse=data.get('adresse', ''),
                    telephone=data.get('telephone', ''),
                    email=data.get('email', ''),
                    contact_principal=contact_principal,
                    specialites=specialites
                )
                organisme.save()
                
                return JsonResponse({
                    'success': True,
                    'organisme_id': organisme.id,
                    'organisme_nom': organisme.nom
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Type de création non reconnu.'
                })
                
        except Employe.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Employé non trouvé.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
@csrf_exempt
def creer_formateur_ajax(request):
    """Créer un formateur ou organisme via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_creation = data.get('type_creation')  # 'formateur_interne' ou 'organisme_externe'
            
            if type_creation == 'formateur_interne':
                # Créer un formateur interne (agent)
                employe_id = data.get('employe_id')
                specialite = data.get('specialite', '')
                
                if not employe_id or not specialite:
                    return JsonResponse({
                        'success': False,
                        'error': 'L\'employé et la spécialité sont obligatoires.'
                    })
                
                employe = Employe.objects.get(id=employe_id)
                
                # Vérifier si l'employé est déjà formateur
                from formateurs.models import Formateur
                if Formateur.objects.filter(employe=employe).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Cet employé est déjà formateur.'
                    })
                
                # Créer le formateur
                formateur = Formateur(
                    nom=employe.user.last_name,
                    prenom=employe.user.first_name,
                    email=employe.user.email,
                    telephone='',  # À compléter
                    type_formateur='I',
                    employe=employe,
                    specialite=specialite,
                    tarif_horaire=data.get('tarif_horaire', 0)
                )
                formateur.save()
                
                return JsonResponse({
                    'success': True,
                    'formateur_id': formateur.id,
                    'formateur_nom': f"{formateur.nom_complet} - {specialite}"
                })
                
            elif type_creation == 'organisme_externe':
                # Créer un organisme formateur
                from formateurs.models import OrganismeFormateur
                nom = data.get('nom')
                siret = data.get('siret')
                contact_principal = data.get('contact_principal')
                specialites = data.get('specialites', '')
                
                if not nom or not siret:
                    return JsonResponse({
                        'success': False,
                        'error': 'Le nom et le SIRET sont obligatoires.'
                    })
                
                # Vérifier si le SIRET existe déjà
                if OrganismeFormateur.objects.filter(siret=siret).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Un organisme avec ce SIRET existe déjà.'
                    })
                
                organisme = OrganismeFormateur(
                    nom=nom,
                    siret=siret,
                    adresse=data.get('adresse', ''),
                    telephone=data.get('telephone', ''),
                    email=data.get('email', ''),
                    contact_principal=contact_principal,
                    specialites=specialites
                )
                organisme.save()
                
                return JsonResponse({
                    'success': True,
                    'organisme_id': organisme.id,
                    'organisme_nom': organisme.nom
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Type de création non reconnu.'
                })
                
        except Employe.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Employé non trouvé.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

# planification/views.py
@login_required
def etape_cout(request):
    """Étape 7: Coût - Doit appeler finaliser_planification à la fin"""
    # Vérifications des étapes précédentes
    required_steps = [
        'planification_infos', 
        'planification_employes', 
        'planification_objectifs',
        'planification_formateur',
        'planification_programme',
        'planification_evaluation'
    ]
    
    for step in required_steps:
        if not request.session.get(step):
            messages.error(request, f"Étape manquante: {step}. Veuillez compléter les étapes précédentes.")
            # Rediriger vers la première étape manquante
            if step == 'planification_infos':
                return redirect('etape_informations')
            elif step == 'planification_employes':
                return redirect('etape_qui')
            elif step == 'planification_objectifs':
                return redirect('etape_objectifs')
            elif step == 'planification_formateur':
                return redirect('etape_par_qui')
            elif step == 'planification_programme':
                return redirect('etape_programme')
            elif step == 'planification_evaluation':
                return redirect('etape_evaluation')
    
    if request.method == 'POST':
        # Sauvegarder les données de coût
        etape7_data = request.POST.dict()
        request.session['planification_cout'] = etape7_data
        request.session.modified = True
        
        # Rediriger vers la finalisation
        return finaliser_planification(request)
    
    return render(request, 'planification/etape_cout.html')

# planification/views.py
@login_required
def detail_planification(request, planification_id):
    planification = get_object_or_404(
        PlanificationFormation.objects.select_related(
            'formation_existante', 'formateur_interne'
        ).prefetch_related(
            'employes'  # Utiliser prefetch_related pour ManyToMany
        ), 
        id=planification_id
    )
    return render(request, 'planification/detail_planification.html', {
        'planification': planification
    })
    
    # planification/views.py - Ajouter les nouvelles étapes
# planification/views.py - Compléter etape_programme
@login_required
def etape_programme(request):
    """Étape 5: Programme pédagogique"""
    # Vérifier que les étapes précédentes sont complétées
    if not request.session.get('planification_formateur'):
        messages.error(request, "Veuillez d'abord sélectionner un formateur.")
        return redirect('etape_par_qui')
    
    competences = Competence.objects.all()
    
    if request.method == 'POST':
        # Récupérer les données des séquences
        sequences_data = []
        sequences_ordre = request.POST.getlist('sequence_ordre[]')
        sequences_intitule = request.POST.getlist('sequence_intitule[]')
        sequences_duree = request.POST.getlist('sequence_duree[]')
        sequences_methode = request.POST.getlist('sequence_methode[]')
        sequences_objectif = request.POST.getlist('sequence_objectif[]')
        sequences_supports = request.POST.getlist('sequence_supports[]')
        
        # Structurer les données des séquences
        for i in range(len(sequences_ordre)):
            if sequences_intitule[i].strip():  # Vérifier que l'intitulé n'est pas vide
                sequences_data.append({
                    'ordre': int(sequences_ordre[i]),
                    'intitule': sequences_intitule[i].strip(),
                    'duree': float(sequences_duree[i]),
                    'methode': sequences_methode[i],
                    'objectif': sequences_objectif[i].strip(),
                    'supports': sequences_supports[i].strip()
                })
        
        # Récupérer les compétences sélectionnées
        competences_visees = request.POST.getlist('competences_visees')
        
        # Sauvegarder dans la session
        etape5_data = {
            'sequences': sequences_data,
            'competences_visees': [int(comp_id) for comp_id in competences_visees],
            'contenu_formation': request.POST.get('contenu_formation', ''),
            'methodologie_retenue': request.POST.get('methodologie_retenue', '')
        }
        request.session['planification_programme'] = etape5_data
        request.session.modified = True
        
        messages.success(request, "Programme pédagogique enregistré !")
        return redirect('etape_evaluation')
    
    # Charger les données existantes si disponibles
    programme_data = request.session.get('planification_programme', {})
    
    return render(request, 'planification/etape_programme.html', {
        'competences': competences,
        'programme_data': programme_data,
        'sequences_count': len(programme_data.get('sequences', [1]))
    })

@login_required
def etape_evaluation(request):
    """Étape 6: Évaluation - Doit rediriger vers Coût, pas finaliser"""
    # Vérifier que les étapes précédentes sont complétées
    if not request.session.get('planification_programme'):
        messages.error(request, "Veuillez d'abord définir le programme pédagogique.")
        return redirect('etape_programme')
    
    if request.method == 'POST':
        # Sauvegarder les données d'évaluation
        etape6_data = request.POST.dict()
        request.session['planification_evaluation'] = etape6_data
        request.session.modified = True
        
        messages.success(request, "Évaluation enregistrée !")
        return redirect('etape_cout')  # ✅ CORRECTION: vers cout
    
    return render(request, 'planification/etape_evaluation.html')

@login_required
def etape_informations(request):
    """Nouvelle étape 1: Informations générales de la formation"""
    if request.method == 'POST':
        # Sauvegarder les informations générales dans la session
        request.session['planification_infos'] = request.POST.dict()
        return redirect('etape_qui')
    
    return render(request, 'planification/etape_informations_generales.html')

# planification/views.py - Compléter finaliser_planification
# planification/views.py - MODIFIER CETTE VUE
@login_required
def finaliser_planification(request):
    """Sauvegarde finale de toute la planification (7 étapes)"""
    if request.method == 'POST':
        try:
            # Récupérer les données de toutes les étapes
            infos_data = request.session.get('planification_infos', {})
            employes_ids = request.session.get('planification_employes', [])
            objectifs_data = request.session.get('planification_objectifs', {})
            etape2_data = request.session.get('planification_etape2', {})
            etape3_data = request.session.get('planification_etape3', {})
            etape5_data = request.session.get('planification_etape5', {})
            etape6_data = request.POST.dict()  # Données de l'étape évaluation
            etape7_data = request.POST.dict()  # Données de l'étape coût

            if not employes_ids:
                messages.error(request, "Veuillez sélectionner au moins un employé.")
                return redirect('etape_qui')

            # employe = Employe.objects.get(id=employe_id)
            
            # Création de la planification principale
            planification = PlanificationFormation(
                # Informations générales
                client=request.client,  # NOUVEAU
                createur=request.user, 
                
                titre_formation=infos_data.get('titre_formation', ''),
                duree_totale_heures=float(infos_data.get('duree_totale_heures', 0) or 0),
                duree_totale_jours=int(infos_data.get('duree_totale_jours', 0) or 0),
                repartition_duree=infos_data.get('repartition_duree', ''),
                lieu_formation=infos_data.get('lieu_formation', ''),
                participants_vises=infos_data.get('participants_vises', ''),
                situation_problematique=infos_data.get('situation_problematique', ''),
                ameliorations_attendues=infos_data.get('ameliorations_attendues', ''),
                enjeux_strategiques=infos_data.get('enjeux_strategiques', ''),
                
                
                # employe=employe,
                demandeur=request.user,
                effectif_groupe=int(etape2_data.get('effectif_groupe', 1)),
                
                # Objectifs (étape 3)
                modalite=etape2_data.get('modalite', 'S'),
                objectif=etape2_data.get('objectif', ''),
                resultat_attendu=etape2_data.get('resultat_attendu', ''),
                performance_attendu=etape2_data.get('performance_attendu', ''),
                
                # Objectifs
                type_formation=objectifs_data.get('type_formation', 'I'),
                formation_existante_id=objectifs_data.get('formation_existante'),
                formation_sur_mesure=objectifs_data.get('formation_sur_mesure', ''),
                objectif_general=objectifs_data.get('objectif_general', ''),
                objectifs_pedagogiques=objectifs_data.get('objectifs_pedagogiques', ''),
                criteres_evaluation=objectifs_data.get('criteres_evaluation', ''),
                indicateurs_reussite=objectifs_data.get('indicateurs_reussite', ''),
                prerequis_connaissances=objectifs_data.get('prerequis_connaissances', ''),
                prerequis_experience=objectifs_data.get('prerequis_experience', ''),
                contexte_professionnel=objectifs_data.get('contexte_professionnel', ''),
                
                # Formateur (étape 4)
                formateur_interne_id=etape3_data.get('formateur_interne'),
                organisme_externe=etape3_data.get('organisme_externe', ''),
                contact_externe=etape3_data.get('contact_externe', ''),
                nom_adresse_formateur=etape3_data.get('nom_adresse_formateur', ''),
                
                # Contenu et méthodologie (étape 5)
                contenu_formation=etape5_data.get('contenu_formation', ''),
                methodologie_retenue=etape5_data.get('methodologie_retenue', ''),
                progression_pedagogique=etape5_data.get('progression_pedagogique', ''),
                
                # Évaluation (étape 6)
                evaluation_diagnostique=etape6_data.get('evaluation_diagnostique', ''),
                evaluation_formative=etape6_data.get('evaluation_formative', ''),
                evaluation_sommative=etape6_data.get('evaluation_sommative', ''),
                evaluation_froide=etape6_data.get('evaluation_froide', ''),
                mode_evaluation=etape6_data.get('mode_evaluation', ''),
                contraintes_logistiques=etape6_data.get('contraintes_logistiques', ''),
                risques_pedagogiques=etape6_data.get('risques_pedagogiques', ''),
                plan_secours=etape6_data.get('plan_secours', ''),
                materiel_requis=etape6_data.get('materiel_requis', ''),
                plan_action=etape6_data.get('plan_action', ''),
                modalites_suivi=etape6_data.get('modalites_suivi', ''),
                ressources_complementaires=etape6_data.get('ressources_complementaires', ''),
                
                # Coûts (étape 7)
                prix_formation=float(etape7_data.get('prix_formation', 0) or 0),
                frais_sejour=float(etape7_data.get('frais_sejour', 0) or 0),
                frais_transport=float(etape7_data.get('frais_transport', 0) or 0),
                frais_restauration=float(etape7_data.get('frais_restauration', 0) or 0),
                autres_frais=float(etape7_data.get('autres_frais', 0) or 0),
                mode_paiement=etape7_data.get('mode_paiement', ''),
                
                statut='B'
            )
            planification.save()
            
            # Ajouter les employés participants
            for employe_id in employes_ids:
                ParticipantFormation.objects.create(
                    planification=planification,
                    employe_id=employe_id,
                    statut_participation='I'
                )
            
            # Création des séquences pédagogiques si disponibles
            sequences_data = etape5_data.get('sequences', [])
            for seq_data in sequences_data:
                SequenceFormation.objects.create(
                    planification=planification,
                    ordre=int(seq_data['ordre']),
                    intitule=seq_data['intitule'],
                    duree_heures=float(seq_data['duree']),
                    objectif_sequence=seq_data['objectif'],
                    methode_pedagogique=seq_data['methode'],
                    supports_utilises=seq_data['supports']
                )
            
            # Création des étapes de planification (7 étapes maintenant)
            for etape_num in [1, 2, 3, 4, 5, 6, 7]:
                EtapePlanification.objects.create(
                    planification=planification,
                    etape=etape_num,
                    complete=True,
                    date_completion=timezone.now()
                )
            
            # Nettoyer complètement la session
            for key in list(request.session.keys()):
                if key.startswith('planification_'):
                    del request.session[key]
            
            messages.success(request, 
                f"✅ Planification créée avec succès pour {len(employes_ids)} participant(s) !")
            return redirect('detail_planification', planification_id=planification.id)
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la création: {str(e)}")
            return render(request, 'planification/etape_cout.html')
    
    return redirect('etape_cout')


@login_required
def soumettre_validation(request, planification_id):
    """Soumettre une planification pour validation"""
    planification = get_object_or_404(
        PlanificationFormation.objects.for_request(request), 
        id=planification_id
    )
    
    # Vérifier les permissions
    if not request.profil.peut_saisir:
        messages.error(request, "Vous n'avez pas la permission de soumettre des planifications.")
        return redirect('detail_planification', planification_id=planification_id)
    
    if planification.statut != 'B':
        messages.error(request, "Cette planification a déjà été soumise.")
        return redirect('detail_planification', planification_id=planification_id)
    
    planification.statut = 'SOUMIS'
    planification.date_soumission = timezone.now()
    planification.save()
    
    # TODO: Envoyer une notification au valideur niveau 1
    
    messages.success(request, "Planification soumise pour validation niveau 1!")
    return redirect('detail_planification', planification_id=planification_id)

@login_required
def valider_planification_n1(request, planification_id):
    """Validation niveau 1 par le manager"""
    planification = get_object_or_404(
        PlanificationFormation.objects.for_request(request), 
        id=planification_id
    )
    
    if not request.profil.peut_valider_niveau_1:
        messages.error(request, "Vous n'avez pas la permission de valider au niveau 1.")
        return redirect('detail_planification', planification_id=planification_id)
    
    if planification.statut != 'SOUMIS':
        messages.error(request, "Cette planification n'est pas en attente de validation niveau 1.")
        return redirect('detail_planification', planification_id=planification_id)
    
    planification.statut = 'VALIDE_1'
    planification.valideur_niveau_1 = request.user
    planification.date_validation_1 = timezone.now()
    planification.save()
    
    # TODO: Envoyer une notification au valideur niveau 2
    
    messages.success(request, "Planification validée niveau 1! En attente de validation niveau 2.")
    return redirect('detail_planification', planification_id=planification_id)

@login_required
def valider_planification_n2(request, planification_id):
    """Validation niveau 2 par la direction"""
    planification = get_object_or_404(
        PlanificationFormation.objects.for_request(request), 
        id=planification_id
    )
    
    if not request.profil.peut_valider_niveau_2:
        messages.error(request, "Vous n'avez pas la permission de valider au niveau 2.")
        return redirect('detail_planification', planification_id=planification_id)
    
    if planification.statut != 'VALIDE_1':
        messages.error(request, "Cette planification n'est pas en attente de validation niveau 2.")
        return redirect('detail_planification', planification_id=planification_id)
    
    planification.statut = 'V'  # Validée
    planification.valideur_niveau_2 = request.user
    planification.date_validation_2 = timezone.now()
    planification.save()
    
    messages.success(request, "✅ Planification validée définitivement!")
    return redirect('detail_planification', planification_id=planification_id)

@login_required
def rejeter_planification(request, planification_id):
    """Rejeter une planification"""
    planification = get_object_or_404(
        PlanificationFormation.objects.for_request(request), 
        id=planification_id
    )
    
    if request.method == 'POST':
        commentaire = request.POST.get('commentaire', '')
        
        if planification.statut == 'SOUMIS' and request.profil.peut_valider_niveau_1:
            planification.statut = 'REJETE'
            planification.valideur_niveau_1 = request.user
        elif planification.statut == 'VALIDE_1' and request.profil.peut_valider_niveau_2:
            planification.statut = 'REJETE'
            planification.valideur_niveau_2 = request.user
        else:
            messages.error(request, "Action non autorisée.")
            return redirect('detail_planification', planification_id=planification_id)
        
        planification.commentaire_validation = commentaire
        planification.save()
        
        messages.success(request, "Planification rejetée.")
    
    return redirect('detail_planification', planification_id=planification_id)

@login_required
def debug_session(request):
    """Vue temporaire pour debugger la session"""
    session_data = {
        'planification_infos': request.session.get('planification_infos'),
        'planification_employes': request.session.get('planification_employes'),
        'planification_etape2': request.session.get('planification_etape2'),
        'planification_etape3': request.session.get('planification_etape3'),
    }
    
    return JsonResponse(session_data)

# planification/views.py
@login_required
def etape_objectifs(request):
    """Étape 3: Objectifs de la formation - Version simplifiée"""
    # Vérifier que les étapes précédentes sont complétées
    if not request.session.get('planification_employes'):
        messages.error(request, "Veuillez d'abord sélectionner des participants.")
        return redirect('etape_qui')
    
    employes_ids = request.session.get('planification_employes', [])
    employes = Employe.objects.filter(id__in=employes_ids)
    formations = CatalogueFormation.objects.all()
    competences = Competence.objects.all()
    
    if request.method == 'POST':
        # Sauvegarder les données de l'étape objectifs
        etape_objectifs_data = {
            'formation_existante': request.POST.get('formation_existante', ''),
            'formation_sur_mesure': request.POST.get('formation_sur_mesure', ''),
            'objectifs_pedagogiques': request.POST.get('objectifs_pedagogiques', ''),
            'competences_visees': request.POST.getlist('competences_visees'),
            'prerequis_connaissances': request.POST.get('prerequis_connaissances', ''),
            'prerequis_experience': request.POST.get('prerequis_experience', ''),
        }
        
        request.session['planification_objectifs'] = etape_objectifs_data
        request.session.modified = True
        
        messages.success(request, "Objectifs enregistrés avec succès !")
        return redirect('etape_par_qui')
    
    # Charger les données existantes si disponibles
    objectifs_data = request.session.get('planification_objectifs', {})
    
    return render(request, 'planification/etape_objectifs.html', {
        'employes': employes,
        'formations': formations,
        'competences': competences,
        'nombre_participants': len(employes_ids),
        'objectifs_data': objectifs_data
    })