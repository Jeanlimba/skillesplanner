# formateurs/models.py
from django.db import models
from django.contrib.auth.models import User

# formateurs/models.py - VERSION SIMPLIFIÉE
from django.db import models

class Formateur(models.Model):
    TYPE_FORMATEUR = [
        ('I', 'Interne'),
        ('E', 'Externe'),
    ]
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    type_formateur = models.CharField(max_length=1, choices=TYPE_FORMATEUR)
    
    # Pour les formateurs internes (agents)
    employe = models.OneToOneField('employes.Employe', on_delete=models.SET_NULL, null=True, blank=True)
    specialite = models.CharField(max_length=200, blank=True)
    
    # Pour les formateurs externes
    organisme = models.CharField(max_length=100, blank=True)
    siret = models.CharField(max_length=14, blank=True)
    
    tarif_horaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    competences = models.ManyToManyField('employes.Competence')
    disponibilites = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_type_formateur_display()})"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class OrganismeFormateur(models.Model):
    """Nouveau modèle pour les organismes formateurs externes"""
    nom = models.CharField(max_length=200)
    siret = models.CharField(max_length=14, unique=True)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    contact_principal = models.CharField(max_length=100)
    specialites = models.TextField(help_text="Spécialités séparées par des virgules")
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom