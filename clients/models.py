# clients/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Client(models.Model):
    nom = models.CharField(max_length=200)
    sigle = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=200)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nom} ({self.sigle})"

class ProfilUtilisateur(models.Model):
    ROLE_CHOICES = [
        ('SAISIE', 'Saisie'),
        ('VALIDATION_1', 'Validation Niveau 1'),
        ('VALIDATION_2', 'Validation Niveau 2'),
        ('ADMIN_CLIENT', 'Administrateur Client'),
        ('SUPER_ADMIN', 'Super Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.client.sigle} - {self.get_role_display()}"
    
    @property
    def peut_saisir(self):
        return self.role in ['SAISIE', 'VALIDATION_1', 'VALIDATION_2', 'ADMIN_CLIENT']
    
    @property
    def peut_valider_niveau_1(self):
        return self.role in ['VALIDATION_1', 'VALIDATION_2', 'ADMIN_CLIENT']
    
    @property
    def peut_valider_niveau_2(self):
        return self.role in ['VALIDATION_2', 'ADMIN_CLIENT']
    
    @property
    def est_admin_client(self):
        return self.role == 'ADMIN_CLIENT'
    
    @property
    def est_super_admin(self):
        return self.role == 'SUPER_ADMIN'