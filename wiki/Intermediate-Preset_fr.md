# Préréglage Intermédiaire

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Préréglage Débutant](Beginner-Preset_fr)*

Le préréglage **Intermédiaire** s'appuie sur le [Préréglage Débutant](Beginner-Preset_fr) en ajoutant des événements et des actions plus avancés. Il est conçu pour les utilisateurs qui ont maîtrisé les bases et souhaitent créer des jeux plus complexes avec des fonctionnalités telles que des événements programmés, du son, des vies et des systèmes de santé.

## Aperçu

Le préréglage Intermédiaire inclut tout ce qui se trouve dans le préréglage Débutant, plus :
- **4 Types d'Événements Supplémentaires** - Dessin, Destruction, Souris, Alarme
- **12 Types d'Actions Supplémentaires** - Vies, Santé, Son, Minuterie et plus d'options de mouvement
- **3 Catégories Supplémentaires** - Minuterie, Son, Dessin

---

## Événements Supplémentaires (Au-delà du Débutant)

### Événement Dessin
| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_draw` |
| **Catégorie** | Dessin |
| **Icône** | 🎨 |
| **Description** | Se déclenche lorsque l'objet doit être rendu |

**Quand il se déclenche :** À chaque image pendant la phase de dessin, après tous les événements step.

**Important :** Lorsque vous ajoutez un événement Dessin, le dessin par défaut du sprite est désactivé. Vous devez dessiner manuellement le sprite si vous voulez qu'il soit visible.

**Utilisations courantes :**
- Rendu personnalisé
- Dessiner des barres de santé
- Afficher du texte
- Dessiner des formes et des effets
- Éléments d'interface

---

### Événement Destruction
| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_destroy` |
| **Catégorie** | Objet |
| **Icône** | 💥 |
| **Description** | Se déclenche lorsque l'instance est détruite |

**Quand il se déclenche :** Juste avant que l'instance soit retirée du jeu.

**Utilisations courantes :**
- Créer des effets d'explosion
- Lâcher des objets
- Jouer un son de mort
- Mettre à jour le score
- Générer des particules

---

### Événement Souris
| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_mouse` |
| **Catégorie** | Entrée |
| **Icône** | 🖱️ |
| **Description** | Se déclenche lors des interactions avec la souris |

**Types d'événements souris :**
- Bouton gauche (pression, relâchement, maintenu)
- Bouton droit (pression, relâchement, maintenu)
- Bouton du milieu (pression, relâchement, maintenu)
- Entrée de souris (le curseur entre dans l'instance)
- Sortie de souris (le curseur quitte l'instance)
- Événements souris globaux (n'importe où sur l'écran)

**Utilisations courantes :**
- Boutons cliquables
- Glisser-déposer
- Effets de survol
- Interactions de menu

---

### Événement Alarme
| Propriété | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_alarm` |
| **Catégorie** | Minuterie |
| **Icône** | ⏰ |
| **Description** | Se déclenche lorsqu'un minuteur d'alarme atteint zéro |

**Quand il se déclenche :** Lorsque le compte à rebours de l'alarme correspondante atteint 0.

**Alarmes disponibles :** 12 alarmes indépendantes (0-11)

**Utilisations courantes :**
- Génération programmée
- Actions retardées
- Temps de recharge
- Minutage d'animation
- Événements périodiques

---

## Actions Supplémentaires (Au-delà du Débutant)

### Actions de Mouvement

#### Déplacer dans une Direction
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `move_direction` |
| **Nom du Bloc** | `move_direction` |
| **Catégorie** | Mouvement |

**Description :** Définir le mouvement en utilisant la direction (0-360 degrés) et la vitesse.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `direction` | Nombre | Direction en degrés (0=droite, 90=haut, 180=gauche, 270=bas) |
| `speed` | Nombre | Vitesse de déplacement |

---

#### Déplacer Vers un Point
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `move_towards_point` |
| **Nom du Bloc** | `move_towards_point` |
| **Catégorie** | Mouvement |

**Description :** Se déplacer vers une position spécifique.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre/Expression | Coordonnée X cible |
| `y` | Nombre/Expression | Coordonnée Y cible |
| `speed` | Nombre | Vitesse de déplacement |

---

### Actions de Minuterie

#### Définir l'Alarme
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_alarm` |
| **Nom du Bloc** | `set_alarm` |
| **Catégorie** | Minuterie |
| **Icône** | ⏰ |

**Description :** Définir une alarme pour se déclencher après un nombre d'étapes.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `alarm` | Nombre | Numéro d'alarme (0-11) |
| `steps` | Nombre | Étapes avant le déclenchement de l'alarme (à 60 FPS, 60 étapes = 1 seconde) |

**Exemple :** Définir l'alarme 0 à 180 étapes pour un délai de 3 secondes.

---

### Actions de Vies

#### Définir les Vies
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_lives` |
| **Nom du Bloc** | `lives_set` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | ❤️ |

**Description :** Définir le nombre de vies.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Valeur des vies |
| `relative` | Booléen | Si vrai, ajoute aux vies actuelles |

---

#### Ajouter des Vies
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_lives` |
| **Nom du Bloc** | `lives_add` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | ➕❤️ |

**Description :** Ajouter ou soustraire des vies.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Quantité à ajouter (négatif pour soustraire) |

**Note :** Lorsque les vies atteignent 0, l'événement `no_more_lives` est déclenché.

---

#### Dessiner les Vies
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_lives` |
| **Nom du Bloc** | `draw_lives` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | 🖼️❤️ |

**Description :** Afficher les vies à l'écran.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Position X |
| `y` | Nombre | Position Y |
| `sprite` | Sprite | Sprite optionnel à utiliser comme icône de vie |

---

### Actions de Santé

#### Définir la Santé
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_health` |
| **Nom du Bloc** | `health_set` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | 💚 |

**Description :** Définir la valeur de santé (0-100).

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Valeur de santé (0-100) |
| `relative` | Booléen | Si vrai, ajoute à la santé actuelle |

---

#### Ajouter de la Santé
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_health` |
| **Nom du Bloc** | `health_add` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | ➕💚 |

**Description :** Ajouter ou soustraire de la santé.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Quantité à ajouter (négatif pour les dégâts) |

**Note :** Lorsque la santé atteint 0, l'événement `no_more_health` est déclenché.

---

#### Dessiner la Barre de Santé
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_health_bar` |
| **Nom du Bloc** | `draw_health_bar` |
| **Catégorie** | Score/Vies/Santé |
| **Icône** | 📊💚 |

**Description :** Dessiner une barre de santé à l'écran.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `x1` | Nombre | Position X gauche |
| `y1` | Nombre | Position Y haut |
| `x2` | Nombre | Position X droite |
| `y2` | Nombre | Position Y bas |
| `back_color` | Couleur | Couleur de fond |
| `bar_color` | Couleur | Couleur de la barre de santé |

---

### Actions Sonores

#### Jouer un Son
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `play_sound` |
| **Nom du Bloc** | `sound_play` |
| **Catégorie** | Son |
| **Icône** | 🔊 |

**Description :** Jouer un effet sonore.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `sound` | Son | Ressource sonore à jouer |
| `loop` | Booléen | Si le son doit être en boucle |

---

#### Jouer de la Musique
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `play_music` |
| **Nom du Bloc** | `music_play` |
| **Catégorie** | Son |
| **Icône** | 🎵 |

**Description :** Jouer de la musique de fond.

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `sound` | Son | Ressource musicale à jouer |
| `loop` | Booléen | Si la musique doit être en boucle (généralement vrai pour la musique) |

---

#### Arrêter la Musique
| Propriété | Valeur |
|-----------|--------|
| **Nom de l'Action** | `stop_music` |
| **Nom du Bloc** | `music_stop` |
| **Catégorie** | Son |
| **Icône** | 🔇 |

**Description :** Arrêter toute la musique en cours de lecture.

**Paramètres :** Aucun

---

## Liste Complète des Fonctionnalités

### Événements dans le Préréglage Intermédiaire

| Événement | Catégorie | Description |
|-----------|-----------|-------------|
| Create | Objet | Instance créée |
| Step | Objet | Chaque image |
| Destroy | Objet | Instance détruite |
| Draw | Dessin | Phase de rendu |
| Keyboard Press | Entrée | Touche pressée une fois |
| Mouse | Entrée | Interactions souris |
| Collision | Collision | Chevauchement d'instances |
| Alarm | Minuterie | Minuteur atteint zéro |

### Actions dans le Préréglage Intermédiaire

| Catégorie | Actions |
|-----------|---------|
| **Mouvement** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards Point |
| **Instance** | Create, Destroy |
| **Score** | Set Score, Add Score, Draw Score |
| **Vies** | Set Lives, Add Lives, Draw Lives |
| **Santé** | Set Health, Add Health, Draw Health Bar |
| **Salle** | Next, Previous, Restart, Go To, If Next/Previous Exists |
| **Minuterie** | Set Alarm |
| **Son** | Play Sound, Play Music, Stop Music |
| **Sortie** | Show Message, Execute Code |

---

## Exemple : Jeu de Tir avec des Vies

### Objet Joueur

**Create :**
- Set Lives : 3

**Keyboard Press (Espace) :**
- Create Instance : obj_bullet à (x, y-20)
- Set Alarm : 0 à 15 (temps de recharge)

**Collision avec obj_enemy :**
- Add Lives : -1
- Play Sound : snd_hurt
- Jump to Position : (320, 400)

**No More Lives :**
- Show Message : "Game Over!"
- Restart Room

### Objet Ennemi

**Create :**
- Set Alarm : 0 à 60

**Alarm 0 :**
- Create Instance : obj_enemy_bullet à (x, y+20)
- Set Alarm : 0 à 60 (répétition)

**Collision avec obj_bullet :**
- Add Score : 100
- Play Sound : snd_explosion
- Destroy Instance : self

---

## Passage aux Préréglages Avancés

Lorsque vous avez besoin de plus de fonctionnalités, envisagez :
- **Préréglage Plateforme** - Gravité, saut, mécaniques de plateforme
- **Préréglage Complet** - Tous les événements et actions disponibles

---

## Voir Aussi

- [Préréglage Débutant](Beginner-Preset_fr) - Commencez ici si vous êtes nouveau
- [Référence Complète des Actions](Full-Action-Reference_fr) - Liste complète des actions
- [Référence des Événements](Event-Reference_fr) - Liste complète des événements
- [Événements et Actions](Evenements_Actions_fr) - Concepts de base
