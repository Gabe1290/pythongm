# Audio

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Vérifier si un son joue

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_sound` |
| **Icône** | ❓🔊 |
| **Catégorie** | Audio |

Condition : vrai si le son indiqué est en cours de lecture

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à vérifier |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Jouer une musique

| Propriété | Valeur |
|----------|-------|
| **Nom** | `play_music` |
| **Icône** | 🎵 |
| **Catégorie** | Audio |

Jouer une musique de fond (en boucle)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `music` | Son | — | Fichier de musique à jouer |
| `loop` | Oui/Non | Oui | Jouer la musique en boucle |
| `volume` | Nombre | `0.7` | Volume (0.0 à 1.0) |

### Jouer un son

| Propriété | Valeur |
|----------|-------|
| **Nom** | `play_sound` |
| **Icône** | 🔊 |
| **Catégorie** | Audio |

Jouer un effet sonore une fois

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à jouer |
| `volume` | Nombre | `1.0` | Volume (0.0 à 1.0) |

### Définir le volume

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_volume` |
| **Icône** | 🔉 |
| **Catégorie** | Audio |

Définir le volume global des sons/de la musique

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `volume` | Nombre | `1.0` | Volume (0.0 à 1.0) |

### Arrêter la musique

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_music` |
| **Icône** | 🔇 |
| **Catégorie** | Audio |

Arrêter la musique de fond

*Paramètres:* aucun

### Arrêter un son

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_sound` |
| **Icône** | 🔇 |
| **Catégorie** | Audio |

Arrêter un son en cours de lecture

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sound` | Son | — | Son à arrêter |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
