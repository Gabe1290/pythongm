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
2. Ajoutez Action : **Control** → **If Collision**
   - X Offset: `0`
   - Y Offset: `0`
   - Against: `obj_target`
3. Ajoutez Action : **Instance** → **Set Sprite**
   - Sprite: `spr_crate_ok`
4. Ajoutez Action : **Control** → **Else**
5. Ajoutez Action : **Instance** → **Set Sprite**
   - Sprite: `spr_crate`

Cela rend la caisse verte quand elle est sur un emplacement cible — **If
Collision** avec les deux décalages à `0` vérifie si la position *actuelle*
de la caisse chevauche un `obj_target`.

---

## Étape 6 : Créer l'Objet Joueur

Le joueur se déplace d'une case de grille à la fois et pousse les caisses qu'il rencontre.

1. Créez un nouvel objet nommé `obj_player`
2. Définissez le sprite sur `spr_player`

### 6.1 Déplacement sur la Grille

Ajoutez un événement **Key Press** par direction, chacun avec une action
**Move** → **Move Grid** :

| Événement | Action Move Grid |
|---|---|
| Key Press → Right Arrow | Direction : `right`, Grid Size : `32` |
| Key Press → Left Arrow | Direction : `left`, Grid Size : `32` |
| Key Press → Up Arrow | Direction : `up`, Grid Size : `32` |
| Key Press → Down Arrow | Direction : `down`, Grid Size : `32` |

**Move Grid** déplace l'instance d'exactement une case de grille et gère
elle-même les collisions — elle ne fera pas entrer le joueur dans un
`obj_wall` solide, donc aucune vérification de mur supplémentaire n'est
nécessaire ici.

### 6.2 S'arrêter aux Murs

**Événement : Collision avec obj_wall**
1. Ajoutez Event → Collision → `obj_wall`
2. Ajoutez Action : **Move** → **Stop Movement**

### 6.3 Pousser les Caisses

**Événement : Collision avec obj_crate**
1. Ajoutez Event → Collision → `obj_crate`
2. Ajoutez Action : **Control** → **If Can Push**
   - Direction : `facing`
   - Object Type : `obj_crate`
   - Then Action : `push_and_move`

**If Can Push** vérifie si l'espace derrière la caisse (dans la direction où
se déplace le joueur) est libre et, si oui, pousse la caisse d'une case et
déplace le joueur à sa place, le tout en une seule action. Si l'espace
derrière la caisse est bloqué par un mur ou une autre caisse, rien ne bouge.

---

## Étape 7 : Créer le Vérificateur de Condition de Victoire

Il nous faut un contrôleur invisible qui surveille si toutes les caisses
sont sur une cible.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Aucun sprite nécessaire

**Événement : Create** — configurez le nombre de cibles une seule fois, avec
**Control** → **Execute Code** (l'action Execute Code de ce projet exécute
du vrai Python, pas le langage GameMaker — `self` est l'instance courante,
`game` est le moteur de jeu) :

```python
# Compte le nombre d'emplacements cibles dans la salle
self.total_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_target'
)
```

**Événement : Step** — vérifie à chaque image si toutes les caisses sont
sur une cible :

```python
# Compte les caisses actuellement sur une cible
crates_on_targets = sum(
    1 for inst in game.current_room.instances
    if inst.object_name == 'obj_crate'
    and game.check_collision_at_position(inst, inst.x, inst.y, 'obj_target')
)

if self.total_targets > 0 and crates_on_targets >= self.total_targets:
    self.restart_room_flag = True
```

`self.restart_room_flag = True` permet à un bloc Execute Code brut de
déclencher le même redémarrage de salle que l'action **Restart Room** — la
boucle principale vérifie cette valeur à chaque image. Ajoutez une action
**Show Message** (depuis **Output**, message `Level Complete!`) juste après
le bloc Execute Code si vous voulez une fenêtre de dialogue avant le
redémarrage.

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

Dans l'événement **Create** de `obj_game_controller`, ajoutez **Control** →
**Set Variable** (Variable : `global.moves`, Value : `0`, Scope : `global`).

Dans chacun des quatre événements Key Press à Move Grid de `obj_player`,
ajoutez une seconde action juste après Move Grid : **Control** → **Set
Variable** (Variable : `global.moves`, Value : `1`, Scope : `global`, case
**Relative** cochée) — cela ajoute 1 au compteur à chaque appui de touche,
que le mouvement ait été bloqué par un mur ou non.

Dans l'événement **Draw** de `obj_game_controller`, ajoutez **Draw** →
**Draw Variable** (Variable : `global.moves`, X : `10`, Y : `30`).

### Ajouter une Fonction Annuler

Stockez les positions précédentes et permettez d'appuyer sur Z pour annuler le dernier mouvement.

### Ajouter Plusieurs Niveaux

Créez plus de salles (`room_level2`, `room_level3`, etc.) et utilisez
l'action **Next Room** (catégorie Room) à la place de **Restart Room** dans
le bloc Execute Code de vérification de victoire (`self.next_room_flag =
True` au lieu de `self.restart_room_flag = True`) quand un niveau est
terminé.

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
| La caisse ne change pas de couleur | Vérifiez que l'action **If Collision** de l'événement Step cible bien `obj_target` |
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
