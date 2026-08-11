# Événements de Collision

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Collision
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `collision` |
| **Icône** | 💥 |
| **Catégorie** | Collision |
| **Préréglage** | Débutant |

**Description :** Se déclenche lorsque cette instance chevauche un autre type d'objet.

**Configuration :** Sélectionnez quel type d'objet déclenche cette collision.

**Variable spéciale :** `other` — Référence à l'instance en collision.

**Quand il se déclenche :** À chaque frame où les instances se chevauchent.

**Utilisations courantes :**
- Collecter des objets
- Subir des dégâts
- Heurter des murs
- Déclencher des événements

**Exemples d'événements de collision :**
- `collision_with_obj_coin` — Le joueur touche une pièce
- `collision_with_obj_enemy` — Le joueur touche un ennemi
- `collision_with_obj_wall` — L'instance heurte un mur

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
