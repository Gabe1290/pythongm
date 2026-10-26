# Score/Lives/Health

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Effacer le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_highscore` |
| **Icône** | 🗑️🏆 |
| **Catégorie** | Score/Lives/Health |

Effacer toutes les entrées du tableau des scores

*Paramètres:* aucun

### Afficher le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_highscore` |
| **Icône** | 🏆 |
| **Catégorie** | Score/Lives/Health |

Afficher la boîte de dialogue du tableau des meilleurs scores

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `background` | Couleur | `#FFFFDD` | Couleur d'arrière-plan de la boîte de dialogue; optionnel |
| `new_color` | Couleur | `#FF0000` | Couleur utilisée pour la nouvelle entrée (qualifiée); optionnel |
| `other_color` | Couleur | `#000000` | Couleur utilisée pour les autres entrées; optionnel |
| `allow_new_entry` | Oui/Non | Oui | Demander le nom si le score actuel se qualifie |

### Tester la santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_health` |
| **Icône** | ❓💚 |
| **Catégorie** | Score/Lives/Health |

Condition : comparer la santé actuelle à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Nombre | `0` | Valeur de comparaison |

### Tester les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_lives` |
| **Icône** | ❓❤️ |
| **Catégorie** | Score/Lives/Health |

Condition : comparer le nombre de vies à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Tester le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_score` |
| **Icône** | ❓🏆 |
| **Catégorie** | Score/Lives/Health |

Condition : comparer le score à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (6)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (14)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Dessin](Full-Action-Reference-Drawing_fr) (11)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (22)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [micro:bit](Full-Action-Reference-Microbit-Actions_fr) (16)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
