# Autres Événements

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Outside Room
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `outside_room` |
| **Icône** | 🚫 |
| **Catégorie** | Autre |
| **Préréglage** | Débutant |

**Description :** Se déclenche quand l'instance est complètement en dehors des limites de la salle.

**Utilisations courantes :**
- Détruire les projectiles hors écran
- Faire le tour de l'autre côté
- Déclencher le game over

---

### Intersect Boundary
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `intersect_boundary` |
| **Icône** | ⚠️ |
| **Catégorie** | Autre |
| **Préréglage** | Débutant |

**Description :** Se déclenche quand l'instance touche la limite de la salle.

**Utilisations courantes :**
- Garder le joueur dans les limites
- Rebondir sur les bords

---

### No More Lives
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `no_more_lives` |
| **Icône** | 💀 |
| **Catégorie** | Autre |
| **Préréglage** | Débutant |

**Description :** Se déclenche quand les vies tombent à 0 ou moins.

**Utilisations courantes :**
- Écran de game over
- Redémarrer le jeu
- Afficher le score final

---

### No More Health
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `no_more_health` |
| **Icône** | 💔 |
| **Catégorie** | Autre |
| **Préréglage** | Débutant |

**Description :** Se déclenche quand la santé tombe à 0 ou moins.

**Utilisations courantes :**
- Perdre une vie
- Faire réapparaître le joueur
- Déclencher l'animation de mort

---

### Animation End
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `animation_end` |
| **Icône** | 🎞️ |
| **Catégorie** | Autre |
| **Préréglage** | Débutant |

**Description :** Se déclenche lorsque l'animation du sprite de l'instance termine un cycle complet (repasse de la dernière image à la première).

**Utilisations courantes :**
- Détruire un effet à usage unique (explosion) après une seule lecture
- Passer à une autre animation quand l'actuelle se termine
- Faire avancer une machine à états à la fin de l'animation

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu

[← Retour à la Référence des Événements](Event-Reference_fr)
