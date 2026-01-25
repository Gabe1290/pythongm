# Tutoriel : Créer un Jeu de Puzzle Sokoban

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Sokoban) | [Français](Tutorial-Sokoban_fr) | [Deutsch](Tutorial-Sokoban_de) | [Italiano](Tutorial-Sokoban_it) | [Español](Tutorial-Sokoban_es) | [Português](Tutorial-Sokoban_pt) | [Slovenščina](Tutorial-Sokoban_sl) | [Українська](Tutorial-Sokoban_uk) | [Русский](Tutorial-Sokoban_ru)

---

## Introduction

Dans ce tutoriel, vous allez créer un jeu de puzzle **Sokoban** - un classique des jeux de puzzle où le joueur doit pousser toutes les caisses vers des emplacements cibles. Sokoban (signifiant « gardien d'entrepôt » en japonais) est parfait pour apprendre les mouvements basés sur une grille et la logique des jeux de puzzle.

**Ce que vous allez apprendre :**
- Les mouvements basés sur une grille (se déplacer par étapes fixes)
- La mécanique de poussée pour déplacer des objets
- La détection de collision avec plusieurs types d'objets
- La détection de la condition de victoire
- La conception de niveaux pour les jeux de puzzle

**Difficulté :** Débutant
**Préréglage :** Beginner Preset

---

## Étape 1 : Comprendre le Jeu

### Règles du Jeu
1. Le joueur peut se déplacer vers le haut, le bas, la gauche ou la droite
2. Le joueur peut pousser les caisses (mais pas les tirer)
3. Une seule caisse peut être poussée à la fois
4. Les caisses ne peuvent pas être poussées à travers les murs ou d'autres caisses
5. Le niveau est complet quand toutes les caisses sont sur les emplacements cibles

### Ce Dont Nous Avons Besoin

| Élément | Objectif |
|---------|----------|
| **Joueur** | Le gardien d'entrepôt que vous contrôlez |
| **Caisse** | Des boîtes que le joueur pousse |
| **Mur** | Des obstacles solides qui bloquent le mouvement |
| **Cible** | Des emplacements objectifs où les caisses doivent être placées |
| **Sol** | Un sol marchable (visuel optionnel) |

---

## Étape 2 : Créer les Sprites

Tous les sprites doivent avoir la même taille (32x32 pixels fonctionne bien) pour créer une grille correcte.

### 2.1 Sprite du Joueur

1. Dans l'**Arborescence des Ressources**, cliquez avec le bouton droit sur **Sprites** et sélectionnez **Create Sprite**
2. Nommez-le `spr_player`
3. Cliquez sur **Edit Sprite** pour ouvrir l'éditeur de sprites
4. Dessinez un simple personnage (une forme de personne ou de robot)
5. Utilisez une couleur distincte comme le bleu ou le vert
6. Taille : 32x32 pixels
7. Cliquez sur **OK** pour enregistrer

### 2.2 Sprite de la Caisse

1. Créez un nouveau sprite nommé `spr_crate`
2. Dessinez une caisse en bois ou une forme de boîte
3. Utilisez des couleurs marron ou orange
4. Taille : 32x32 pixels

### 2.3 Sprite de la Caisse sur la Cible

1. Créez un nouveau sprite nommé `spr_crate_ok`
2. Dessinez la même caisse mais avec une couleur différente (verte) pour montrer qu'elle est correctement placée
3. Taille : 32x32 pixels

### 2.4 Sprite du Mur

1. Créez un nouveau sprite nommé `spr_wall`
2. Dessinez un motif de brique ou de pierre solide
3. Utilisez des couleurs grises ou foncées
4. Taille : 32x32 pixels

### 2.5 Sprite de la Cible

1. Créez un nouveau sprite nommé `spr_target`
2. Dessinez une marque X ou un indicateur d'objectif
3. Utilisez une couleur vive comme le rouge ou le jaune
4. Taille : 32x32 pixels

### 2.6 Sprite du Sol (Optionnel)

1. Créez un nouveau sprite nommé `spr_floor`
2. Dessinez un motif simple de carrelage de sol
3. Utilisez une couleur neutre
4. Taille : 32x32 pixels

---

## Étape 3 : Créer l'Objet Mur

Le mur est l'objet le plus simple - il bloque simplement le mouvement.

1. Cliquez avec le bouton droit sur **Objects** et sélectionnez **Create Object**
2. Nommez-le `obj_wall`
3. Définissez le sprite sur `spr_wall`
4. **Cochez la case "Solid"**
5. Aucun événement nécessaire

---

## Étape 4 : Créer l'Objet Cible

Les cibles marquent l'endroit où les caisses doivent être placées.

1. Créez un nouvel objet nommé `obj_target`
2. Définissez le sprite sur `spr_target`
3. Aucun événement nécessaire - c'est juste un marqueur
4. Laissez "Solid" décoché (le joueur et les caisses peuvent être dessus)

---

## Étape 5 : Créer l'Objet Caisse

La caisse est poussée par le joueur et change d'apparence quand elle est sur une cible.

1. Créez un nouvel objet nommé `obj_crate`
2. Définissez le sprite sur `spr_crate`
3. **Cochez la case "Solid"**

**Événement : Step**
1. Ajoutez Event → Step → Step
2. Ajoutez Action : **Control** → **Test Variable**
   - Variable: `place_meeting(x, y, obj_target)`
   - Value: `1`
   - Operation: Equal to
3. Ajoutez Action : **Main1** → **Change Sprite**
   - Sprite: `spr_crate_ok`
   - Subimage: `0`
   - Speed: `1`
4. Ajoutez Action : **Control** → **Else**
5. Ajoutez Action : **Main1** → **Change Sprite**
   - Sprite: `spr_crate`
   - Subimage: `0`
   - Speed: `1`

Cela rend la caisse verte quand elle est sur un emplacement cible.

---

## Étape 6 : Créer l'Objet Joueur

Le joueur est l'objet le plus complexe avec des mouvements basés sur une grille et une mécanique de poussée.

1. Créez un nouvel objet nommé `obj_player`
2. Définissez le sprite sur `spr_player`

### 6.1 Se Déplacer vers la Droite

**Événement : Keyboard Press Right Arrow**
1. Ajoutez Event → Keyboard → Press Right

Tout d'abord, vérifiez s'il y a un mur sur le chemin :
2. Ajoutez Action : **Control** → **Test Collision**
   - Object: `obj_wall`
   - X: `32`
   - Y: `0`
   - Check: NOT (signifiant « s'il n'y a PAS de mur »)

S'il n'y a pas de mur, vérifiez s'il y a une caisse :
3. Ajoutez Action : **Control** → **Test Collision**
   - Object: `obj_crate`
   - X: `32`
   - Y: `0`

S'il y a une caisse, nous devons vérifier si nous pouvons la pousser :
4. Ajoutez Action : **Control** → **Test Collision** (pour la destination de la caisse)
   - Object: `obj_wall`
   - X: `64`
   - Y: `0`
   - Check: NOT

5. Ajoutez Action : **Control** → **Test Collision**
   - Object: `obj_crate`
   - X: `64`
   - Y: `0`
   - Check: NOT

Si les deux vérifications réussissent, poussez la caisse :
6. Ajoutez Action : **Control** → **Code Block**
```
var crate = instance_place(x + 32, y, obj_crate);
if (crate != noone) {
    crate.x += 32;
}
```

Maintenant, déplacez le joueur :
7. Ajoutez Action : **Move** → **Jump to Position**
   - X: `32`
   - Y: `0`
   - Cochez "Relative"

### 6.2 Se Déplacer vers la Gauche

**Événement : Keyboard Press Left Arrow**
Suivez le même modèle qu'en se déplaçant vers la droite, mais utilisez :
- X offset: `-32` pour vérifier le mur/la caisse
- X offset: `-64` pour vérifier si la caisse peut être poussée
- Déplacer la caisse de `-32`
- Sauter à la position X: `-32`

### 6.3 Se Déplacer vers le Haut

**Événement : Keyboard Press Up Arrow**
Suivez le même modèle, mais utilisez les valeurs Y :
- Y offset: `-32` pour la vérification
- Y offset: `-64` pour la destination de la caisse
- Déplacer la caisse de Y: `-32`
- Sauter à la position Y: `-32`

### 6.4 Se Déplacer vers le Bas

**Événement : Keyboard Press Down Arrow**
Utilisez :
- Y offset: `32` pour la vérification
- Y offset: `64` pour la destination de la caisse
- Déplacer la caisse de Y: `32`
- Sauter à la position Y: `32`

---

## Étape 7 : Mouvement du Joueur Simplifié (Alternative)

Si l'approche basée sur les blocs ci-dessus semble complexe, voici une approche plus simple basée sur le code pour chaque direction :

**Événement : Keyboard Press Right Arrow**
Ajoutez Action : **Control** → **Execute Code**
```
// Check if we can move right
if (!place_meeting(x + 32, y, obj_wall)) {
    // Check if there's a crate
    var crate = instance_place(x + 32, y, obj_crate);
    if (crate != noone) {
        // There's a crate - can we push it?
        if (!place_meeting(x + 64, y, obj_wall) && !place_meeting(x + 64, y, obj_crate)) {
            crate.x += 32;
            x += 32;
        }
    } else {
        // No crate, just move
        x += 32;
    }
}
```

Répétez pour les autres directions avec des changements de coordonnées appropriés.

---

## Étape 8 : Créer le Vérificateur de Condition de Victoire

Nous avons besoin d'un objet pour vérifier si toutes les caisses sont sur les cibles.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Aucun sprite nécessaire

**Événement : Create**
1. Ajoutez Event → Create
2. Ajoutez Action : **Score** → **Set Variable**
   - Variable: `global.total_targets`
   - Value: `0`
3. Ajoutez Action : **Control** → **Execute Code**
```
// Count how many targets exist
global.total_targets = instance_number(obj_target);
```

**Événement : Step**
1. Ajoutez Event → Step → Step
2. Ajoutez Action : **Control** → **Execute Code**
```
// Count crates that are on targets
var crates_on_targets = 0;
with (obj_crate) {
    if (place_meeting(x, y, obj_target)) {
        crates_on_targets += 1;
    }
}

// Check if all targets have crates
if (crates_on_targets >= global.total_targets && global.total_targets > 0) {
    // Level complete!
    show_message("Level Complete!");
    room_restart();
}
```

**Événement : Draw**
1. Ajoutez Event → Draw
2. Ajoutez Action : **Draw** → **Draw Text**
   - Text: `Sokoban - Push all crates to targets!`
   - X: `10`
   - Y: `10`

---

## Étape 9 : Concevoir Votre Niveau

1. Cliquez avec le bouton droit sur **Rooms** et sélectionnez **Create Room**
2. Nommez-le `room_level1`
3. Définissez la taille de la salle sur un multiple de 32 (par exemple, 640x480)
4. Activez "Snap to Grid" et définissez la grille sur 32x32

### Placer des Objets

Construisez votre niveau en suivant ces directives :

1. **Entourez le niveau de murs** - Créez une bordure
2. **Ajoutez des murs internes** - Créez la structure du puzzle
3. **Placez les cibles** - Où les caisses doivent aller
4. **Placez les caisses** - Le même nombre que les cibles !
5. **Placez le joueur** - Position de départ
6. **Placez le contrôleur de jeu** - N'importe où (c'est invisible)

### Exemple de Disposition de Niveau

```
W W W W W W W W W W
W . . . . . . . . W
W . P . . . C . . W
W . . W W . . . . W
W . . W T . . C . W
W . . . . . W W . W
W . T . . . . . . W
W . . . . . . . . W
W W W W W W W W W W

W = Wall
P = Player
C = Crate
T = Target
. = Empty floor
```

**Important :** Ayez toujours le même nombre de caisses et de cibles !

---

## Étape 10 : Testez Votre Jeu !

1. Cliquez sur **Run** ou appuyez sur **F5** pour tester
2. Utilisez les touches fléchées pour vous déplacer
3. Poussez les caisses sur les cibles X rouges
4. Quand toutes les caisses sont sur les cibles, vous gagnez !

---

## Améliorations (Optionnel)

### Ajouter un Compteur de Mouvements

Dans `obj_game_controller` :

**Événement : Create** - Ajoutez :
```
global.moves = 0;
```

Dans `obj_player`, après chaque mouvement réussi, ajoutez :
```
global.moves += 1;
```

Dans `obj_game_controller` **Événement : Draw** - Ajoutez :
```
draw_text(10, 30, "Moves: " + string(global.moves));
```

### Ajouter une Fonction Annuler

Stockez les positions précédentes et permettez d'appuyer sur Z pour annuler le dernier mouvement.

### Ajouter Plusieurs Niveaux

Créez plus de salles (`room_level2`, `room_level3`, etc.) et utilisez :
```
room_goto_next();
```
au lieu de `room_restart()` quand vous terminez un niveau.

### Ajouter des Effets Sonores

Ajoutez des sons pour :
- Le joueur se déplaçant
- Pousser une caisse
- Une caisse atterrissant sur une cible
- Niveau complet

---

## Dépannage

| Problème | Solution |
|---------|----------|
| Le joueur se déplace à travers les murs | Vérifiez que `obj_wall` a "Solid" coché |
| La caisse ne change pas de couleur | Vérifiez que l'événement Step vérifie `place_meeting` correctement |
| Peut pousser la caisse à travers le mur | Vérifiez la détection de collision avant de déplacer la caisse |
| Le message de victoire apparaît immédiatement | Assurez-vous que les cibles sont placées séparément des caisses |
| Le joueur se déplace sur plusieurs carrés | Utilisez l'événement Keyboard Press, pas l'événement Keyboard |

---

## Ce Que Vous Avez Appris

Félicitations ! Vous avez créé un jeu de puzzle Sokoban complet ! Vous avez appris :

- **Mouvement basé sur une grille** - Se déplacer par étapes de 32 pixels fixes
- **Mécanique de poussée** - Détecter et déplacer les objets que le joueur pousse
- **Logique de collision complexe** - Vérifier plusieurs conditions avant d'autoriser le mouvement
- **Changements d'état** - Changer le sprite en fonction de la position de l'objet
- **Conditions de victoire** - Vérifier quand tous les objectifs sont terminés
- **Conception de niveaux** - Créer des dispositions de puzzle solubles

---

## Défi : Concevez Vos Propres Niveaux !

Le vrai plaisir de Sokoban est de concevoir des puzzles. Essayez de créer des niveaux qui :
- Commencent faciles et deviennent progressivement plus difficiles
- Nécessitent une planification anticipée
- N'ont qu'une seule solution
- Utilisent l'espace minimal efficacement

Souvenez-vous : Un bon puzzle Sokoban devrait être difficile mais juste !

---

## Voir Aussi

- [Tutorials](Tutorials_fr) - Plus de tutoriels de jeux
- [Beginner Preset](Beginner-Preset_fr) - Aperçu des fonctionnalités pour débutants
- [Tutorial: Pong](Tutorial-Pong_fr) - Créer un jeu à deux joueurs
- [Tutorial: Breakout](Tutorial-Breakout_fr) - Créer un jeu de casse-briques
- [Event Reference](Event-Reference_fr) - Documentation complète des événements
