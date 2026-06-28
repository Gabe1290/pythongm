# Evenements et actions

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

> [Retour a l'accueil](Home_fr)

Ceci est une reference complete de tous les evenements et actions disponibles dans PyGameMaker.

---

## Reference des evenements

### Evenement Create
**Quand:** Une fois quand une instance est creee
**Utilisation:** Initialisation, definition de variables, demarrage de minuteurs

### Evenement Destroy
**Quand:** Quand l'instance est detruite
**Utilisation:** Nettoyage, creation d'effets, attribution de points

### Evenements Step

| Evenement | Quand |
|-----------|-------|
| **Step** | A chaque frame (60 fois/seconde) |
| **Begin Step** | Avant les verifications de collision |
| **End Step** | Apres tous les autres evenements |

### Evenements Alarm

| Evenement | Quand |
|-----------|-------|
| **Alarm[0-11]** | Quand le compteur atteint 0 |

Utilisez l'action `Definir Alarm` pour demarrer un compte a rebours. Les valeurs d'alarme sont en frames (60 = 1 seconde a 60 FPS).

### Evenements clavier

| Evenement | Quand |
|-----------|-------|
| **Clavier [touche]** | Tant que la touche est maintenue (repete) |
| **Touche pressee [touche]** | Une fois quand la touche est enfoncee |
| **Touche relachee [touche]** | Une fois quand la touche est relachee |
| **Aucune touche** | Quand aucune touche n'est pressee |

Touches disponibles: Lettres (A-Z), Chiffres (0-9), Fleches, Espace, Entree, Maj, Ctrl, Alt, Touches de fonction (F1-F12)

### Evenements souris

| Evenement | Quand |
|-----------|-------|
| **Bouton gauche** | Clic gauche sur l'instance |
| **Bouton droit** | Clic droit sur l'instance |
| **Bouton central** | Clic central sur l'instance |
| **Pression gauche** | Bouton gauche presse (une fois) |
| **Relachement gauche** | Bouton gauche relache (une fois) |
| **Entree souris** | Le curseur entre dans l'instance |
| **Sortie souris** | Le curseur quitte l'instance |
| **Bouton gauche global** | Clic gauche n'importe ou |
| **Bouton droit global** | Clic droit n'importe ou |

### Evenements de collision

| Evenement | Quand |
|-----------|-------|
| **Collision avec [objet]** | Quand on touche l'objet specifie |

Les verifications de collision ont lieu entre les evenements Step et Draw.

### Autres evenements

| Evenement | Quand |
|-----------|-------|
| **Hors de la salle** | L'instance est completement hors de la salle |
| **Intersection limite** | L'instance touche le bord de la salle |
| **Debut du jeu** | Le jeu commence (premiere salle chargee) |
| **Fin du jeu** | Le jeu se ferme |
| **Debut de salle** | En entrant dans une salle |
| **Fin de salle** | En quittant une salle |
| **Plus de vies** | Les vies atteignent 0 |
| **Plus de sante** | La sante atteint 0 |
| **Fin d'animation** | L'animation du sprite est terminee |

### Evenements Draw

| Evenement | Quand |
|-----------|-------|
| **Draw** | Pendant la phase de rendu |
| **Draw GUI** | Apres le dessin de la salle (espace ecran) |

---

## Reference des actions

### Actions de mouvement

| Action | Description | Parametres |
|--------|-------------|------------|
| **Definir vitesse** | Definir la vitesse de deplacement | vitesse, relatif |
| **Definir direction** | Definir la direction | direction (0-360), relatif |
| **Definir vitesse horizontale** | Definir hspeed | hspeed, relatif |
| **Definir vitesse verticale** | Definir vspeed | vspeed, relatif |
| **Definir gravite** | Definir la force de gravite | gravite, direction |
| **Definir friction** | Definir la friction | friction |
| **Aller vers un point** | Se deplacer vers des coordonnees | x, y, vitesse |
| **Sauter a une position** | Teleportation aux coordonnees | x, y |
| **Sauter au depart** | Retour a la position de creation | - |
| **Sauter aleatoirement** | Deplacement aleatoire | - |
| **Rebondir** | Rebondir sur les objets solides | precis |

### Actions d'instance

| Action | Description | Parametres |
|--------|-------------|------------|
| **Creer une instance** | Faire apparaitre un nouvel objet | objet, x, y, relatif |
| **Creer en mouvement** | Faire apparaitre avec velocite | objet, x, y, vitesse, direction |
| **Detruire l'instance** | Supprimer l'instance | - |
| **Changer d'instance** | Transformer en un autre objet | objet, executer_evenements |

### Actions de timing

| Action | Description | Parametres |
|--------|-------------|------------|
| **Definir Alarm** | Demarrer un compte a rebours | alarm_id (0-11), steps |
| **Pause** | Mettre en pause l'execution | millisecondes |

### Actions Score/Vies/Sante

| Action | Description | Parametres |
|--------|-------------|------------|
| **Definir score** | Changer le score | valeur, relatif |
| **Definir vies** | Changer les vies | valeur, relatif |
| **Definir sante** | Changer la sante | valeur, relatif |
| **Dessiner score** | Afficher le score | x, y, legende |
| **Dessiner vies** | Afficher les vies | x, y, legende |
| **Dessiner sante** | Afficher la barre de sante | x, y, largeur, hauteur |

### Actions de dessin

| Action | Description | Parametres |
|--------|-------------|------------|
| **Dessiner sprite** | Dessiner un sprite | sprite, x, y, sous-image |
| **Dessiner texte** | Afficher du texte | x, y, texte |
| **Dessiner rectangle** | Dessiner un rectangle | x1, y1, x2, y2, rempli |
| **Dessiner cercle** | Dessiner un cercle | x, y, rayon, rempli |
| **Dessiner ligne** | Dessiner une ligne | x1, y1, x2, y2 |
| **Definir couleur** | Definir la couleur de dessin | couleur |
| **Definir police** | Definir la police de texte | police |

### Actions de salle

| Action | Description | Parametres |
|--------|-------------|------------|
| **Salle suivante** | Aller a la salle suivante | transition |
| **Salle precedente** | Aller a la salle precedente | transition |
| **Redemarrer la salle** | Reinitialiser la salle | - |
| **Aller a la salle** | Aller a une salle specifique | salle, transition |
| **Si salle suivante existe** | Verifier s'il y a une salle suivante | - |
| **Si salle precedente existe** | Verifier s'il y a une salle precedente | - |

### Actions de son

| Action | Description | Parametres |
|--------|-------------|------------|
| **Jouer un son** | Jouer un effet sonore | son, boucle |
| **Arreter un son** | Arreter un son | son |
| **Si son en cours** | Verifier si un son est en cours | son |
| **Jouer musique** | Jouer une musique de fond | son, boucle |
| **Arreter musique** | Arreter toute musique | - |

### Actions de variable

| Action | Description | Parametres |
|--------|-------------|------------|
| **Definir variable** | Assigner une valeur | variable, valeur, relatif |
| **Si variable** | Verifier une valeur | variable, valeur, operation |
| **Dessiner variable** | Afficher une variable | x, y, variable, legende |

### Actions de controle de flux

| Action | Description | Parametres |
|--------|-------------|------------|
| **Si expression** | Verification conditionnelle | expression |
| **Sinon** | Branche alternative | - |
| **Debut bloc** | Commencer un groupe d'actions | - |
| **Fin bloc** | Terminer un groupe d'actions | - |
| **Repeter** | Boucle N fois | nombre |
| **Quitter evenement** | Arreter l'evenement actuel | - |

### Actions diverses

| Action | Description | Parametres |
|--------|-------------|------------|
| **Afficher message** | Afficher un message popup | message |
| **Redemarrer jeu** | Redemarrer le jeu | - |
| **Terminer jeu** | Fermer le jeu | - |

---

## Variables integrees

Ces variables sont disponibles pour toutes les instances:

| Variable | Description |
|----------|-------------|
| `x` | Position horizontale |
| `y` | Position verticale |
| `xstart` | Position x de depart |
| `ystart` | Position y de depart |
| `hspeed` | Vitesse horizontale |
| `vspeed` | Vitesse verticale |
| `speed` | Vitesse de deplacement totale |
| `direction` | Direction du mouvement (0-360) |
| `gravity` | Force de gravite |
| `gravity_direction` | Direction de la gravite |
| `friction` | Friction du mouvement |
| `image_index` | Frame d'animation actuelle |
| `image_speed` | Vitesse d'animation |
| `image_xscale` | Echelle horizontale |
| `image_yscale` | Echelle verticale |
| `image_angle` | Angle de rotation |
| `visible` | Si dessine |
| `solid` | Si solide pour les collisions |
| `depth` | Profondeur de dessin |
| `sprite_index` | Sprite actuel |
| `alarm[0-11]` | Minuteurs d'alarme |

### Variables globales

| Variable | Description |
|----------|-------------|
| `score` | Score du jeu |
| `lives` | Vies du joueur |
| `health` | Sante du joueur (0-100) |
| `room` | Salle actuelle |
| `room_width` | Largeur de la salle actuelle |
| `room_height` | Hauteur de la salle actuelle |
| `mouse_x` | Position x de la souris |
| `mouse_y` | Position y de la souris |

---

## Prochaines etapes

- [[Programmation-Visuelle_fr]] - Utilisez les blocs Blockly pour la meme logique
- [[Editeur-Objets_fr]] - Appliquez les evenements et actions aux objets
- [[Premier-Jeu_fr]] - Voyez les evenements en action
