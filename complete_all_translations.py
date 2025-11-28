#!/usr/bin/env python3
"""Add all 129 missing translations to French, German, and Italian translation files"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Complete translation mappings for all 129 missing strings
# Format: English -> (French, German, Italian)
TRANSLATIONS = {
    # Empty string
    "": ("", "", ""),

    # Comments and headers
    "# No events or actions have been added yet.\n": (
        "# Aucun événement ou action n'a encore été ajouté.\n",
        "# Es wurden noch keine Ereignisse oder Aktionen hinzugefügt.\n",
        "# Nessun evento o azione è stato ancora aggiunto.\n"
    ),
    "# Python code editor\n": (
        "# Éditeur de code Python\n",
        "# Python-Code-Editor\n",
        "# Editor di codice Python\n"
    ),

    # Buttons and UI elements
    "+ Add Event": ("+ Ajouter un événement", "+ Ereignis hinzufügen", "+ Aggiungi evento"),
    "- Remove Event": ("- Supprimer l'événement", "- Ereignis entfernen", "- Rimuovi evento"),
    "Add Action": ("Ajouter une action", "Aktion hinzufügen", "Aggiungi azione"),
    "Remove Action": ("Supprimer l'action", "Aktion entfernen", "Rimuovi azione"),
    "Edit Action": ("Modifier l'action", "Aktion bearbeiten", "Modifica azione"),
    "Remove Event": ("Supprimer l'événement", "Ereignis entfernen", "Rimuovi evento"),
    "↑ Move Up": ("↑ Monter", "↑ Nach oben", "↑ Sposta su"),
    "↓ Move Down": ("↓ Descendre", "↓ Nach unten", "↓ Sposta giù"),
    "✅ Apply Changes": ("✅ Appliquer les modifications", "✅ Änderungen übernehmen", "✅ Applica modifiche"),
    "✏️ Edit Custom Code": ("✏️ Modifier le code personnalisé", "✏️ Benutzerdefinierten Code bearbeiten", "✏️ Modifica codice personalizzato"),
    "🎮 Test Object": ("🎮 Tester l'objet", "🎮 Objekt testen", "🎮 Testa oggetto"),
    "💻 Code Editor": ("💻 Éditeur de code", "💻 Code-Editor", "💻 Editor di codice"),
    "💾 Save": ("💾 Enregistrer", "💾 Speichern", "💾 Salva"),
    "📋 Event List": ("📋 Liste des événements", "📋 Ereignisliste", "📋 Elenco eventi"),
    "📋 View Code": ("📋 Voir le code", "📋 Code anzeigen", "📋 Visualizza codice"),
    "📖 View Generated Code": ("📖 Voir le code généré", "📖 Generierten Code anzeigen", "📖 Visualizza codice generato"),
    "🔄 Refresh": ("🔄 Actualiser", "🔄 Aktualisieren", "🔄 Aggiorna"),
    "🧩 Visual Programming": ("🧩 Programmation visuelle", "🧩 Visuelle Programmierung", "🧩 Programmazione visuale"),

    # Labels and descriptions
    "Actions": ("Actions", "Aktionen", "Azioni"),
    "Event": ("Événement", "Ereignis", "Evento"),
    "Event ": ("Événement ", "Ereignis ", "Evento "),
    "Object ": ("Objet ", "Objekt ", "Oggetto "),
    "Room ": ("Salle ", "Raum ", "Stanza "),
    "Referenced sprite ": ("Sprite référencé ", "Referenzierter Sprite ", "Sprite referenziato "),
    "Arrow": ("Flèche", "Pfeil", "Freccia"),
    "Solid": ("Solide", "Fest", "Solido"),
    "Persistent": ("Persistant", "Persistent", "Persistente"),
    "Visible": ("Visible", "Sichtbar", "Visibile"),
    "Mode:": ("Mode :", "Modus:", "Modalità:"),
    "Sprite:": ("Sprite :", "Sprite:", "Sprite:"),
    "View Code": ("Voir le code", "Code anzeigen", "Visualizza codice"),
    "action": ("action", "Aktion", "azione"),
    "actions": ("actions", "Aktionen", "azioni"),
    "negate": ("inverser", "negieren", "nega"),
    "parameters": ("paramètres", "Parameter", "parametri"),
    "target_object": ("objet_cible", "ziel_objekt", "oggetto_destinazione"),

    # Titles and headers
    "Object Events": ("Événements de l'objet", "Objektereignisse", "Eventi oggetto"),
    "Object Properties": ("Propriétés de l'objet", "Objekteigenschaften", "Proprietà oggetto"),
    "Collision Event Options": ("Options de l'événement de collision", "Kollisionsereignisoptionen", "Opzioni evento collisione"),
    "Configuration Saved": ("Configuration enregistrée", "Konfiguration gespeichert", "Configurazione salvata"),
    "Code Applied": ("Code appliqué", "Code angewendet", "Codice applicato"),
    "Event Exists": ("L'événement existe", "Ereignis existiert", "L'evento esiste"),
    "Key Event Exists": ("L'événement de touche existe", "Tastenereignis existiert", "L'evento tasto esiste"),
    "Mouse Event Exists": ("L'événement de souris existe", "Mausereignis existiert", "L'evento mouse esiste"),
    "Collision Event Exists": ("L'événement de collision existe", "Kollisionsereignis existiert", "L'evento collisione esiste"),
    "Cannot Add Action": ("Impossible d'ajouter une action", "Aktion kann nicht hinzugefügt werden", "Impossibile aggiungere azione"),
    "Remove Collision Event": ("Supprimer l'événement de collision", "Kollisionsereignis entfernen", "Rimuovi evento collisione"),
    "Remove Key Event": ("Supprimer l'événement de touche", "Tastenereignis entfernen", "Rimuovi evento tasto"),
    "Remove Mouse Event": ("Supprimer l'événement de souris", "Mausereignis entfernen", "Rimuovi evento mouse"),
    "Validation Error": ("Erreur de validation", "Validierungsfehler", "Errore di validazione"),

    # Messages with formatting
    "<b>Collision with: {0}</b>": ("<b>Collision avec : {0}</b>", "<b>Kollision mit: {0}</b>", "<b>Collisione con: {0}</b>"),
    "Event: {0}": ("Événement : {0}", "Ereignis: {0}", "Evento: {0}"),
    "Editing event: {0}": ("Modification de l'événement : {0}", "Ereignis bearbeiten: {0}", "Modifica evento: {0}"),
    "Object: {0} | Sprite: {1}": ("Objet : {0} | Sprite : {1}", "Objekt: {0} | Sprite: {1}", "Oggetto: {0} | Sprite: {1}"),
    "Selected action: {0} ({1})": ("Action sélectionnée : {0} ({1})", "Ausgewählte Aktion: {0} ({1})", "Azione selezionata: {0} ({1})"),
    "Saved: {0}": ("Enregistré : {0}", "Gespeichert: {0}", "Salvato: {0}"),
    "Cannot save: {0}": ("Impossible d'enregistrer : {0}", "Speichern nicht möglich: {0}", "Impossibile salvare: {0}"),
    "{0} actions": ("{0} actions", "{0} Aktionen", "{0} azioni"),
    "{0} total actions": ("{0} actions au total", "{0} Aktionen insgesamt", "{0} azioni totali"),

    # Long messages
    "Actions are managed through the Object Events panel on the left.\n\n": (
        "Les actions sont gérées par le panneau Événements de l'objet à gauche.\n\n",
        "Aktionen werden über das Objektereignisfenster auf der linken Seite verwaltet.\n\n",
        "Le azioni sono gestite tramite il pannello Eventi oggetto a sinistra.\n\n"
    ),
    "Cannot add actions directly to %1.\n\n": (
        "Impossible d'ajouter des actions directement à %1.\n\n",
        "Aktionen können nicht direkt zu %1 hinzugefügt werden.\n\n",
        "Impossibile aggiungere azioni direttamente a %1.\n\n"
    ),

    # Questions and confirmations
    "Are you sure you want to remove this action?": (
        "Voulez-vous vraiment supprimer cette action ?",
        "Möchten Sie diese Aktion wirklich entfernen?",
        "Sei sicuro di voler rimuovere questa azione?"
    ),
    "Are you sure you want to remove the {0} event?": (
        "Voulez-vous vraiment supprimer l'événement {0} ?",
        "Möchten Sie das Ereignis {0} wirklich entfernen?",
        "Sei sicuro di voler rimuovere l'evento {0}?"
    ),
    "Are you sure you want to remove the {0} event and all its actions?": (
        "Voulez-vous vraiment supprimer l'événement {0} et toutes ses actions ?",
        "Möchten Sie das Ereignis {0} und alle seine Aktionen wirklich entfernen?",
        "Sei sicuro di voler rimuovere l'evento {0} e tutte le sue azioni?"
    ),
    "Are you sure you want to remove the {0} arrow key event and all its actions?": (
        "Voulez-vous vraiment supprimer l'événement de touche fléchée {0} et toutes ses actions ?",
        "Möchten Sie das Pfeiltastenereignis {0} und alle seine Aktionen wirklich entfernen?",
        "Sei sicuro di voler rimuovere l'evento tasto freccia {0} e tutte le sue azioni?"
    ),
    "Are you sure you want to remove the collision event with {0}?": (
        "Voulez-vous vraiment supprimer l'événement de collision avec {0} ?",
        "Möchten Sie das Kollisionsereignis mit {0} wirklich entfernen?",
        "Sei sicuro di voler rimuovere l'evento collisione con {0}?"
    ),

    # Status messages
    "Assets loaded: {0} sprites": ("Ressources chargées : {0} sprites", "Assets geladen: {0} Sprites", "Risorse caricate: {0} sprite"),
    "Loaded {0} sprites": ("{0} sprites chargés", "{0} Sprites geladen", "{0} sprite caricati"),
    "Applied {0} events from visual blocks": ("{0} événements appliqués depuis les blocs visuels", "{0} Ereignisse aus visuellen Blöcken angewendet", "{0} eventi applicati da blocchi visivi"),
    "Custom code applied to {0} event": ("Code personnalisé appliqué à l'événement {0}", "Benutzerdefinierter Code auf Ereignis {0} angewendet", "Codice personalizzato applicato all'evento {0}"),
    "Generated code view updated": ("Vue du code généré mise à jour", "Generierte Code-Ansicht aktualisiert", "Vista codice generato aggiornata"),
    "Object: Not loaded": ("Objet : Non chargé", "Objekt: Nicht geladen", "Oggetto: Non caricato"),

    # Descriptions and tooltips
    "Object is visible in the game": ("L'objet est visible dans le jeu", "Objekt ist im Spiel sichtbar", "L'oggetto è visibile nel gioco"),
    "Object persists between rooms": ("L'objet persiste entre les salles", "Objekt bleibt zwischen Räumen bestehen", "L'oggetto persiste tra le stanze"),
    "Solid objects block movement": ("Les objets solides bloquent le mouvement", "Feste Objekte blockieren Bewegung", "Gli oggetti solidi bloccano il movimento"),
    "Sprite to display for this object": ("Sprite à afficher pour cet objet", "Sprite, der für dieses Objekt angezeigt wird", "Sprite da visualizzare per questo oggetto"),
    "Check this to trigger actions when the object is NOT colliding with the target": (
        "Cochez ceci pour déclencher des actions lorsque l'objet N'est PAS en collision avec la cible",
        "Aktivieren Sie dies, um Aktionen auszulösen, wenn das Objekt NICHT mit dem Ziel kollidiert",
        "Seleziona questo per attivare azioni quando l'oggetto NON è in collisione con il bersaglio"
    ),
    "❌ NOT colliding (trigger when NOT touching)": (
        "❌ NON en collision (déclencher quand PAS en contact)",
        "❌ NICHT kollidierend (auslösen, wenn NICHT berührt)",
        "❌ NON in collisione (attiva quando NON tocca)"
    ),
    "Move selected action up (Ctrl+Up)": ("Monter l'action sélectionnée (Ctrl+Haut)", "Ausgewählte Aktion nach oben verschieben (Strg+Oben)", "Sposta azione selezionata su (Ctrl+Su)"),
    "Move selected action down (Ctrl+Down)": ("Descendre l'action sélectionnée (Ctrl+Bas)", "Ausgewählte Aktion nach unten verschieben (Strg+Unten)", "Sposta azione selezionata giù (Ctrl+Giù)"),
    "Ctrl+Up": ("Ctrl+Haut", "Strg+Oben", "Ctrl+Su"),
    "Ctrl+Down": ("Ctrl+Bas", "Strg+Unten", "Ctrl+Giù"),
    "Save object (Ctrl+S)": ("Enregistrer l'objet (Ctrl+S)", "Objekt speichern (Strg+S)", "Salva oggetto (Ctrl+S)"),
    "Edit Python code or view generated code": ("Modifier le code Python ou voir le code généré", "Python-Code bearbeiten oder generierten Code anzeigen", "Modifica codice Python o visualizza codice generato"),
    "Edit mode: Write custom Python code": ("Mode édition : Écrire du code Python personnalisé", "Bearbeitungsmodus: Benutzerdefinierten Python-Code schreiben", "Modalità modifica: Scrivi codice Python personalizzato"),
    "View mode: Showing generated code from events": ("Mode visualisation : Affichage du code généré depuis les événements", "Anzeigemodus: Zeigt generierten Code aus Ereignissen", "Modalità visualizzazione: Mostra codice generato da eventi"),
    "Show generated code in Code Editor tab": ("Afficher le code généré dans l'onglet Éditeur de code", "Generierten Code im Code-Editor-Tab anzeigen", "Mostra codice generato nella scheda Editor di codice"),
    "Scratch-like block programming": ("Programmation par blocs type Scratch", "Scratch-ähnliche Blockprogrammierung", "Programmazione a blocchi in stile Scratch"),
    "Event for custom code:": ("Événement pour le code personnalisé :", "Ereignis für benutzerdefinierten Code:", "Evento per codice personalizzato:"),

    # Error messages
    "Error loading assets: {0}": ("Erreur lors du chargement des ressources : {0}", "Fehler beim Laden der Assets: {0}", "Errore nel caricamento delle risorse: {0}"),
    "Error saving object: {0}": ("Erreur lors de l'enregistrement de l'objet : {0}", "Fehler beim Speichern des Objekts: {0}", "Errore nel salvataggio dell'oggetto: {0}"),
    "Validation error: {0}": ("Erreur de validation : {0}", "Validierungsfehler: {0}", "Errore di validazione: {0}"),
    "Failed to run game:\n\n{0}\n\nCheck console for details.": (
        "Échec du lancement du jeu :\n\n{0}\n\nConsultez la console pour plus de détails.",
        "Spiel konnte nicht ausgeführt werden:\n\n{0}\n\nÜberprüfen Sie die Konsole für Details.",
        "Impossibile avviare il gioco:\n\n{0}\n\nControlla la console per i dettagli."
    ),

    # Validation and requirements
    "Object name is required": ("Le nom de l'objet est requis", "Objektname ist erforderlich", "Il nome dell'oggetto è obbligatorio"),
    "No event selected": ("Aucun événement sélectionné", "Kein Ereignis ausgewählt", "Nessun evento selezionato"),
    "No objects available": ("Aucun objet disponible", "Keine Objekte verfügbar", "Nessun oggetto disponibile"),
    "Project validation found the following issues:\n\n": (
        "La validation du projet a trouvé les problèmes suivants :\n\n",
        "Die Projektvalidierung hat folgende Probleme gefunden:\n\n",
        "La validazione del progetto ha trovato i seguenti problemi:\n\n"
    ),

    # Event type messages
    "The {0} event already exists.": ("L'événement {0} existe déjà.", "Das Ereignis {0} existiert bereits.", "L'evento {0} esiste già."),
    "The {0} arrow key event already exists.": ("L'événement de touche fléchée {0} existe déjà.", "Das Pfeiltastenereignis {0} existiert bereits.", "L'evento tasto freccia {0} esiste già."),
    "The {0} key event already exists for {1}.": ("L'événement de touche {0} existe déjà pour {1}.", "Das Tastenereignis {0} existiert bereits für {1}.", "L'evento tasto {0} esiste già per {1}."),
    "This collision event already exists.": ("Cet événement de collision existe déjà.", "Dieses Kollisionsereignis existiert bereits.", "Questo evento collisione esiste già."),
    "This mouse event already exists.": ("Cet événement de souris existe déjà.", "Dieses Mausereignis existiert bereits.", "Questo evento mouse esiste già."),

    # Custom code messages
    "Custom Python code has been applied to the {0} event.\n\n": (
        "Du code Python personnalisé a été appliqué à l'événement {0}.\n\n",
        "Benutzerdefinierter Python-Code wurde auf das Ereignis {0} angewendet.\n\n",
        "Il codice Python personalizzato è stato applicato all'evento {0}.\n\n"
    ),

    # Configuration and settings
    "Blockly configuration has been saved.\n\n": (
        "La configuration Blockly a été enregistrée.\n\n",
        "Die Blockly-Konfiguration wurde gespeichert.\n\n",
        "La configurazione Blockly è stata salvata.\n\n"
    ),
    "Configure &Blockly Blocks...": ("Configurer les blocs &Blockly...", "&Blockly-Blöcke konfigurieren...", "Configura blocchi &Blockly..."),
    "Settings have been saved successfully.\n\n": (
        "Les paramètres ont été enregistrés avec succès.\n\n",
        "Die Einstellungen wurden erfolgreich gespeichert.\n\n",
        "Le impostazioni sono state salvate con successo.\n\n"
    ),
    "Debug mode will start the game with verbose console output.\n\n": (
        "Le mode débogage lancera le jeu avec une sortie console détaillée.\n\n",
        "Der Debug-Modus startet das Spiel mit ausführlicher Konsolenausgabe.\n\n",
        "La modalità debug avvierà il gioco con output console dettagliato.\n\n"
    ),
    "Language changed to {0}.\n\n": (
        "Langue changée en {0}.\n\n",
        "Sprache geändert zu {0}.\n\n",
        "Lingua cambiata in {0}.\n\n"
    ),

    # Not implemented messages (shortened versions from line 17, 34, 70, 71, 90, 91)
    "Asset Manager is not yet implemented.\n\n": (
        "Le gestionnaire de ressources n'est pas encore implémenté.\n\n",
        "Der Asset-Manager ist noch nicht implementiert.\n\n",
        "Il gestore delle risorse non è ancora implementato.\n\n"
    ),
    "Documentation is not yet available.\n\n": (
        "La documentation n'est pas encore disponible.\n\n",
        "Die Dokumentation ist noch nicht verfügbar.\n\n",
        "La documentazione non è ancora disponibile.\n\n"
    ),
    "Project cleanup is not yet implemented.\n\n": (
        "Le nettoyage du projet n'est pas encore implémenté.\n\n",
        "Die Projektbereinigung ist noch nicht implementiert.\n\n",
        "La pulizia del progetto non è ancora implementata.\n\n"
    ),
    "Project structure is valid!\n\n": (
        "La structure du projet est valide !\n\n",
        "Die Projektstruktur ist gültig!\n\n",
        "La struttura del progetto è valida!\n\n"
    ),
    "Standalone build is not yet implemented.\n\n": (
        "La construction autonome n'est pas encore implémentée.\n\n",
        "Standalone-Build ist noch nicht implementiert.\n\n",
        "La build autonoma non è ancora implementata.\n\n"
    ),
    "Standalone executable building is not yet implemented.\n\n": (
        "La création d'exécutables autonomes n'est pas encore implémentée.\n\n",
        "Das Erstellen von Standalone-Executables ist noch nicht implementiert.\n\n",
        "La creazione di eseguibili autonomi non è ancora implementata.\n\n"
    ),
    "This feature will be available in a future update.\n\n": (
        "Cette fonctionnalité sera disponible dans une future mise à jour.\n\n",
        "Diese Funktion wird in einem zukünftigen Update verfügbar sein.\n\n",
        "Questa funzionalità sarà disponibile in un aggiornamento futuro.\n\n"
    ),
    "This export format is not yet available.\n\n": (
        "Ce format d'export n'est pas encore disponible.\n\n",
        "Dieses Exportformat ist noch nicht verfügbar.\n\n",
        "Questo formato di esportazione non è ancora disponibile.\n\n"
    ),
    "Editor for {0} not yet implemented.\n": (
        "Éditeur pour {0} pas encore implémenté.\n",
        "Editor für {0} noch nicht implementiert.\n",
        "Editor per {0} non ancora implementato.\n"
    ),
    "Object testing not implemented yet": (
        "Test d'objet pas encore implémenté",
        "Objekttest noch nicht implementiert",
        "Test oggetto non ancora implementato"
    ),
    "This will build a standalone executable and run it.\n\n": (
        "Cela créera un exécutable autonome et le lancera.\n\n",
        "Dies erstellt eine eigenständige ausführbare Datei und führt sie aus.\n\n",
        "Questo creerà un eseguibile autonomo e lo eseguirà.\n\n"
    ),

    # Project messages
    "Please open or create a project first before testing a game.": (
        "Veuillez d'abord ouvrir ou créer un projet avant de tester un jeu.",
        "Bitte öffnen oder erstellen Sie zuerst ein Projekt, bevor Sie ein Spiel testen.",
        "Apri o crea prima un progetto prima di testare un gioco."
    ),
    "Please open or create a project first before exporting a game.": (
        "Veuillez d'abord ouvrir ou créer un projet avant d'exporter un jeu.",
        "Bitte öffnen oder erstellen Sie zuerst ein Projekt, bevor Sie ein Spiel exportieren.",
        "Apri o crea prima un progetto prima di esportare un gioco."
    ),
    "You need to create or open a project before importing sprites.\n\n": (
        "Vous devez créer ou ouvrir un projet avant d'importer des sprites.\n\n",
        "Sie müssen ein Projekt erstellen oder öffnen, bevor Sie Sprites importieren.\n\n",
        "Devi creare o aprire un progetto prima di importare sprite.\n\n"
    ),
    "You need to create or open a project before {0}.\n\n": (
        "Vous devez créer ou ouvrir un projet avant {0}.\n\n",
        "Sie müssen ein Projekt erstellen oder öffnen, bevor {0}.\n\n",
        "Devi creare o aprire un progetto prima di {0}.\n\n"
    ),
    "Would you like to export the current project as a zip file now?\n\n": (
        "Voulez-vous exporter le projet actuel en fichier zip maintenant ?\n\n",
        "Möchten Sie das aktuelle Projekt jetzt als Zip-Datei exportieren?\n\n",
        "Vuoi esportare il progetto corrente come file zip ora?\n\n"
    ),
    "Translation file for {0} is not available.\n\n": (
        "Le fichier de traduction pour {0} n'est pas disponible.\n\n",
        "Die Übersetzungsdatei für {0} ist nicht verfügbar.\n\n",
        "Il file di traduzione per {0} non è disponibile.\n\n"
    ),

    # Tips
    "\n💡 Tip: Check the documentation (F1) for quick help!": (
        "\n💡 Astuce : Consultez la documentation (F1) pour une aide rapide !",
        "\n💡 Tipp: Überprüfen Sie die Dokumentation (F1) für schnelle Hilfe!",
        "\n💡 Suggerimento: Controlla la documentazione (F1) per un aiuto rapido!"
    ),
}

def update_translation_file(ts_file, lang_index):
    """Update a single translation file with missing strings

    Args:
        ts_file: Path to the .ts translation file
        lang_index: 0 for French, 1 for German, 2 for Italian
    """
    lang_names = ['French', 'German', 'Italian']
    lang_name = lang_names[lang_index]

    print(f"\n{'='*60}")
    print(f"Updating {lang_name} translations...")
    print(f"{'='*60}")

    tree = ET.parse(ts_file)
    root = tree.getroot()

    updated_count = 0
    added_count = 0

    for source_text, translations in TRANSLATIONS.items():
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
                        break
            if found:
                break

        if not found:
            # Determine context based on string content
            if any(keyword in source_text.lower() for keyword in ['event', 'action', 'collision', 'key', 'mouse']):
                context_name = 'ObjectEditor'
            elif 'blockly' in source_text.lower():
                context_name = 'BlocklyConfig'
            elif any(keyword in source_text.lower() for keyword in ['project', 'export', 'import']):
                context_name = 'PyGameMakerIDE'
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

    # Write updated file
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    print(f"✓ Updated: {updated_count} existing translations")
    print(f"+ Added: {added_count} new translations")
    print(f"{'='*60}")

    return updated_count, added_count

# Update all three translation files
results = {}
for lang, (ts_file, idx) in [
    ('French', ('translations/pygamemaker_fr.ts', 0)),
    ('German', ('translations/pygamemaker_de.ts', 1)),
    ('Italian', ('translations/pygamemaker_it.ts', 2))
]:
    updated, added = update_translation_file(ts_file, idx)
    results[lang] = (updated, added)

print(f"\n{'='*60}")
print("SUMMARY - All translations updated!")
print(f"{'='*60}")
for lang, (updated, added) in results.items():
    print(f"{lang:8s}: {updated:3d} updated, {added:3d} added = {updated+added:3d} total")
print(f"{'='*60}")
print("\nNext step: Compile .qm files with pyside6-lrelease")
