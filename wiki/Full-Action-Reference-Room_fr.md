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

### Définir l'arrière-plan

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_background` |
| **Icône** | 🖼️ |
| **Catégorie** | Salle |

Définir l'image d'arrière-plan de la salle actuelle, avec des options de répétition et de défilement

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Texte | — | Nom de la ressource d'arrière-plan ou de sprite |
| `visible` | Oui/Non | Oui | Afficher l'arrière-plan; optionnel |
| `foreground` | Oui/Non | Non | Dessiner devant les instances au lieu de derrière; optionnel |
| `tiled_h` | Oui/Non | Non | Répéter l'arrière-plan sur toute la largeur de la salle; optionnel |
| `tiled_v` | Oui/Non | Non | Répéter l'arrière-plan sur toute la hauteur de la salle; optionnel |
| `hspeed` | Nombre | `0` | Vitesse de défilement automatique horizontal en pixels/image; optionnel |
| `vspeed` | Nombre | `0` | Vitesse de défilement automatique vertical en pixels/image; optionnel |

### Définir la couleur d'arrière-plan

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_background_color` |
| **Icône** | 🎨 |
| **Catégorie** | Salle |

Changer la couleur d'arrière-plan de la salle actuelle

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `color` | Couleur | `#87CEEB` | Couleur d'arrière-plan |
| `show_color` | Oui/Non | Oui | Si la couleur d'arrière-plan est visible (désactivé remplit en noir à la place); optionnel |

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

### Définir la persistance de la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_persistent` |
| **Icône** | 💾 |
| **Catégorie** | Salle |

Si la salle actuelle conserve son état actif (positions des instances, instances détruites, etc.) quand le joueur la quitte puis y revient, au lieu de la reconstruire entièrement depuis sa disposition d'origine à chaque visite

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `persistent` | Oui/Non | Oui | Conserver l'état de cette salle lors d'une nouvelle visite |

### Définir la vitesse de la salle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_room_speed` |
| **Icône** | ⏱️ |
| **Catégorie** | Salle |

Changer la fréquence d'images du jeu (images par seconde)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `30` | Images par seconde cibles (1-240) |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
