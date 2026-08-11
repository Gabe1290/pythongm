# Salle

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Vérifier la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_room` |
| **Icône** | ❓🚪 |
| **Catégorie** | Salle |

Condition : vrai si la salle actuelle correspond

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `room` | Salle | — | Salle à comparer |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Terminer le jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `game_end` |
| **Icône** | 🛑🎮 |
| **Catégorie** | Salle |

Terminer le jeu

*Paramètres:* aucun

### Aller à la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `goto_room` |
| **Icône** | 🚪 |
| **Catégorie** | Salle |

Basculer vers une salle spécifique

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `room` | Salle | — | Nom de la salle cible |
| `transition` | Choix | `none` | Effet de transition (actuellement accepté mais non rendu); Choix: `none`; optionnel |

### Si salle suivante existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_next_room_exists` |
| **Icône** | ❓➡️ |
| **Catégorie** | Salle |

Vérifier s'il existe une salle après la salle actuelle

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `then_actions` | Liste d'actions | — | Actions si la salle suivante existe |
| `else_actions` | Liste d'actions | — | Actions si la salle suivante n'existe pas |

### Si salle précédente existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_previous_room_exists` |
| **Icône** | ❓⬅️ |
| **Catégorie** | Salle |

Vérifier s'il existe une salle avant la salle actuelle

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `then_actions` | Liste d'actions | — | Actions si la salle précédente existe |
| `else_actions` | Liste d'actions | — | Actions si la salle précédente n'existe pas |

### Salle suivante

| Propriété | Valeur |
|----------|-------|
| **Nom** | `next_room` |
| **Icône** | ➡️ |
| **Catégorie** | Salle |

Aller à la salle suivante

*Paramètres:* aucun

### Salle précédente

| Propriété | Valeur |
|----------|-------|
| **Nom** | `previous_room` |
| **Icône** | ⬅️ |
| **Catégorie** | Salle |

Aller à la salle précédente

*Paramètres:* aucun

### Redémarrer la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `restart_room` |
| **Icône** | 🔄 |
| **Catégorie** | Salle |

Redémarrer la salle actuelle

*Paramètres:* aucun

### Set Background

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_background` |
| **Icône** | 🖼️ |
| **Catégorie** | Salle |

Set the current room's background image, with tiling and scrolling options

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Texte | — | Background or sprite asset name |
| `visible` | Oui/Non | Oui | Show the background; optionnel |
| `foreground` | Oui/Non | Non | Draw in front of instances instead of behind them; optionnel |
| `tiled_h` | Oui/Non | Non | Repeat the background across the width of the room; optionnel |
| `tiled_v` | Oui/Non | Non | Repeat the background across the height of the room; optionnel |
| `hspeed` | Nombre | `0` | Horizontal auto-scroll speed in pixels/frame; optionnel |
| `vspeed` | Nombre | `0` | Vertical auto-scroll speed in pixels/frame; optionnel |

### Set Background Color

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_background_color` |
| **Icône** | 🎨 |
| **Catégorie** | Salle |

Change the current room's background color

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#87CEEB` | Background color |
| `show_color` | Oui/Non | Oui | Whether the background color is visible (off fills black instead); optionnel |

### Définir le titre de la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_caption` |
| **Icône** | 🏷️ |
| **Catégorie** | Salle |

Définir le titre de la fenêtre de jeu

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `caption` | Texte | — | Texte du titre de la fenêtre |

### Set Room Persistent

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_persistent` |
| **Icône** | 💾 |
| **Catégorie** | Salle |

Whether the current room keeps its live state (instance positions, destroyed instances, etc.) when the player leaves and later returns to it, instead of rebuilding fresh from its authored layout every revisit

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `persistent` | Oui/Non | Oui | Keep this room's state across a revisit |

### Set Room Speed

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_speed` |
| **Icône** | ⏱️ |
| **Catégorie** | Salle |

Change the game's frame rate (frames per second)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `30` | Target frames per second (1-240) |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
