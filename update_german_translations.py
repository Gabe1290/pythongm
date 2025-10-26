#!/usr/bin/env python3
"""
German (Deutsch) translation script for PyGameMaker IDE
Translates all 289 UI strings from English to German
"""

import xml.etree.ElementTree as ET
from pathlib import Path


# Complete German translation dictionary
TRANSLATIONS = {
    # Main menu items
    "&File": "&Datei",
    "&Edit": "&Bearbeiten",
    "&Assets": "&Ressourcen",
    "&Build": "&Erstellen",
    "&Tools": "&Werkzeuge",
    "🌐 &Language": "🌐 &Sprache",
    "&Help": "&Hilfe",

    # File menu
    "&New Project...": "&Neues Projekt...",
    "&Open Project...": "Projekt &öffnen...",
    "&Save Project": "Projekt &speichern",
    "Save Project &As...": "Projekt speichern &unter...",
    "Recent Projects": "Zuletzt verwendete Projekte",
    "Export as HTML5...": "Als HTML5 exportieren...",
    "Export as &Zip...": "Als &Zip exportieren...",
    "Export to Kivy...": "Nach Kivy exportieren...",
    "Export Project...": "Projekt exportieren...",
    "Open &Zip Project...": "&Zip-Projekt öffnen...",
    "Auto-Save to Zip": "Auto-Speichern als Zip",
    "Enable Auto-Save": "Auto-Speichern aktivieren",
    "Auto-Save Settings...": "Auto-Speichern-Einstellungen...",
    "Project &Settings...": "Projekt&einstellungen...",
    "E&xit": "&Beenden",

    # Edit menu
    "&Undo": "&Rückgängig",
    "&Redo": "&Wiederholen",
    "Cu&t": "&Ausschneiden",
    "&Copy": "&Kopieren",
    "&Paste": "&Einfügen",
    "&Duplicate": "&Duplizieren",
    "&Find...": "&Suchen...",
    "Find and &Replace...": "Suchen und &Ersetzen...",

    # Assets menu
    "Import &Sprite...": "&Sprite importieren...",
    "Import &Sound...": "&Sound importieren...",
    "Import &Background...": "&Hintergrund importieren...",
    "Create &Object...": "&Objekt erstellen...",
    "Create &Room...": "&Raum erstellen...",
    "Create S&cript...": "S&kript erstellen...",
    "Create &Font...": "S&chriftart erstellen...",
    "Import Object Package...": "Objekt-Paket importieren...",
    "Import Room Package...": "Raum-Paket importieren...",

    # Build menu
    "&Test Game": "Spiel &testen",
    "&Debug Game": "Spiel &debuggen",
    "&Build Game...": "Spiel &erstellen...",
    "Build and &Run": "Erstellen und &ausführen",
    "&Export Game...": "Spiel &exportieren...",

    # Tools menu
    "&Preferences...": "&Einstellungen...",
    "&Asset Manager...": "&Ressourcen-Manager...",
    "&Validate Project": "Projekt &validieren",
    "&Clean Project": "Projekt &bereinigen",

    # Help menu
    "&Documentation": "&Dokumentation",
    "&Tutorials": "&Anleitungen",
    "&About PyGameMaker": "Ü&ber PyGameMaker",
    "About &Qt": "Über &Qt",

    # Toolbar
    "Main": "Haupt",
    "New": "Neu",
    "Open": "Öffnen",
    "Save": "Speichern",
    "Test": "Testen",
    "Debug": "Debuggen",
    "Build": "Erstellen",
    "Import Sprite": "Sprite importieren",
    "Import Sound": "Sound importieren",

    # Status messages
    "Ready": "Bereit",
    "No project loaded": "Kein Projekt geladen",
    "Project loaded: {0}": "Projekt geladen: {0}",
    "Project: {0}": "Projekt: {0}",
    "Project saved": "Projekt gespeichert",
    "Project created successfully": "Projekt erfolgreich erstellt",
    "Created {0}": "{0} erstellt",
    "Imported {0}": "{0} importiert",
    "Opened room: {0}": "Raum geöffnet: {0}",
    "Opened object: {0}": "Objekt geöffnet: {0}",

    # Status bar messages
    "Loading project...": "Projekt wird geladen...",
    "Saving project...": "Projekt wird gespeichert...",
    "Creating new project...": "Neues Projekt wird erstellt...",
    "Opening file...": "Datei wird geöffnet...",
    "Importing asset...": "Ressource wird importiert...",
    "Please wait...": "Bitte warten...",
    "Processing...": "Wird verarbeitet...",
    "Calculating...": "Wird berechnet...",
    "Compiling...": "Wird kompiliert...",
    "Optimizing...": "Wird optimiert...",
    "Finishing...": "Wird abgeschlossen...",
    "Running game...": "Spiel wird ausgeführt...",
    "Exporting to HTML5...": "Export nach HTML5...",
    "HTML5 export complete": "HTML5-Export abgeschlossen",
    "Exporting project...": "Projekt wird exportiert...",
    "Project exported": "Projekt exportiert",
    "Loading project from zip...": "Projekt wird aus Zip geladen...",
    "Project loaded from zip": "Projekt aus Zip geladen",
    "Auto-save enabled": "Auto-Speichern aktiviert",
    "Auto-save disabled": "Auto-Speichern deaktiviert",
    "Auto-save settings updated": "Auto-Speichern-Einstellungen aktualisiert",
    "Importing object...": "Objekt wird importiert...",
    "Object imported: {0}": "Objekt importiert: {0}",
    "Import failed": "Import fehlgeschlagen",
    "Importing room...": "Raum wird importiert...",
    "Room imported: {0}": "Raum importiert: {0}",
    "Building game...": "Spiel wird erstellt...",
    "Building and running game...": "Spiel wird erstellt und ausgeführt...",
    "Preparing export...": "Export wird vorbereitet...",
    "Auto-save to zip disabled": "Auto-Speichern als Zip deaktiviert",

    # Dialog titles
    "Error": "Fehler",
    "Warning": "Warnung",
    "No Project": "Kein Projekt",
    "Unsaved Changes": "Nicht gespeicherte Änderungen",
    "Language Changed": "Sprache geändert",
    "Translation Not Available": "Übersetzung nicht verfügbar",
    "Export Successful": "Export erfolgreich",
    "Export Failed": "Export fehlgeschlagen",
    "Import Successful": "Import erfolgreich",
    "Import Failed": "Import fehlgeschlagen",
    "Invalid Zip": "Ungültige Zip-Datei",
    "Save Error": "Speicherfehler",
    "Not Implemented": "Nicht implementiert",
    "Coming Soon": "Demnächst verfügbar",
    "Auto-Save Enabled": "Auto-Speichern aktiviert",
    "Auto-Save Disabled": "Auto-Speichern deaktiviert",
    "Project Error": "Projektfehler",
    "Game Test Error": "Spieltestfehler",
    "Game Running": "Spiel läuft",
    "Debug Mode": "Debug-Modus",
    "Game Error": "Spielfehler",
    "Build Game": "Spiel erstellen",
    "Build and Run": "Erstellen und ausführen",
    "Export Game": "Spiel exportieren",
    "Validation Issues Found": "Validierungsprobleme gefunden",
    "Validation Passed": "Validierung bestanden",
    "Asset Manager": "Ressourcen-Manager",
    "Clean Project": "Projekt bereinigen",
    "Documentation": "Dokumentation",
    "Tutorials": "Anleitungen",
    "About PyGameMaker": "Über PyGameMaker",
    "No Project Loaded": "Kein Projekt geladen",
    "Export Complete": "Export abgeschlossen",
    "Exporting Game": "Spiel wird exportiert",

    # Dialog messages
    "Please open a project first": "Bitte öffnen Sie zuerst ein Projekt",
    "Please open or create a project first.": "Bitte öffnen oder erstellen Sie zuerst ein Projekt.",
    "Failed to create project": "Projekt konnte nicht erstellt werden",
    "Failed to load project": "Projekt konnte nicht geladen werden",
    "Failed to save project": "Projekt konnte nicht gespeichert werden",
    "Failed to load project from zip": "Projekt konnte nicht aus Zip geladen werden",
    "This zip file does not contain a valid PyGameMaker project": "Diese Zip-Datei enthält kein gültiges PyGameMaker-Projekt",
    "Failed to save project to disk": "Projekt konnte nicht auf Datenträger gespeichert werden",
    "Failed to save {0}: {1}": "{0} konnte nicht gespeichert werden: {1}",

    # Language change
    "Language changed to {0}.\n\nPlease restart PyGameMaker IDE for the changes to take full effect.": "Sprache geändert zu {0}.\n\nBitte starten Sie PyGameMaker IDE neu, damit die Änderungen vollständig wirksam werden.",
    "Translation file for {0} is not available.\n\nThe language has been set, but the interface will remain in English until a translation file is provided.\n\nExpected file: translations/pygamemaker_{1}.qm": "Übersetzungsdatei für {0} ist nicht verfügbar.\n\nDie Sprache wurde eingestellt, aber die Benutzeroberfläche bleibt auf Englisch, bis eine Übersetzungsdatei bereitgestellt wird.\n\nErwartete Datei: translations/pygamemaker_{1}.qm",

    # Export dialogs
    "Select Export Directory": "Exportverzeichnis auswählen",
    "Game exported as HTML5!\n\n{0}\n\nOpen in browser now?": "Spiel als HTML5 exportiert!\n\n{0}\n\nJetzt im Browser öffnen?",
    "Failed to export game as HTML5. Check console for details.": "Spiel konnte nicht als HTML5 exportiert werden. Überprüfen Sie die Konsole für Details.",
    "Export failed": "Export fehlgeschlagen",
    "Export Project as Zip": "Projekt als Zip exportieren",
    "Zip Files (*.zip)": "Zip-Dateien (*.zip)",
    "Project exported to:\n{0}": "Projekt exportiert nach:\n{0}",
    "Failed to export project as zip": "Projekt konnte nicht als Zip exportiert werden",
    "Open Zip Project": "Zip-Projekt öffnen",
    "Auto-Save to Zip Enabled": "Auto-Speichern als Zip aktiviert",
    "The project will now automatically save to the original zip file.": "Das Projekt wird nun automatisch in der ursprünglichen Zip-Datei gespeichert.",
    "Export as Zip?": "Als Zip exportieren?",
    "Would you like to export the current project as a zip file now?\n\nThis will allow auto-save to work with the zip file.": "Möchten Sie das aktuelle Projekt jetzt als Zip-Datei exportieren?\n\nDadurch kann Auto-Speichern mit der Zip-Datei funktionieren.",
    "Your project will be automatically saved every {0} seconds.": "Ihr Projekt wird automatisch alle {0} Sekunden gespeichert.",
    "Remember to save your project manually (Ctrl+S).": "Denken Sie daran, Ihr Projekt manuell zu speichern (Strg+S).",

    # Import dialogs
    "Import Object Package": "Objekt-Paket importieren",
    "GameMaker Objects (*.gmobj)": "GameMaker-Objekte (*.gmobj)",
    "Object '{0}' imported successfully!": "Objekt '{0}' erfolgreich importiert!",
    "Failed to import object package": "Objekt-Paket konnte nicht importiert werden",
    "Import Room Package": "Raum-Paket importieren",
    "GameMaker Rooms (*.gmroom)": "GameMaker-Räume (*.gmroom)",
    "Room '{0}' imported successfully!": "Raum '{0}' erfolgreich importiert!",
    "Failed to import room package": "Raum-Paket konnte nicht importiert werden",

    # Unsaved changes
    '"{0}" has unsaved changes. Save before closing?': '"{0}" hat nicht gespeicherte Änderungen. Vor dem Schließen speichern?',
    "You have unsaved changes. Do you want to save before closing?": "Sie haben nicht gespeicherte Änderungen. Möchten Sie vor dem Schließen speichern?",
    "You have unsaved changes. Save before building?": "Sie haben nicht gespeicherte Änderungen. Vor dem Erstellen speichern?",

    # File dialogs
    "Open Project": "Projekt öffnen",
    "Project Files (project.json);;Zip Files (*.zip);;All Files (*)": "Projektdateien (project.json);;Zip-Dateien (*.zip);;Alle Dateien (*)",
    "Save Project As": "Projekt speichern unter",
    "Select Build Output Directory": "Build-Ausgabeverzeichnis auswählen",
    "Choose Export Location": "Exportort auswählen",

    # Welcome tab
    "Welcome": "Willkommen",
    "Welcome to PyGameMaker IDE": "Willkommen bei PyGameMaker IDE",
    "Create amazing 2D games with visual scripting": "Erstellen Sie erstaunliche 2D-Spiele mit visueller Programmierung",
    "Quick Actions": "Schnellaktionen",
    "🆕 New Project (Ctrl+N)": "🆕 Neues Projekt (Strg+N)",
    "📂 Open Project (Ctrl+O)": "📂 Projekt öffnen (Strg+O)",
    "🏠 Create Room (Ctrl+R)": "🏠 Raum erstellen (Strg+R)",

    # Recent projects
    "No recent projects": "Keine zuletzt verwendeten Projekte",

    # Create dialogs
    "Create {0}": "{0} erstellen",
    "Enter name for new {0}:": "Namen für neues {0} eingeben:",

    # Game running
    "project.json not found in project directory": "project.json im Projektverzeichnis nicht gefunden",
    "Game closed": "Spiel geschlossen",
    "Failed to run game:\n\n{0}\n\nCheck console for details.": "Spiel konnte nicht ausgeführt werden:\n\n{0}\n\nÜberprüfen Sie die Konsole für Details.",
    "Game test failed": "Spieltest fehlgeschlagen",
    "A game is already running. Please stop it first.": "Ein Spiel läuft bereits. Bitte stoppen Sie es zuerst.",
    "Starting game in debug mode...": "Spiel wird im Debug-Modus gestartet...",
    "Debug mode will start the game with verbose console output.\n\nFuture features:\n• Breakpoints\n• Variable inspection\n• Step-through execution\n• Performance profiling\n\nFor now, check the console for debug messages.": "Der Debug-Modus startet das Spiel mit ausführlicher Konsolenausgabe.\n\nZukünftige Funktionen:\n• Haltepunkte\n• Variableninspektion\n• Schrittweise Ausführung\n• Leistungsprofilerstellung\n\nÜberprüfen Sie vorerst die Konsole auf Debug-Meldungen.",
    "Game started in debug mode - Check console for debug output": "Spiel im Debug-Modus gestartet - Überprüfen Sie die Konsole für Debug-Ausgabe",
    "Failed to start game": "Spiel konnte nicht gestartet werden",
    "Failed to start the game. Check console for details.": "Spiel konnte nicht gestartet werden. Überprüfen Sie die Konsole für Details.",

    # Build dialogs
    "Standalone executable building is not yet implemented.\n\nCurrent workaround:\n• Use 'Export as HTML5' to create a web version\n• Use 'Test Game' to run from source\n\nFuture build targets:\n• Windows .exe\n• Linux binary\n• macOS .app\n• Android .apk\n\nWould you like to export as HTML5 instead?": "Das Erstellen eigenständiger ausführbarer Dateien ist noch nicht implementiert.\n\nAktueller Workaround:\n• Verwenden Sie 'Als HTML5 exportieren', um eine Webversion zu erstellen\n• Verwenden Sie 'Spiel testen', um aus der Quelle auszuführen\n\nZukünftige Build-Ziele:\n• Windows .exe\n• Linux-Binärdatei\n• macOS .app\n• Android .apk\n\nMöchten Sie stattdessen als HTML5 exportieren?",
    "Build cancelled - use HTML5 export instead": "Erstellen abgebrochen - verwenden Sie stattdessen HTML5-Export",
    "This will build a standalone executable and run it.\n\nBuilding may take several minutes.\n\nContinue?": "Dies erstellt eine eigenständige ausführbare Datei und führt sie aus.\n\nDas Erstellen kann mehrere Minuten dauern.\n\nFortfahren?",
    "Standalone build is not yet implemented.\n\nRunning game in test mode instead...": "Eigenständiger Build ist noch nicht implementiert.\n\nStattdessen wird das Spiel im Testmodus ausgeführt...",

    # Export game dialog
    "<h3>Export Game</h3>": "<h3>Spiel exportieren</h3>",
    "Choose export format:": "Exportformat wählen:",
    "HTML5 (Web Browser) - ✅ Available": "HTML5 (Webbrowser) - ✅ Verfügbar",
    "Windows Executable (.exe) - ✅ Available": "Windows-Programm (.exe) - ✅ Verfügbar",
    "Linux Binary - 🚧 Coming Soon": "Linux-Binärdatei - 🚧 Demnächst",
    "macOS Application (.app) - 🚧 Coming Soon": "macOS-Anwendung (.app) - 🚧 Demnächst",
    "Android Package (.apk) - 🚧 Coming Soon": "Android-Paket (.apk) - 🚧 Demnächst",
    "Export": "Exportieren",
    "Cancel": "Abbrechen",
    "This export format is not yet available.\n\nPlease use HTML5 or Windows EXE export for now.": "Dieses Exportformat ist noch nicht verfügbar.\n\nBitte verwenden Sie vorerst HTML5- oder Windows-EXE-Export.",
    "Would you like to open the output folder?": "Möchten Sie den Ausgabeordner öffnen?",

    # Not implemented features
    "Find functionality is not yet implemented.": "Suchfunktion ist noch nicht implementiert.",
    "Find and Replace functionality is not yet implemented.": "Suchen-und-Ersetzen-Funktion ist noch nicht implementiert.",
    "Please open a project first to manage assets.": "Bitte öffnen Sie zuerst ein Projekt, um Ressourcen zu verwalten.",
    "Asset Manager is not yet implemented.\n\nCurrent workaround:\nUse the Asset Tree panel on the left to manage your assets.\n\nFuture features:\n• Bulk asset operations\n• Asset search and filter\n• Asset usage tracking\n• Unused asset cleanup": "Ressourcen-Manager ist noch nicht implementiert.\n\nAktueller Workaround:\nVerwenden Sie das Ressourcenbaum-Panel auf der linken Seite, um Ihre Ressourcen zu verwalten.\n\nZukünftige Funktionen:\n• Massenressourcenoperationen\n• Ressourcensuche und -filter\n• Ressourcennutzungsverfolgung\n• Bereinigung nicht verwendeter Ressourcen",

    # Validation
    "Please open a project first to validate.": "Bitte öffnen Sie zuerst ein Projekt zum Validieren.",
    "Project validation found the following issues:\n\n": "Projektvalidierung hat die folgenden Probleme gefunden:\n\n",
    "Project structure is valid!\n\n✓ All required directories exist\n✓ project.json is present": "Projektstruktur ist gültig!\n\n✓ Alle erforderlichen Verzeichnisse existieren\n✓ project.json ist vorhanden",

    # Clean project
    "Please open a project first to clean.": "Bitte öffnen Sie zuerst ein Projekt zum Bereinigen.",
    "Project cleanup is not yet implemented.\n\nFuture features:\n• Remove temporary files\n• Delete unused assets\n• Clean build artifacts\n• Optimize project size\n\nWould you like to learn more?": "Projektbereinigung ist noch nicht implementiert.\n\nZukünftige Funktionen:\n• Temporäre Dateien entfernen\n• Nicht verwendete Ressourcen löschen\n• Build-Artefakte bereinigen\n• Projektgröße optimieren\n\nMöchten Sie mehr erfahren?",
    "This feature will be available in a future update.\n\nFor now, you can manually delete temporary files from:\n• .cache/ directory\n• __pycache__/ directories\n• *.pyc files": "Diese Funktion wird in einem zukünftigen Update verfügbar sein.\n\nVorerst können Sie temporäre Dateien manuell löschen aus:\n• .cache/ Verzeichnis\n• __pycache__/ Verzeichnisse\n• *.pyc Dateien",

    # Documentation and tutorials
    "Documentation is not yet available.\n\nQuick Help:\n• F1: Open this help\n• Ctrl+N: New Project\n• Ctrl+O: Open Project\n• Ctrl+S: Save Project\n• Double-click assets to edit them\n• Right-click for more options\n\nOnline documentation coming soon!": "Dokumentation ist noch nicht verfügbar.\n\nSchnellhilfe:\n• F1: Diese Hilfe öffnen\n• Strg+N: Neues Projekt\n• Strg+O: Projekt öffnen\n• Strg+S: Projekt speichern\n• Doppelklicken Sie auf Ressourcen, um sie zu bearbeiten\n• Rechtsklick für weitere Optionen\n\nOnline-Dokumentation demnächst verfügbar!",
    "<h3>PyGameMaker Tutorials</h3>": "<h3>PyGameMaker-Anleitungen</h3>",
    "Coming soon! Tutorials will include:": "Demnächst verfügbar! Anleitungen werden Folgendes beinhalten:",
    "\n💡 Tip: Check the documentation (F1) for quick help!": "\n💡 Tipp: Überprüfen Sie die Dokumentation (F1) für schnelle Hilfe!",
    "Close": "Schließen",

    # About dialog
    "PyGameMaker IDE v1.0.0\n\nA visual game development environment\ninspired by GameMaker Studio.": "PyGameMaker IDE v1.0.0\n\nEine visuelle Spielentwicklungsumgebung\ninspiriert von GameMaker Studio.",

    # Editor messages
    "Editor": "Editor",
    "Editor for {0} not yet implemented.\nAsset: {1}": "Editor für {0} noch nicht implementiert.\nRessource: {1}",
    "Failed to open room editor: {0}": "Raumeditor konnte nicht geöffnet werden: {0}",
    "Failed to open object editor: {0}": "Objekteditor konnte nicht geöffnet werden: {0}",

    # Create or open project
    "You need to create or open a project before importing sprites.\n\nWould you like to create a new project now?": "Sie müssen ein Projekt erstellen oder öffnen, bevor Sie Sprites importieren können.\n\nMöchten Sie jetzt ein neues Projekt erstellen?",
    "You need to create or open a project before {0}.\n\nWould you like to:\n• Create a new project, or\n• Open an existing project?": "Sie müssen ein Projekt erstellen oder öffnen, bevor Sie {0}.\n\nMöchten Sie:\n• Ein neues Projekt erstellen, oder\n• Ein vorhandenes Projekt öffnen?",
    "Create or Open Project": "Projekt erstellen oder öffnen",
    "Choose project action:": "Projektaktion wählen:",

    # Toolbar items
    "Save Project": "Projekt speichern",
    "Save Project As...": "Projekt speichern unter...",
    "Project Settings...": "Projekteinstellungen...",
    "Import": "Importieren",
    "Create": "Erstellen",
    "Test Game": "Spiel testen",
    "Debug Game": "Spiel debuggen",
    "Export Game...": "Spiel exportieren...",

    # Preferences Dialog
    "Preferences": "Einstellungen",
    "Note: Some settings require restarting the IDE to take effect.": "Hinweis: Einige Einstellungen erfordern einen Neustart der IDE, um wirksam zu werden.",
    "Font Settings": "Schrifteinstellungen",
    "Font Size:": "Schriftgröße:",
    "System Default": "Systemstandard",
    "Font Family:": "Schriftart:",
    "Preview: The quick brown fox jumps over the lazy dog": "Vorschau: Franz jagt im komplett verwahrlosten Taxi quer durch Bayern",
    "Preview:": "Vorschau:",
    "Theme Settings": "Designeinstellungen",
    "Theme:": "Design:",
    "UI Scale:": "UI-Skalierung:",
    "Show tooltips": "Tooltips anzeigen",
    "Appearance": "Aussehen",
    "Auto-Save Settings": "Auto-Speichern-Einstellungen",
    "Enable auto-save": "Auto-Speichern aktivieren",
    " minutes": " Minuten",
    "Auto-save interval:": "Auto-Speichern-Intervall:",
    "Grid & Snapping": "Raster & Einrasten",
    "Show grid in editors": "Raster in Editoren anzeigen",
    "Grid size:": "Rastergröße:",
    "Snap to grid": "Am Raster einrasten",
    "Show collision boxes": "Kollisionsboxen anzeigen",
    "Editor": "Editor",
    "Project Paths": "Projektpfade",
    "Browse...": "Durchsuchen...",
    "Default projects folder:": "Standard-Projektordner:",
    "Project Settings": "Projekteinstellungen",
    "Recent projects limit:": "Limit für zuletzt verwendete Projekte:",
    "Create backup on save": "Sicherung beim Speichern erstellen",
    "Project": "Projekt",
    "Debug Settings": "Debug-Einstellungen",
    "Enable debug mode": "Debug-Modus aktivieren",
    "Show console output": "Konsolenausgabe anzeigen",
    "Performance": "Leistung",
    "Maximum undo steps:": "Maximale Anzahl Rückgängig-Schritte:",
    "Advanced": "Erweitert",
    "Select Default Projects Directory": "Standard-Projektverzeichnis auswählen",
    "Settings Saved": "Einstellungen gespeichert",
    "Settings have been saved successfully.\n\nSome changes may require restarting the IDE to take effect.": "Einstellungen wurden erfolgreich gespeichert.\n\nEinige Änderungen erfordern möglicherweise einen Neustart der IDE, um wirksam zu werden.",

    # Auto-Save Dialog
    "Auto-Save": "Auto-Speichern",
    "Enable automatic saving": "Automatisches Speichern aktivieren",
    "When enabled, your project will be saved automatically at regular intervals.": "Wenn aktiviert, wird Ihr Projekt automatisch in regelmäßigen Abständen gespeichert.",
    "Save Interval": "Speicherintervall",
    " seconds": " Sekunden",
    "Save every:": "Speichern alle:",
    "15s": "15s",
    "30s": "30s",
    "1m": "1m",
    "2m": "2m",
    "5m": "5m",
    "Presets:": "Voreinstellungen:",
    "⚠️  Shorter intervals may impact performance on large projects.": "⚠️  Kürzere Intervalle können die Leistung bei großen Projekten beeinträchtigen.",

    # Component messages
    "Actions are now managed through the Events panel": "Aktionen werden jetzt über das Ereignis-Panel verwaltet",
    "Visual scripting is now managed through the Events panel": "Visuelle Programmierung wird jetzt über das Ereignis-Panel verwaltet",
}


def update_translations():
    """Update the German translation file with new translations"""

    ts_file = Path("translations/pygamemaker_de.ts")

    if not ts_file.exists():
        print(f"❌ Translation file not found: {ts_file}")
        print("Please run pylupdate6 first to create the template file.")
        return False

    try:
        tree = ET.parse(ts_file)
        root = tree.getroot()

        updated = 0
        total_unfinished = 0

        for context in root.findall('context'):
            for message in context.findall('message'):
                source = message.find('source')
                translation = message.find('translation')

                if source is None or translation is None:
                    continue

                source_text = source.text

                # Count unfinished translations
                if translation.get('type') == 'unfinished':
                    total_unfinished += 1

                # Update if we have a translation
                if source_text in TRANSLATIONS:
                    translation.text = TRANSLATIONS[source_text]
                    # Remove 'type="unfinished"' attribute
                    if 'type' in translation.attrib:
                        del translation.attrib['type']
                    updated += 1
                    print(f"✓ {source_text[:60]}...")

        # Write back to file
        tree.write(ts_file, encoding='utf-8', xml_declaration=True)

        print(f"\n{'='*60}")
        print(f"✓ Updated {updated} translations!")
        print(f"📊 Total unfinished before: {total_unfinished}")
        print(f"📊 Remaining unfinished: {total_unfinished - updated}")
        print(f"{'='*60}")

        return True

    except Exception as e:
        print(f"❌ Error updating translations: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("German (Deutsch) Translation Updater")
    print("="*60)
    print()

    success = update_translations()

    if success:
        print("\n✓ Translation file updated successfully!")
        print("\nNext steps:")
        print("1. Run: lrelease translations/pygamemaker_de.ts -qm translations/pygamemaker_de.qm")
        print("2. Test in IDE: Tools → 🌐 Language → Deutsch")
        print("3. Restart IDE to see all changes")
    else:
        print("\n✗ Translation update failed")
