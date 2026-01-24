# Reference des Evenements

*[Accueil](Home_fr) | [Guide des Presets](Preset-Guide_fr) | [Reference Complete des Actions](Full-Action-Reference_fr)*

Cette page documente tous les evenements disponibles dans PyGameMaker. Les evenements sont des declencheurs qui executent des actions lorsque des conditions specifiques se produisent dans votre jeu.

## Categories d'Evenements

- [Evenements d'Objet](#evenements-dobjet) - Create, Step, Destroy
- [Evenements d'Entree](#evenements-dentree) - Clavier, Souris
- [Evenements de Collision](#evenements-de-collision) - Collisions d'objets
- [Evenements de Temps](#evenements-de-temps) - Alarmes, Variantes de Step
- [Evenements de Dessin](#evenements-de-dessin) - Rendu personnalise
- [Evenements de Salle](#evenements-de-salle) - Transitions de salles
- [Evenements de Jeu](#evenements-de-jeu) - Debut/Fin de jeu
- [Autres Evenements](#autres-evenements) - Limites, Vies, Sante

---

## Evenements d'Objet

### Create
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `create` |
| **Icone** | 🎯 |
| **Categorie** | Objet |
| **Preset** | Debutant |

**Description:** Execute une fois lors de la premiere creation d'une instance.

**Quand il se declenche:**
- Quand une instance est placee dans une salle au demarrage du jeu
- Quand creee via l'action "Creer Instance"
- Apres les transitions de salle pour les nouvelles instances

**Utilisations courantes:**
- Initialiser les variables
- Definir les valeurs de depart
- Configurer l'etat initial

---

### Step
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `step` |
| **Icone** | ⭐ |
| **Categorie** | Objet |
| **Preset** | Debutant |

**Description:** Execute a chaque frame (generalement 60 fois par seconde).

**Quand il se declenche:** En continu, a chaque frame du jeu.

**Utilisations courantes:**
- Mouvement continu
- Verification des conditions
- Mise a jour des positions
- Logique de jeu

**Note:** Attention aux performances - le code ici s'execute constamment.

---

### Destroy
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `destroy` |
| **Icone** | 💥 |
| **Categorie** | Objet |
| **Preset** | Intermediaire |

**Description:** Execute lorsqu'une instance est detruite.

**Quand il se declenche:** Juste avant que l'instance soit retiree du jeu.

**Utilisations courantes:**
- Generer des effets (explosions, particules)
- Lacher des objets
- Mettre a jour les scores
- Jouer des sons

---

## Evenements d'Entree

### Clavier (Continu)
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `keyboard` |
| **Icone** | ⌨️ |
| **Categorie** | Entree |
| **Preset** | Debutant |

**Description:** Se declenche en continu tant qu'une touche est maintenue enfoncee.

**Ideal pour:** Mouvement fluide et continu

**Touches Supportees:**
- Touches flechees (haut, bas, gauche, droite)
- Lettres (A-Z)
- Chiffres (0-9)
- Espace, Entree, Echap
- Touches de fonction (F1-F12)
- Touches de modification (Maj, Ctrl, Alt)

---

### Appui Clavier
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `keyboard_press` |
| **Icone** | 🔘 |
| **Categorie** | Entree |
| **Preset** | Debutant |

**Description:** Se declenche une fois lorsqu'une touche est pressee pour la premiere fois.

**Ideal pour:** Actions uniques (sauter, tirer, selectionner dans un menu)

**Difference avec Clavier:** Ne se declenche qu'une fois par appui, pas pendant le maintien.

---

### Relachement Clavier
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `keyboard_release` |
| **Icone** | ⬆️ |
| **Categorie** | Entree |
| **Preset** | Avance |

**Description:** Se declenche une fois lorsqu'une touche est relachee.

**Utilisations courantes:**
- Arreter le mouvement quand la touche est relachee
- Terminer les attaques chargees
- Basculer les etats

---

### Souris
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `mouse` |
| **Icone** | 🖱️ |
| **Categorie** | Entree |
| **Preset** | Intermediaire |

**Description:** Evenements de bouton de souris et de mouvement.

**Types d'Evenements:**

| Type | Description |
|------|-------------|
| Bouton Gauche | Clic avec le bouton gauche de la souris |
| Bouton Droit | Clic avec le bouton droit de la souris |
| Bouton du Milieu | Clic avec le bouton du milieu/molette |
| Entree Souris | Le curseur entre dans les limites de l'instance |
| Sortie Souris | Le curseur quitte les limites de l'instance |
| Bouton Gauche Global | Clic gauche n'importe ou |
| Bouton Droit Global | Clic droit n'importe ou |

---

## Evenements de Collision

### Collision
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `collision` |
| **Icone** | 💥 |
| **Categorie** | Collision |
| **Preset** | Debutant |

**Description:** Se declenche lorsque cette instance chevauche un autre type d'objet.

**Configuration:** Selectionnez quel type d'objet declenche cette collision.

**Variable speciale:** `other` - Reference a l'instance en collision.

**Quand il se declenche:** A chaque frame ou les instances se chevauchent.

**Utilisations courantes:**
- Collecter des objets
- Subir des degats
- Heurter des murs
- Declencher des evenements

**Exemples d'evenements de collision:**
- `collision_with_obj_coin` - Le joueur touche une piece
- `collision_with_obj_enemy` - Le joueur touche un ennemi
- `collision_with_obj_wall` - L'instance heurte un mur

---

## Evenements de Temps

### Alarme
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `alarm` |
| **Icone** | ⏰ |
| **Categorie** | Temps |
| **Preset** | Intermediaire |

**Description:** Se declenche quand un compte a rebours d'alarme atteint zero.

**Alarmes disponibles:** 12 alarmes independantes (alarm[0] a alarm[11])

**Reglage des alarmes:** Utilisez l'action "Definir Alarme" avec des steps (60 steps ≈ 1 seconde a 60 FPS)

**Utilisations courantes:**
- Generation programmee
- Temps de recharge
- Effets retardes
- Actions repetitives (redefinir l'alarme dans l'evenement d'alarme)

---

### Begin Step
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `begin_step` |
| **Icone** | ▶️ |
| **Categorie** | Step |
| **Preset** | Avance |

**Description:** Se declenche au debut de chaque frame, avant les evenements Step reguliers.

**Ordre d'execution:** Begin Step → Step → End Step

**Utilisations courantes:**
- Traitement des entrees
- Calculs pre-mouvement

---

### End Step
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `end_step` |
| **Icone** | ⏹️ |
| **Categorie** | Step |
| **Preset** | Avance |

**Description:** Se declenche a la fin de chaque frame, apres les collisions.

**Utilisations courantes:**
- Ajustements finaux de position
- Operations de nettoyage
- Mises a jour d'etat apres les collisions

---

## Evenements de Dessin

### Draw
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `draw` |
| **Icone** | 🎨 |
| **Categorie** | Dessin |
| **Preset** | Intermediaire |

**Description:** Se declenche pendant la phase de rendu.

**Important:** Ajouter un evenement Draw desactive le dessin automatique du sprite. Vous devez dessiner le sprite manuellement si vous voulez qu'il soit visible.

**Utilisations courantes:**
- Rendu personnalise
- Dessiner des formes
- Afficher du texte
- Barres de vie
- Elements d'interface

**Actions de dessin disponibles:**
- Dessiner Sprite
- Dessiner Texte
- Dessiner Rectangle
- Dessiner Cercle
- Dessiner Ligne
- Dessiner Barre de Vie

---

## Evenements de Salle

### Room Start
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `room_start` |
| **Icone** | 🚪 |
| **Categorie** | Salle |
| **Preset** | Avance |

**Description:** Se declenche lors de l'entree dans une salle, apres tous les evenements Create.

**Utilisations courantes:**
- Initialisation de la salle
- Jouer la musique de la salle
- Definir des variables specifiques a la salle

---

### Room End
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `room_end` |
| **Icone** | 🚪 |
| **Categorie** | Salle |
| **Preset** | Avance |

**Description:** Se declenche lors de la sortie d'une salle.

**Utilisations courantes:**
- Sauvegarder la progression
- Arreter la musique
- Nettoyage

---

## Evenements de Jeu

### Game Start
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `game_start` |
| **Icone** | 🎮 |
| **Categorie** | Jeu |
| **Preset** | Avance |

**Description:** Se declenche une fois au premier demarrage du jeu (dans la premiere salle uniquement).

**Utilisations courantes:**
- Initialiser les variables globales
- Charger les donnees sauvegardees
- Jouer l'introduction

---

### Game End
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `game_end` |
| **Icone** | 🎮 |
| **Categorie** | Jeu |
| **Preset** | Avance |

**Description:** Se declenche lorsque le jeu se termine.

**Utilisations courantes:**
- Sauvegarder les donnees du jeu
- Liberer les ressources

---

## Autres Evenements

### Outside Room
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `outside_room` |
| **Icone** | 🚫 |
| **Categorie** | Autre |
| **Preset** | Avance |

**Description:** Se declenche quand l'instance est completement en dehors des limites de la salle.

**Utilisations courantes:**
- Detruire les projectiles hors ecran
- Faire le tour de l'autre cote
- Declencher le game over

---

### Intersect Boundary
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `intersect_boundary` |
| **Icone** | ⚠️ |
| **Categorie** | Autre |
| **Preset** | Avance |

**Description:** Se declenche quand l'instance touche la limite de la salle.

**Utilisations courantes:**
- Garder le joueur dans les limites
- Rebondir sur les bords

---

### No More Lives
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `no_more_lives` |
| **Icone** | 💀 |
| **Categorie** | Autre |
| **Preset** | Intermediaire |

**Description:** Se declenche quand les vies deviennent 0 ou moins.

**Utilisations courantes:**
- Ecran de game over
- Redemarrer le jeu
- Afficher le score final

---

### No More Health
| Propriete | Valeur |
|-----------|--------|
| **Nom** | `no_more_health` |
| **Icone** | 💔 |
| **Categorie** | Autre |
| **Preset** | Intermediaire |

**Description:** Se declenche quand la sante devient 0 ou moins.

**Utilisations courantes:**
- Perdre une vie
- Reapparaitre le joueur
- Declencher l'animation de mort

---

## Ordre d'Execution des Evenements

Comprendre quand les evenements se declenchent aide a creer un comportement de jeu previsible:

1. **Begin Step** - Debut de la frame
2. **Alarm** - Toutes les alarmes declenchees
3. **Keyboard/Mouse** - Evenements d'entree
4. **Step** - Logique de jeu principale
5. **Collision** - Apres le mouvement
6. **End Step** - Apres les collisions
7. **Draw** - Phase de rendu

---

## Evenements par Preset

| Preset | Evenements Inclus |
|--------|-------------------|
| **Debutant** | Create, Step, Keyboard Press, Collision |
| **Intermediaire** | + Draw, Destroy, Mouse, Alarm |
| **Avance** | + Toutes les variantes de clavier, Begin/End Step, Evenements de salle, Evenements de jeu, Evenements de limite |

---

## Voir Aussi

- [Reference Complete des Actions](Full-Action-Reference_fr) - Liste complete des actions
- [Preset Debutant](Beginner-Preset_fr) - Evenements essentiels pour debutants
- [Preset Intermediaire](Intermediate-Preset_fr) - Evenements supplementaires
- [Evenements et Actions](Events-and-Actions_fr) - Apercu des concepts de base
