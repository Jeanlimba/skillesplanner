# Créer un fichier check_compatibility.py
import sys
print(f"Python version: {sys.version}")

# Vérifications Django
try:
    import django
    print(f"Django version: {django.get_version()}")
    print("✓ Django fonctionne correctement")
except Exception as e:
    print(f"✗ Problème avec Django: {e}")