# Particules

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Émettre une salve de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `burst_particles` |
| **Icône** | 💥 |
| **Catégorie** | Particules |

Émet une salve unique de particules depuis l'émetteur créé le plus récemment

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `particle_type` | Nombre | `0` | Identifiant du type de particule (issu de « Créer un type de particule ») |
| `number` | Nombre | `10` | Nombre de particules à émettre |

### Effacer les particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_particles` |
| **Icône** | 🧹 |
| **Catégorie** | Particules |

Supprime toutes les particules actives, mais conserve les types de particules et les émetteurs

*Paramètres:* aucun

### Créer un émetteur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_emitter` |
| **Icône** | 🌀 |
| **Catégorie** | Particules |

Crée une zone d'émission de particules (l'identifiant renvoyé est retenu pour la prochaine action utilisant un émetteur)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | X du centre de l'émetteur (coordonnées de la salle) |
| `y` | Nombre | `0` | Y du centre de l'émetteur (coordonnées de la salle) |
| `width` | Nombre | `0` | Largeur de la zone d'émission |
| `height` | Nombre | `0` | Hauteur de la zone d'émission |
| `shape` | Choix | `rectangle` | Forme de la zone d'émission dans laquelle les particules apparaissent; Choix: `rectangle`, `ellipse`, `diamond`, `line` |

### Créer un système de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_system` |
| **Icône** | ✨ |
| **Catégorie** | Particules |

Crée un système de particules rattaché à cette instance (remplace celui qui existait)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `depth` | Nombre | `0` | Profondeur de dessin du système de particules (pas encore utilisée pour l'ordre entre instances) |

### Créer un type de particule

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_type` |
| **Icône** | ⚙️ |
| **Catégorie** | Particules |

Définit une nouvelle apparence ou un nouveau comportement de particule (l'identifiant de type renvoyé est retenu pour la prochaine action utilisant un type de particule)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite avec lequel dessiner chaque particule ; laissez vide pour un simple cercle coloré; optionnel |
| `size_min` | Nombre | `1.0` | Taille minimale de la particule (facteur d'échelle) |
| `size_max` | Nombre | `1.0` | Taille maximale de la particule (facteur d'échelle) |
| `size_increase` | Nombre | `0.0` | Variation de taille par pas (négatif = rétrécit, plancher à 0) |
| `color` | Couleur | `#FFFFFF` | Couleur de la particule (utilisée quand aucun sprite n'est défini) |
| `alpha` | Nombre | `1.0` | Transparence (0 = invisible, 1 = opaque) |
| `speed_min` | Nombre | `0.0` | Vitesse de déplacement minimale |
| `speed_max` | Nombre | `0.0` | Vitesse de déplacement maximale |
| `direction_min` | Nombre | `0` | Angle de direction minimal (0 = à droite, 90 = vers le haut) |
| `direction_max` | Nombre | `360` | Angle de direction maximal |
| `life_min` | Nombre | `100` | Durée de vie minimale, en pas |
| `life_max` | Nombre | `100` | Durée de vie maximale, en pas |

### Supprimer l'émetteur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_emitter` |
| **Icône** | 💥 |
| **Catégorie** | Particules |

Détruit l'émetteur créé le plus récemment

*Paramètres:* aucun

### Supprimer le système de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_particle_system` |
| **Icône** | 💥 |
| **Catégorie** | Particules |

Supprime le système de particules de cette instance, en effaçant toutes ses particules et tous ses émetteurs

*Paramètres:* aucun

### Émettre des particules en continu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stream_particles` |
| **Icône** | 🌊 |
| **Catégorie** | Particules |

Émet des particules en continu, à chaque pas, depuis l'émetteur créé le plus récemment (0 pour arrêter)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `particle_type` | Nombre | `0` | Identifiant du type de particule (issu de « Créer un type de particule ») |
| `number` | Nombre | `1` | Particules émises par pas (0 arrête l'émission) |

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
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
