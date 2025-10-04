# formations/models.py
from django.db import models

class CatalogueFormation(models.Model):
    MODALITES = [
        ('P', 'Présentiel'),
        ('D', 'Distanciel'),
        ('M', 'Mixte'),
    ]
    
    TYPES = [
        ('I', 'Interne'),
        ('E', 'Externe'),
        ('C', 'Certifiante'),
        ('O', 'Obligatoire'),
    ]
    
    intitule = models.CharField(max_length=200)
    description = models.TextField()
    duree_jours = models.IntegerField()
    modalite = models.CharField(max_length=1, choices=MODALITES)
    type_formation = models.CharField(max_length=1, choices=TYPES)
    competences_visees = models.ManyToManyField('employes.Competence')
    public_cible = models.TextField()
    prerequis = models.TextField(blank=True)
    
    def __str__(self):
        return self.intitule

class SessionFormation(models.Model):
    STATUTS = [
        ('P', 'Planifiée'),
        ('C', 'Confirmée'),
        ('E', 'En cours'),
        ('T', 'Terminée'),
        ('A', 'Annulée'),
    ]
    
    formation = models.ForeignKey(CatalogueFormation, on_delete=models.CASCADE)
    formateur = models.ForeignKey('formateurs.Formateur', on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=200)
    capacite_max = models.IntegerField(default=20)
    statut = models.CharField(max_length=1, choices=STATUTS, default='P')
    cout_estime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.formation.intitule} - {self.date_debut.strftime('%d/%m/%Y')}"
    
    @property
    def participants_count(self):
        return self.inscription_set.filter(statut__in=['I', 'P']).count()

class Inscription(models.Model):
    STATUTS = [
        ('I', 'Inscrit'),
        ('P', 'Présent'),
        ('A', 'Absent'),
        ('D', 'Abandon'),
    ]
    
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE)
    session = models.ForeignKey(SessionFormation, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=1, choices=STATUTS, default='I')
    evaluation_froide = models.TextField(blank=True)
    date_evaluation_froide = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('employe', 'session')
    
    def __str__(self):
        return f"{self.employe} - {self.session}"