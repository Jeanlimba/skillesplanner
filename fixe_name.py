# fix_project_name.py
import os
import re

OLD_NAME = "chirpa_formation"
NEW_NAME = "chirpa_planing"

def replace_in_file(filepath):
    """Remplace l'ancien nom par le nouveau dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace(OLD_NAME, NEW_NAME)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Corrigé : {filepath}")
    except Exception as e:
        print(f"✗ Erreur avec {filepath}: {e}")

# Fichiers à corriger
files_to_fix = [
    'manage.py',
    f'{NEW_NAME}/wsgi.py',
    f'{NEW_NAME}/asgi.py', 
    f'{NEW_NAME}/settings.py',
    f'{NEW_NAME}/urls.py',
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        replace_in_file(filepath)
    else:
        print(f"⚠ Fichier non trouvé : {filepath}")

print("Correction terminée!")