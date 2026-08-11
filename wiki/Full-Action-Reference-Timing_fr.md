# Minuterie

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

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

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
