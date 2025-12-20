#!/usr/bin/env python3
"""Add Blockly configuration dialog translations to French, German, and Italian"""

import xml.etree.ElementTree as ET

# Blockly configuration dialog translations
# Format: English -> (French, German, Italian)
BLOCKLY_TRANSLATIONS = {
    "Configure Blockly Blocks": (
        "Configurer les blocs Blockly",
        "Blockly-Blöcke konfigurieren",
        "Configura blocchi Blockly"
    ),
    "Preset:": (
        "Préréglage :",
        "Voreinstellung:",
        "Preset:"
    ),
    "Full (All Blocks)": (
        "Complet (tous les blocs)",
        "Vollständig (alle Blöcke)",
        "Completo (tutti i blocchi)"
    ),
    "Beginner (Basic Blocks)": (
        "Débutant (blocs de base)",
        "Anfänger (Grundblöcke)",
        "Principiante (blocchi base)"
    ),
    "Intermediate (More Features)": (
        "Intermédiaire (plus de fonctionnalités)",
        "Fortgeschritten (mehr Funktionen)",
        "Intermedio (più funzionalità)"
    ),
    "Platformer Game": (
        "Jeu de plateforme",
        "Plattformspiel",
        "Gioco platform"
    ),
    "Grid-based RPG": (
        "RPG sur grille",
        "Gitterbasiertes RPG",
        "RPG a griglia"
    ),
    "Custom": (
        "Personnalisé",
        "Benutzerdefiniert",
        "Personalizzato"
    ),
    "Select blocks to enable:": (
        "Sélectionnez les blocs à activer :",
        "Wählen Sie die zu aktivierenden Blöcke:",
        "Seleziona i blocchi da abilitare:"
    ),
    "Block": (
        "Bloc",
        "Block",
        "Blocco"
    ),
    "Description": (
        "Description",
        "Beschreibung",
        "Descrizione"
    ),
    "Select All": (
        "Tout sélectionner",
        "Alle auswählen",
        "Seleziona tutto"
    ),
    "Select None": (
        "Tout désélectionner",
        "Nichts auswählen",
        "Deseleziona tutto"
    ),
    "Save": (
        "Enregistrer",
        "Speichern",
        "Salva"
    ),
    "Cancel": (
        "Annuler",
        "Abbrechen",
        "Annulla"
    ),
    "{0} blocks": (
        "{0} blocs",
        "{0} Blöcke",
        "{0} blocchi"
    ),
    "Requires: {0}": (
        "Nécessite : {0}",
        "Erfordert: {0}",
        "Richiede: {0}"
    ),
    "{0} blocks, {1} categories": (
        "{0} blocs, {1} catégories",
        "{0} Blöcke, {1} Kategorien",
        "{0} blocchi, {1} categorie"
    ),
    "⚠️ Warning: Some blocks are missing dependencies:\n{0}": (
        "⚠️ Avertissement : Certains blocs ont des dépendances manquantes :\n{0}",
        "⚠️ Warnung: Einigen Blöcken fehlen Abhängigkeiten:\n{0}",
        "⚠️ Avviso: Ad alcuni blocchi mancano le dipendenze:\n{0}"
    ),
    "Missing Dependencies": (
        "Dépendances manquantes",
        "Fehlende Abhängigkeiten",
        "Dipendenze mancanti"
    ),
    "Some enabled blocks are missing their dependencies. The blocks may not work correctly.\n\nDo you want to save anyway?": (
        "Certains blocs activés ont des dépendances manquantes. Les blocs peuvent ne pas fonctionner correctement.\n\nVoulez-vous enregistrer quand même ?",
        "Einigen aktivierten Blöcken fehlen ihre Abhängigkeiten. Die Blöcke funktionieren möglicherweise nicht korrekt.\n\nTrotzdem speichern?",
        "Ad alcuni blocchi abilitati mancano le dipendenze. I blocchi potrebbero non funzionare correttamente.\n\nVuoi salvare comunque?"
    ),
}

def update_translation_file(ts_file, lang_index, lang_name):
    """Update a single translation file with Blockly strings"""

    print(f"\n{'='*60}")
    print(f"Updating {lang_name} Blockly translations...")
    print(f"{'='*60}")

    tree = ET.parse(ts_file)
    root = tree.getroot()

    updated_count = 0
    added_count = 0

    for source_text, translations in BLOCKLY_TRANSLATIONS.items():
        target_text = translations[lang_index]
        found = False

        # Search for existing message
        for context in root.findall('.//context'):
            for message in context.findall('.//message'):
                source = message.find('source')
                if source is not None and source.text == source_text:
                    translation = message.find('translation')
                    if translation is not None:
                        translation.text = target_text
                        if 'type' in translation.attrib:
                            del translation.attrib['type']
                        updated_count += 1
                        found = True
                        print(f"✓ Updated: {source_text[:50]}...")
                        break
            if found:
                break

        if not found:
            # Add new message to BlocklyConfigDialog context
            context_name = 'BlocklyConfigDialog'

            # Find or create context
            target_context = None
            for context in root.findall('.//context'):
                name_elem = context.find('name')
                if name_elem is not None and name_elem.text == context_name:
                    target_context = context
                    break

            if target_context is None:
                target_context = ET.SubElement(root, 'context')
                name_elem = ET.SubElement(target_context, 'name')
                name_elem.text = context_name

            # Add new message
            message = ET.SubElement(target_context, 'message')
            source_elem = ET.SubElement(message, 'source')
            source_elem.text = source_text
            translation_elem = ET.SubElement(message, 'translation')
            translation_elem.text = target_text
            added_count += 1
            print(f"+ Added: {source_text[:50]}...")

    # Write updated file
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    print(f"{'='*60}")
    print(f"✓ {lang_name}: {updated_count} updated, {added_count} added")
    print(f"{'='*60}")

    return updated_count, added_count

# Update all three translation files
results = {}
for lang, (ts_file, idx) in [
    ('French', ('translations/pygamemaker_fr.ts', 0)),
    ('German', ('translations/pygamemaker_de.ts', 1)),
    ('Italian', ('translations/pygamemaker_it.ts', 2))
]:
    updated, added = update_translation_file(ts_file, idx, lang)
    results[lang] = (updated, added)

print(f"\n{'='*60}")
print("SUMMARY - Blockly translations complete!")
print(f"{'='*60}")
for lang, (updated, added) in results.items():
    total = updated + added
    print(f"{lang:8s}: {updated:2d} updated + {added:2d} added = {total:2d} total")
print(f"{'='*60}")
print("\nNext: Compile .qm files with pyside6-lrelease")
