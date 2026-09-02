# Grille

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Si aligné sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_on_grid` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Vérifier si l'objet est aligné sur la grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |
| `then_actions` | Liste d'actions | — | Actions si aligné sur la grille |
| `else_actions` | Liste d'actions | — | Actions si non aligné sur la grille |

### Aligner sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `snap_to_grid` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Aligner la position de l'instance sur la grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |

### Arrêter si aucune touche

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stop_if_no_keys` |
| **Icône** | ▦ |
| **Catégorie** | Grille |

Arrêter le mouvement sur la grille quand aucune touche de déplacement n'est enfoncée (parfait pour un alignement fluide sur la grille)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `grid_size` | Nombre | `32` | Taille de la case de grille en pixels |

### Tester l'alignement sur la grille

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_alignment` |
| **Icône** | ❓▦ |
| **Catégorie** | Grille |

Condition : vrai si l'instance est alignée sur une grille

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `hsnap` | Nombre | `32` | Espacement horizontal de la grille en pixels |
| `vsnap` | Nombre | `32` | Espacement vertical de la grille en pixels |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
