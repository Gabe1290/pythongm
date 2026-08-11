# Événements de Jeu

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Game Start
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `game_start` |
| **Icône** | 🎮 |
| **Catégorie** | Jeu |
| **Préréglage** | Débutant |

**Description :** Se déclenche une fois au premier démarrage du jeu (dans la première salle uniquement).

**Utilisations courantes :**
- Initialiser les variables globales
- Charger les données sauvegardées
- Jouer l'introduction

---

### Game End
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `game_end` |
| **Icône** | 🎮 |
| **Catégorie** | Jeu |
| **Préréglage** | Débutant |

**Description :** Se déclenche lorsque le jeu se termine.

**Utilisations courantes :**
- Sauvegarder les données du jeu
- Libérer les ressources

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
