#!/usr/bin/env python3
"""
Create a minimal French translation for testing
"""

from pathlib import Path

project_root = Path(__file__).parent.parent
translations_dir = project_root / "translations"
translations_dir.mkdir(exist_ok=True)

# Create minimal .ts file
ts_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr_FR">
<context>
    <name>PyGameMakerIDE</name>
    <message>
        <source>&amp;File</source>
        <translation>&amp;Fichier</translation>
    </message>
    <message>
        <source>&amp;Edit</source>
        <translation>&amp;Édition</translation>
    </message>
    <message>
        <source>&amp;Assets</source>
        <translation>&amp;Ressources</translation>
    </message>
    <message>
        <source>&amp;Build</source>
        <translation>&amp;Construire</translation>
    </message>
    <message>
        <source>&amp;Tools</source>
        <translation>&amp;Outils</translation>
    </message>
    <message>
        <source>&amp;Help</source>
        <translation>&amp;Aide</translation>
    </message>
    <message>
        <source>Ready</source>
        <translation>Prêt</translation>
    </message>
    <message>
        <source>No project loaded</source>
        <translation>Aucun projet chargé</translation>
    </message>
</context>
<context>
    <name>WelcomeTab</name>
    <message>
        <source>Welcome to PyGameMaker IDE</source>
        <translation>Bienvenue dans PyGameMaker IDE</translation>
    </message>
    <message>
        <source>Quick Actions</source>
        <translation>Actions rapides</translation>
    </message>
</context>
</TS>
'''

ts_file = translations_dir / "pygamemaker_fr.ts"
with open(ts_file, 'w', encoding='utf-8') as f:
    f.write(ts_content)

print(f"✅ Created: {ts_file}")
print(f"\nNow compile it with:")
print(f"  lrelease {ts_file}")