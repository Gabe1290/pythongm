#!/usr/bin/env python3
"""Localized text for the Blockly workspace CANVAS's auto-generated blocks.

TODO.md (found 2026-10-16): every action in `config.blockly_config.
GENERATED_ACTION_NAMES` (~80 actions with no hand-written Blockly block)
rendered its block face -- the top label, every parameter's inline field
label, and the tooltip -- in raw English regardless of the IDE's selected
language, because `editors/object_editor/blockly_widget.py`'s
`_register_custom_blocks()` sent `ActionType.display_name`/`description`/
parameter `display_name` straight to `blockly_workspace.html`'s
`registerCustomBlocks()` with zero language awareness. This is a
SEPARATE i18n table/surface from `config.blockly_translations` (which
covers the "Configure Action Blocks" dialog, a different UI) -- the two
can and do translate the same action name independently.

Scoping decision made 2026-10-18 (the two directions TODO.md left open:
"(a) a per-language table" vs "(b) hand-write blocks for common
actions"): **direction (a)**, reusing the existing generic
`registerCustomBlocks()` pipeline (no new JS, no per-block duplication)
by substituting translated strings into the exact same JSON fields on
the Python side before they're sent -- `blockly_workspace.html` needed
zero changes.

**French only, this pass** -- matching this project's established
"French first, English-fallback the rest" precedent (the ja/zh/pt UI
arcs, the wiki translation rollout). The action-level `display_name`/
`description` text cost nothing fresh: every one of the 79 generated
actions already had a real French translation sitting in either
`config.blockly_translations.BLOCK_TRANSLATIONS` (the Configure dialog
fix, 2026-10-18 -- 31 of 79 actions, since Game/Views/Particles/Timing
blocks are both dialog-listed AND canvas-generated) or
`tools/action_ref_i18n.py`'s `ACTIONS_FR` (the wiki action reference,
48 of 79) -- ported here mechanically, not retranslated. Parameter
FIELD labels had no existing source anywhere (`ACTIONS_FR`'s companion
`NOTES_FR` is keyed by exact English wiki-note sentences, not short
field labels) -- `PARAM_LABEL_TRANSLATIONS` below is fresh work, but
119 distinct strings (not 181 -- most of the 79 actions' parameters
reuse common names like "Speed"/"Object"/"X"/"Y") made that tractable
in one sitting.

**Not done here, left as a follow-up** (logged in TODO.md): the other
9 shipped languages. de/uk/ru/it/es/pt/sl can mechanically reuse
`tools/action_ref_i18n.py`'s own `ACTIONS_<LANG>` tables for the
action-level half exactly as fr did here (zero fresh cost); ja/zh have
no existing action-reference translation at all, so even that half
would be fresh work for those two. Every language's 119 param labels
need fresh translation regardless -- there is no existing source for
them in any language yet.

English ('en') and any language with no entry here fall back to the
raw ActionType text, via `get_translated_action_display_name` /
`get_translated_action_description` / `get_translated_param_label`.
"""

# --------------------------------------------------------------------------- #
# Per-action display_name + description, keyed by the stable action name.
# Covers every name in config.blockly_config.GENERATED_ACTION_NAMES.
# --------------------------------------------------------------------------- #

ACTION_TRANSLATIONS = {
    "bounce": {"fr": {"display_name": "Rebondir", "description": "Rebondir sur les objets solides"}},
    "burst_particles": {"fr": {"display_name": "Explosion de particules", "description": "Émettre particules une fois"}},
    "change_instance": {"fr": {"display_name": "Changer d'instance", "description": "Se transformer en un autre type d'objet"}},
    "check_empty": {"fr": {"display_name": "Vérifier Vide", "description": "Vrai quand (x, y) n'a aucune collision — conditionne la/les action(s) suivante(s) en déplacement sur grille"}},
    "check_room": {"fr": {"display_name": "Vérifier salle", "description": "Vérifier si dans la salle"}},
    "clear_highscore": {"fr": {"display_name": "Effacer le tableau des scores", "description": "Effacer toutes les entrées du tableau des scores"}},
    "clear_particles": {"fr": {"display_name": "Effacer toutes les particules", "description": "Supprimer toutes les particules actives"}},
    "comment": {"fr": {"display_name": "Commentaire", "description": "Un commentaire dans la liste d'actions (sans effet à l'exécution)"}},
    "create_emitter": {"fr": {"display_name": "Créer émetteur", "description": "Créer émetteur de particules"}},
    "create_moving_instance": {"fr": {"display_name": "Créer une instance en mouvement", "description": "Créer une instance et la faire se déplacer dans une direction"}},
    "create_particle_system": {"fr": {"display_name": "Créer système de particules", "description": "Créer nouveau système de particules"}},
    "create_particle_type": {"fr": {"display_name": "Créer type de particule", "description": "Définir nouveau type de particule"}},
    "create_random_instance": {"fr": {"display_name": "Créer une instance aléatoire", "description": "Créer l'un de plusieurs types d'objets choisi au hasard"}},
    "destroy_at_position": {"fr": {"display_name": "Détruire à une position", "description": "Détruire les instances dans un rayon autour de (x, y)"}},
    "destroy_emitter": {"fr": {"display_name": "Détruire émetteur", "description": "Supprimer émetteur de particules"}},
    "destroy_particle_system": {"fr": {"display_name": "Détruire système de particules", "description": "Supprimer système de particules"}},
    "draw_arrow": {"fr": {"display_name": "Dessiner une flèche", "description": "Dessiner une flèche d'un point à un autre"}},
    "draw_background": {"fr": {"display_name": "Dessiner un arrière-plan", "description": "Dessiner une image d'arrière-plan, éventuellement répétée sur tout l'écran"}},
    "draw_ellipse": {"fr": {"display_name": "Dessiner une ellipse", "description": "Dessiner une ellipse pleine ou en contour dans un cadre englobant"}},
    "draw_line": {"fr": {"display_name": "Dessiner une ligne", "description": "Dessiner une ligne entre deux points"}},
    "draw_scaled_text": {"fr": {"display_name": "Dessiner du texte mis à l'échelle", "description": "Dessiner du texte à une échelle arbitraire"}},
    "draw_sprite": {"fr": {"display_name": "Dessiner un sprite", "description": "Dessiner une image de sprite à une position"}},
    "draw_variable": {"fr": {"display_name": "Afficher variable", "description": "Afficher valeur de variable"}},
    "else_action": {"fr": {"display_name": "Sinon", "description": "Exécute l'action suivante seulement si le test précédent était faux — associer à Début/Fin de Bloc pour mettre plus d'une action du côté sinon"}},
    "enable_views": {"fr": {"display_name": "Activer les Vues", "description": "Active ou désactive le système de caméra/vue de la salle (permet à un niveau de défiler s'il est plus grand que la fenêtre)"}},
    "end_block": {"fr": {"display_name": "Fin de Bloc", "description": "Ferme un groupe Début de Bloc"}},
    "execute_script": {"fr": {"display_name": "Exécuter un script", "description": "Exécuter l'un des scripts du projet"}},
    "fill_color": {"fr": {"display_name": "Remplir l'écran d'une couleur", "description": "Remplir toute la zone d'affichage d'une couleur unie"}},
    "game_end": {"fr": {"display_name": "Terminer le jeu", "description": "Terminer le jeu"}},
    "if_collision": {"fr": {"display_name": "Si collision", "description": "Condition : vrai si l'instance entrerait en collision au décalage (x, y)"}},
    "if_collision_at": {"fr": {"display_name": "Si collision à", "description": "Vérifier une collision à une position"}},
    "if_object_exists": {"fr": {"display_name": "Si l'objet existe", "description": "Condition : vrai s'il existe au moins une instance de l'objet"}},
    "jump_to_random": {"fr": {"display_name": "Sauter à une position aléatoire", "description": "Se téléporter à une position aléatoire (éventuellement alignée sur la grille)"}},
    "jump_to_start": {"fr": {"display_name": "Sauter à la position de départ", "description": "Ramener l'instance à sa position de création"}},
    "load_game": {"fr": {"display_name": "Charger la Partie", "description": "Restaure la salle, le score/vies/santé, les variables globales et les états d'instance depuis un fichier de sauvegarde"}},
    "move_grid": {"fr": {"display_name": "Déplacer sur la grille", "description": "Se déplacer d'une case de grille dans la direction indiquée"}},
    "move_to_contact": {"fr": {"display_name": "Déplacer jusqu'au contact", "description": "Se déplacer dans une direction jusqu'à toucher un objet (ou une distance maximale)"}},
    "move_towards_point": {"fr": {"display_name": "Se déplacer vers un point", "description": "Se déplacer vers un point à une vitesse donnée"}},
    "open_webpage": {"fr": {"display_name": "Ouvrir une Page Web", "description": "Ouvre une URL dans le navigateur par défaut"}},
    "pause_timeline": {"fr": {"display_name": "Mettre en pause timeline", "description": "Mettre en pause lecture de timeline"}},
    "repeat": {"fr": {"display_name": "Répéter", "description": "Répéter l'action/le bloc suivant N fois"}},
    "restart_game": {"fr": {"display_name": "Redémarrer le Jeu", "description": "Redémarre depuis la première salle"}},
    "save_game": {"fr": {"display_name": "Sauvegarder la Partie", "description": "Enregistre la salle actuelle, le score/vies/santé, les variables globales et les états d'instance dans un fichier"}},
    "set_background": {"fr": {"display_name": "Définir l'arrière-plan", "description": "Définir l'image d'arrière-plan de la salle actuelle, avec des options de répétition et de défilement"}},
    "set_background_color": {"fr": {"display_name": "Définir la couleur d'arrière-plan", "description": "Changer la couleur d'arrière-plan de la salle actuelle"}},
    "set_color": {"fr": {"display_name": "Définir la couleur", "description": "Définir la couleur et l'alpha de dessin pour les dessins suivants"}},
    "set_direction_speed": {"fr": {"display_name": "Définir direction et vitesse", "description": "Définir la direction (en degrés) et la magnitude de vitesse de l'instance"}},
    "set_draw_color": {"fr": {"display_name": "Définir la couleur de dessin", "description": "Définir la couleur utilisée par les actions draw_* suivantes"}},
    "set_draw_font": {"fr": {"display_name": "Définir la police de dessin", "description": "Définir la police et l'alignement pour le dessin de texte suivant"}},
    "set_image_index": {"fr": {"display_name": "Définir l'image d'animation", "description": "Définir l'image d'animation actuelle du sprite de l'instance"}},
    "set_image_speed": {"fr": {"display_name": "Définir la vitesse d'animation", "description": "Définir la vitesse de lecture de l'animation du sprite de l'instance"}},
    "set_room_caption": {"fr": {"display_name": "Définir le titre de la salle", "description": "Définir le titre de la fenêtre de jeu"}},
    "set_room_persistent": {"fr": {"display_name": "Définir la persistance de la salle", "description": "Si la salle actuelle conserve son état actif (positions des instances, instances détruites, etc.) quand le joueur la quitte puis y revient, au lieu de la reconstruire entièrement depuis sa disposition d'origine à chaque visite"}},
    "set_room_speed": {"fr": {"display_name": "Définir la vitesse de la salle", "description": "Changer la fréquence d'images du jeu (images par seconde)"}},
    "set_timeline": {"fr": {"display_name": "Définir timeline", "description": "Définir la timeline de l'instance"}},
    "set_timeline_position": {"fr": {"display_name": "Définir position timeline", "description": "Définir position actuelle dans timeline"}},
    "set_timeline_speed": {"fr": {"display_name": "Définir vitesse timeline", "description": "Vitesse de lecture de la timeline"}},
    "set_view": {"fr": {"display_name": "Définir une Vue", "description": "Configure une vue de caméra : quelle partie de la salle elle montre, où elle s'affiche à l'écran, et un objet à suivre"}},
    "set_window_caption": {"fr": {"display_name": "Définir le Titre de Fenêtre", "description": "Configure l'affichage du score/vies/santé dans le titre de la fenêtre"}},
    "show_highscore": {"fr": {"display_name": "Afficher le tableau des scores", "description": "Afficher la boîte de dialogue du tableau des meilleurs scores"}},
    "show_info": {"fr": {"display_name": "Afficher Infos du Jeu", "description": "Affiche l'écran d'informations du jeu"}},
    "show_video": {"fr": {"display_name": "Afficher une Vidéo", "description": "Lit un fichier vidéo dans le lecteur vidéo par défaut du système"}},
    "sleep": {"fr": {"display_name": "Attendre", "description": "Mettre le jeu en pause pendant un certain nombre de millisecondes, puis continuer. Les sons continuent de jouer pendant la pause (par exemple pour laisser un son se terminer avant de changer de salle). Remarque : le rendu et les entrées sont figés pendant l'attente, gardez donc des durées courtes."}},
    "splash_show_image": {"fr": {"display_name": "Splash : Afficher une Image", "description": "Affiche un sprite en plein écran et met le jeu en pause jusqu'à ce que le joueur le ferme"}},
    "splash_show_text": {"fr": {"display_name": "Splash : Afficher un Texte", "description": "Affiche un message et met le jeu en pause jusqu'à ce que le joueur le ferme"}},
    "start_animation": {"fr": {"display_name": "Démarrer l'animation", "description": "Reprendre l'animation du sprite de l'instance (image_speed = 1)"}},
    "start_block": {"fr": {"display_name": "Début de Bloc", "description": "Regroupe plusieurs actions pour qu'une condition précédente s'applique à toutes, pas seulement à la suivante"}},
    "start_moving_direction": {"fr": {"display_name": "Commencer à bouger (direction)", "description": "Commencer à se déplacer dans une direction à une vitesse donnée"}},
    "start_timeline": {"fr": {"display_name": "Démarrer timeline", "description": "Démarrer lecture de timeline"}},
    "stop_animation": {"fr": {"display_name": "Arrêter l'animation", "description": "Mettre en pause l'animation du sprite de l'instance (image_speed = 0)"}},
    "stop_timeline": {"fr": {"display_name": "Arrêter timeline", "description": "Arrêter et réinitialiser timeline"}},
    "stream_particles": {"fr": {"display_name": "Flux de particules", "description": "Émettre particules en continu"}},
    "test_alignment": {"fr": {"display_name": "Tester l'alignement sur la grille", "description": "Condition : vrai si l'instance est alignée sur une grille"}},
    "test_chance": {"fr": {"display_name": "Tester la chance", "description": "Condition : vrai avec une probabilité de 1 sur « sides »"}},
    "test_health": {"fr": {"display_name": "Tester la santé", "description": "Condition : comparer la santé actuelle à une valeur"}},
    "test_instance_count": {"fr": {"display_name": "Tester le nombre d'instances", "description": "Condition : comparer le nombre d'instances d'un objet"}},
    "test_lives": {"fr": {"display_name": "Tester les vies", "description": "Condition : comparer le nombre de vies à une valeur"}},
    "test_question": {"fr": {"display_name": "Poser une question", "description": "Condition : afficher une boîte de dialogue oui/non ; vrai si l'utilisateur répond oui"}},
    "test_score": {"fr": {"display_name": "Tester le score", "description": "Condition : comparer le score à une valeur"}},
}

# --------------------------------------------------------------------------- #
# Parameter FIELD label translations, keyed by the exact English
# ActionParameter.display_name string (not by action+param -- the same
# label is reused across many actions, e.g. "Speed", "Object", "X"/"Y").
# No existing source anywhere for these; fresh translation.
# --------------------------------------------------------------------------- #

PARAM_LABEL_TRANSLATIONS = {
    "fr": {
        "Actions": "Actions",
        "Against": "Contre",
        "Allow New Entry": "Autoriser une nouvelle entrée",
        "Alpha": "Alpha",
        "Argument 0": "Argument 0",
        "Argument 1": "Argument 1",
        "Argument 2": "Argument 2",
        "Argument 3": "Argument 3",
        "Argument 4": "Argument 4",
        "Background": "Arrière-plan",
        "Background Color": "Couleur d'arrière-plan",
        "Caption": "Légende",
        "Caption Prefix": "Préfixe de légende",
        "Change Into": "Changer en",
        "Color": "Couleur",
        "Comment": "Commentaire",
        "Comparison": "Comparaison",
        "Depth": "Profondeur",
        "Direction": "Direction",
        "Direction Expression": "Expression de direction",
        "Direction Max": "Direction max",
        "Direction Min": "Direction min",
        "Directions": "Directions",
        "Else Actions": "Actions sinon",
        "Enable": "Activer",
        "Filename": "Nom de fichier",
        "Filled": "Rempli",
        "Follow Object": "Objet à suivre",
        "Font": "Police",
        "Foreground": "Premier plan",
        "Frame": "Image",
        "Fullscreen": "Plein écran",
        "Grid Size": "Taille de la grille",
        "H Border": "Bordure H",
        "Height": "Hauteur",
        "Horizontal Align": "Alignement horizontal",
        "Horizontal Scroll Speed": "Vitesse de défilement horizontal",
        "Horizontal Snap": "Accrochage horizontal",
        "Life Max (steps)": "Durée de vie max (étapes)",
        "Life Min (steps)": "Durée de vie min (étapes)",
        "Max Distance": "Distance max",
        "Max H Scroll": "Défilement H max",
        "Max V Scroll": "Défilement V max",
        "Milliseconds": "Millisecondes",
        "Negate": "Négation",
        "New Entry Color": "Couleur nouvelle entrée",
        "Number": "Nombre",
        "Number/Step": "Nombre/pas",
        "Object": "Objet",
        "Object 1": "Objet 1",
        "Object 2": "Objet 2",
        "Object 3": "Objet 3",
        "Object 4": "Objet 4",
        "Object Type": "Type d'objet",
        "Objects": "Objets",
        "Operation": "Opération",
        "Other Entries Color": "Couleur des autres entrées",
        "Particle Type": "Type de particule",
        "Perform Events": "Exécuter les événements",
        "Persistent": "Persistant",
        "Port Height": "Hauteur du port",
        "Port Width": "Largeur du port",
        "Port X (screen)": "Port X (écran)",
        "Port Y (screen)": "Port Y (écran)",
        "Position": "Position",
        "Question": "Question",
        "Radius": "Rayon",
        "Relative": "Relatif",
        "Room": "Salle",
        "Script": "Script",
        "Shape": "Forme",
        "Show Color": "Afficher la couleur",
        "Show Health": "Afficher la santé",
        "Show Lives": "Afficher les vies",
        "Show Score": "Afficher le score",
        "Sides": "Côtés",
        "Size Change/Step": "Variation de taille/pas",
        "Size Max": "Taille max",
        "Size Min": "Taille min",
        "Speed": "Vitesse",
        "Speed (FPS)": "Vitesse (images/s)",
        "Speed Max": "Vitesse max",
        "Speed Min": "Vitesse min",
        "Sprite": "Sprite",
        "Text": "Texte",
        "Then Actions": "Actions alors",
        "Tile Horizontally": "Répéter horizontalement",
        "Tile Vertically": "Répéter verticalement",
        "Tiled": "Répété",
        "Timeline": "Timeline",
        "Times": "Fois",
        "Tip Size": "Taille de la pointe",
        "URL": "URL",
        "V Border": "Bordure V",
        "Value": "Valeur",
        "Variable": "Variable",
        "Vertical Align": "Alignement vertical",
        "Vertical Scroll Speed": "Vitesse de défilement vertical",
        "Vertical Snap": "Accrochage vertical",
        "Video File": "Fichier vidéo",
        "View (0-7)": "Vue (0-7)",
        "View Height": "Hauteur de la vue",
        "View Width": "Largeur de la vue",
        "View X (room)": "Vue X (salle)",
        "View Y (room)": "Vue Y (salle)",
        "Visible": "Visible",
        "Width": "Largeur",
        "X": "X",
        "X Offset": "Décalage X",
        "X Position": "Position X",
        "X Scale": "Échelle X",
        "X1": "X1",
        "X2": "X2",
        "Y": "Y",
        "Y Offset": "Décalage Y",
        "Y Position": "Position Y",
        "Y Scale": "Échelle Y",
        "Y1": "Y1",
        "Y2": "Y2",
    },
}


def register_generated_block_translations(mapping) -> None:
    """Merge an extension's PLUGIN_GENERATED_BLOCK_TRANSLATIONS into the
    tables above, so an extension carries its own canvas translations instead
    of core listing its actions. Shape::

        {"actions": {action_name: {lang: {"display_name": ..., "description": ...}}},
         "params":  {lang: {english_label: translated_label}}}

    Existing entries are kept (first one wins), so an extension can never
    change how a core action or a shared parameter label reads.
    """
    mapping = mapping or {}
    for action_name, languages in (mapping.get("actions") or {}).items():
        entry = ACTION_TRANSLATIONS.setdefault(action_name, {})
        for language, texts in (languages or {}).items():
            entry.setdefault(language, texts)
    for language, labels in (mapping.get("params") or {}).items():
        table = PARAM_LABEL_TRANSLATIONS.setdefault(language, {})
        for label, text in (labels or {}).items():
            table.setdefault(label, text)


def get_translated_action_display_name(action_name: str, language: str, fallback: str) -> str:
    """Translated block label for a generated Blockly block, or `fallback`
    (the raw English ActionType.display_name) for 'en' or any
    untranslated action/language."""
    if language == "en":
        return fallback
    entry = ACTION_TRANSLATIONS.get(action_name, {}).get(language)
    return entry["display_name"] if entry else fallback


def get_translated_action_description(action_name: str, language: str, fallback: str) -> str:
    """Translated tooltip text for a generated Blockly block, or
    `fallback` (the raw English ActionType.description)."""
    if language == "en":
        return fallback
    entry = ACTION_TRANSLATIONS.get(action_name, {}).get(language)
    return entry["description"] if entry else fallback


def get_translated_param_label(label: str, language: str) -> str:
    """Translated inline field label for a generated block's parameter, or
    the original English `label` for 'en' or any untranslated label/
    language."""
    if language == "en":
        return label
    return PARAM_LABEL_TRANSLATIONS.get(language, {}).get(label, label)
