# finances/models.py
from django.db import models

class BudgetFormation(models.Model):
    annee = models.IntegerField()
    departement = models.ForeignKey('employes.Departement', on_delete=models.CASCADE)
    montant_alloue = models.DecimalField(max_digits=12, decimal_places=2)
    montant_consomme = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('annee', 'departement')
    
    def __str__(self):
        return f"Budget {self.annee} - {self.departement.nom}"

class DepenseFormation(models.Model):
    CATEGORIES = [
        ('F', 'Formateur'),
        ('L', 'Location salle'),
        ('M', 'Matériel'),
        ('D', 'Déplacement'),
        ('R', 'Restauration'),
        ('A', 'Autre'),
    ]
    
    # Utiliser un nom de modèle en string pour éviter les imports circulaires
    session = models.ForeignKey('formations.SessionFormation', on_delete=models.CASCADE)
    categorie = models.CharField(max_length=1, choices=CATEGORIES)
    description = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField()
    justificatif = models.FileField(upload_to='justificatifs/', blank=True)
    
    def __str__(self):
        return f"{self.description} - {self.montant}€"

class ROIFormation(models.Model):
    # Utiliser un nom de modèle en string
    session = models.OneToOneField('formations.SessionFormation', on_delete=models.CASCADE)
    gains_productivite = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reduction_erreurs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    satisfaction_employes = models.IntegerField(default=0)  # /100
    date_calcul = models.DateField(auto_now_add=True)
    
    @property
    def cout_total(self):
        # Cette méthode sera implémentée plus tard, après les migrations
        depenses = DepenseFormation.objects.filter(session=self.session)
        return sum(depense.montant for depense in depenses)
    
    @property
    def gains_totaux(self):
        return self.gains_productivite + self.reduction_erreurs
    
    @property
    def roi(self):
        cout_total = self.cout_total
        if cout_total > 0:
            return (self.gains_totaux - cout_total) / cout_total * 100
        return 0
    
    def __str__(self):
        return f"ROI Session {self.session.id}"