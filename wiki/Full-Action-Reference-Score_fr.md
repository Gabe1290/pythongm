# Score

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Effacer le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_highscore` |
| **Icône** | 🗑️🏆 |
| **Catégorie** | Score |

Effacer toutes les entrées du tableau des scores

*Paramètres:* aucun

### Dessiner la barre de santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_health_bar` |
| **Icône** | 🩺 |
| **Catégorie** | Score |

Dessiner la santé actuelle sous forme de barre à deux couleurs

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X gauche |
| `y1` | Nombre | `0` | Y supérieur |
| `x2` | Nombre | `100` | X droit |
| `y2` | Nombre | `20` | Y inférieur |
| `back_color` | Couleur | `#FF0000` | Couleur de l'arrière-plan (vide) |
| `bar_color` | Couleur | `#00FF00` | Couleur de remplissage (santé) |

### Dessiner les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_lives` |
| **Icône** | 🖍️❤️ |
| **Catégorie** | Score |

Dessiner le nombre de vies actuel sous forme d'images de sprite répétées

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `sprite` | Sprite | — | Sprite dessiné une fois par vie restante; optionnel |
| `scale` | Nombre | `1.0` | Facteur d'échelle uniforme pour l'icône de vie (1.0 = taille native); optionnel |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |

### Dessiner le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_score` |
| **Icône** | 🖍️🏆 |
| **Catégorie** | Score |

Dessiner le score actuel à l'écran

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `caption` | Texte | `Score: ` | Texte affiché avant la valeur du score; optionnel |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |

### Définir la santé

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_health` |
| **Icône** | 💚 |
| **Catégorie** | Score |

Définir la santé, ou l'incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `100` | Valeur de santé (0-100) |
| `relative` | Oui/Non | Non | Ajouter à la santé actuelle au lieu de la remplacer |

### Définir les vies

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_lives` |
| **Icône** | ❤️ |
| **Catégorie** | Score |

Définir les vies, ou les incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `3` | Nombre de vies |
| `relative` | Oui/Non | Non | Ajouter aux vies actuelles au lieu de les remplacer |

### Définir le score

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_score` |
| **Icône** | 🏆 |
| **Catégorie** | Score |

Définir le score, ou l'incrémenter avec Relatif

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de score à définir |
| `relative` | Oui/Non | Non | Ajouter au score actuel au lieu de le remplacer |

### Afficher le tableau des scores

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_highscore` |
| **Icône** | 🏆 |
| **Catégorie** | Score |

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
| **Catégorie** | Score |

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
| **Catégorie** | Score |

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
| **Catégorie** | Score |

Condition : comparer le score à une valeur

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `value` | Nombre | `0` | Valeur de comparaison |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (2)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (20)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (4)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
