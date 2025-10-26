#!/usr/bin/env python3
"""
Create French translation file for PyGameMaker IDE
This creates a .ts file with French translations
"""

import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent
translations_dir = project_root / "translations"
translations_dir.mkdir(exist_ok=True)

# French translations
french_translations = {
    # Welcome Tab
    "Welcome to PyGameMaker IDE": "Bienvenue dans PyGameMaker IDE",
    "Create amazing 2D games with visual scripting": "Créez des jeux 2D incroyables avec la programmation visuelle",
    "Quick Actions": "Actions rapides",
    "🆕 New Project (Ctrl+N)": "🆕 Nouveau projet (Ctrl+N)",
    "📂 Open Project (Ctrl+O)": "📂 Ouvrir un projet (Ctrl+O)",
    "🏠 Create Room (Ctrl+R)": "🏠 Créer une salle (Ctrl+R)",
    
    # IDE Window - Menus
    "&File": "&Fichier",
    "&New Project...": "&Nouveau projet...",
    "&Open Project...": "&Ouvrir un projet...",
    "&Save Project": "&Enregistrer le projet",
    "Save Project &As...": "Enregistrer le projet &sous...",
    "Recent Projects": "Projets récents",
    "Project &Settings...": "&Paramètres du projet...",
    "E&xit": "&Quitter",
    
    "&Edit": "&Édition",
    "&Undo": "&Annuler",
    "&Redo": "&Rétablir",
    "Cu&t": "&Couper",
    "&Copy": "&Copier",
    "&Paste": "C&oller",
    "&Duplicate": "&Dupliquer",
    "&Find...": "&Rechercher...",
    "Find and &Replace...": "Rechercher et re&mplacer...",
    
    "&Assets": "&Ressources",
    "Import &Sprite...": "Importer un &sprite...",
    "Import &Sound...": "Importer un &son...",
    "Import &Background...": "Importer un &arrière-plan...",
    "Create &Object...": "Créer un &objet...",
    "Create &Room...": "Créer une &salle...",
    "Create S&cript...": "Créer un s&cript...",
    "Create &Font...": "Créer une &police...",
    
    "&Build": "&Construire",
    "&Test Game": "&Tester le jeu",
    "&Debug Game": "&Déboguer le jeu",
    "&Build Game...": "&Construire le jeu...",
    "Build and &Run": "Construire et &exécuter",
    "&Export Game...": "&Exporter le jeu...",
    
    "&Tools": "&Outils",
    "&Preferences...": "&Préférences...",
    "&Asset Manager...": "Gestionnaire de &ressources...",
    "&Validate Project": "&Valider le projet",
    "&Clean Project": "&Nettoyer le projet",
    "🌐 &Language": "🌐 &Langue",
    
    "&Help": "&Aide",
    "&Documentation": "&Documentation",
    "&Tutorials": "&Tutoriels",
    "&About PyGameMaker": "À &propos de PyGameMaker",
    "About &Qt": "À propos de &Qt",
    
    # Status messages
    "Ready": "Prêt",
    "No project loaded": "Aucun projet chargé",
    "Project created successfully": "Projet créé avec succès",
    "Project saved": "Projet enregistré",
    "Project loaded: {0}": "Projet chargé : {0}",
    "Imported {0}": "Importé {0}",
    "Created {0}": "Créé {0}",
    "Opened room: {0}": "Salle ouverte : {0}",
    "Opened object: {0}": "Objet ouvert : {0}",
    "Saved: {0}": "Enregistré : {0}",
    
    # Dialogs
    "Language Changed": "Langue modifiée",
    "Language changed to {0}.\n\nPlease restart PyGameMaker IDE for the changes to take full effect.": 
        "Langue changée en {0}.\n\nVeuillez redémarrer PyGameMaker IDE pour que les changements prennent effet.",
    "Translation Not Available": "Traduction non disponible",
    "Translation file for {0} is not available.\n\nThe language has been set, but the interface will remain in English until a translation file is provided.\n\nExpected file: translations/pygamemaker_{1}.qm":
        "Le fichier de traduction pour {0} n'est pas disponible.\n\nLa langue a été définie, mais l'interface restera en anglais jusqu'à ce qu'un fichier de traduction soit fourni.\n\nFichier attendu : translations/pygamemaker_{1}.qm",
    
    "Error": "Erreur",
    "Failed to create project": "Échec de la création du projet",
    "Failed to load project": "Échec du chargement du projet",
    "Failed to save project": "Échec de l'enregistrement du projet",
    "Save Error": "Erreur d'enregistrement",
    "Failed to save project to disk": "Échec de l'enregistrement du projet sur le disque",
    "Failed to save {0}: {1}": "Échec de l'enregistrement de {0} : {1}",
    
    "No Project": "Aucun projet",
    "Please open a project first": "Veuillez d'abord ouvrir un projet",
    "No Project Loaded": "Aucun projet chargé",
    "You need to create or open a project before importing sprites.\n\nWould you like to create a new project now?":
        "Vous devez créer ou ouvrir un projet avant d'importer des sprites.\n\nVoulez-vous créer un nouveau projet maintenant ?",
    
    "Unsaved Changes": "Modifications non enregistrées",
    '"{0}" has unsaved changes. Save before closing?': '"{0}" contient des modifications non enregistrées. Enregistrer avant de fermer ?',
    "You have unsaved changes. Do you want to save before closing?": "Vous avez des modifications non enregistrées. Voulez-vous enregistrer avant de fermer ?",
    
    "Game Running": "Jeu en cours",
    "A game is already running. Stop it?": "Un jeu est déjà en cours d'exécution. L'arrêter ?",
    "Game Error": "Erreur de jeu",
    "Failed to start the game. Check console for details.": "Échec du démarrage du jeu. Vérifiez la console pour plus de détails.",
    
    # Project Dialog
    "New Project": "Nouveau projet",
    "Project Details": "Détails du projet",
    "Project Name:": "Nom du projet :",
    "Enter project name...": "Entrez le nom du projet...",
    "Location:": "Emplacement :",
    "Choose project location...": "Choisissez l'emplacement du projet...",
    "Browse...": "Parcourir...",
    "Description:": "Description :",
    "Optional project description...": "Description facultative du projet...",
    "Invalid Input": "Entrée invalide",
    "Please enter a project name.": "Veuillez entrer un nom de projet.",
    "Please choose a project location.": "Veuillez choisir un emplacement pour le projet.",
    
    # Project Settings
    "Project Settings": "Paramètres du projet",
    "Project Information": "Informations du projet",
    "Project Path:": "Chemin du projet :",
    "Settings": "Paramètres",
    "Auto-save:": "Enregistrement automatique :",
    "Target Platform:": "Plateforme cible :",
    "Desktop": "Bureau",
    "Web": "Web",
    "Mobile": "Mobile",
}

# Create .ts XML file
ts_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr_FR">
'''

# Group by context
contexts = {
    "WelcomeTab": [],
    "PyGameMakerIDE": [],
    "NewProjectDialog": [],
    "ProjectSettingsDialog": []
}

# Categorize translations
for english, french in french_translations.items():
    # Determine context based on content
    if any(x in english for x in ["Welcome", "Quick Actions", "Create amazing"]):
        context = "WelcomeTab"
    elif any(x in english for x in ["New Project", "Project Name", "Location:", "Browse"]):
        context = "NewProjectDialog"
    elif "Project Settings" in english or "Target Platform" in english:
        context = "ProjectSettingsDialog"
    else:
        context = "PyGameMakerIDE"
    
    contexts[context].append((english, french))

# Build XML
for context_name, messages in contexts.items():
    if not messages:
        continue
    
    ts_content += f'<context>\n    <name>{context_name}</name>\n'
    
    for english, french in messages:
        # Escape XML special characters
        english_escaped = english.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        french_escaped = french.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        ts_content += f'''    <message>
        <source>{english_escaped}</source>
        <translation>{french_escaped}</translation>
    </message>
'''
    
    ts_content += '</context>\n'

ts_content += '</TS>\n'

# Write .ts file
ts_file = translations_dir / "pygamemaker_fr.ts"
with open(ts_file, 'w', encoding='utf-8') as f:
    f.write(ts_content)

print(f"✅ Created translation file: {ts_file}")
print(f"\nTo compile:")
print(f"  lrelease {ts_file}")
print(f"\nOr run:")
print(f"  python scripts/compile_translations.py")