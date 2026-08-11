# Événements d'Objet

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Create
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `create` |
| **Icône** | 🎯 |
| **Catégorie** | Objet |
| **Préréglage** | Débutant |

**Description :** S'exécute une fois lors de la première création d'une instance.

**Quand il se déclenche :**
- Quand une instance est placée dans une salle au démarrage du jeu
- Quand elle est créée via l'action « Créer une instance »
- Après les transitions de salle pour les nouvelles instances

**Utilisations courantes :**
- Initialiser les variables
- Définir les valeurs de départ
- Configurer l'état initial

---

### Step
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `step` |
| **Icône** | ⭐ |
| **Catégorie** | Objet |
| **Préréglage** | Débutant |

**Description :** S'exécute à chaque frame (généralement 60 fois par seconde).

**Quand il se déclenche :** En continu, à chaque frame du jeu.

**Utilisations courantes :**
- Mouvement continu
- Vérification des conditions
- Mise à jour des positions
- Logique de jeu

**Note :** Attention aux performances — le code ici s'exécute constamment.

---

### Destroy
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `destroy` |
| **Icône** | 💥 |
| **Catégorie** | Objet |
| **Préréglage** | Intermédiaire |

**Description :** S'exécute lorsqu'une instance est détruite.

**Quand il se déclenche :** Juste avant que l'instance soit retirée du jeu.

**Utilisations courantes :**
- Générer des effets (explosions, particules)
- Lâcher des objets
- Mettre à jour les scores
- Jouer des sons

---

## Autres Catégories d'Événements

- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
