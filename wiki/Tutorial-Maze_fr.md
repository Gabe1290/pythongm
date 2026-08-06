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
**Preset :** Preset Intermédiaire (l'action Exécuter du Code utilisée pour
le chronomètre ne fait pas partie du Preset Débutant)

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
2. Ajouter Action : **Output** → **Show Message**
   - Message : `Vous avez gagné !`
3. Ajouter Action : **Room** → **Next Room** (ou **Restart Room** pour un seul niveau)

Le texte de Show Message est une chaîne fixe — il ne peut pas afficher une
valeur en direct comme le temps écoulé. Le chronomètre reste visible dans le
HUD (Étape 7) jusqu'à la victoire, le joueur a donc déjà vu son temps.

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

### 6.1 Mouvement

Ajoutez quatre événements **Keyboard** (maintenue) plus un événement **No
Key**, chacun avec une action **Move** → **Set Horizontal/Vertical Speed** :

| Événement | Action |
|---|---|
| Keyboard (maintenue) → Right Arrow | Set Horizontal Speed à `4` |
| Keyboard (maintenue) → Left Arrow | Set Horizontal Speed à `-4` |
| Keyboard (maintenue) → Down Arrow | Set Vertical Speed à `4` |
| Keyboard (maintenue) → Up Arrow | Set Vertical Speed à `-4` |
| Keyboard: No Key | Set Horizontal Speed à `0` **et** Set Vertical Speed à `0` |

### 6.2 S'arrêter aux Murs

**Événement : Collision avec obj_wall**
1. Ajouter Événement → Collision → `obj_wall`
2. Ajouter Action : **Move** → **Stop Movement**

Aucun code de vérification manuelle de position n'est nécessaire ici. La
boucle de mouvement de ce moteur refuse déjà de déplacer une instance dans
un objet solide avant même que l'image ne soit dessinée (`obj_wall` est
Solid), donc le joueur ne peut jamais réellement chevaucher un mur —
l'événement de collision ci-dessus se contente de remettre à zéro toute
vitesse restante pour que le joueur n'essaie pas de continuer à "pousser"
contre le mur.

---

## Étape 7 : Créer le Contrôleur de Jeu

Le contrôleur de jeu gère le chronomètre et affiche les informations.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Pas de sprite nécessaire

**Événement : Create** — démarrez le chronomètre avec **Control** →
**Execute Code** (l'action Execute Code de ce projet exécute du vrai Python,
pas le langage GameMaker) :

```python
self.timer = 0.0
```

**Événement : Step** — faites-le avancer à chaque image :

```python
self.timer += 1.0 / game.fps
```

**Événement : Draw** — construisez le HUD avec de vraies commandes de la
file de dessin. Ajoutez trois actions **Draw** → **Draw Text** :

| Action Draw Text | Texte | Position |
|---|---|---|
| 1ère | `Score :` | X `10`, Y `10` |
| 2ème | `Temps :` | X `10`, Y `30` |
| 3ème | `Pièces :` | X `10`, Y `50` |

puis trois actions **Draw** → **Draw Variable** juste après, pour afficher
les valeurs en direct à côté de chaque étiquette :

| Action Draw Variable | Variable | Position |
|---|---|---|
| 1ère | `score` | X `70`, Y `10` |
| 2ème | `self.timer` | X `70`, Y `30` |
| 3ème | *(voir ci-dessous)* | X `70`, Y `50` |

Il n'existe pas de compteur intégré "pièces restantes" — ajoutez une action
**Control** → **Execute Code** de plus, juste avant les actions Draw
Variable, pour le calculer dans une variable d'instance que Draw Variable
pourra ensuite lire :

```python
self.coins_left = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_coin'
)
```

(puis réglez le champ Variable de la 3ème Draw Variable sur
`self.coins_left`).

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

**Événement : Create** — Ajouter Action : **Move** → **Start Moving
Direction** (Directions : `right`, Speed : `2`)

**Événement : Collision avec obj_wall** — Ajouter Action : **Move** →
**Reverse Horizontal** (fait demi-tour à l'ennemi quand il touche un mur —
aucun code nécessaire ; combiné à la collision solide intégrée de l'étape
6.2, l'ennemi ne peut de toute façon jamais traverser un mur)

**Événement : Collision avec obj_player** — Ajouter Action : **Room** →
**Restart Room**

### Ajouter un Système de Vies

Dans l'événement **Create** de `obj_game_controller`, ajoutez **Score** →
**Set Lives** (Value : `3`).

Dans l'événement **Collision avec obj_player** de `obj_enemy`, remplacez
**Restart Room** par deux actions : **Score** → **Set Lives** (Value : `-1`,
case **Relative** cochée), puis **Move** → **Jump to Start Position** (sur
le joueur, via **Applies to: Other**) pour faire réapparaître le joueur au
lieu de redémarrer tout le labyrinthe.

Ajoutez un événement de plus à `obj_game_controller` : **Other Events** →
**No More Lives** — il se déclenche automatiquement dès que les vies
atteignent 0, inutile de le vérifier vous-même. Ajoutez **Output** → **Show
Message** (`Game Over !`) puis **Room** → **Restart Game**.

### Ajouter des Clés et des Portes Verrouillées

1. Créez `obj_key` — en collision avec `obj_player`, **Set Variable**
   (Variable : `global.has_key`, Value : `true`, Scope : `global`), puis
   **Destroy Instance** (self).
2. Créez `obj_locked_door`, case Solid cochée. Donnez-lui un événement
   **Step** avec **Control** → **Test Variable** (Variable :
   `global.has_key`, Value : `true`, Scope : `global`) → **Instance** →
   **Destroy Instance** (self) — la porte disparaît (et arrête de bloquer)
   dès que la clé est ramassée.

### Ajouter Plusieurs Niveaux

1. Créez des rooms supplémentaires (`room_maze2`, `room_maze3`)
2. Dans `obj_exit`, utilisez l'action **Next Room** au lieu de **Restart
   Room**

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
- **Collision solide intégrée** - Les murs bloquent le mouvement automatiquement une fois marqués Solid, sans code de vérification manuelle
- **Objets à collecter** - Créer des objets qui augmentent le score et disparaissent
- **Système de chronomètre** - Suivre le temps écoulé avec des variables d'instance
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
- [Preset Intermédiaire](Intermediate-Preset_fr) - Aperçu du préréglage nécessaire pour ce tutoriel
- [Tutoriel : Pong](Tutorial-Pong_fr) - Créer un jeu à deux joueurs
- [Tutoriel : Breakout](Tutorial-Breakout_fr) - Créer un jeu de casse-briques
- [Tutoriel : Sokoban](Tutorial-Sokoban_fr) - Créer un jeu de puzzle
- [Référence des Événements](Event-Reference_fr) - Documentation complète des événements
