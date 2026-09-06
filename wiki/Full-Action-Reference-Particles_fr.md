# Particles

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Émettre une salve de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `burst_particles` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Émet une salve unique de particules depuis l'émetteur créé le plus récemment

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `particle_type` | Nombre | `0` | Particle type id (from Create Particle Type) |
| `number` | Nombre | `10` | Number of particles to emit |

### Effacer les particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_particles` |
| **Icône** | 🧹 |
| **Catégorie** | Particles |

Supprime toutes les particules actives, mais conserve les types de particules et les émetteurs

*Paramètres:* aucun

### Créer un émetteur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_emitter` |
| **Icône** | 🌀 |
| **Catégorie** | Particles |

Crée une zone d'émission de particules (l'identifiant renvoyé est retenu pour la prochaine action utilisant un émetteur)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Emitter center X (room coordinates) |
| `y` | Nombre | `0` | Emitter center Y (room coordinates) |
| `width` | Nombre | `0` | Emitter area width |
| `height` | Nombre | `0` | Emitter area height |
| `shape` | Choix | `rectangle` | Shape of the emitter area particles spawn within; Choix: `rectangle`, `ellipse`, `diamond`, `line` |

### Créer un système de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_system` |
| **Icône** | ✨ |
| **Catégorie** | Particles |

Crée un système de particules rattaché à cette instance (remplace celui qui existait)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `depth` | Nombre | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Créer un type de particule

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_type` |
| **Icône** | ⚙️ |
| **Catégorie** | Particles |

Définit une nouvelle apparence ou un nouveau comportement de particule (l'identifiant de type renvoyé est retenu pour la prochaine action utilisant un type de particule)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite to draw each particle as; leave empty for a plain colored circle; optionnel |
| `size_min` | Nombre | `1.0` | Minimum particle size (scale factor) |
| `size_max` | Nombre | `1.0` | Maximum particle size (scale factor) |
| `size_increase` | Nombre | `0.0` | Size change per step (negative shrinks, floored at 0) |
| `color` | Couleur | `#FFFFFF` | Particle color (used when no sprite is set) |
| `alpha` | Nombre | `1.0` | Transparency (0=invisible, 1=opaque) |
| `speed_min` | Nombre | `0.0` | Minimum movement speed |
| `speed_max` | Nombre | `0.0` | Maximum movement speed |
| `direction_min` | Nombre | `0` | Minimum direction angle (0=right, 90=up) |
| `direction_max` | Nombre | `360` | Maximum direction angle |
| `life_min` | Nombre | `100` | Minimum lifetime in steps |
| `life_max` | Nombre | `100` | Maximum lifetime in steps |

### Supprimer l'émetteur

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_emitter` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Détruit l'émetteur créé le plus récemment

*Paramètres:* aucun

### Supprimer le système de particules

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_particle_system` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Supprime le système de particules de cette instance, en effaçant toutes ses particules et tous ses émetteurs

*Paramètres:* aucun

### Émettre des particules en continu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stream_particles` |
| **Icône** | 🌊 |
| **Catégorie** | Particles |

Émet des particules en continu, à chaque pas, depuis l'émetteur créé le plus récemment (0 pour arrêter)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `particle_type` | Nombre | `0` | Particle type id (from Create Particle Type) |
| `number` | Nombre | `1` | Particles to emit per step (0 stops streaming) |

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
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Network](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
