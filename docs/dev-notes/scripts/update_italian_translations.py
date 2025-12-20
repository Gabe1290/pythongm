#!/usr/bin/env python3
"""
Italian (Italiano) translation script for PyGameMaker IDE
Translates all 289 UI strings from English to Italian
"""

import xml.etree.ElementTree as ET
from pathlib import Path


# Complete Italian translation dictionary
TRANSLATIONS = {
    # Main menu items
    "&File": "&File",
    "&Edit": "&Modifica",
    "&Assets": "&Risorse",
    "&Build": "&Costruisci",
    "&Tools": "&Strumenti",
    "🌐 &Language": "🌐 &Lingua",
    "&Help": "&Aiuto",

    # File menu
    "&New Project...": "&Nuovo progetto...",
    "&Open Project...": "&Apri progetto...",
    "&Save Project": "&Salva progetto",
    "Save Project &As...": "Salva progetto &come...",
    "Recent Projects": "Progetti recenti",
    "Export as HTML5...": "Esporta come HTML5...",
    "Export as &Zip...": "Esporta come &Zip...",
    "Export to Kivy...": "Esporta in Kivy...",
    "Export Project...": "Esporta progetto...",
    "Open &Zip Project...": "Apri progetto &Zip...",
    "Auto-Save to Zip": "Salvataggio automatico in Zip",
    "Enable Auto-Save": "Abilita salvataggio automatico",
    "Auto-Save Settings...": "Impostazioni salvataggio automatico...",
    "Project &Settings...": "Impostazioni &progetto...",
    "E&xit": "&Esci",

    # Edit menu
    "&Undo": "&Annulla",
    "&Redo": "&Ripeti",
    "Cu&t": "&Taglia",
    "&Copy": "&Copia",
    "&Paste": "&Incolla",
    "&Duplicate": "&Duplica",
    "&Find...": "&Trova...",
    "Find and &Replace...": "Trova e &sostituisci...",

    # Assets menu
    "Import &Sprite...": "Importa &sprite...",
    "Import &Sound...": "Importa &suono...",
    "Import &Background...": "Importa &sfondo...",
    "Create &Object...": "Crea &oggetto...",
    "Create &Room...": "Crea &stanza...",
    "Create S&cript...": "Crea s&cript...",
    "Create &Font...": "Crea &font...",
    "Import Object Package...": "Importa pacchetto oggetto...",
    "Import Room Package...": "Importa pacchetto stanza...",

    # Build menu
    "&Test Game": "&Testa gioco",
    "&Debug Game": "&Debug gioco",
    "&Build Game...": "&Costruisci gioco...",
    "Build and &Run": "Costruisci ed &esegui",
    "&Export Game...": "&Esporta gioco...",

    # Tools menu
    "&Preferences...": "&Preferenze...",
    "&Asset Manager...": "Gestore &risorse...",
    "&Validate Project": "&Valida progetto",
    "&Clean Project": "&Pulisci progetto",

    # Help menu
    "&Documentation": "&Documentazione",
    "&Tutorials": "&Tutorial",
    "&About PyGameMaker": "&Informazioni su PyGameMaker",
    "About &Qt": "Informazioni su &Qt",

    # Toolbar
    "Main": "Principale",
    "New": "Nuovo",
    "Open": "Apri",
    "Save": "Salva",
    "Test": "Testa",
    "Debug": "Debug",
    "Build": "Costruisci",
    "Import Sprite": "Importa sprite",
    "Import Sound": "Importa suono",

    # Status messages
    "Ready": "Pronto",
    "No project loaded": "Nessun progetto caricato",
    "Project loaded: {0}": "Progetto caricato: {0}",
    "Project: {0}": "Progetto: {0}",
    "Project saved": "Progetto salvato",
    "Project created successfully": "Progetto creato con successo",
    "Created {0}": "{0} creato",
    "Imported {0}": "{0} importato",
    "Opened room: {0}": "Stanza aperta: {0}",
    "Opened object: {0}": "Oggetto aperto: {0}",

    # Status bar messages
    "Loading project...": "Caricamento progetto...",
    "Saving project...": "Salvataggio progetto...",
    "Creating new project...": "Creazione nuovo progetto...",
    "Opening file...": "Apertura file...",
    "Importing asset...": "Importazione risorsa...",
    "Please wait...": "Attendere prego...",
    "Processing...": "Elaborazione...",
    "Calculating...": "Calcolo...",
    "Compiling...": "Compilazione...",
    "Optimizing...": "Ottimizzazione...",
    "Finishing...": "Completamento...",
    "Running game...": "Esecuzione gioco...",
    "Exporting to HTML5...": "Esportazione in HTML5...",
    "HTML5 export complete": "Esportazione HTML5 completata",
    "Exporting project...": "Esportazione progetto...",
    "Project exported": "Progetto esportato",
    "Loading project from zip...": "Caricamento progetto da zip...",
    "Project loaded from zip": "Progetto caricato da zip",
    "Auto-save enabled": "Salvataggio automatico abilitato",
    "Auto-save disabled": "Salvataggio automatico disabilitato",
    "Auto-save settings updated": "Impostazioni salvataggio automatico aggiornate",
    "Importing object...": "Importazione oggetto...",
    "Object imported: {0}": "Oggetto importato: {0}",
    "Import failed": "Importazione fallita",
    "Importing room...": "Importazione stanza...",
    "Room imported: {0}": "Stanza importata: {0}",
    "Building game...": "Costruzione gioco...",
    "Building and running game...": "Costruzione ed esecuzione gioco...",
    "Preparing export...": "Preparazione esportazione...",
    "Auto-save to zip disabled": "Salvataggio automatico in zip disabilitato",

    # Dialog titles
    "Error": "Errore",
    "Warning": "Avviso",
    "No Project": "Nessun progetto",
    "Unsaved Changes": "Modifiche non salvate",
    "Language Changed": "Lingua cambiata",
    "Translation Not Available": "Traduzione non disponibile",
    "Export Successful": "Esportazione riuscita",
    "Export Failed": "Esportazione fallita",
    "Import Successful": "Importazione riuscita",
    "Import Failed": "Importazione fallita",
    "Invalid Zip": "Zip non valido",
    "Save Error": "Errore di salvataggio",
    "Not Implemented": "Non implementato",
    "Coming Soon": "Prossimamente",
    "Auto-Save Enabled": "Salvataggio automatico abilitato",
    "Auto-Save Disabled": "Salvataggio automatico disabilitato",
    "Project Error": "Errore progetto",
    "Game Test Error": "Errore test gioco",
    "Game Running": "Gioco in esecuzione",
    "Debug Mode": "Modalità debug",
    "Game Error": "Errore gioco",
    "Build Game": "Costruisci gioco",
    "Build and Run": "Costruisci ed esegui",
    "Export Game": "Esporta gioco",
    "Validation Issues Found": "Problemi di validazione trovati",
    "Validation Passed": "Validazione superata",
    "Asset Manager": "Gestore risorse",
    "Clean Project": "Pulisci progetto",
    "Documentation": "Documentazione",
    "Tutorials": "Tutorial",
    "About PyGameMaker": "Informazioni su PyGameMaker",
    "No Project Loaded": "Nessun progetto caricato",
    "Export Complete": "Esportazione completata",
    "Exporting Game": "Esportazione gioco",

    # Dialog messages
    "Please open a project first": "Si prega di aprire prima un progetto",
    "Please open or create a project first.": "Si prega di aprire o creare prima un progetto.",
    "Failed to create project": "Impossibile creare il progetto",
    "Failed to load project": "Impossibile caricare il progetto",
    "Failed to save project": "Impossibile salvare il progetto",
    "Failed to load project from zip": "Impossibile caricare il progetto da zip",
    "This zip file does not contain a valid PyGameMaker project": "Questo file zip non contiene un progetto PyGameMaker valido",
    "Failed to save project to disk": "Impossibile salvare il progetto su disco",
    "Failed to save {0}: {1}": "Impossibile salvare {0}: {1}",

    # Language change
    "Language changed to {0}.\n\nPlease restart PyGameMaker IDE for the changes to take full effect.": "Lingua cambiata in {0}.\n\nSi prega di riavviare PyGameMaker IDE affinché le modifiche abbiano pieno effetto.",
    "Translation file for {0} is not available.\n\nThe language has been set, but the interface will remain in English until a translation file is provided.\n\nExpected file: translations/pygamemaker_{1}.qm": "Il file di traduzione per {0} non è disponibile.\n\nLa lingua è stata impostata, ma l'interfaccia rimarrà in inglese finché non verrà fornito un file di traduzione.\n\nFile previsto: translations/pygamemaker_{1}.qm",

    # Export dialogs
    "Select Export Directory": "Seleziona directory di esportazione",
    "Game exported as HTML5!\n\n{0}\n\nOpen in browser now?": "Gioco esportato come HTML5!\n\n{0}\n\nAprire nel browser ora?",
    "Failed to export game as HTML5. Check console for details.": "Impossibile esportare il gioco come HTML5. Controllare la console per i dettagli.",
    "Export failed": "Esportazione fallita",
    "Export Project as Zip": "Esporta progetto come Zip",
    "Zip Files (*.zip)": "File Zip (*.zip)",
    "Project exported to:\n{0}": "Progetto esportato in:\n{0}",
    "Failed to export project as zip": "Impossibile esportare il progetto come zip",
    "Open Zip Project": "Apri progetto Zip",
    "Auto-Save to Zip Enabled": "Salvataggio automatico in Zip abilitato",
    "The project will now automatically save to the original zip file.": "Il progetto verrà ora salvato automaticamente nel file zip originale.",
    "Export as Zip?": "Esportare come Zip?",
    "Would you like to export the current project as a zip file now?\n\nThis will allow auto-save to work with the zip file.": "Vuoi esportare il progetto corrente come file zip ora?\n\nCiò consentirà al salvataggio automatico di funzionare con il file zip.",
    "Your project will be automatically saved every {0} seconds.": "Il tuo progetto verrà salvato automaticamente ogni {0} secondi.",
    "Remember to save your project manually (Ctrl+S).": "Ricorda di salvare il tuo progetto manualmente (Ctrl+S).",

    # Import dialogs
    "Import Object Package": "Importa pacchetto oggetto",
    "GameMaker Objects (*.gmobj)": "Oggetti GameMaker (*.gmobj)",
    "Object '{0}' imported successfully!": "Oggetto '{0}' importato con successo!",
    "Failed to import object package": "Impossibile importare il pacchetto oggetto",
    "Import Room Package": "Importa pacchetto stanza",
    "GameMaker Rooms (*.gmroom)": "Stanze GameMaker (*.gmroom)",
    "Room '{0}' imported successfully!": "Stanza '{0}' importata con successo!",
    "Failed to import room package": "Impossibile importare il pacchetto stanza",

    # Unsaved changes
    '"{0}" has unsaved changes. Save before closing?': '"{0}" ha modifiche non salvate. Salvare prima di chiudere?',
    "You have unsaved changes. Do you want to save before closing?": "Hai modifiche non salvate. Vuoi salvare prima di chiudere?",
    "You have unsaved changes. Save before building?": "Hai modifiche non salvate. Salvare prima di costruire?",

    # File dialogs
    "Open Project": "Apri progetto",
    "Project Files (project.json);;Zip Files (*.zip);;All Files (*)": "File di progetto (project.json);;File Zip (*.zip);;Tutti i file (*)",
    "Save Project As": "Salva progetto come",
    "Select Build Output Directory": "Seleziona directory di output build",
    "Choose Export Location": "Scegli posizione esportazione",

    # Welcome tab
    "Welcome": "Benvenuto",
    "Welcome to PyGameMaker IDE": "Benvenuto in PyGameMaker IDE",
    "Create amazing 2D games with visual scripting": "Crea giochi 2D incredibili con programmazione visuale",
    "Quick Actions": "Azioni rapide",
    "🆕 New Project (Ctrl+N)": "🆕 Nuovo progetto (Ctrl+N)",
    "📂 Open Project (Ctrl+O)": "📂 Apri progetto (Ctrl+O)",
    "🏠 Create Room (Ctrl+R)": "🏠 Crea stanza (Ctrl+R)",

    # Recent projects
    "No recent projects": "Nessun progetto recente",

    # Create dialogs
    "Create {0}": "Crea {0}",
    "Enter name for new {0}:": "Inserisci nome per nuovo {0}:",

    # Game running
    "project.json not found in project directory": "project.json non trovato nella directory del progetto",
    "Game closed": "Gioco chiuso",
    "Failed to run game:\n\n{0}\n\nCheck console for details.": "Impossibile eseguire il gioco:\n\n{0}\n\nControllare la console per i dettagli.",
    "Game test failed": "Test gioco fallito",
    "A game is already running. Please stop it first.": "Un gioco è già in esecuzione. Si prega di fermarlo prima.",
    "Starting game in debug mode...": "Avvio gioco in modalità debug...",
    "Debug mode will start the game with verbose console output.\n\nFuture features:\n• Breakpoints\n• Variable inspection\n• Step-through execution\n• Performance profiling\n\nFor now, check the console for debug messages.": "La modalità debug avvierà il gioco con output console dettagliato.\n\nFunzionalità future:\n• Punti di interruzione\n• Ispezione variabili\n• Esecuzione passo-passo\n• Profilazione prestazioni\n\nPer ora, controllare la console per i messaggi di debug.",
    "Game started in debug mode - Check console for debug output": "Gioco avviato in modalità debug - Controllare la console per l'output di debug",
    "Failed to start game": "Impossibile avviare il gioco",
    "Failed to start the game. Check console for details.": "Impossibile avviare il gioco. Controllare la console per i dettagli.",

    # Build dialogs
    "Standalone executable building is not yet implemented.\n\nCurrent workaround:\n• Use 'Export as HTML5' to create a web version\n• Use 'Test Game' to run from source\n\nFuture build targets:\n• Windows .exe\n• Linux binary\n• macOS .app\n• Android .apk\n\nWould you like to export as HTML5 instead?": "La creazione di eseguibili autonomi non è ancora implementata.\n\nSoluzione alternativa attuale:\n• Usa 'Esporta come HTML5' per creare una versione web\n• Usa 'Testa gioco' per eseguire dal sorgente\n\nTarget di build futuri:\n• Windows .exe\n• Binario Linux\n• macOS .app\n• Android .apk\n\nVuoi esportare come HTML5 invece?",
    "Build cancelled - use HTML5 export instead": "Build annullato - usa esportazione HTML5 invece",
    "This will build a standalone executable and run it.\n\nBuilding may take several minutes.\n\nContinue?": "Questo creerà un eseguibile autonomo e lo eseguirà.\n\nLa creazione potrebbe richiedere diversi minuti.\n\nContinuare?",
    "Standalone build is not yet implemented.\n\nRunning game in test mode instead...": "Build autonomo non ancora implementato.\n\nEsecuzione gioco in modalità test invece...",

    # Export game dialog
    "<h3>Export Game</h3>": "<h3>Esporta gioco</h3>",
    "Choose export format:": "Scegli formato esportazione:",
    "HTML5 (Web Browser) - ✅ Available": "HTML5 (browser web) - ✅ Disponibile",
    "Windows Executable (.exe) - ✅ Available": "Eseguibile Windows (.exe) - ✅ Disponibile",
    "Linux Binary - 🚧 Coming Soon": "Binario Linux - 🚧 Prossimamente",
    "macOS Application (.app) - 🚧 Coming Soon": "Applicazione macOS (.app) - 🚧 Prossimamente",
    "Android Package (.apk) - 🚧 Coming Soon": "Pacchetto Android (.apk) - 🚧 Prossimamente",
    "Export": "Esporta",
    "Cancel": "Annulla",
    "This export format is not yet available.\n\nPlease use HTML5 or Windows EXE export for now.": "Questo formato di esportazione non è ancora disponibile.\n\nSi prega di utilizzare l'esportazione HTML5 o Windows EXE per ora.",
    "Would you like to open the output folder?": "Vuoi aprire la cartella di output?",

    # Not implemented features
    "Find functionality is not yet implemented.": "La funzionalità di ricerca non è ancora implementata.",
    "Find and Replace functionality is not yet implemented.": "La funzionalità Trova e sostituisci non è ancora implementata.",
    "Please open a project first to manage assets.": "Si prega di aprire prima un progetto per gestire le risorse.",
    "Asset Manager is not yet implemented.\n\nCurrent workaround:\nUse the Asset Tree panel on the left to manage your assets.\n\nFuture features:\n• Bulk asset operations\n• Asset search and filter\n• Asset usage tracking\n• Unused asset cleanup": "Il gestore risorse non è ancora implementato.\n\nSoluzione alternativa attuale:\nUsa il pannello Albero risorse a sinistra per gestire le tue risorse.\n\nFunzionalità future:\n• Operazioni in blocco sulle risorse\n• Ricerca e filtro risorse\n• Tracciamento utilizzo risorse\n• Pulizia risorse inutilizzate",

    # Validation
    "Please open a project first to validate.": "Si prega di aprire prima un progetto da validare.",
    "Project validation found the following issues:\n\n": "La validazione del progetto ha trovato i seguenti problemi:\n\n",
    "Project structure is valid!\n\n✓ All required directories exist\n✓ project.json is present": "La struttura del progetto è valida!\n\n✓ Tutte le directory richieste esistono\n✓ project.json è presente",

    # Clean project
    "Please open a project first to clean.": "Si prega di aprire prima un progetto da pulire.",
    "Project cleanup is not yet implemented.\n\nFuture features:\n• Remove temporary files\n• Delete unused assets\n• Clean build artifacts\n• Optimize project size\n\nWould you like to learn more?": "La pulizia del progetto non è ancora implementata.\n\nFunzionalità future:\n• Rimuovere file temporanei\n• Eliminare risorse inutilizzate\n• Pulire artefatti di build\n• Ottimizzare dimensione progetto\n\nVuoi saperne di più?",
    "This feature will be available in a future update.\n\nFor now, you can manually delete temporary files from:\n• .cache/ directory\n• __pycache__/ directories\n• *.pyc files": "Questa funzionalità sarà disponibile in un aggiornamento futuro.\n\nPer ora, puoi eliminare manualmente i file temporanei da:\n• directory .cache/\n• directory __pycache__/\n• file *.pyc",

    # Documentation and tutorials
    "Documentation is not yet available.\n\nQuick Help:\n• F1: Open this help\n• Ctrl+N: New Project\n• Ctrl+O: Open Project\n• Ctrl+S: Save Project\n• Double-click assets to edit them\n• Right-click for more options\n\nOnline documentation coming soon!": "La documentazione non è ancora disponibile.\n\nGuida rapida:\n• F1: Apri questa guida\n• Ctrl+N: Nuovo progetto\n• Ctrl+O: Apri progetto\n• Ctrl+S: Salva progetto\n• Doppio clic sulle risorse per modificarle\n• Clic destro per più opzioni\n\nDocumentazione online in arrivo!",
    "<h3>PyGameMaker Tutorials</h3>": "<h3>Tutorial PyGameMaker</h3>",
    "Coming soon! Tutorials will include:": "Prossimamente! I tutorial includeranno:",
    "\n💡 Tip: Check the documentation (F1) for quick help!": "\n💡 Suggerimento: Controlla la documentazione (F1) per aiuto rapido!",
    "Close": "Chiudi",

    # About dialog
    "PyGameMaker IDE v1.0.0\n\nA visual game development environment\ninspired by GameMaker Studio.": "PyGameMaker IDE v1.0.0\n\nUn ambiente di sviluppo giochi visuale\nispirato a GameMaker Studio.",

    # Editor messages
    "Editor": "Editor",
    "Editor for {0} not yet implemented.\nAsset: {1}": "Editor per {0} non ancora implementato.\nRisorsa: {1}",
    "Failed to open room editor: {0}": "Impossibile aprire l'editor stanza: {0}",
    "Failed to open object editor: {0}": "Impossibile aprire l'editor oggetto: {0}",

    # Create or open project
    "You need to create or open a project before importing sprites.\n\nWould you like to create a new project now?": "Devi creare o aprire un progetto prima di importare sprite.\n\nVuoi creare un nuovo progetto ora?",
    "You need to create or open a project before {0}.\n\nWould you like to:\n• Create a new project, or\n• Open an existing project?": "Devi creare o aprire un progetto prima di {0}.\n\nVuoi:\n• Creare un nuovo progetto, o\n• Aprire un progetto esistente?",
    "Create or Open Project": "Crea o apri progetto",
    "Choose project action:": "Scegli azione progetto:",

    # Toolbar items
    "Save Project": "Salva progetto",
    "Save Project As...": "Salva progetto come...",
    "Project Settings...": "Impostazioni progetto...",
    "Import": "Importa",
    "Create": "Crea",
    "Test Game": "Testa gioco",
    "Debug Game": "Debug gioco",
    "Export Game...": "Esporta gioco...",

    # Preferences Dialog
    "Preferences": "Preferenze",
    "Note: Some settings require restarting the IDE to take effect.": "Nota: Alcune impostazioni richiedono il riavvio dell'IDE per avere effetto.",
    "Font Settings": "Impostazioni carattere",
    "Font Size:": "Dimensione carattere:",
    "System Default": "Predefinito di sistema",
    "Font Family:": "Famiglia carattere:",
    "Preview: The quick brown fox jumps over the lazy dog": "Anteprima: Ma la volpe col suo balzo ha raggiunto il quieto Fido",
    "Preview:": "Anteprima:",
    "Theme Settings": "Impostazioni tema",
    "Theme:": "Tema:",
    "UI Scale:": "Scala UI:",
    "Show tooltips": "Mostra suggerimenti",
    "Appearance": "Aspetto",
    "Auto-Save Settings": "Impostazioni salvataggio automatico",
    "Enable auto-save": "Abilita salvataggio automatico",
    " minutes": " minuti",
    "Auto-save interval:": "Intervallo salvataggio automatico:",
    "Grid & Snapping": "Griglia e aggancio",
    "Show grid in editors": "Mostra griglia negli editor",
    "Grid size:": "Dimensione griglia:",
    "Snap to grid": "Aggancia alla griglia",
    "Show collision boxes": "Mostra box di collisione",
    "Editor": "Editor",
    "Project Paths": "Percorsi progetto",
    "Browse...": "Sfoglia...",
    "Default projects folder:": "Cartella progetti predefinita:",
    "Project Settings": "Impostazioni progetto",
    "Recent projects limit:": "Limite progetti recenti:",
    "Create backup on save": "Crea backup al salvataggio",
    "Project": "Progetto",
    "Debug Settings": "Impostazioni debug",
    "Enable debug mode": "Abilita modalità debug",
    "Show console output": "Mostra output console",
    "Performance": "Prestazioni",
    "Maximum undo steps:": "Passi annulla massimi:",
    "Advanced": "Avanzato",
    "Select Default Projects Directory": "Seleziona directory progetti predefinita",
    "Settings Saved": "Impostazioni salvate",
    "Settings have been saved successfully.\n\nSome changes may require restarting the IDE to take effect.": "Le impostazioni sono state salvate con successo.\n\nAlcune modifiche potrebbero richiedere il riavvio dell'IDE per avere effetto.",

    # Auto-Save Dialog
    "Auto-Save": "Salvataggio automatico",
    "Enable automatic saving": "Abilita salvataggio automatico",
    "When enabled, your project will be saved automatically at regular intervals.": "Quando abilitato, il tuo progetto verrà salvato automaticamente a intervalli regolari.",
    "Save Interval": "Intervallo salvataggio",
    " seconds": " secondi",
    "Save every:": "Salva ogni:",
    "15s": "15s",
    "30s": "30s",
    "1m": "1m",
    "2m": "2m",
    "5m": "5m",
    "Presets:": "Preimpostazioni:",
    "⚠️  Shorter intervals may impact performance on large projects.": "⚠️  Intervalli più brevi potrebbero influire sulle prestazioni su progetti grandi.",

    # Component messages
    "Actions are now managed through the Events panel": "Le azioni sono ora gestite tramite il pannello Eventi",
    "Visual scripting is now managed through the Events panel": "La programmazione visuale è ora gestita tramite il pannello Eventi",
}


def update_translations():
    """Update the Italian translation file with new translations"""

    ts_file = Path("translations/pygamemaker_it.ts")

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
    print("Italian (Italiano) Translation Updater")
    print("="*60)
    print()

    success = update_translations()

    if success:
        print("\n✓ Translation file updated successfully!")
        print("\nNext steps:")
        print("1. Run: lrelease translations/pygamemaker_it.ts -qm translations/pygamemaker_it.qm")
        print("2. Test in IDE: Tools → 🌐 Language → Italiano")
        print("3. Restart IDE to see all changes")
    else:
        print("\n✗ Translation update failed")
