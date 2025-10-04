# planification/models.py
from django.db import models
from django.utils import timezone
from employes.models import Employe
from formations.models import CatalogueFormation
from formateurs.models import Formateur
from django.contrib.auth.models import User



class ParticipantFormation(models.Model):
    """Table intermédiaire pour gérer les participants avec des métadonnées"""
    planification = models.ForeignKey('PlanificationFormation', on_delete=models.CASCADE)
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)
    statut_participation = models.CharField(max_length=1, choices=[
        ('I', 'Inscrit'),
        ('C', 'Confirmé'),
        ('A', 'Annulé'),
        ('T', 'Terminé'),
    ], default='I')
    commentaire = models.TextField(blank=True, default="")
    
    class Meta:
        unique_together = ('planification', 'employe')
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.planification.formation_nom}"

class PlanificationFormation(models.Model):
    TYPE_FORMATION = [
        ('I', 'Interne'),
        ('E', 'Externe'),
    ]
    
    MODALITE_FORMATION = [
        ('S', 'En Salle'),
        ('L', 'En Ligne'),
        ('T', 'Entrainement à la Tâche'),
        ('M', 'Mentorat'),
        ('U', 'Tutorat'),
        ('H', 'Hybride'),
    ]
    
    STATUT_PLANIFICATION = [
        ('B', 'Brouillon'),
        ('SOUMIS', 'Soumis pour validation'),
        ('VALIDE_1', 'Validé Niveau 1'),
        ('VALIDE_2', 'Validé Niveau 2'),
        ('V', 'Validée'),
        ('P', 'En Préparation'),
        ('C', 'Confirmée'),
        ('T', 'Terminée'),
        ('A', 'Annulée'),
        ('REJETE', 'Rejeté'),
    ]
    
    # STATUT_PLANIFICATION = [
    #     ('B', 'Brouillon'),
    #     ('V', 'Validée'),
    #     ('P', 'En Préparation'),
    #     ('C', 'Confirmée'),
    #     ('T', 'Terminée'),
    #     ('A', 'Annulée'),
    # ]

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    
    # === INFORMATIONS GÉNÉRALES ===
    titre_formation = models.CharField(max_length=200, blank=True, default="", verbose_name="Titre de la formation")
    date_demande = models.DateTimeField(auto_now_add=True)
    demandeur = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    # Relation ManyToMany avec through
    employes = models.ManyToManyField(
        'employes.Employe', 
        through=ParticipantFormation,  # Référence à la classe, pas une chaîne
        verbose_name="Employés à former",
        related_name='planifications'  # related_name unique
    )
    
    # Durée et lieu
    duree_totale_heures = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name="Durée totale (heures)")
    duree_totale_jours = models.IntegerField(default=0, verbose_name="Durée totale (jours)")
    repartition_duree = models.TextField(blank=True, default="", verbose_name="Répartition de la durée")
    lieu_formation = models.TextField(blank=True, default="", verbose_name="Lieu de formation")
    
    # === PUBLIC CIBLE ÉTENDU ===
    effectif_groupe = models.IntegerField(default=1, verbose_name="Effectif du groupe")
    prerequis_connaissances = models.TextField(blank=True, default="", verbose_name="Prérequis connaissances")
    prerequis_experience = models.TextField(blank=True, default="", verbose_name="Prérequis expérience")
    contexte_professionnel = models.TextField(blank=True, default="", verbose_name="Contexte professionnel")
    participants_vises = models.TextField(blank=True, default="", verbose_name="Participants visés")

    # === JUSTIFICATION DE LA FORMATION ===
    situation_problematique = models.TextField(blank=True, default="", verbose_name="Situation à améliorer ou problématique")
    ameliorations_attendues = models.TextField(blank=True, default="", verbose_name="Améliorations attendues")
    enjeux_strategiques = models.TextField(blank=True, default="", verbose_name="Enjeux stratégiques")

    # === OBJECTIFS PÉDAGOGIQUES SMART ===
    type_formation = models.CharField(max_length=1, choices=TYPE_FORMATION, default='I')
    modalite = models.CharField(max_length=1, choices=MODALITE_FORMATION, default='S')
    formation_existante = models.ForeignKey(CatalogueFormation, on_delete=models.SET_NULL, null=True, blank=True)
    formation_sur_mesure = models.CharField(max_length=200, blank=True, default="", verbose_name="Formation sur mesure")
    
    # Objectifs existants (compatibilité)
    objectif = models.TextField(blank=True, default="", verbose_name="Objectif de la formation")
    resultat_attendu = models.TextField(blank=True, default="", verbose_name="Résultat attendu")
    performance_attendu = models.TextField(blank=True, default="", verbose_name="Performance attendue")
    
    # Objectifs SMART étendus
    objectif_general = models.TextField(blank=True, default="", verbose_name="Objectif général (finalité)")
    objectifs_pedagogiques = models.TextField(blank=True, default="", verbose_name="Objectifs pédagogiques SMART")
    criteres_evaluation = models.TextField(blank=True, default="", verbose_name="Critères d'évaluation")
    indicateurs_reussite = models.TextField(blank=True, default="", verbose_name="Indicateurs de réussite")

    # === FORMATEUR ===
    formateur_interne = models.ForeignKey(Formateur, on_delete=models.SET_NULL, null=True, blank=True, 
                                        limit_choices_to={'type_formateur': 'I'})
    organisme_externe = models.CharField(max_length=200, blank=True, default="", verbose_name="Organisme formateur")
    contact_externe = models.TextField(blank=True, default="", verbose_name="Contact organisme externe")
    nom_adresse_formateur = models.TextField(blank=True, default="", verbose_name="Nom et adresse du formateur")

    # === CONTENU ET MÉTHODOLOGIE ===
    contenu_formation = models.TextField(blank=True, default="", verbose_name="Contenu de la formation")
    methodologie_retenue = models.TextField(blank=True, default="", verbose_name="Méthodologie retenue")
    progression_pedagogique = models.TextField(blank=True, default="", verbose_name="Progression pédagogique")

    # === ÉVALUATION ===
    evaluation_diagnostique = models.TextField(blank=True, default="", verbose_name="Évaluation diagnostique")
    evaluation_formative = models.TextField(blank=True, default="", verbose_name="Évaluation formative")
    evaluation_sommative = models.TextField(blank=True, default="", verbose_name="Évaluation sommative")
    evaluation_froide = models.TextField(blank=True, default="", verbose_name="Évaluation à froid (3 mois)")
    mode_evaluation = models.TextField(blank=True, default="", verbose_name="Mode d'évaluation")

    # === MATÉRIEL ET LOGISTIQUE ===
    materiel_requis = models.TextField(blank=True, default="", verbose_name="Matériel requis pour la formation")
    contraintes_logistiques = models.TextField(blank=True, default="", verbose_name="Contraintes logistiques")
    risques_pedagogiques = models.TextField(blank=True, default="", verbose_name="Risques pédagogiques")
    plan_secours = models.TextField(blank=True, default="", verbose_name="Plan de secours")

    # === SUIVI POST-FORMATION ===
    plan_action = models.TextField(blank=True, default="", verbose_name="Plan d'action post-formation")
    modalites_suivi = models.TextField(blank=True, default="", verbose_name="Modalités de suivi")
    ressources_complementaires = models.TextField(blank=True, default="", verbose_name="Ressources complémentaires")

    # === COÛTS ===
    prix_formation = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix de la formation")
    frais_sejour = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais de séjour")
    frais_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais de transport")
    frais_restauration = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais de restauration")
    autres_frais = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Autres frais")
    mode_paiement = models.CharField(max_length=100, blank=True, default="", verbose_name="Mode de paiement")

    # === MÉTADONNÉES ===
    statut = models.CharField(max_length=1, choices=STATUT_PLANIFICATION, default='B')
    date_debut_prevu = models.DateField(null=True, blank=True, verbose_name="Date de début prévue")
    date_fin_prevu = models.DateField(null=True, blank=True, verbose_name="Date de fin prévue")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # ========= VALIDATION ============
    statut = models.CharField(max_length=10, choices=STATUT_PLANIFICATION, default='B')
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planifications_creees')
    valideur_niveau_1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='planifications_validees_n1')
    valideur_niveau_2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='planifications_validees_n2')
    date_soumission = models.DateTimeField(null=True, blank=True)
    date_validation_1 = models.DateTimeField(null=True, blank=True)
    date_validation_2 = models.DateTimeField(null=True, blank=True)
    commentaire_validation = models.TextField(blank=True)

    @property
    def cout_total(self):
        return (self.prix_formation + self.frais_sejour + self.frais_transport + 
                self.frais_restauration + self.autres_frais)
    
    @property
    def formation_nom(self):
        if self.formation_existante:
            return self.formation_existante.intitule
        return self.formation_sur_mesure or self.titre_formation or "Formation personnalisée"
    
    @property
    def nombre_participants(self):
        return self.employes.count()
    
    @property
    def cout_par_participant(self):
        if self.nombre_participants > 0:
            return self.cout_total / self.nombre_participants
        return self.cout_total

    def __str__(self):
        count = self.nombre_participants
        if count == 1:
            return f"{self.formation_nom} - {self.employes.first().nom_complet}"
        elif count > 1:
            return f"{self.formation_nom} - {count} participants"
        return f"{self.formation_nom} - Aucun participant"

class SequenceFormation(models.Model):
    
    
    METHODE_PEDAGOGIQUE = [
        ('EX', 'Exposé interactif'),
        ('AT', 'Atelier pratique'),
        ('CI', 'Classe inversée'),
        ('EC', 'Étude de cas'),
        ('SJ', 'Serious game'),
        ('CO', 'Co-développement'),
        ('JR', 'Jeux de rôle'),
        ('DI', 'Démonstration'),
        ('DD', 'Discussion dirigée'),
    ]
    
    """Séquences pédagogiques détaillées"""
    planification = models.ForeignKey(PlanificationFormation, on_delete=models.CASCADE, related_name='sequences')
    ordre = models.IntegerField(verbose_name="Ordre de la séquence")
    intitule = models.CharField(max_length=200, verbose_name="Intitulé de la séquence")
    duree_heures = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Durée (heures)")
    objectif_sequence = models.TextField(verbose_name="Objectif de la séquence")
    methode_pedagogique = models.CharField(max_length=2, choices=METHODE_PEDAGOGIQUE)
    supports_utilises = models.TextField(verbose_name="Supports utilisés")
    activites_apprenants = models.TextField(verbose_name="Activités des apprenants")
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.ordre}. {self.intitule} ({self.duree_heures}h)"

class CompetenceVisee(models.Model):
    """Compétences spécifiques visées par la formation"""
    planification = models.ForeignKey(PlanificationFormation, on_delete=models.CASCADE, related_name='competences_visees')
    competence = models.ForeignKey('employes.Competence', on_delete=models.CASCADE)
    niveau_visé = models.CharField(max_length=1, choices=[
        ('N', 'Novice'),
        ('I', 'Intermédiaire'),
        ('E', 'Expert'),
    ])
    indicateur_acquisition = models.TextField(verbose_name="Indicateur d'acquisition")
    
    class Meta:
        unique_together = ('planification', 'competence')
    
    def __str__(self):
        return f"{self.competence.nom} ({self.get_niveau_visé_display()})"

class EtapePlanification(models.Model):
    planification = models.ForeignKey(PlanificationFormation, on_delete=models.CASCADE)
    etape = models.IntegerField(choices=[
        (1, 'Informations générales'), 
        (2, 'Qui former'), 
        (3, 'En quoi former'), 
        (4, 'Par qui former'), 
        (5, 'Programme pédagogique'), 
        (6, 'Évaluation et suivi'),
        (7, 'Coût et budget')
    ])
    complete = models.BooleanField(default=False)
    date_completion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('planification', 'etape')