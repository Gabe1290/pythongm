# Preset Intermediaire

*[Accueil](Home_fr) | [Guide des Presets](Preset-Guide_fr) | [Preset Debutant](Beginner-Preset_fr)*

Le preset **Intermediaire** s'appuie sur le [Preset Debutant](Beginner-Preset_fr) en ajoutant des evenements et des actions plus avances. Il est concu pour les utilisateurs qui ont maitrise les bases et souhaitent creer des jeux plus complexes avec des fonctionnalites telles que des evenements programmes, du son, des vies et des systemes de sante.

## Apercu

Le preset Intermediaire inclut tout ce qui se trouve dans le preset Debutant, plus :
- **4 Types d'Evenements Supplementaires** - Dessin, Destruction, Souris, Alarme
- **12 Types d'Actions Supplementaires** - Vies, Sante, Son, Minuterie et plus d'options de mouvement
- **3 Categories Supplementaires** - Minuterie, Son, Dessin

---

## Evenements Supplementaires (Au-dela du Debutant)

### Evenement Dessin
| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_draw` |
| **Categorie** | Dessin |
| **Icone** | 🎨 |
| **Description** | Declenche lorsque l'objet doit etre rendu |

**Quand il se declenche :** A chaque image pendant la phase de dessin, apres tous les evenements step.

**Important :** Lorsque vous ajoutez un evenement Dessin, le dessin par defaut du sprite est desactive. Vous devez dessiner manuellement le sprite si vous voulez qu'il soit visible.

**Utilisations courantes :**
- Rendu personnalise
- Dessiner des barres de sante
- Afficher du texte
- Dessiner des formes et des effets
- Elements d'interface

---

### Evenement Destruction
| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_destroy` |
| **Categorie** | Objet |
| **Icone** | 💥 |
| **Description** | Declenche lorsque l'instance est detruite |

**Quand il se declenche :** Juste avant que l'instance soit retiree du jeu.

**Utilisations courantes :**
- Creer des effets d'explosion
- Lacher des objets
- Jouer un son de mort
- Mettre a jour le score
- Generer des particules

---

### Evenement Souris
| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_mouse` |
| **Categorie** | Entree |
| **Icone** | 🖱️ |
| **Description** | Declenche lors des interactions avec la souris |

**Types d'evenements souris :**
- Bouton gauche (pression, relachement, maintenu)
- Bouton droit (pression, relachement, maintenu)
- Bouton du milieu (pression, relachement, maintenu)
- Entree de souris (le curseur entre dans l'instance)
- Sortie de souris (le curseur quitte l'instance)
- Evenements souris globaux (n'importe ou sur l'ecran)

**Utilisations courantes :**
- Boutons cliquables
- Glisser-deposer
- Effets de survol
- Interactions de menu

---

### Evenement Alarme
| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_alarm` |
| **Categorie** | Minuterie |
| **Icone** | ⏰ |
| **Description** | Declenche lorsqu'un minuteur d'alarme atteint zero |

**Quand il se declenche :** Lorsque le compte a rebours de l'alarme correspondante atteint 0.

**Alarmes disponibles :** 12 alarmes independantes (0-11)

**Utilisations courantes :**
- Generation programmee
- Actions retardees
- Temps de recharge
- Minutage d'animation
- Evenements periodiques

---

## Actions Supplementaires (Au-dela du Debutant)

### Actions de Mouvement

#### Deplacer dans une Direction
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `move_direction` |
| **Nom du Bloc** | `move_direction` |
| **Categorie** | Mouvement |

**Description :** Definir le mouvement en utilisant la direction (0-360 degres) et la vitesse.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `direction` | Nombre | Direction en degres (0=droite, 90=haut, 180=gauche, 270=bas) |
| `speed` | Nombre | Vitesse de deplacement |

---

#### Deplacer Vers un Point
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `move_towards` |
| **Nom du Bloc** | `move_towards` |
| **Categorie** | Mouvement |

**Description :** Se deplacer vers une position specifique.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre/Expression | Coordonnee X cible |
| `y` | Nombre/Expression | Coordonnee Y cible |
| `speed` | Nombre | Vitesse de deplacement |

---

### Actions de Minuterie

#### Definir l'Alarme
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_alarm` |
| **Nom du Bloc** | `set_alarm` |
| **Categorie** | Minuterie |
| **Icone** | ⏰ |

**Description :** Definir une alarme pour se declencher apres un nombre d'etapes.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `alarm` | Nombre | Numero d'alarme (0-11) |
| `steps` | Nombre | Etapes avant le declenchement de l'alarme (a 60 FPS, 60 etapes = 1 seconde) |

**Exemple :** Definir l'alarme 0 a 180 etapes pour un delai de 3 secondes.

---

### Actions de Vies

#### Definir les Vies
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_lives` |
| **Nom du Bloc** | `lives_set` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | ❤️ |

**Description :** Definir le nombre de vies.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Valeur des vies |
| `relative` | Booleen | Si vrai, ajoute aux vies actuelles |

---

#### Ajouter des Vies
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_lives` |
| **Nom du Bloc** | `lives_add` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | ➕❤️ |

**Description :** Ajouter ou soustraire des vies.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Quantite a ajouter (negatif pour soustraire) |

**Note :** Lorsque les vies atteignent 0, l'evenement `no_more_lives` est declenche.

---

#### Dessiner les Vies
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_lives` |
| **Nom du Bloc** | `draw_lives` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | 🖼️❤️ |

**Description :** Afficher les vies a l'ecran.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Position X |
| `y` | Nombre | Position Y |
| `sprite` | Sprite | Sprite optionnel a utiliser comme icone de vie |

---

### Actions de Sante

#### Definir la Sante
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_health` |
| **Nom du Bloc** | `health_set` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | 💚 |

**Description :** Definir la valeur de sante (0-100).

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Valeur de sante (0-100) |
| `relative` | Booleen | Si vrai, ajoute a la sante actuelle |

---

#### Ajouter de la Sante
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_health` |
| **Nom du Bloc** | `health_add` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | ➕💚 |

**Description :** Ajouter ou soustraire de la sante.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Quantite a ajouter (negatif pour les degats) |

**Note :** Lorsque la sante atteint 0, l'evenement `no_more_health` est declenche.

---

#### Dessiner la Barre de Sante
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_health_bar` |
| **Nom du Bloc** | `draw_health_bar` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | 📊💚 |

**Description :** Dessiner une barre de sante a l'ecran.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `x1` | Nombre | Position X gauche |
| `y1` | Nombre | Position Y haut |
| `x2` | Nombre | Position X droite |
| `y2` | Nombre | Position Y bas |
| `back_color` | Couleur | Couleur de fond |
| `bar_color` | Couleur | Couleur de la barre de sante |

---

### Actions Sonores

#### Jouer un Son
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `play_sound` |
| **Nom du Bloc** | `sound_play` |
| **Categorie** | Son |
| **Icone** | 🔊 |

**Description :** Jouer un effet sonore.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `sound` | Son | Ressource sonore a jouer |
| `loop` | Booleen | Si le son doit etre en boucle |

---

#### Jouer de la Musique
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `play_music` |
| **Nom du Bloc** | `music_play` |
| **Categorie** | Son |
| **Icone** | 🎵 |

**Description :** Jouer de la musique de fond.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `sound` | Son | Ressource musicale a jouer |
| `loop` | Booleen | Si la musique doit etre en boucle (generalement vrai pour la musique) |

---

#### Arreter la Musique
| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `stop_music` |
| **Nom du Bloc** | `music_stop` |
| **Categorie** | Son |
| **Icone** | 🔇 |

**Description :** Arreter toute la musique en cours de lecture.

**Parametres :** Aucun

---

## Liste Complete des Fonctionnalites

### Evenements dans le Preset Intermediaire

| Evenement | Categorie | Description |
|-----------|-----------|-------------|
| Create | Objet | Instance creee |
| Step | Objet | Chaque image |
| Destroy | Objet | Instance detruite |
| Draw | Dessin | Phase de rendu |
| Keyboard Press | Entree | Touche pressee une fois |
| Mouse | Entree | Interactions souris |
| Collision | Collision | Chevauchement d'instances |
| Alarm | Minuterie | Minuteur atteint zero |

### Actions dans le Preset Intermediaire

| Categorie | Actions |
|-----------|---------|
| **Mouvement** | Set H/V Speed, Stop, Jump To, Move Direction, Move Towards |
| **Instance** | Create, Destroy |
| **Score** | Set Score, Add Score, Draw Score |
| **Vies** | Set Lives, Add Lives, Draw Lives |
| **Sante** | Set Health, Add Health, Draw Health Bar |
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
- Create Instance : obj_bullet a (x, y-20)
- Set Alarm : 0 a 15 (temps de recharge)

**Collision avec obj_enemy :**
- Add Lives : -1
- Play Sound : snd_hurt
- Jump to Position : (320, 400)

**No More Lives :**
- Show Message : "Game Over!"
- Restart Room

### Objet Ennemi

**Create :**
- Set Alarm : 0 a 60

**Alarm 0 :**
- Create Instance : obj_enemy_bullet a (x, y+20)
- Set Alarm : 0 a 60 (repetition)

**Collision avec obj_bullet :**
- Add Score : 100
- Play Sound : snd_explosion
- Destroy Instance : self

---

## Passage aux Presets Avances

Lorsque vous avez besoin de plus de fonctionnalites, considerez :
- **Preset Platformer** - Gravite, saut, mecaniques de plateforme
- **Preset Complet** - Tous les evenements et actions disponibles

---

## Voir Aussi

- [Preset Debutant](Beginner-Preset_fr) - Commencez ici si vous etes nouveau
- [Reference Complete des Actions](Full-Action-Reference_fr) - Liste complete des actions
- [Reference des Evenements](Event-Reference_fr) - Liste complete des evenements
- [Evenements et Actions](Events-and-Actions_fr) - Concepts de base
