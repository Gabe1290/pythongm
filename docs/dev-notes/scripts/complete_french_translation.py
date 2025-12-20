#!/usr/bin/env python3
"""
Complete French translation - manually add remaining translations
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Complete list of remaining translations
REMAINING_TRANSLATIONS = {
    "You have unsaved changes. Save before building?": "Vous avez des modifications non enregistrées. Enregistrer avant de construire ?",
    "Select Build Output Directory": "Sélectionner le répertoire de sortie",
    "Standalone executable building is not yet implemented.\n\nCurrent workaround:\n• Use 'Export as HTML5' to create a web version\n• Use 'Test Game' to run from source\n\nFuture build targets:\n• Windows .exe\n• Linux binary\n• macOS .app\n• Android .apk\n\nWould you like to export as HTML5 instead?": "La création d'exécutable autonome n'est pas encore implémentée.\n\nSolution de contournement actuelle :\n• Utilisez « Exporter en HTML5 » pour créer une version web\n• Utilisez « Tester le jeu » pour exécuter depuis la source\n\nCibles de construction futures :\n• Windows .exe\n• Binaire Linux\n• macOS .app\n• Android .apk\n\nVoulez-vous exporter en HTML5 à la place ?",
    "Build cancelled - use HTML5 export instead": "Construction annulée - utilisez l'export HTML5 à la place",
    "This will build a standalone executable and run it.\n\nBuilding may take several minutes.\n\nContinue?": "Ceci va construire un exécutable autonome et l'exécuter.\n\nLa construction peut prendre plusieurs minutes.\n\nContinuer ?",
    "Standalone build is not yet implemented.\n\nRunning game in test mode instead...": "La construction autonome n'est pas encore implémentée.\n\nExécution du jeu en mode test à la place...",
    "<h3>Export Game</h3>": "<h3>Exporter le jeu</h3>",
    "Choose export format:": "Choisissez le format d'export :",
    "HTML5 (Web Browser) - ✅ Available": "HTML5 (navigateur web) - ✅ Disponible",
    "Windows Executable (.exe) - ✅ Available": "Exécutable Windows (.exe) - ✅ Disponible",
    "Linux Binary - 🚧 Coming Soon": "Binaire Linux - 🚧 Bientôt disponible",
    "macOS Application (.app) - 🚧 Coming Soon": "Application macOS (.app) - 🚧 Bientôt disponible",
    "Android Package (.apk) - 🚧 Coming Soon": "Package Android (.apk) - 🚧 Bientôt disponible",
    "Coming Soon": "Bientôt disponible",
    "This export format is not yet available.\n\nPlease use HTML5 or Windows EXE export for now.": "Ce format d'export n'est pas encore disponible.\n\nVeuillez utiliser l'export HTML5 ou Windows EXE pour l'instant.",
    "Please open or create a project first.": "Veuillez d'abord ouvrir ou créer un projet.",
    "Choose Export Location": "Choisir l'emplacement d'export",
    "Exporting Game": "Export du jeu",
    "Preparing export...": "Préparation de l'export...",
    "Would you like to open the output folder?": "Voulez-vous ouvrir le dossier de sortie ?",
    "Not Implemented": "Non implémenté",
    "Find functionality is not yet implemented.": "La fonctionnalité de recherche n'est pas encore implémentée.",
    "Find and Replace functionality is not yet implemented.": "La fonctionnalité rechercher et remplacer n'est pas encore implémentée.",
    "Please open a project first to manage assets.": "Veuillez d'abord ouvrir un projet pour gérer les ressources.",
    "Asset Manager is not yet implemented.\n\nCurrent workaround:\nUse the Asset Tree panel on the left to manage sprites, objects, sounds, and rooms.": "Le gestionnaire de ressources n'est pas encore implémenté.\n\nSolution de contournement actuelle :\nUtilisez le panneau Arbre des ressources à gauche pour gérer les sprites, objets, sons et salles.",
    "Please open a project first to validate.": "Veuillez d'abord ouvrir un projet pour valider.",
    "Validation Issues Found": "Problèmes de validation trouvés",
    "Project validation found the following issues:\n\n": "La validation du projet a trouvé les problèmes suivants :\n\n",
    "Validation Passed": "Validation réussie",
    "Project structure is valid!\n\n✓ All required directories exist\n✓ project.json is valid\n✓ No missing dependencies": "La structure du projet est valide !\n\n✓ Tous les répertoires requis existent\n✓ project.json est valide\n✓ Aucune dépendance manquante",
    "Please open a project first to clean.": "Veuillez d'abord ouvrir un projet pour nettoyer.",
    "Project cleanup is not yet implemented.\n\nFuture features:\n• Remove temporary files\n• Clear build cache\n• Reset project settings": "Le nettoyage du projet n'est pas encore implémenté.\n\nFonctionnalités futures :\n• Supprimer les fichiers temporaires\n• Vider le cache de construction\n• Réinitialiser les paramètres du projet",
    "This feature will be available in a future update.\n\nFor now, you can manually delete temporary files from the project directory.": "Cette fonctionnalité sera disponible dans une mise à jour future.\n\nPour l'instant, vous pouvez supprimer manuellement les fichiers temporaires du répertoire du projet.",
    "Documentation is not yet available.\n\nQuick Help:\n• F1: Open this help\n• Ctrl+N: New Project\n• Ctrl+O: Open Project\n• Ctrl+S: Save Project\n• F5: Test Game\n• F6: Debug Game": "La documentation n'est pas encore disponible.\n\nAide rapide :\n• F1 : Ouvrir cette aide\n• Ctrl+N : Nouveau projet\n• Ctrl+O : Ouvrir un projet\n• Ctrl+S : Enregistrer le projet\n• F5 : Tester le jeu\n• F6 : Déboguer le jeu",
    "<h3>PyGameMaker Tutorials</h3>": "<h3>Tutoriels PyGameMaker</h3>",
    "Coming soon! Tutorials will include:": "Bientôt disponible ! Les tutoriels incluront :",
    "\n💡 Tip: Check the documentation (F1) for quick help!": "\n💡 Astuce : Consultez la documentation (F1) pour une aide rapide !",
}

ts_file = Path("translations/pygamemaker_fr.ts")
tree = ET.parse(ts_file)
root = tree.getroot()

updated = 0
for context in root.findall('context'):
    for message in context.findall('message'):
        source = message.find('source')
        translation = message.find('translation')

        if source is None or translation is None:
            continue

        source_text = source.text

        if translation.get('type') == 'unfinished' and source_text in REMAINING_TRANSLATIONS:
            translation.text = REMAINING_TRANSLATIONS[source_text]
            if 'type' in translation.attrib:
                del translation.attrib['type']
            updated += 1
            print(f"✓ {source_text[:60]}...")

tree.write(ts_file, encoding='utf-8', xml_declaration=True)

print(f"\n{'='*60}")
print(f"✓ Updated {updated} final translations!")
print(f"{'='*60}")
print("\nNow compiling to .qm file...")
