# Événements d'Entrée

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Clavier (Continu)
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `keyboard` |
| **Icône** | ⌨️ |
| **Catégorie** | Entrée |
| **Préréglage** | Débutant |

**Description :** Se déclenche en continu tant qu'une touche est maintenue enfoncée.

**Idéal pour :** Mouvement fluide et continu

**Touches supportées :**
- Touches fléchées (haut, bas, gauche, droite)
- Lettres (A-Z)
- Chiffres (0-9)
- Espace, Entrée, Échap
- Touches de fonction (F1-F12)
- Touches de modification (Maj, Ctrl, Alt)

---

### Appui Clavier
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `keyboard_press` |
| **Icône** | 🔘 |
| **Catégorie** | Entrée |
| **Préréglage** | Intermédiaire |

**Description :** Se déclenche une fois lorsqu'une touche est pressée pour la première fois.

**Idéal pour :** Actions uniques (sauter, tirer, sélectionner dans un menu)

**Différence avec Clavier :** Ne se déclenche qu'une fois par appui, pas pendant le maintien.

---

### Relâchement Clavier
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `keyboard_release` |
| **Icône** | ⬆️ |
| **Catégorie** | Entrée |
| **Préréglage** | Full (édition Développement) |

**Description :** Se déclenche une fois lorsqu'une touche est relâchée.

**Utilisations courantes :**
- Arrêter le mouvement quand la touche est relâchée
- Terminer les attaques chargées
- Basculer les états

---

### Clavier (Aucune touche)
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `keyboard_no_key` |
| **Icône** | ⌨️ |
| **Catégorie** | Entrée |
| **Préréglage** | Débutant |

**Description :** Se déclenche à chaque frame tant qu'**aucune** touche n'est maintenue.

**Quand il se déclenche :** À chaque frame où le clavier est inactif, *avant* l'événement Step.

**Utilisations courantes :**
- Arrêter le mouvement quand le joueur relâche toutes les touches (jeux de grille/labyrinthe)
- Animations au repos

---

### Souris
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `mouse` |
| **Icône** | 🖱️ |
| **Catégorie** | Entrée |
| **Préréglage** | Full (édition Développement) |

**Description :** Événements de bouton de souris et de mouvement.

**Types d'événements :**

| Type | Description |
|------|-------------|
| Bouton Gauche | Clic avec le bouton gauche de la souris |
| Bouton Droit | Clic avec le bouton droit de la souris |
| Bouton du Milieu | Clic avec le bouton du milieu/molette |
| Entrée Souris | Le curseur entre dans les limites de l'instance |
| Sortie Souris | Le curseur quitte les limites de l'instance |
| Bouton Gauche Global | Clic gauche n'importe où |
| Bouton Droit Global | Clic droit n'importe où |

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
