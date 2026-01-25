# Tutoriel : Créer un Jeu de Labyrinthe

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Maze) | [Français](Tutorial-Maze_fr) | [Deutsch](Tutorial-Maze_de) | [Italiano](Tutorial-Maze_it) | [Español](Tutorial-Maze_es) | [Português](Tutorial-Maze_pt) | [Slovenščina](Tutorial-Maze_sl) | [Українська](Tutorial-Maze_uk) | [Русский](Tutorial-Maze_ru)

---

## Introduction

Dans ce tutoriel, vous allez créer un **Jeu de Labyrinthe** où le joueur navigue à travers des couloirs pour atteindre la sortie tout en évitant les obstacles et en collectant des pièces. Ce type de jeu classique est parfait pour apprendre le mouvement fluide, la détection de collision et la conception de niveaux.

**Ce que vous apprendrez :**
- Mouvement fluide du joueur avec le clavier
- Gestion des collisions avec les murs
- Détection de l'objectif (atteindre la sortie)
- Objets à collecter
- Système de chronomètre simple

**Difficulté :** Débutant
**Preset :** Preset Débutant

---

## Étape 1 : Comprendre le Jeu

### Règles du Jeu
1. Le joueur se déplace dans un labyrinthe avec les touches fléchées
2. Les murs bloquent le mouvement du joueur
3. Collectez des pièces pour marquer des points
4. Atteignez la sortie pour terminer le niveau
5. Terminez le labyrinthe le plus vite possible !

### Ce Dont Nous Avons Besoin

| Élément | Rôle |
|---------|------|
| **Joueur** | Le personnage que vous contrôlez |
| **Mur** | Obstacles solides qui bloquent le mouvement |
| **Sortie** | Objectif qui termine le niveau |
| **Pièce** | Objets à collecter pour le score |
| **Sol** | Arrière-plan visuel (optionnel) |

---

## Étape 2 : Créer les Sprites

Tous les sprites de mur et de sol doivent faire 32x32 pixels pour créer une grille correcte.

### 2.1 Sprite du Joueur

1. Dans l'**Arbre des Ressources**, faites un clic droit sur **Sprites** et sélectionnez **Créer Sprite**
2. Nommez-le `spr_player`
3. Cliquez sur **Éditer Sprite** pour ouvrir l'éditeur
4. Dessinez un petit personnage (cercle, personne ou forme de flèche)
5. Utilisez une couleur vive comme le bleu ou le vert
6. Taille : 24x24 pixels (plus petit que les murs pour une navigation plus facile)
7. Cliquez sur **OK** pour sauvegarder

### 2.2 Sprite du Mur

1. Créez un nouveau sprite nommé `spr_wall`
2. Dessinez un motif de brique ou de pierre solide
3. Utilisez des couleurs grises ou foncées
4. Taille : 32x32 pixels

### 2.3 Sprite de la Sortie

1. Créez un nouveau sprite nommé `spr_exit`
2. Dessinez une porte, un drapeau ou un marqueur d'objectif lumineux
3. Utilisez des couleurs vertes ou dorées
4. Taille : 32x32 pixels

### 2.4 Sprite de la Pièce

1. Créez un nouveau sprite nommé `spr_coin`
2. Dessinez un petit cercle jaune/doré
3. Taille : 16x16 pixels

### 2.5 Sprite du Sol (Optionnel)

1. Créez un nouveau sprite nommé `spr_floor`
2. Dessinez un motif de carrelage simple
3. Utilisez une couleur neutre claire
4. Taille : 32x32 pixels

---

## Étape 3 : Créer l'Objet Mur

Le mur bloque le mouvement du joueur.

1. Faites un clic droit sur **Objets** et sélectionnez **Créer Objet**
2. Nommez-le `obj_wall`
3. Définissez le sprite sur `spr_wall`
4. **Cochez la case "Solide"**
5. Aucun événement nécessaire

---

## Étape 4 : Créer l'Objet Sortie

La sortie termine le niveau quand le joueur l'atteint.

1. Créez un nouvel objet nommé `obj_exit`
2. Définissez le sprite sur `spr_exit`

**Événement : Collision avec obj_player**
1. Ajouter Événement → Collision → obj_player
2. Ajouter Action : **Main2** → **Afficher Message**
   - Message : `Vous avez gagné ! Temps : ` + string(floor(global.timer)) + ` secondes`
3. Ajouter Action : **Main1** → **Room Suivante** (ou **Redémarrer Room** pour un seul niveau)

---

## Étape 5 : Créer l'Objet Pièce

Les pièces ajoutent au score quand elles sont collectées.

1. Créez un nouvel objet nommé `obj_coin`
2. Définissez le sprite sur `spr_coin`

**Événement : Collision avec obj_player**
1. Ajouter Événement → Collision → obj_player
2. Ajouter Action : **Score** → **Définir Score**
   - Nouveau Score : `10`
   - Cochez "Relatif" pour ajouter 10 points
3. Ajouter Action : **Main1** → **Détruire Instance**
   - S'applique à : Self

---

## Étape 6 : Créer l'Objet Joueur

Le joueur se déplace de manière fluide avec les touches fléchées.

1. Créez un nouvel objet nommé `obj_player`
2. Définissez le sprite sur `spr_player`

### 6.1 Événement Create - Initialiser les Variables

**Événement : Create**
1. Ajouter Événement → Create
2. Ajouter Action : **Contrôle** → **Définir Variable**
   - Variable : `move_speed`
   - Valeur : `4`

### 6.2 Mouvement avec Collision

**Événement : Step**
1. Ajouter Événement → Step → Step
2. Ajouter Action : **Contrôle** → **Exécuter Code**

```gml
// Mouvement horizontal
var hspd = 0;
if (keyboard_check(vk_right)) hspd = move_speed;
if (keyboard_check(vk_left)) hspd = -move_speed;

// Mouvement vertical
var vspd = 0;
if (keyboard_check(vk_down)) vspd = move_speed;
if (keyboard_check(vk_up)) vspd = -move_speed;

// Vérification collision horizontale
if (!place_meeting(x + hspd, y, obj_wall)) {
    x += hspd;
} else {
    // Se rapprocher du mur autant que possible
    while (!place_meeting(x + sign(hspd), y, obj_wall)) {
        x += sign(hspd);
    }
}

// Vérification collision verticale
if (!place_meeting(x, y + vspd, obj_wall)) {
    y += vspd;
} else {
    // Se rapprocher du mur autant que possible
    while (!place_meeting(x, y + sign(vspd), obj_wall)) {
        y += sign(vspd);
    }
}
```

### 6.3 Alternative : Mouvement Simple par Blocs

Si vous préférez utiliser des blocs d'action au lieu du code :

**Événement : Touche Enfoncée - Flèche Droite**
1. Ajouter Événement → Clavier → \<Droite\>
2. Ajouter Action : **Contrôle** → **Tester Collision**
   - Objet : `obj_wall`
   - X : `4`
   - Y : `0`
   - Cocher : NOT
3. Ajouter Action : **Mouvement** → **Sauter à Position**
   - X : `4`
   - Y : `0`
   - Cochez "Relatif"

Répétez pour Gauche (-4, 0), Haut (0, -4), et Bas (0, 4).

---

## Étape 7 : Créer le Contrôleur de Jeu

Le contrôleur de jeu gère le chronomètre et affiche les informations.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Pas de sprite nécessaire

**Événement : Create**
1. Ajouter Événement → Create
2. Ajouter Action : **Contrôle** → **Définir Variable**
   - Variable : `global.timer`
   - Valeur : `0`

**Événement : Step**
1. Ajouter Événement → Step → Step
2. Ajouter Action : **Contrôle** → **Définir Variable**
   - Variable : `global.timer`
   - Valeur : `1/room_speed`
   - Cochez "Relatif"

**Événement : Draw**
1. Ajouter Événement → Draw → Draw
2. Ajouter Action : **Contrôle** → **Exécuter Code**

```gml
// Afficher le score
draw_set_color(c_white);
draw_text(10, 10, "Score : " + string(score));

// Afficher le chronomètre
draw_text(10, 30, "Temps : " + string(floor(global.timer)) + "s");

// Afficher les pièces restantes
var coins_left = instance_number(obj_coin);
draw_text(10, 50, "Pièces : " + string(coins_left));
```

---

## Étape 8 : Concevoir Votre Labyrinthe

1. Faites un clic droit sur **Rooms** et sélectionnez **Créer Room**
2. Nommez-la `room_maze`
3. Définissez la taille de la room (ex : 640x480)
4. Activez "Aligner sur la Grille" et réglez la grille sur 32x32

### Placement des Objets

Construisez votre labyrinthe en suivant ces directives :

1. **Créez la bordure** - Entourez la room de murs
2. **Construisez des couloirs** - Créez des chemins à travers le labyrinthe
3. **Placez la sortie** - Mettez-la à la fin du labyrinthe
4. **Dispersez les pièces** - Placez-les le long des chemins
5. **Placez le joueur** - Près de l'entrée
6. **Ajoutez le contrôleur de jeu** - N'importe où (il est invisible)

### Exemple de Disposition de Labyrinthe

```
W W W W W W W W W W W W W W W W W W W W
W P . . . . W . . . . . . . W . . . . W
W . W W W . W . W W W W W . W . W W . W
W . W . . . . . . . . . . . . . . W . W
W . W . W W W W W . W W W W W W . W . W
W . . . W . . . . . . . . C . W . . . W
W W W . W . W W W W W W W . . W W W . W
W C . . . . W . . . . . W . . . . . . W
W . W W W W W . W W W . W W W W W W . W
W . . . . . . . . C . . . . . . . . . W
W . W W W W W W W W W . W W W W W W . W
W . . . . . . . . . . . W . . . . . . W
W W W W W W W W W W W . W . W W W W . W
W . . . . . . . . . . . . . W . C . E W
W W W W W W W W W W W W W W W W W W W W

W = Mur    P = Joueur    E = Sortie    C = Pièce    . = Vide
```

---

## Étape 9 : Testez Votre Jeu !

1. Cliquez sur **Exécuter** ou appuyez sur **F5** pour tester
2. Utilisez les touches fléchées pour naviguer dans le labyrinthe
3. Collectez les pièces pour des points
4. Trouvez la sortie pour gagner !

---

## Améliorations (Optionnel)

### Ajouter des Ennemis

Créez un ennemi qui patrouille simplement :

1. Créez `spr_enemy` (couleur rouge, 24x24)
2. Créez `obj_enemy` avec le sprite `spr_enemy`

**Événement : Create**
```gml
hspeed = 2;  // Se déplace horizontalement
```

**Événement : Collision avec obj_wall**
```gml
hspeed = -hspeed;  // Inverse la direction
```

**Événement : Collision avec obj_player**
```gml
room_restart();  // Le joueur perd
```

### Ajouter un Système de Vies

Dans l'événement Create de `obj_game_controller` :
```gml
global.lives = 3;
```

Quand le joueur touche un ennemi (au lieu de redémarrer) :
```gml
global.lives -= 1;
if (global.lives <= 0) {
    show_message("Game Over !");
    game_restart();
} else {
    // Faire réapparaître le joueur au départ
    obj_player.x = start_x;
    obj_player.y = start_y;
}
```

### Ajouter des Clés et des Portes Verrouillées

1. Créez `obj_key` - disparaît quand collectée, définit `global.has_key = true`
2. Créez `obj_locked_door` - s'ouvre seulement quand `global.has_key == true`

### Ajouter Plusieurs Niveaux

1. Créez des rooms supplémentaires (`room_maze2`, `room_maze3`)
2. Dans `obj_exit`, utilisez `room_goto_next()` au lieu de `room_restart()`

### Ajouter des Effets Sonores

Ajoutez des sons pour :
- Collecter des pièces
- Atteindre la sortie
- Toucher des ennemis (si ajoutés)
- Musique de fond

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Le joueur traverse les murs | Vérifiez que `obj_wall` a "Solide" coché |
| Le joueur reste coincé dans les murs | Assurez-vous que le sprite du joueur est plus petit que les espaces entre les murs |
| Les pièces ne disparaissent pas | Vérifiez que l'événement de collision détruit Self, pas Other |
| Le chronomètre ne fonctionne pas | Assurez-vous que le contrôleur de jeu est placé dans la room |
| Le mouvement est saccadé | Ajustez la valeur de `move_speed` (essayez 3-5) |

---

## Ce que Vous Avez Appris

Félicitations ! Vous avez créé un jeu de labyrinthe ! Vous avez appris :

- **Mouvement fluide** - Vérifier l'état des touches enfoncées pour un mouvement continu
- **Détection de collision** - Utiliser `place_meeting` pour vérifier avant de se déplacer
- **Collision pixel-perfect** - Se rapprocher des murs autant que possible
- **Objets à collecter** - Créer des objets qui augmentent le score et disparaissent
- **Système de chronomètre** - Suivre le temps écoulé avec des variables
- **Conception de niveau** - Créer des dispositions de labyrinthe navigables

---

## Idées de Défis

1. **Contre la Montre** - Ajoutez un compte à rebours. Atteignez la sortie avant la fin du temps !
2. **Score Parfait** - Exigez de collecter toutes les pièces avant que la sortie ne s'ouvre
3. **Labyrinthe Aléatoire** - Recherchez la génération procédurale de labyrinthes
4. **Brouillard de Guerre** - N'affichez que la zone autour du joueur
5. **Minimap** - Affichez un petit aperçu du labyrinthe

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels de jeux
- [Preset Débutant](Beginner-Preset_fr) - Aperçu des fonctionnalités débutant
- [Tutoriel : Pong](Tutorial-Pong_fr) - Créer un jeu à deux joueurs
- [Tutoriel : Breakout](Tutorial-Breakout_fr) - Créer un jeu de casse-briques
- [Tutoriel : Sokoban](Tutorial-Sokoban_fr) - Créer un jeu de puzzle
- [Référence des Événements](Event-Reference_fr) - Documentation complète des événements
