# Minuterie

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Pause Timeline

| Propriété | Valeur |
|----------|-------|
| **Nom** | `pause_timeline` |
| **Icône** | ⏸️ |
| **Catégorie** | Minuterie |

Pause timeline playback at the current position

*Paramètres:* aucun

### Régler une alarme

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_alarm` |
| **Icône** | ⏰ |
| **Catégorie** | Minuterie |

Régler une alarme

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `alarm_number` | Nombre | `0` | Quelle alarme (0-11) |
| `steps` | Nombre | `30` | Nombre d'étapes avant le déclenchement de l'alarme (30 = 0,5 s à 60 IPS) |

### Set Timeline

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_timeline` |
| **Icône** | ⏱️ |
| **Catégorie** | Minuterie |

Set this instance's timeline label and reset its position to 0 (bookkeeping only — see category note)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `timeline` | Texte | — | A label for your own reference; not a resource lookup |

### Set Timeline Position

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_timeline_position` |
| **Icône** | ⏱️ |
| **Catégorie** | Minuterie |

Set (or offset) this instance's timeline position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `position` | Nombre | `0` | Position in steps |
| `relative` | Oui/Non | Non | Add to the current position instead of setting it absolutely |

### Set Timeline Speed

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_timeline_speed` |
| **Icône** | ⏱️ |
| **Catégorie** | Minuterie |

Set the timeline playback speed multiplier

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `speed` | Nombre | `1.0` | 1.0=normal, 0.5=half speed, 2.0=double speed |

### Attendre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `sleep` |
| **Icône** | 💤 |
| **Catégorie** | Minuterie |

Mettre le jeu en pause pendant un certain nombre de millisecondes, puis continuer. Les sons continuent de jouer pendant la pause (par exemple pour laisser un son se terminer avant de changer de salle). Remarque : le rendu et les entrées sont figés pendant l'attente, gardez donc des durées courtes

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `milliseconds` | Nombre | `1000` | Durée de la pause, en millisecondes (1000 = 1 seconde) |

### Start Timeline

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_timeline` |
| **Icône** | ▶️ |
| **Catégorie** | Minuterie |

Begin or resume timeline playback from the current position

*Paramètres:* aucun

### Stop Timeline

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_timeline` |
| **Icône** | ⏹️ |
| **Catégorie** | Minuterie |

Stop timeline playback and reset the position to 0

*Paramètres:* aucun

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
