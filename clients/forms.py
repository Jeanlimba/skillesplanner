# clients/forms.py
from django import forms
from .models import Client, ProfilUtilisateur
from django.contrib.auth.models import User

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'sigle', 'contact', 'email', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'sigle': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UtilisateurClientForm(forms.Form):
    nom = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    prenom = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        min_length=8, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Minimum 8 caractères"
    )
    telephone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
        choices=[
            ('SAISIE', 'Saisie'),
            ('VALIDATION_1', 'Validation Niveau 1'),
            ('VALIDATION_2', 'Validation Niveau 2'),
            ('ADMIN_CLIENT', 'Administrateur Client'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )