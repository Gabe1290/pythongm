# Particles

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Burst Particles

| Propriété | Valeur |
|----------|-------|
| **Nom** | `burst_particles` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Emit a one-time burst of particles from the most recently created emitter

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `particle_type` | Nombre | `0` | Particle type id (from Create Particle Type) |
| `number` | Nombre | `10` | Number of particles to emit |

### Clear Particles

| Propriété | Valeur |
|----------|-------|
| **Nom** | `clear_particles` |
| **Icône** | 🧹 |
| **Catégorie** | Particles |

Remove all active particles but keep particle types and emitters

*Paramètres:* aucun

### Create Emitter

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_emitter` |
| **Icône** | 🌀 |
| **Catégorie** | Particles |

Create a particle emitter area (returned id is stored for the next emitter-using action)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Emitter center X (room coordinates) |
| `y` | Nombre | `0` | Emitter center Y (room coordinates) |
| `width` | Nombre | `0` | Emitter area width |
| `height` | Nombre | `0` | Emitter area height |
| `shape` | Choix | `rectangle` | Shape of the emitter area particles spawn within; Choix: `rectangle`, `ellipse`, `diamond`, `line` |

### Create Particle System

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_system` |
| **Icône** | ✨ |
| **Catégorie** | Particles |

Create a particle system attached to this instance (replaces any existing one)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `depth` | Nombre | `0` | Drawing depth for the particle system (not yet used for cross-instance sort order) |

### Create Particle Type

| Propriété | Valeur |
|----------|-------|
| **Nom** | `create_particle_type` |
| **Icône** | ⚙️ |
| **Catégorie** | Particles |

Define a new particle appearance/behavior (returned type id is stored for the next particle_type-using action)

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

### Destroy Emitter

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_emitter` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Destroy the most recently created emitter

*Paramètres:* aucun

### Destroy Particle System

| Propriété | Valeur |
|----------|-------|
| **Nom** | `destroy_particle_system` |
| **Icône** | 💥 |
| **Catégorie** | Particles |

Remove this instance's particle system, clearing all particles and emitters

*Paramètres:* aucun

### Stream Particles

| Propriété | Valeur |
|----------|-------|
| **Nom** | `stream_particles` |
| **Icône** | 🌊 |
| **Catégorie** | Particles |

Continuously emit particles every step from the most recently created emitter (0 to stop)

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
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
