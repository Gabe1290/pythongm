# Événements de Temps

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Alarme
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `alarm` |
| **Icône** | ⏰ |
| **Catégorie** | Temps |
| **Préréglage** | Débutant |

**Description :** Se déclenche quand un compte à rebours d'alarme atteint zéro.

**Alarmes disponibles :** 12 alarmes indépendantes (alarm[0] à alarm[11])

**Réglage des alarmes :** Utilisez l'action « Régler une alarme » avec des steps (60 steps ≈ 1 seconde à 60 FPS)

**Utilisations courantes :**
- Génération programmée
- Temps de recharge
- Effets retardés
- Actions répétitives (redéfinir l'alarme dans l'événement d'alarme)

---

### Begin Step
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `begin_step` |
| **Icône** | ▶️ |
| **Catégorie** | Step |
| **Préréglage** | Débutant |

**Description :** Se déclenche au début de chaque frame, avant les événements Step réguliers.

**Ordre d'exécution :** Begin Step → Step → End Step

**Utilisations courantes :**
- Traitement des entrées
- Calculs pré-mouvement

---

### End Step
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `end_step` |
| **Icône** | ⏹️ |
| **Catégorie** | Step |
| **Préréglage** | Débutant |

**Description :** Se déclenche à la fin de chaque frame, après les collisions.

**Utilisations courantes :**
- Ajustements finaux de position
- Opérations de nettoyage
- Mises à jour d'état après les collisions

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
