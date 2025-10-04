# evaluation/models.py
from django.db import models
from employes.models import Employe, Competence

class EvaluationBesoin(models.Model):
    TYPE_EVALUATION = [
        ('G', 'Gap Analysis'),
        ('P', 'Plan de Développement'),
        ('A', 'Audit des Compétences'),
        ('B', 'Besoins Projet'),
    ]
    
    STATUT_EVALUATION = [
        ('B', 'Brouillon'),
        ('E', 'En cours'),
        ('T', 'Terminée'),
        ('V', 'Validée'),
    ]
    
    intitule = models.CharField(max_length=200)
    description = models.TextField()
    type_evaluation = models.CharField(max_length=1, choices=TYPE_EVALUATION)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=1, choices=STATUT_EVALUATION, default='B')
    createur = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.intitule

class BesoinFormation(models.Model):
    evaluation = models.ForeignKey(EvaluationBesoin, on_delete=models.CASCADE)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    competence_requise = models.ForeignKey(Competence, on_delete=models.CASCADE)
    niveau_actuel = models.CharField(max_length=1, choices=[
        ('N', 'Novice'),
        ('I', 'Intermédiaire'),
        ('E', 'Expert'),
    ])
    niveau_souhaite = models.CharField(max_length=1, choices=[
        ('N', 'Novice'),
        ('I', 'Intermédiaire'),
        ('E', 'Expert'),
    ])
    priorite = models.IntegerField(choices=[(1, 'Faible'), (2, 'Moyenne'), (3, 'Élevée'), (4, 'Critique')])
    commentaire = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('evaluation', 'employe', 'competence_requise')
    
    def __str__(self):
        return f"{self.employe} - {self.competence_requise}"