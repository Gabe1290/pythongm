#!/usr/bin/env python3
"""Add missing French translations to pygamemaker_fr.ts"""

import xml.etree.ElementTree as ET
from pathlib import Path

# French translations for missing strings
TRANSLATIONS = {
    # Dialog strings missing from translation file
    "No Selection": "Aucune sélection",
    "Please select a key first.": "Veuillez d'abord sélectionner une touche.",
    "Please select a mouse event first.": "Veuillez d'abord sélectionner un événement de souris.",
    "Search:": "Rechercher :",
    "Select Key": "Sélectionner une touche",
    "Select Mouse Event": "Sélectionner un événement de souris",
    "Select which key to respond to:": "Sélectionnez la touche à laquelle répondre :",
    "Select which mouse event to respond to:": "Sélectionnez l'événement de souris auquel répondre :",
    "Settings have been saved successfully.\n\n": "Les paramètres ont été enregistrés avec succès.\n\n",
    "Type to filter events...": "Tapez pour filtrer les événements...",
    "Type to filter keys...": "Tapez pour filtrer les touches...",

    # Unfinished multi-line translations
    """Asset Manager is not yet implemented.

Current workaround:
Use the Asset Tree panel on the left to manage your assets.

Future features:
• Bulk asset operations
• Asset search and filter
• Asset usage tracking
• Unused asset cleanup""": """Le gestionnaire de ressources n'est pas encore implémenté.

Solution de contournement actuelle :
Utilisez le panneau Arbre des ressources à gauche pour gérer vos ressources.

Fonctionnalités futures :
• Opérations groupées sur les ressources
• Recherche et filtrage des ressources
• Suivi de l'utilisation des ressources
• Nettoyage des ressources inutilisées""",

    """Project structure is valid!

✓ All required directories exist
✓ project.json is present""": """La structure du projet est valide !

✓ Tous les répertoires requis existent
✓ project.json est présent""",

    """Project cleanup is not yet implemented.

Future features:
• Remove temporary files
• Delete unused assets
• Clean build artifacts
• Optimize project size

Would you like to learn more?""": """Le nettoyage du projet n'est pas encore implémenté.

Fonctionnalités futures :
• Supprimer les fichiers temporaires
• Supprimer les ressources inutilisées
• Nettoyer les artefacts de compilation
• Optimiser la taille du projet

Souhaitez-vous en savoir plus ?""",

    """This feature will be available in a future update.

For now, you can manually delete temporary files from:
• .cache/ directory
• __pycache__/ directories
• *.pyc files""": """Cette fonctionnalité sera disponible dans une future mise à jour.

Pour l'instant, vous pouvez supprimer manuellement les fichiers temporaires de :
• Répertoire .cache/
• Répertoires __pycache__/
• Fichiers *.pyc""",

    """Documentation is not yet available.

Quick Help:
• F1: Open this help
• Ctrl+N: New Project
• Ctrl+O: Open Project
• Ctrl+S: Save Project
• Double-click assets to edit them
• Right-click for more options

Online documentation coming soon!""": """La documentation n'est pas encore disponible.

Aide rapide :
• F1 : Ouvrir cette aide
• Ctrl+N : Nouveau projet
• Ctrl+O : Ouvrir un projet
• Ctrl+S : Enregistrer le projet
• Double-cliquez sur les ressources pour les modifier
• Clic droit pour plus d'options

Documentation en ligne bientôt disponible !"""
}

# Parse the translation file
tree = ET.parse('translations/pygamemaker_fr.ts')
root = tree.getroot()

# Track what we update
updated_count = 0
added_count = 0

# Find contexts and update/add translations
for source_text, french_text in TRANSLATIONS.items():
    found = False

    # Search for existing message in all contexts
    for context in root.findall('.//context'):
        for message in context.findall('.//message'):
            source = message.find('source')
            if source is not None and source.text == source_text:
                # Found existing message - update translation
                translation = message.find('translation')
                if translation is not None:
                    translation.text = french_text
                    # Remove 'type="unfinished"' attribute if present
                    if 'type' in translation.attrib:
                        del translation.attrib['type']
                    updated_count += 1
                    found = True
                    print(f"✓ Updated: {source_text[:50]}...")
                    break
        if found:
            break

    if not found:
        # Need to add new message - find appropriate context
        # For dialog strings, use context based on source
        if any(keyword in source_text.lower() for keyword in ['key', 'mouse event', 'select']):
            context_name = 'KeyMouseSelectors'
        elif 'settings' in source_text.lower():
            context_name = 'PreferencesDialog'
        else:
            context_name = 'PyGameMakerIDE'

        # Find or create context
        target_context = None
        for context in root.findall('.//context'):
            name_elem = context.find('name')
            if name_elem is not None and name_elem.text == context_name:
                target_context = context
                break

        if target_context is None:
            # Create new context
            target_context = ET.SubElement(root, 'context')
            name_elem = ET.SubElement(target_context, 'name')
            name_elem.text = context_name

        # Add new message
        message = ET.SubElement(target_context, 'message')
        source_elem = ET.SubElement(message, 'source')
        source_elem.text = source_text
        translation_elem = ET.SubElement(message, 'translation')
        translation_elem.text = french_text
        added_count += 1
        print(f"+ Added: {source_text[:50]}...")

# Write updated file
tree.write('translations/pygamemaker_fr.ts', encoding='utf-8', xml_declaration=True)

print(f"\n{'='*60}")
print(f"Translation update complete!")
print(f"{'='*60}")
print(f"✓ Updated: {updated_count} existing translations")
print(f"+ Added: {added_count} new translations")
print(f"{'='*60}")
print(f"\nNext step: Compile with pyside6-lrelease")
