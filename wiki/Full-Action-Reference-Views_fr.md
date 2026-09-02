# Vues

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Activer les vues

| Propriété | Valeur |
|----------|-------|
| **Nom** | `enable_views` |
| **Icône** | 🎥 |
| **Catégorie** | Vues |

Activer ou désactiver le système de caméra/vue de la salle (permet à un niveau de défiler lorsqu'il est plus grand que la fenêtre)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `enable` | Oui/Non | Oui | Activé = vues de caméra ; désactivé = dessiner toute la salle d'un coup |

### Définir une vue

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_view` |
| **Icône** | 🎥 |
| **Catégorie** | Vues |

Configurer une vue de caméra : quelle partie de la salle elle montre, où elle s'affiche à l'écran, et un objet à suivre

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `view` | Choix | `0` | Laquelle des 8 vues configurer; Choix: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Oui/Non | Oui | Dessiner cette vue |
| `view_x` | Nombre | `0` | Bord gauche de la région de la salle affichée |
| `view_y` | Nombre | `0` | Bord supérieur de la région de la salle affichée |
| `view_w` | Nombre | `800` | Largeur de la région de la salle affichée |
| `view_h` | Nombre | `600` | Hauteur de la région de la salle affichée |
| `port_x` | Nombre | `0` | Bord gauche à l'écran |
| `port_y` | Nombre | `0` | Bord supérieur à l'écran |
| `port_w` | Nombre | `800` | Largeur dessinée à l'écran |
| `port_h` | Nombre | `600` | Hauteur dessinée à l'écran |
| `follow` | Objet | — | Objet suivi par la caméra (vide = vue fixe); optionnel |
| `hborder` | Nombre | `32` | Bordure horizontale avant que la caméra ne défile |
| `vborder` | Nombre | `32` | Bordure verticale avant que la caméra ne défile |
| `hspeed` | Nombre | `-1` | Vitesse de défilement horizontal maximale (-1 = instantané) |
| `vspeed` | Nombre | `-1` | Vitesse de défilement vertical maximale (-1 = instantané) |

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
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
