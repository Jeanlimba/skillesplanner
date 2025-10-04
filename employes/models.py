# employes/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 

# Définition globale des constantes
NIVEAU_COMPETENCE = [
    ('N', 'Novice'),
    ('I', 'Intermédiaire'),
    ('E', 'Expert'),
]

class Departement(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom
    
    @property
    def responsable(self):
        """Retourne l'employé responsable du département"""
        return self.employe_set.filter(est_responsable=True).first()

class Employe(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    matricule = models.CharField(max_length=20, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    poste = models.CharField(max_length=100)
    date_embauche = models.DateField(null=True, blank=True)  # Rendre optionnel
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordonnes')
    est_responsable = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.poste}"
    
    @property
    def nom_complet(self):
        return self.user.get_full_name()
    
    def competences_actuelles(self):
        """Retourne les compétences actuelles de l'employé"""
        return self.competenceemploye_set.all()

class Competence(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    est_obligatoire = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nom

class CompetenceEmploye(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    niveau = models.CharField(max_length=1, choices=NIVEAU_COMPETENCE)
    date_acquisition = models.DateField(auto_now_add=True)
    date_validation = models.DateField(null=True, blank=True)
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='competences_validees')
    
    class Meta:
        unique_together = ('employe', 'competence')
        verbose_name = "Compétence employé"
        verbose_name_plural = "Compétences employés"
    
    def __str__(self):
        return f"{self.employe} - {self.competence} ({self.get_niveau_display()})"