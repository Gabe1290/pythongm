# Référence des Événements

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

Cette page documente tous les événements disponibles dans PyGameMaker. Les événements sont des déclencheurs qui exécutent des actions lorsque des conditions spécifiques se produisent dans votre jeu.

## Catégories d'Événements

- [Événements d'Objet](#événements-dobjet) - Create, Step, Destroy
- [Événements d'Entrée](#événements-dentrée) - Clavier, Souris
- [Événements de Collision](#événements-de-collision) - Collisions d'objets
- [Événements de Temps](#événements-de-temps) - Alarmes, Variantes de Step
- [Événements de Dessin](#événements-de-dessin) - Rendu personnalisé
- [Événements de Salle](#événements-de-salle) - Transitions de salles
- [Événements de Jeu](#événements-de-jeu) - Début/Fin de jeu
- [Autres Événements](#autres-événements) - Limites, Vies, Santé

---

## Événements d'Objet

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

## Événements d'Entrée

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

## Événements de Collision

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

## Événements de Temps

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

## Événements de Dessin

### Draw
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw` |
| **Icône** | 🎨 |
| **Catégorie** | Dessin |
| **Préréglage** | Débutant |

**Description :** Se déclenche pendant la phase de rendu.

**Important :** Ajouter un événement Draw désactive le dessin automatique du sprite. Vous devez dessiner le sprite manuellement si vous voulez qu'il soit visible.

**Utilisations courantes :**
- Rendu personnalisé
- Dessiner des formes
- Afficher du texte
- Barres de vie
- Éléments d'interface

**Actions de dessin disponibles :**
- Dessiner un sprite
- Dessiner du texte
- Dessiner un rectangle
- Dessiner un cercle
- Dessiner une ligne
- Dessiner la barre de santé

---

### Draw GUI
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_gui` |
| **Icône** | 🖥️ |
| **Catégorie** | Dessin |
| **Préréglage** | Débutant |

**Description :** Dessine dans l'**espace écran (GUI)**, par-dessus la salle et sans être affecté par le défilement des vues/de la caméra.

**Différence avec Draw :** l'événement Draw habituel est en coordonnées de salle (il défile avec la vue) ; Draw GUI reste fixe à l'écran — à utiliser pour les ATH (HUD), les scores et les menus.

---

## Événements de Salle

### Room Start
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `room_start` |
| **Icône** | 🚪 |
| **Catégorie** | Salle |
| **Préréglage** | Débutant |

**Description :** Se déclenche lors de l'entrée dans une salle, après tous les événements Create.

**Utilisations courantes :**
- Initialisation de la salle
- Jouer la musique de la salle
- Définir des variables spécifiques à la salle

---

### Room End
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `room_end` |
| **Icône** | 🚪 |
| **Catégorie** | Salle |
| **Préréglage** | Débutant |

**Description :** Se déclenche lors de la sortie d'une salle.

**Utilisations courantes :**
- Sauvegarder la progression
- Arrêter la musique
- Nettoyage

---

## Événements de Jeu

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

## Autres Événements

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

## Ordre d'Exécution des Événements

Comprendre quand les événements se déclenchent aide à créer un comportement
de jeu prévisible (confirmé dans la boucle principale de
`runtime/game_runner.py`) :

1. **Begin Step** — Début de la frame
2. **Alarm** — Toutes les alarmes déclenchées comptent à rebours et se déclenchent
3. **Step** (et **Keyboard (maintenue)**) — Logique de jeu principale, puis
   vérification continue des touches maintenues pour la même instance
4. **Keyboard Press/Release, Mouse** — Les événements d'entrée en file
   d'attente pour la frame sont distribués (cela se produit *après* Step,
   pas avant — le code de Step réagit aux touches déjà maintenues au
   *début* de la frame, pas à celles pressées pendant celle-ci)
5. **Movement, puis Collision** — La physique (gravité/friction/hspeed/vspeed)
   est appliquée, puis les collisions sont détectées et leurs événements se déclenchent
6. **End Step** (et **Destroy**) — Après les collisions
7. **Draw** — Phase de rendu

---

## Événements par Préréglage

Confirmé via `events.event_types.get_available_events()` alimenté par
chaque préréglage réel de `config/blockly_config.py` — voir le
[Guide des Préréglages](Preset-Guide_fr) pour ce qu'un « préréglage »
restreint réellement (à la fois le sélecteur Blockly et le panneau
structuré Événements/Actions) et comment le préréglage d'un projet est défini.

| Préréglage | Événements inclus |
|------------|-------------------|
| **Débutant** (19 événements) | Create, Step, Keyboard (maintenue), Keyboard \<No Key\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermédiaire** (21 événements) | + Destroy, Keyboard Press |
| **Full** (édition Développement uniquement, 23 événements) | + Keyboard Release, Mouse |

---

## Voir Aussi

- [Référence Complète des Actions](Full-Action-Reference_fr) - Liste complète des actions
- [Préréglage Débutant](Beginner-Preset_fr) - Événements essentiels pour débutants
- [Préréglage Intermédiaire](Intermediate-Preset_fr) - Événements supplémentaires
- [Événements et Actions](Evenements_Actions_fr) - Aperçu des concepts de base
