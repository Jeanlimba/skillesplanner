# clients/views.py - VERSION COMPLÈTE
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import Client, ProfilUtilisateur
from .forms import ClientForm, UtilisateurClientForm

def est_super_admin(user):
    try:
        return hasattr(user, 'profil') and user.profil.est_super_admin
    except:
        return False

@login_required
@user_passes_test(est_super_admin)
def tableau_de_bord_super_admin(request):
    """Tableau de bord du super administrateur"""
    clients = Client.objects.all()
    stats = {
        'total_clients': clients.count(),
        'clients_actifs': clients.filter(actif=True).count(),
        'total_utilisateurs': ProfilUtilisateur.objects.count(),
    }
    
    return render(request, 'clients/tableau_de_bord_super_admin.html', {
        'clients': clients,
        'stats': stats
    })

@login_required
@user_passes_test(est_super_admin)
def creer_client(request):
    """Créer un nouveau client avec son admin"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            
            # Créer l'utilisateur admin du client
            username = f"admin_{client.sigle.lower()}"
            password = User.objects.make_random_password()
            
            user = User.objects.create_user(
                username=username,
                email=client.email,
                password=password,
                first_name="Admin",
                last_name=client.sigle
            )
            
            ProfilUtilisateur.objects.create(
                user=user,
                client=client,
                role='ADMIN_CLIENT'
            )
            
            messages.success(request, f"Client {client.nom} créé avec succès!")
            messages.info(request, f"Identifiants admin générés:<br><strong>Login:</strong> {username}<br><strong>Mot de passe:</strong> {password}")
            
            return redirect('tableau_de_bord_super_admin')
    else:
        form = ClientForm()
    
    return render(request, 'clients/creer_client.html', {'form': form})

@login_required
@user_passes_test(est_super_admin)
def gerer_utilisateurs_client(request, client_id):
    """Gérer les utilisateurs d'un client spécifique"""
    client = get_object_or_404(Client, id=client_id)
    utilisateurs = ProfilUtilisateur.objects.filter(client=client).select_related('user')
    
    if request.method == 'POST':
        form = UtilisateurClientForm(request.POST)
        if form.is_valid():
            # Vérifier si le username existe déjà
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
            else:
                # Créer l'utilisateur Django
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['prenom'],
                    last_name=form.cleaned_data['nom']
                )
                
                # Créer le profil utilisateur
                ProfilUtilisateur.objects.create(
                    user=user,
                    client=client,
                    role=form.cleaned_data['role'],
                    telephone=form.cleaned_data['telephone'] or ''
                )
                
                messages.success(request, f"Utilisateur {user.get_full_name()} créé avec succès!")
                return redirect('gerer_utilisateurs_client', client_id=client.id)
    else:
        form = UtilisateurClientForm()
    
    return render(request, 'clients/gerer_utilisateurs_client.html', {
        'client': client,
        'utilisateurs': utilisateurs,
        'form': form
    })