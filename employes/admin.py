# employes/admin.py
from django.contrib import admin
from .models import Departement, Employe, Competence, CompetenceEmploye

class EmployeInline(admin.TabularInline):
    model = Employe
    extra = 0
    fields = ['matricule', 'user', 'poste']
    readonly_fields = ['matricule', 'user', 'poste']

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'get_responsable']
    
    def get_responsable(self, obj):
        # Trouver le responsable dans les employés du département
        responsable = Employe.objects.filter(departement=obj, est_responsable=True).first()
        return responsable.user.get_full_name() if responsable else "Aucun"
    get_responsable.short_description = 'Responsable'

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'get_nom_complet', 'departement', 'poste', 'est_responsable']
    list_filter = ['departement', 'est_responsable']
    search_fields = ['user__first_name', 'user__last_name', 'matricule']
    
    def get_nom_complet(self, obj):
        return obj.user.get_full_name()
    get_nom_complet.short_description = 'Nom'

admin.site.register(Competence)
admin.site.register(CompetenceEmploye)