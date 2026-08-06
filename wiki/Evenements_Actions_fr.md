# Événements et actions

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Retour à l'accueil](Home_fr)

Ceci est une référence complète de tous les événements et actions disponibles dans PyGameMaker.

---

## Référence des événements

### Événement Create
**Quand :** Une fois quand une instance est créée
**Utilisation :** Initialisation, définition de variables, démarrage de minuteurs

### Événement Destroy
**Quand :** Quand l'instance est détruite
**Utilisation :** Nettoyage, création d'effets, attribution de points

### Événements Step

| Événement | Quand |
|-----------|-------|
| **Step** | À chaque frame (60 fois/seconde) |
| **Begin Step** | Avant les vérifications de collision |
| **End Step** | Après tous les autres événements |

### Événements Alarm

| Événement | Quand |
|-----------|-------|
| **Alarm[0-11]** | Quand le compteur atteint 0 |

Utilisez l'action `Régler une alarme` pour démarrer un compte à rebours. Les valeurs d'alarme sont en frames (60 = 1 seconde à 60 FPS).

### Événements clavier

| Événement | Quand |
|-----------|-------|
| **Clavier [touche]** | Tant que la touche est maintenue (répété) |
| **Touche pressée [touche]** | Une fois quand la touche est enfoncée |
| **Touche relâchée [touche]** | Une fois quand la touche est relâchée |
| **Aucune touche** | Quand aucune touche n'est pressée |

Touches disponibles : Lettres (A-Z), Chiffres (0-9), Flèches, Espace, Entrée, Maj, Ctrl, Alt, Touches de fonction (F1-F12)

### Événements souris

| Événement | Quand |
|-----------|-------|
| **Bouton gauche** | Clic gauche sur l'instance |
| **Bouton droit** | Clic droit sur l'instance |
| **Bouton central** | Clic central sur l'instance |
| **Pression gauche** | Bouton gauche pressé (une fois) |
| **Relâchement gauche** | Bouton gauche relâché (une fois) |
| **Entrée souris** | Le curseur entre dans l'instance |
| **Sortie souris** | Le curseur quitte l'instance |
| **Bouton gauche global** | Clic gauche n'importe où |
| **Bouton droit global** | Clic droit n'importe où |

### Événements de collision

| Événement | Quand |
|-----------|-------|
| **Collision avec [objet]** | Quand on touche l'objet spécifié |

Les vérifications de collision ont lieu entre les événements Step et Draw.

### Autres événements

| Événement | Quand |
|-----------|-------|
| **Hors de la salle** | L'instance est complètement hors de la salle |
| **Intersection limite** | L'instance touche le bord de la salle |
| **Début du jeu** | Le jeu commence (première salle chargée) |
| **Fin du jeu** | Le jeu se ferme |
| **Début de salle** | En entrant dans une salle |
| **Fin de salle** | En quittant une salle |
| **Plus de vies** | Les vies atteignent 0 |
| **Plus de santé** | La santé atteint 0 |
| **Fin d'animation** | L'animation du sprite est terminée |

### Événements Draw

| Événement | Quand |
|-----------|-------|
| **Draw** | Pendant la phase de rendu |
| **Draw GUI** | Après le dessin de la salle (espace écran) |

---

## Référence des actions

### Actions de mouvement

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Définir la vitesse** | Définir la vitesse de déplacement | vitesse, relatif |
| **Définir la direction** | Définir la direction | direction (0-360), relatif |
| **Définir la vitesse horizontale** | Définir hspeed | hspeed, relatif |
| **Définir la vitesse verticale** | Définir vspeed | vspeed, relatif |
| **Définir la gravité** | Définir la force de gravité | gravité, direction |
| **Définir le frottement** | Définir la friction | friction |
| **Se déplacer vers un point** | Se déplacer vers des coordonnées | x, y, vitesse |
| **Commencer à bouger (direction)** | Se déplacer dans une direction | direction, vitesse |
| **Sauter à une position** | Téléportation aux coordonnées | x, y, relatif |
| **Sauter à la position de départ** | Retour à la position de création | - |
| **Sauter à une position aléatoire** | Téléportation à une position entièrement aléatoire (les deux axes ; alignable sur la grille) | snap_h, snap_v |
| **Rebondir** | Rebondir sur les objets solides | précis |

### Actions d'instance

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Créer une instance** | Faire apparaître un nouvel objet | objet, x, y, relatif |
| **Créer en mouvement** | Faire apparaître avec une vélocité | objet, x, y, vitesse, direction |
| **Détruire l'instance** | Supprimer l'instance | - |
| **Changer d'instance** | Transformer en un autre objet | objet, exécuter_événements |

### Actions de timing

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Régler une alarme** | Démarrer un compte à rebours | alarm_id (0-11), steps |
| **Pause** | Mettre en pause l'exécution | millisecondes |

### Actions Score/Vies/Santé

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Définir le score** | Changer le score | valeur, relatif |
| **Définir les vies** | Changer les vies | valeur, relatif |
| **Définir la santé** | Changer la santé | valeur, relatif |
| **Dessiner le score** | Afficher le score | x, y, légende |
| **Dessiner les vies** | Afficher les vies sous forme d'icônes de sprite répétées | x, y, sprite, échelle, tuilé |
| **Dessiner la barre de santé** | Afficher la santé sous forme de barre à deux couleurs | x1, y1, x2, y2, couleur_fond, couleur_barre |

### Actions de dessin

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Dessiner un sprite** | Dessiner un sprite | sprite, x, y, sous-image |
| **Dessiner du texte** | Afficher du texte | x, y, texte |
| **Dessiner un rectangle** | Dessiner un rectangle | x1, y1, x2, y2, rempli |
| **Dessiner un cercle** | Dessiner un cercle | x, y, rayon, rempli |
| **Dessiner une ligne** | Dessiner une ligne | x1, y1, x2, y2 |
| **Définir la couleur de dessin** | Définir la couleur utilisée par Dessiner du texte/Dessiner un rectangle/etc. | couleur |
| **Définir la couleur** | Définir la teinte et la transparence d'un sprite (pas la couleur de dessin ci-dessus) | couleur, alpha |
| **Définir la police de dessin** | Définir la police et l'alignement pour le prochain dessin de texte | police, alignement_h, alignement_v |

### Actions de salle

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Salle suivante** | Aller à la salle suivante | transition |
| **Salle précédente** | Aller à la salle précédente | transition |
| **Redémarrer la salle** | Réinitialiser la salle | - |
| **Aller à la salle** | Aller à une salle spécifique | salle, transition |
| **Si salle suivante existe** | Vérifier s'il y a une salle suivante | - |
| **Si salle précédente existe** | Vérifier s'il y a une salle précédente | - |

### Actions de son

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Jouer un son** | Jouer un effet sonore | son, boucle |
| **Arrêter un son** | Arrêter un son | son |
| **Vérifier si un son est en cours** | Vérifier si un son est en cours de lecture | son |
| **Jouer une musique** | Jouer une musique de fond | son, boucle |
| **Arrêter la musique** | Arrêter toute musique | - |

### Actions de variable

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Définir une variable** | Assigner une valeur | variable, valeur, relatif |
| **Tester une variable** | Vérifier une valeur | variable, valeur, opération |
| **Dessiner une variable** | Afficher une variable | x, y, variable |

### Actions de contrôle de flux

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Tester une expression** | Vérification conditionnelle (une expression booléenne Python) | expression |
| **Sinon** | Branche alternative | - |
| **Début de bloc** | Commencer un groupe d'actions | - |
| **Fin de bloc** | Terminer un groupe d'actions | - |
| **Répéter** | Boucle N fois | nombre |
| **Quitter l'événement** | Arrêter l'événement actuel | - |

### Actions diverses

| Action | Description | Paramètres |
|--------|-------------|------------|
| **Afficher un message** | Afficher un message popup | message |
| **Redémarrer le jeu** | Redémarrer le jeu | - |
| **Terminer le jeu** | Fermer le jeu | - |

---

## Variables intégrées

Ces variables sont disponibles pour toutes les instances :

| Variable | Description |
|----------|-------------|
| `x` | Position horizontale |
| `y` | Position verticale |
| `xstart` | Position x de départ |
| `ystart` | Position y de départ |
| `hspeed` | Vitesse horizontale |
| `vspeed` | Vitesse verticale |
| `speed` | Vitesse d'animation du sprite (images par seconde) — **pas** la vitesse de déplacement. Il n'existe pas de variable intégrée pour la « vitesse totale » ; calculez-la vous-même à partir de `hspeed`/`vspeed`, ex. `(hspeed**2 + vspeed**2)**0.5` |
| `direction` | Direction du mouvement (0-360) |
| `gravity` | Force de gravité |
| `gravity_direction` | Direction de la gravité |
| `friction` | Friction du mouvement |
| `image_index` | Frame d'animation actuelle |
| `image_speed` | Vitesse d'animation |
| `image_xscale` | Échelle horizontale |
| `image_yscale` | Échelle verticale |
| `image_angle` | Angle de rotation |
| `visible` | Si dessiné |
| `solid` | Si solide pour les collisions |
| `depth` | Profondeur de dessin |
| `sprite_index` | Sprite actuel |
| `alarm[0-11]` | Minuteurs d'alarme |

### Variables globales

| Variable | Description |
|----------|-------------|
| `score` | Score du jeu |
| `lives` | Vies du joueur |
| `health` | Santé du joueur (0-100) |
| `room` | Salle actuelle |
| `room_width` | Largeur de la salle actuelle |
| `room_height` | Hauteur de la salle actuelle |
| `mouse_x` | Position x de la souris |
| `mouse_y` | Position y de la souris |

---

## Prochaines étapes

- [[Programmation_Visuelle_fr]] - Utilisez les blocs Blockly pour la même logique
- [[Editeur_Objets_fr]] - Appliquez les événements et actions aux objets
- [[Premier_Jeu_fr]] - Voyez les événements en action
