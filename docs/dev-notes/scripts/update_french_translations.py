#!/usr/bin/env python3
"""
Update French translations in pygamemaker_fr.ts file
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Comprehensive French translations
TRANSLATIONS = {
    # PreferencesDialog
    "Preferences": "Préférences",
    "Note: Some settings require restarting the IDE to take effect.": "Note : Certains paramètres nécessitent le redémarrage de l'IDE pour prendre effet.",
    "Font Settings": "Paramètres de police",
    "Font Size:": "Taille de police :",
    "System Default": "Système par défaut",
    "Font Family:": "Famille de police :",
    "Preview: The quick brown fox jumps over the lazy dog": "Aperçu : Portez ce vieux whisky au juge blond qui fume",
    "Preview:": "Aperçu :",
    "Theme Settings": "Paramètres de thème",
    "Theme:": "Thème :",
    "UI Scale:": "Échelle de l'interface :",
    "Show tooltips": "Afficher les infobulles",
    "Appearance": "Apparence",
    "Auto-Save Settings": "Paramètres d'enregistrement automatique",
    "Enable auto-save": "Activer l'enregistrement automatique",
    " minutes": " minutes",
    "Auto-save interval:": "Intervalle d'enregistrement automatique :",
    "Grid & Snapping": "Grille et alignement",
    "Show grid in editors": "Afficher la grille dans les éditeurs",
    "Grid size:": "Taille de la grille :",
    "Snap to grid": "Aligner sur la grille",
    "Show collision boxes": "Afficher les boîtes de collision",
    "Editor": "Éditeur",
    "Project Paths": "Chemins du projet",
    "Browse...": "Parcourir...",
    "Default projects folder:": "Dossier de projets par défaut :",
    "Project Settings": "Paramètres du projet",
    "Recent projects limit:": "Limite de projets récents :",
    "Create backup on save": "Créer une sauvegarde lors de l'enregistrement",
    "Project": "Projet",

    # Export options
    "Export to Kivy...": "Exporter vers Kivy...",
    "Export Project...": "Exporter le projet...",
    "Select Export Format": "Sélectionner le format d'export",
    "Exporting to Kivy...": "Exportation vers Kivy...",
    "Kivy export complete": "Exportation Kivy terminée",
    "Game exported to Kivy!": "Jeu exporté vers Kivy !",
    "Failed to export to Kivy": "Échec de l'exportation vers Kivy",
    "Kivy Export": "Export Kivy",

    # Object Editor Components
    "Object Name:": "Nom de l'objet :",
    "Sprite Name:": "Nom du sprite :",
    "Parent Object:": "Objet parent :",
    "Depth:": "Profondeur :",
    "Visible": "Visible",
    "Solid": "Solide",
    "Persistent": "Persistant",
    "Uses Physics": "Utilise la physique",
    "Object Properties": "Propriétés de l'objet",
    "Events": "Événements",
    "Actions": "Actions",
    "Add Event": "Ajouter un événement",
    "Remove Event": "Supprimer l'événement",
    "Edit Event": "Modifier l'événement",
    "Duplicate Event": "Dupliquer l'événement",

    # Event types
    "Create": "Création",
    "Destroy": "Destruction",
    "Step": "Étape",
    "Alarm": "Alarme",
    "Keyboard": "Clavier",
    "Mouse": "Souris",
    "Collision": "Collision",
    "Draw": "Dessin",
    "Other": "Autre",
    "Begin Step": "Début d'étape",
    "End Step": "Fin d'étape",

    # Actions
    "Movement": "Mouvement",
    "Main Actions": "Actions principales",
    "Control": "Contrôle",
    "Questions": "Questions",
    "Code": "Code",
    "Instance": "Instance",
    "Drawing": "Dessin",
    "Score": "Score",
    "Game": "Jeu",
    "Resources": "Ressources",

    # Room Editor
    "Room Editor": "Éditeur de salle",
    "Room Name:": "Nom de la salle :",
    "Room Width:": "Largeur de la salle :",
    "Room Height:": "Hauteur de la salle :",
    "Grid Size:": "Taille de la grille :",
    "Show Grid": "Afficher la grille",
    "Snap to Grid": "Aligner sur la grille",
    "Background Color:": "Couleur d'arrière-plan :",
    "Background Image:": "Image d'arrière-plan :",
    "Instances": "Instances",
    "Layers": "Calques",
    "Tiles": "Tuiles",
    "Settings": "Paramètres",
    "Room Speed:": "Vitesse de la salle :",
    "Caption:": "Titre :",

    # Asset Tree
    "Sprites": "Sprites",
    "Sounds": "Sons",
    "Objects": "Objets",
    "Rooms": "Salles",
    "Scripts": "Scripts",
    "Fonts": "Polices",
    "Backgrounds": "Arrière-plans",
    "Paths": "Chemins",
    "Time Lines": "Lignes temporelles",
    "Include Files": "Fichiers inclus",
    "Extensions": "Extensions",
    "Add": "Ajouter",
    "Delete": "Supprimer",
    "Rename": "Renommer",
    "Duplicate": "Dupliquer",
    "Properties": "Propriétés",

    # Common UI
    "OK": "OK",
    "Cancel": "Annuler",
    "Apply": "Appliquer",
    "Close": "Fermer",
    "Yes": "Oui",
    "No": "Non",
    "Save": "Enregistrer",
    "Don't Save": "Ne pas enregistrer",
    "Select": "Sélectionner",
    "Select All": "Tout sélectionner",
    "Deselect All": "Tout désélectionner",
    "None": "Aucun",
    "All": "Tout",
    "Name:": "Nom :",
    "Description:": "Description :",
    "Type:": "Type :",
    "Value:": "Valeur :",

    # File operations
    "New": "Nouveau",
    "Open": "Ouvrir",
    "Save": "Enregistrer",
    "Save As...": "Enregistrer sous...",
    "Import": "Importer",
    "Export": "Exporter",
    "Recent Files": "Fichiers récents",
    "Clear Recent": "Effacer les récents",

    # Status messages
    "Ready": "Prêt",
    "Loading...": "Chargement...",
    "Saving...": "Enregistrement...",
    "Done": "Terminé",
    "Failed": "Échoué",
    "Success": "Succès",
    "Error": "Erreur",
    "Warning": "Avertissement",
    "Information": "Information",
    "Confirmation": "Confirmation",

    # Dialogs
    "Are you sure?": "Êtes-vous sûr ?",
    "This action cannot be undone.": "Cette action ne peut pas être annulée.",
    "Do you want to save changes?": "Voulez-vous enregistrer les modifications ?",
    "File already exists. Overwrite?": "Le fichier existe déjà. Écraser ?",

    # Game running
    "Test Game": "Tester le jeu",
    "Debug Game": "Déboguer le jeu",
    "Stop Game": "Arrêter le jeu",
    "Game is running": "Le jeu est en cours d'exécution",
    "Starting game...": "Démarrage du jeu...",
    "Stopping game...": "Arrêt du jeu...",

    # Build and Export
    "Build Game": "Construire le jeu",
    "Build and Run": "Construire et exécuter",
    "Export Game": "Exporter le jeu",
    "Clean Build": "Nettoyer la construction",
    "Rebuild All": "Tout reconstruire",

    # Help
    "Documentation": "Documentation",
    "Tutorials": "Tutoriels",
    "About": "À propos",
    "Check for Updates": "Vérifier les mises à jour",
    "Report Bug": "Signaler un bug",
    "Community": "Communauté",

    # Preferences categories
    "General": "Général",
    "Appearance": "Apparence",
    "Editor": "Éditeur",
    "Project": "Projet",
    "Advanced": "Avancé",

    # Window titles
    "PyGameMaker IDE": "PyGameMaker IDE",
    "Project Manager": "Gestionnaire de projet",
    "Asset Manager": "Gestionnaire de ressources",
    "Code Editor": "Éditeur de code",
    "Resource Editor": "Éditeur de ressources",

    # Additional PreferencesDialog strings
    "Debug Settings": "Paramètres de débogage",
    "Enable debug mode": "Activer le mode débogage",
    "Show console output": "Afficher la sortie console",
    "Performance": "Performance",
    "Maximum undo steps:": "Nombre maximal d'annulations :",
    "Select Default Projects Directory": "Sélectionner le répertoire des projets par défaut",
    "Settings Saved": "Paramètres enregistrés",
    "Settings have been saved successfully.\n\nSome changes may require restarting the IDE to take effect.": "Les paramètres ont été enregistrés avec succès.\n\nCertaines modifications peuvent nécessiter le redémarrage de l'IDE pour prendre effet.",

    # Game running messages
    "Running game...": "Exécution du jeu...",
    "Project Error": "Erreur de projet",
    "project.json not found in project directory": "project.json introuvable dans le répertoire du projet",
    "Game closed": "Jeu fermé",
    "Game Test Error": "Erreur de test du jeu",
    "Failed to run game:\n\n{0}\n\nCheck console for details.": "Échec de l'exécution du jeu :\n\n{0}\n\nConsultez la console pour plus de détails.",
    "Game test failed": "Échec du test du jeu",
    "A game is already running. Please stop it first.": "Un jeu est déjà en cours d'exécution. Veuillez d'abord l'arrêter.",
    "Starting game in debug mode...": "Démarrage du jeu en mode débogage...",
    "Debug Mode": "Mode débogage",
    "Debug mode will start the game with verbose console output.\n\nFuture features:\n• Breakpoints\n• Variable inspection\n• Step-through execution\n• Performance profiling\n\nFor now, check the console for debug messages.": "Le mode débogage démarre le jeu avec une sortie console détaillée.\n\nFonctionnalités futures :\n• Points d'arrêt\n• Inspection des variables\n• Exécution pas à pas\n• Profilage de performance\n\nPour l'instant, vérifiez la console pour les messages de débogage.",
    "Game started in debug mode - Check console for debug output": "Jeu démarré en mode débogage - Consultez la console pour les messages de débogage",

    # Export dialogs
    "Select Export Format": "Sélectionner le format d'export",
    "Choose the format to export your game:": "Choisissez le format pour exporter votre jeu :",
    "HTML5 (Web Browser)": "HTML5 (navigateur web)",
    "Kivy (Mobile/Desktop)": "Kivy (mobile/bureau)",
    "Executable (Standalone)": "Exécutable (autonome)",
    "Android APK": "APK Android",
    "iOS IPA": "IPA iOS",
    "Export Location": "Emplacement d'export",
    "Select Export Location": "Sélectionner l'emplacement d'export",
    "Exporting...": "Exportation...",
    "Export Complete": "Export terminé",
    "Export Cancelled": "Export annulé",
    "Open export folder": "Ouvrir le dossier d'export",
    "Your game has been exported to:\n{0}": "Votre jeu a été exporté vers :\n{0}",

    # Asset dialogs
    "Create New Sprite": "Créer un nouveau sprite",
    "Create New Object": "Créer un nouvel objet",
    "Create New Room": "Créer une nouvelle salle",
    "Create New Script": "Créer un nouveau script",
    "Create New Sound": "Créer un nouveau son",
    "Create New Font": "Créer une nouvelle police",
    "Enter name:": "Entrez le nom :",
    "Asset name cannot be empty": "Le nom de la ressource ne peut pas être vide",
    "Asset name already exists": "Le nom de la ressource existe déjà",
    "Invalid asset name": "Nom de ressource invalide",
    "Asset name can only contain letters, numbers, and underscores": "Le nom de la ressource ne peut contenir que des lettres, chiffres et traits de soulignement",

    # Delete confirmations
    "Delete Asset": "Supprimer la ressource",
    "Are you sure you want to delete '{0}'?": "Êtes-vous sûr de vouloir supprimer « {0} » ?",
    "This will delete the asset and cannot be undone.": "Cela supprimera la ressource et ne peut pas être annulé.",
    "Delete Room": "Supprimer la salle",
    "Delete Object": "Supprimer l'objet",
    "Delete Sprite": "Supprimer le sprite",
    "Delete Sound": "Supprimer le son",
    "Delete Script": "Supprimer le script",
    "Delete Font": "Supprimer la police",

    # Validation
    "Validate Project": "Valider le projet",
    "Validating project...": "Validation du projet...",
    "Project Validation": "Validation du projet",
    "Project is valid": "Le projet est valide",
    "Validation complete. No errors found.": "Validation terminée. Aucune erreur trouvée.",
    "Validation Errors": "Erreurs de validation",
    "The following errors were found:": "Les erreurs suivantes ont été trouvées :",
    "Warnings": "Avertissements",
    "The following warnings were found:": "Les avertissements suivants ont été trouvés :",

    # Clean project
    "Clean Project": "Nettoyer le projet",
    "Cleaning project...": "Nettoyage du projet...",
    "Project cleaned": "Projet nettoyé",
    "Project has been cleaned successfully.": "Le projet a été nettoyé avec succès.",
    "Clean Failed": "Échec du nettoyage",
    "Failed to clean project.": "Échec du nettoyage du projet.",

    # About dialog
    "About PyGameMaker": "À propos de PyGameMaker",
    "Version": "Version",
    "A game development IDE inspired by GameMaker": "Un IDE de développement de jeux inspiré de GameMaker",
    "License": "Licence",
    "Contributors": "Contributeurs",
    "Third-Party Libraries": "Bibliothèques tierces",

    # Update notifications
    "Update Available": "Mise à jour disponible",
    "A new version is available": "Une nouvelle version est disponible",
    "Download": "Télécharger",
    "Remind me later": "Me le rappeler plus tard",
    "Skip this version": "Ignorer cette version",
    "Checking for updates...": "Vérification des mises à jour...",
    "You are using the latest version": "Vous utilisez la dernière version",
    "No updates available": "Aucune mise à jour disponible",

    # Miscellaneous
    "Loading project...": "Chargement du projet...",
    "Saving project...": "Enregistrement du projet...",
    "Creating new project...": "Création d'un nouveau projet...",
    "Opening file...": "Ouverture du fichier...",
    "Importing asset...": "Importation de la ressource...",
    "Please wait...": "Veuillez patienter...",
    "Processing...": "Traitement en cours...",
    "Calculating...": "Calcul en cours...",
    "Compiling...": "Compilation...",
    "Optimizing...": "Optimisation...",
    "Finishing...": "Finalisation...",
}


def update_translations():
    """Update the French translation file with new translations"""

    ts_file = Path("translations/pygamemaker_fr.ts")

    if not ts_file.exists():
        print(f"Error: {ts_file} not found!")
        return False

    # Parse the XML file
    try:
        tree = ET.parse(ts_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return False

    # Track statistics
    updated = 0
    not_found = []

    # Update translations
    for context in root.findall('context'):
        context_name = context.find('name').text

        for message in context.findall('message'):
            source = message.find('source')
            translation = message.find('translation')

            if source is None or translation is None:
                continue

            source_text = source.text

            # Skip if already translated
            if translation.get('type') != 'unfinished':
                continue

            # Check if we have a translation
            if source_text in TRANSLATIONS:
                # Update the translation
                translation.text = TRANSLATIONS[source_text]
                # Remove the 'type' attribute to mark as finished
                if 'type' in translation.attrib:
                    del translation.attrib['type']
                updated += 1
                print(f"✓ [{context_name}] {source_text[:50]}...")
            else:
                not_found.append((context_name, source_text))

    # Save the updated file
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    print(f"\n{'='*60}")
    print(f"Translation Update Complete")
    print(f"{'='*60}")
    print(f"✓ Updated: {updated} translations")
    print(f"⚠ Not found: {len(not_found)} translations")

    if not_found:
        print(f"\nStrings that still need translation:")
        for ctx, src in not_found[:20]:  # Show first 20
            print(f"  [{ctx}] {src}")
        if len(not_found) > 20:
            print(f"  ... and {len(not_found) - 20} more")

    return True


if __name__ == "__main__":
    success = update_translations()
    if success:
        print("\n✓ Translation file updated successfully!")
        print("\nNext steps:")
        print("1. Run: lrelease-qt6 translations/pygamemaker_fr.ts")
        print("2. This will compile the .qm file for use in the IDE")
    else:
        print("\n✗ Translation update failed")

# Add final batch of translations
FINAL_TRANSLATIONS = {
    # Build and export messages
    "You have unsaved changes. Save before building?": "Vous avez des modifications non enregistrées. Enregistrer avant de construire ?",
    "Select Build Output Directory": "Sélectionner le répertoire de sortie",
    "Standalone executable building is not yet implemented.\n\nCurrent workaround:\n• Use 'Export as HTML5' to create a web version\n• Use 'Test Game' to run from source\n\nFuture build targets:\n• Windows .exe\n• Linux binary\n• macOS .app\n• Android .apk\n\nWould you like to export as HTML5 instead?": "La création d'exécutable autonome n'est pas encore implémentée.\n\nSolution de contournement actuelle :\n• Utilisez « Exporter en HTML5 » pour créer une version web\n• Utilisez « Tester le jeu » pour exécuter depuis la source\n\nCibles de construction futures :\n• Windows .exe\n• Binaire Linux\n• macOS .app\n• Android .apk\n\nVoulez-vous exporter en HTML5 à la place ?",
    "Build cancelled - use HTML5 export instead": "Construction annulée - utilisez l'export HTML5 à la place",
    "This will build a standalone executable and run it.\n\nBuilding may take several minutes.\n\nContinue?": "Ceci va construire un exécutable autonome et l'exécuter.\n\nLa construction peut prendre plusieurs minutes.\n\nContinuer ?",
    "Standalone build is not yet implemented.\n\nRunning game in test mode instead...": "La construction autonome n'est pas encore implémentée.\n\nExécution du jeu en mode test à la place...",

    # Export dialog HTML
    "<h3>Export Game</h3>": "<h3>Exporter le jeu</h3>",
    "Choose export format:": "Choisissez le format d'export :",
    "HTML5 (Web Browser) - ✅ Available": "HTML5 (navigateur web) - ✅ Disponible",
    "Windows Executable (.exe) - ✅ Available": "Exécutable Windows (.exe) - ✅ Disponible",
    "Linux Binary - 🚧 Coming Soon": "Binaire Linux - 🚧 Bientôt disponible",
    "macOS Application (.app) - 🚧 Coming Soon": "Application macOS (.app) - 🚧 Bientôt disponible",
    "Android Package (.apk) - 🚧 Coming Soon": "Package Android (.apk) - 🚧 Bientôt disponible",
    "Coming Soon": "Bientôt disponible",
    "This export format is not yet available.\n\nPlease use HTML5 or Windows EXE export for now.": "Ce format d'export n'est pas encore disponible.\n\nVeuillez utiliser l'export HTML5 ou Windows EXE pour l'instant.",
    
    # Project messages
    "Please open or create a project first.": "Veuillez d'abord ouvrir ou créer un projet.",
    "Choose Export Location": "Choisir l'emplacement d'export",
    "Exporting Game": "Export du jeu",
    "Preparing export...": "Préparation de l'export...",
    "Would you like to open the output folder?": "Voulez-vous ouvrir le dossier de sortie ?",

    # Not implemented features
    "Not Implemented": "Non implémenté",
    "Find functionality is not yet implemented.": "La fonctionnalité de recherche n'est pas encore implémentée.",
    "Find and Replace functionality is not yet implemented.": "La fonctionnalité rechercher et remplacer n'est pas encore implémentée.",
    "Please open a project first to manage assets.": "Veuillez d'abord ouvrir un projet pour gérer les ressources.",
    "Asset Manager is not yet implemented.\n\nCurrent workaround:\nUse the Asset Tree panel on the left to manage sprites, objects, sounds, and rooms.": "Le gestionnaire de ressources n'est pas encore implémenté.\n\nSolution de contournement actuelle :\nUtilisez le panneau Arbre des ressources à gauche pour gérer les sprites, objets, sons et salles.",

    # Validation messages
    "Please open a project first to validate.": "Veuillez d'abord ouvrir un projet pour valider.",
    "Validation Issues Found": "Problèmes de validation trouvés",
    "Project validation found the following issues:\n\n": "La validation du projet a trouvé les problèmes suivants :\n\n",
    "Validation Passed": "Validation réussie",
    "Project structure is valid!\n\n✓ All required directories exist\n✓ project.json is valid\n✓ No missing dependencies": "La structure du projet est valide !\n\n✓ Tous les répertoires requis existent\n✓ project.json est valide\n✓ Aucune dépendance manquante",

    # Clean project messages
    "Please open a project first to clean.": "Veuillez d'abord ouvrir un projet pour nettoyer.",
    "Project cleanup is not yet implemented.\n\nFuture features:\n• Remove temporary files\n• Clear build cache\n• Reset project settings": "Le nettoyage du projet n'est pas encore implémenté.\n\nFonctionnalités futures :\n• Supprimer les fichiers temporaires\n• Vider le cache de construction\n• Réinitialiser les paramètres du projet",
    
    # Feature not available
    "This feature will be available in a future update.\n\nFor now, you can manually delete temporary files from the project directory.": "Cette fonctionnalité sera disponible dans une mise à jour future.\n\nPour l'instant, vous pouvez supprimer manuellement les fichiers temporaires du répertoire du projet.",
    
    # Documentation and tutorials
    "Documentation is not yet available.\n\nQuick Help:\n• F1: Open this help\n• Ctrl+N: New Project\n• Ctrl+O: Open Project\n• Ctrl+S: Save Project\n• F5: Test Game\n• F6: Debug Game": "La documentation n'est pas encore disponible.\n\nAide rapide :\n• F1 : Ouvrir cette aide\n• Ctrl+N : Nouveau projet\n• Ctrl+O : Ouvrir un projet\n• Ctrl+S : Enregistrer le projet\n• F5 : Tester le jeu\n• F6 : Déboguer le jeu",
    "<h3>PyGameMaker Tutorials</h3>": "<h3>Tutoriels PyGameMaker</h3>",
    "Coming soon! Tutorials will include:": "Bientôt disponible ! Les tutoriels incluront :",
    "\n💡 Tip: Check the documentation (F1) for quick help!": "\n💡 Astuce : Consultez la documentation (F1) pour une aide rapide !",
}

# Merge with main translations
TRANSLATIONS.update(FINAL_TRANSLATIONS)
