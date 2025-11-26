#!/usr/bin/env python3
"""Add missing Italian translations to pygamemaker_it.ts"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Italian translations for missing strings
TRANSLATIONS = {
    # Dialog strings missing from translation file
    "No Selection": "Nessuna selezione",
    "Please select a key first.": "Seleziona prima un tasto.",
    "Please select a mouse event first.": "Seleziona prima un evento del mouse.",
    "Search:": "Cerca:",
    "Select Key": "Seleziona tasto",
    "Select Mouse Event": "Seleziona evento del mouse",
    "Select which key to respond to:": "Seleziona il tasto a cui rispondere:",
    "Select which mouse event to respond to:": "Seleziona l'evento del mouse a cui rispondere:",
    "Settings have been saved successfully.\n\n": "Le impostazioni sono state salvate con successo.\n\n",
    "Type to filter events...": "Digita per filtrare gli eventi...",
    "Type to filter keys...": "Digita per filtrare i tasti...",

    # Unfinished translations
    "Failed to load": "Caricamento non riuscito",
    "Failed to create {0}: {1}": "Impossibile creare {0}: {1}",
}

# Parse the translation file
tree = ET.parse('translations/pygamemaker_it.ts')
root = tree.getroot()

# Track what we update
updated_count = 0
added_count = 0

# Find contexts and update/add translations
for source_text, italian_text in TRANSLATIONS.items():
    found = False

    # Search for existing message in all contexts
    for context in root.findall('.//context'):
        for message in context.findall('.//message'):
            source = message.find('source')
            if source is not None and source.text == source_text:
                # Found existing message - update translation
                translation = message.find('translation')
                if translation is not None:
                    translation.text = italian_text
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
        translation_elem.text = italian_text
        added_count += 1
        print(f"+ Added: {source_text[:50]}...")

# Write updated file
tree.write('translations/pygamemaker_it.ts', encoding='utf-8', xml_declaration=True)

print(f"\n{'='*60}")
print(f"Translation update complete!")
print(f"{'='*60}")
print(f"✓ Updated: {updated_count} existing translations")
print(f"+ Added: {added_count} new translations")
print(f"{'='*60}")
print(f"\nNext step: Compile with pyside6-lrelease")
