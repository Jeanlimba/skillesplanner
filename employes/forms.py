# employes/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Employe, Departement, Competence, CompetenceEmploye

class EmployeForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = Employe
        fields = ['matricule', 'departement', 'poste', 'date_embauche', 'manager', 'est_responsable']
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        employe = super().save(commit=False)
        
        if employe.user:
            user = employe.user
        else:
            user = User()
        
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            employe.user = user
            employe.save()
        
        return employe

class CompetenceEmployeForm(forms.ModelForm):
    class Meta:
        model = CompetenceEmploye
        fields = ['competence', 'niveau', 'date_validation', 'valide_par']
        widgets = {
            'date_validation': forms.DateInput(attrs={'type': 'date'}),
        }

class EmployeFormSimple(forms.ModelForm):
    """Formulaire simplifié pour la création rapide"""
    nom = forms.CharField(max_length=150, required=True, label="Nom")
    prenom = forms.CharField(max_length=150, required=True, label="Prénom")
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Employe
        fields = ['matricule', 'poste']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matricule'].required = True
        self.fields['poste'].required = True