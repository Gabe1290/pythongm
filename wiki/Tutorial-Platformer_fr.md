# Tutoriel : Créer un Jeu de Plateforme

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduction

Dans ce tutoriel, vous allez créer un **Jeu de Plateforme** - un jeu d'action à défilement horizontal où le joueur court, saute et navigue sur des plateformes tout en évitant les dangers et en collectant des pièces. Ce genre classique est parfait pour apprendre la gravité, les mécaniques de saut et la collision avec les plateformes.

**Ce que vous apprendrez :**
- La gravité et la physique de chute
- Les mécaniques de saut avec détection du sol
- La collision avec les plateformes (atterrir dessus)
- Le mouvement gauche/droite
- Les objets à collecter et les dangers

**Difficulté :** Débutant
**Preset :** Preset Intermédiaire (les actions Execute Code de la section Améliorations ne sont pas dans le preset Débutant ; le tutoriel de base jusqu'à l'étape 10 n'a besoin que d'actions du preset Débutant)

---

## Étape 1 : Comprendre le Jeu

### Mécaniques de Jeu
1. Le joueur est affecté par la gravité et tombe
2. Le joueur peut se déplacer à gauche et à droite
3. Le joueur peut sauter quand il est sur le sol
4. Les plateformes empêchent le joueur de tomber à travers
5. Collectez des pièces pour des points
6. Atteignez le drapeau pour terminer le niveau

### Ce Dont Nous Avons Besoin

| Élément | Rôle |
|---------|------|
| **Joueur** | Le personnage que vous contrôlez |
| **Sol/Plateforme** | Surfaces solides pour se tenir debout |
| **Pièce** | Objets à collecter pour le score |
| **Pic** | Danger qui blesse le joueur |
| **Drapeau** | Objectif qui termine le niveau |

---

## Étape 2 : Créer les Sprites

### 2.1 Sprite du Joueur

1. Dans l'**Arbre des Ressources**, faites un clic droit sur **Sprites** et sélectionnez **Créer Sprite**
2. Nommez-le `spr_player`
3. Cliquez sur **Éditer Sprite** pour ouvrir l'éditeur de sprite
4. Dessinez un personnage simple (rectangle avec visage, ou bonhomme allumette)
5. Utilisez une couleur vive comme le bleu ou le rouge
6. Taille : 32x48 pixels (plus haut que large pour un personnage)
7. Cliquez sur **OK** pour sauvegarder

### 2.2 Sprite du Sol

1. Créez un nouveau sprite nommé `spr_ground`
2. Dessinez une tuile de plateforme herbe/terre
3. Utilisez des couleurs marron et vert
4. Taille : 32x32 pixels

### 2.3 Sprite de Plateforme

1. Créez un nouveau sprite nommé `spr_platform`
2. Dessinez une plateforme flottante (bois ou pierre)
3. Taille : 64x16 pixels (large et fine)

### 2.4 Sprite de Pièce

1. Créez un nouveau sprite nommé `spr_coin`
2. Dessinez un petit cercle jaune/doré
3. Taille : 16x16 pixels

### 2.5 Sprite de Pic

1. Créez un nouveau sprite nommé `spr_spike`
2. Dessinez des pics triangulaires pointant vers le haut
3. Utilisez des couleurs grises ou rouges
4. Taille : 32x32 pixels

### 2.6 Sprite du Drapeau

1. Créez un nouveau sprite nommé `spr_flag`
2. Dessinez un drapeau sur un poteau
3. Utilisez des couleurs vives (drapeau vert, poteau marron)
4. Taille : 32x64 pixels

![The Sprite Editor with spr_player open (32x48), origin centered; spr_player, spr_ground, spr_platform, spr_coin, spr_spike and spr_flag in the resource tree](images/tutorial-platformer-02-sprites.png)

---

## Étape 3 : Créer l'Objet Sol

Le sol est une plateforme solide qui empêche le joueur de tomber.

1. Faites un clic droit sur **Objets** et sélectionnez **Créer Objet**
2. Nommez-le `obj_ground`
3. Définissez le sprite sur `spr_ground`
4. **Cochez la case "Solide"**
5. Aucun événement nécessaire

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-platformer-03-ground-object.png)

---

## Étape 4 : Créer l'Objet Plateforme

Les plateformes fonctionnent comme le sol mais peuvent être placées dans l'air.

1. Créez un nouvel objet nommé `obj_platform`
2. Définissez le sprite sur `spr_platform`
3. **Cochez la case "Solide"**
4. Aucun événement nécessaire

**Astuce :** vous pouvez faire de la plateforme un enfant de `obj_ground` pour partager le même comportement de collision.

![obj_platform's Object Events panel: empty, with Solid checked -- a wide, thin sprite is the only difference from obj_ground](images/tutorial-platformer-04-platform-object.png)

---

## Étape 5 : Créer l'Objet Joueur

Le joueur est l'objet le plus complexe, avec la gravité, le saut et le mouvement.

1. Créez un nouvel objet nommé `obj_player`
2. Définissez le sprite sur `spr_player`

### 5.1 Gravité

**Événement : Create** — Ajoutez l'action **Move** → **Set Gravity**
(Direction : `270`, Gravity : `0.5`) — 270° correspond à tout droit vers le
bas ; la valeur est ajoutée à la vitesse verticale du joueur à chaque pas,
donc le joueur accélère vers le bas tout seul à partir de maintenant.

### 5.2 Mouvement, Saut et Collision avec le Sol

Ajoutez ces événements, selon le même modèle que les tutoriels précédents
de ce wiki :

| Événement | Action |
|---|---|
| Keyboard (maintenue) → Left Arrow | Set Horizontal Speed à `-4` |
| Keyboard (maintenue) → Right Arrow | Set Horizontal Speed à `4` |
| Keyboard: No Key | Set Horizontal Speed à `0` |
| Key Press → Up Arrow | Set Vertical Speed à `-10` |
| Collision avec obj_ground | Stop Movement |

Deux détails qui rendent la sensation correcte :

- **No Key ne règle QUE la vitesse horizontale à 0** — n'utilisez jamais
  Stop Movement ici, car Stop Movement remet aussi la vitesse verticale à
  zéro, ce qui annulerait la gravité à chaque fois que le joueur relâche
  une touche de direction.
- **Key Press (pas maintenue)** est ce qui fait de Up une seule impulsion
  de saut au lieu de propulser le joueur vers le haut à chaque image où la
  touche est maintenue. **Stop Movement** à l'atterrissage annule ensuite
  cette impulsion, pour que le joueur ne continue pas à monter une fois
  posé — la collision solide intégrée du moteur (l'étape 3 a déjà rendu
  `obj_ground` Solid) empêche déjà le joueur de s'enfoncer dans le sol ;
  l'événement ici se contente d'effacer la vitesse de chute restante.

![obj_player's Object Events panel: Create (Set Gravity), Keyboard (held) with two Set Horizontal Speed actions, Keyboard <No Key>, Keyboard Press with the Up-Arrow jump, and Collision with obj_ground (Stop Movement)](images/tutorial-platformer-05-player-object.png)

---

## Étape 6 : Créer l'Objet Pièce

Les pièces ajoutent au score quand elles sont collectées.

1. Créez un nouvel objet nommé `obj_coin`
2. Définissez le sprite sur `spr_coin`

**Événement : Collision avec obj_player**
1. Ajoutez Événement → Collision → obj_player
2. Ajoutez l'action **Score** → **Set Score**
   - Nouveau Score : `10`
   - Cochez "Relative"
3. Ajoutez l'action **Main1** → **Destroy Instance**
   - S'applique à : Self

![obj_coin's Object Events panel: a Collision with obj_player event holding Set Score (Relative) and Destroy Instance](images/tutorial-platformer-06-coin-object.png)

---

## Étape 7 : Créer l'Objet Pic

Les pics blessent le joueur et redémarrent le niveau.

1. Créez un nouvel objet nommé `obj_spike`
2. Définissez le sprite sur `spr_spike`

**Événement : Collision avec obj_player**
1. Ajoutez Événement → Collision → obj_player
2. Ajoutez l'action **Main2** → **Show Message**
   - Message : `Ouch! You hit a spike!`
3. Ajoutez l'action **Main1** → **Restart Room**

![obj_spike's Object Events panel: a Collision with obj_player event holding Show Message and Restart Room](images/tutorial-platformer-07-spike-object.png)

---

## Étape 8 : Créer l'Objet Drapeau

Le drapeau termine le niveau quand le joueur l'atteint.

1. Créez un nouvel objet nommé `obj_flag`
2. Définissez le sprite sur `spr_flag`

**Événement : Collision avec obj_player**
1. Ajoutez Événement → Collision → obj_player
2. Ajoutez l'action **Output** → **Show Message**
   - Message : `Level Complete!`
3. Ajoutez l'action **Room** → **Next Room** (ou **Restart Room** pour un niveau unique)

Le texte de Show Message est une chaîne fixe — il ne peut pas intégrer une
valeur en direct comme le score. Le HUD du contrôleur de jeu (étape 9)
affiche déjà le score à l'écran pendant tout le niveau, donc le joueur l'a
déjà vu.

![obj_flag's Object Events panel: a Collision with obj_player event holding Show Message and Next Room](images/tutorial-platformer-08-flag-object.png)

---

## Étape 9 : Créer le Contrôleur de Jeu

Le contrôleur de jeu affiche le score.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Aucun sprite nécessaire

**Événement : Draw**
1. Ajoutez Événement → Draw → Draw
2. Ajoutez l'action **Draw** → **Draw Text** (Text : `Score:`, X : `10`, Y : `10`)
3. Ajoutez l'action **Draw** → **Draw Variable** (Variable : `score`, X : `70`, Y : `10`)

Optionnel : ajoutez une paire **Draw Text** (`Lives:`, X `10`, Y `30`) +
**Draw Variable** (`lives`, X `70`, Y `30`) de la même façon, une fois
l'amélioration Système de Vies ci-dessous en place.

![obj_game_controller's Object Events panel: a Draw event with one Draw Text and one Draw Variable action, with no sprite set](images/tutorial-platformer-09-controller-object.png)

---

## Étape 10 : Concevoir Votre Niveau

1. Faites un clic droit sur **Rooms** et sélectionnez **Créer Room**
2. Nommez-la `room_level1`
3. Définissez la taille de la room (ex : 800x480)
4. Activez "Aligner sur la Grille" et réglez la grille sur 32x32

### Placement des Objets

Construisez votre niveau en suivant ces indications :

1. **Créez le sol** - Placez `obj_ground` le long du bas
2. **Ajoutez des plateformes** - Placez `obj_platform` dans l'air pour des défis de saut
3. **Ajoutez des trous** - Laissez des espaces dans le sol (fosses)
4. **Placez des pièces** - Dispersez-les sur les plateformes et dans des endroits difficiles d'accès
5. **Ajoutez des pics** - Près des fosses ou sur les plateformes pour le défi
6. **Placez le drapeau** - À la fin du niveau
7. **Placez le joueur** - Au début (côté gauche)
8. **Ajoutez le contrôleur de jeu** - N'importe où (il est invisible)

### Exemple de Disposition de Niveau

```
                                        F
                                      ===
                          C       C
                        =====   =====
            C                           C
          ===== X     X         X     =====
    P                   C
  ====== === ===   ===   === === ===== ======
  GGGGGG     GGG   GGG   GGG         GGGGGGGG

G = Sol    P = Joueur    F = Drapeau    C = Pièce
X = Pic    === = Plateforme
```

![The Room Editor for room_level1: a brown ground row with two pit gaps, four tan floating platforms at rising heights, gold coins on and above them, two grey spikes on the ground, the red player at the far left and the green flag at the far right](images/tutorial-platformer-10-room.png)

---

## Étape 11 : Testez Votre Jeu !

1. Cliquez sur **Exécuter** ou appuyez sur **F5** pour tester
2. Utilisez les flèches **Gauche/Droite** pour vous déplacer
3. Appuyez sur **Haut** ou **Espace** pour sauter
4. Collectez les pièces pour des points
5. Évitez les pics !
6. Atteignez le drapeau pour gagner !

---

## Améliorations (Optionnel)

### Ajouter une Hauteur de Saut Variable

Ajoutez un événement **Step** à `obj_player` avec **Control** → **Execute
Code** (du vrai Python — `self` est l'instance courante, `keyboard` permet
de tester une touche maintenue par son nom) :

```python
# Coupe le saut si Up est relâchée pendant la montée
if self.vspeed < 0 and not keyboard.check('up'):
    self.vspeed = max(self.vspeed, -5)  # moitié de l'impulsion de saut -10
```

### Ajouter un Double Saut

Cela peut se faire entièrement avec des actions structurées — aucun code
nécessaire.

**Événement : Create** — Ajoutez l'action **Control** → **Set Variable**
(Variable : `jumps_left`, Value : `2`)

**Événement : Collision avec obj_ground** — après **Stop Movement**,
ajoutez **Control** → **Set Variable** (Variable : `jumps_left`, Value :
`2`) pour refaire le plein des deux sauts à l'atterrissage.

Remplacez l'unique action de l'événement **Key Press → Up Arrow** existant
par trois, dans l'ordre :
1. **Control** → **Test Variable** (Variable : `jumps_left`, Value : `0`,
   Operation : `greater`)
2. **Control** → **Start Block**
3. **Move** → **Set Vertical Speed** (`-10`)
4. **Control** → **Set Variable** (Variable : `jumps_left`, Value : `-1`,
   **Relative** cochée)
5. **Control** → **End Block**

La paire Start/End Block signifie que les deux actions à l'intérieur ne
s'exécutent que lorsque le Test Variable au-dessus est vrai — le même
modèle de bloc gardé que les tutoriels Sokoban et Labyrinthe utilisent
pour leurs propres conditions.

### Ajouter des Plateformes Mobiles

1. Créez `obj_moving_platform` en tant qu'enfant de `obj_platform`

**Événement : Create** — Ajoutez l'action **Control** → **Execute Code** :

```python
self.start_x = self.x
self.hspeed = 2
```

**Événement : Step** — Ajoutez l'action **Control** → **Execute Code** :

```python
if self.x > self.start_x + 100:
    self.hspeed = -2
elif self.x < self.start_x:
    self.hspeed = 2
```

### Ajouter un Ennemi

1. Créez `obj_enemy` avec une IA simple

**Événement : Create** — Ajoutez l'action **Move** → **Start Moving
Direction** (Directions : `right`, Speed : `2`)

**Événement : Collision avec obj_ground** — Ajoutez l'action **Move** →
**Reverse Horizontal** (fait demi-tour aux murs ; combiné au fait que
`obj_ground` est Solid, l'ennemi ne peut jamais sortir du bord d'une
plateforme dans le sol en dessous ni traverser un mur)

**Événement : Collision avec obj_player** — cet événement se déclenche sur
`obj_enemy`, donc `self` est l'ennemi et `other` est le joueur. Ajoutez
l'action **Control** → **Test Expression**, avec des actions Then/Else
imbriquées (le même modèle que l'échantillon fourni `plateforme_3` utilise
pour exactement cette vérification de « saut sur la tête », juste inversé
puisque la vérification vit sur l'ennemi ici au lieu du joueur) :
   - Expression : `other.vspeed > 0 and other.y - other.vspeed < y - 16`
   - Then Actions : **Control** → **Execute Code** avec `other.vspeed = -5`
     (un petit rebond pour le joueur — `set_vspeed` n'a pas d'option
     « s'applique à other », donc c'est le seul endroit qui a besoin d'une
     ligne de vrai Python au lieu d'une action structurée), puis
     **Instance** → **Destroy Instance** (self)
   - Else Actions : **Room** → **Restart Room** (le joueur meurt)

`other.vspeed > 0 and other.y - other.vspeed < y - 16` vérifie la position
*du joueur* d'avant le mouvement de chute de cette image (en utilisant le
`vspeed` du joueur lui-même, puisque c'est lui qui tombe), donc une chute
rapide ne peut pas traverser la fenêtre de saut de 16 px en un seul pas —
voir le README de `plateforme_3` pour l'histoire complète de pourquoi la
version naïve `other.y < y - 16` est fragile.

### Ajouter un Système de Vies

Dans l'événement **Create** de `obj_game_controller`, ajoutez **Score** →
**Set Lives** (Value : `3`).

Quand le joueur meurt (la collision avec le pic, et la branche Else de
l'ennemi ci-dessus), remplacez **Restart Room** par **Score** → **Set
Lives** (Value : `-1`, **Relative** cochée) — la room redémarre
automatiquement car l'événement **No More Lives** ne se déclenche qu'une
fois que les vies atteignent réellement 0. Ajoutez cet événement à
`obj_game_controller` : **Other Events** → **No More Lives** → **Output** →
**Show Message** (`Game Over!`) → **Room** → **Restart Game**.

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Le joueur tombe à travers le sol | Vérifiez que `obj_ground` a "Solide" coché |
| Le joueur ne peut pas sauter | Vérifiez que l'événement Key Press → Up Arrow existe et que Set Vertical Speed est négatif |
| Le joueur continue de monter après l'atterrissage | Assurez-vous que Collision avec obj_ground a une action Stop Movement |
| Le saut paraît flottant | Augmentez la valeur Gravity de Set Gravity, ou rendez la valeur de saut de Set Vertical Speed plus négative |
| Le saut paraît trop faible | Diminuez la valeur Gravity de Set Gravity, ou rendez la valeur de saut de Set Vertical Speed plus négative |

---

## Ce que Vous Avez Appris

Félicitations ! Vous avez créé un jeu de plateforme ! Vous avez appris :

- **La physique de gravité** - Set Gravity applique une force constante vers le bas à chaque pas
- **Les mécaniques de saut** - Un événement Key Press (pas maintenue) donne une seule impulsion de vitesse vers le haut
- **La collision solide intégrée** - Le sol bloque le joueur automatiquement une fois marqué Solid, sans code de vérification manuelle de position
- **Les dangers** - Créer des objets qui redémarrent le niveau
- **La conception de niveau** - Construire des défis de plateforme

---

## Idées de Défis

1. **Saut Mural** - Permettre de sauter depuis les murs
2. **Mouvement de Dash** - Une courte accélération horizontale
3. **Plateformes Qui S'effondrent** - Des plateformes qui tombent après qu'on marche dessus
4. **Points de Contrôle** - Sauvegarder la progression en milieu de niveau
5. **Combat de Boss** - Ajouter un ennemi final avec plusieurs coups

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels de jeux
- [Preset Intermédiaire](Intermediate-Preset_fr) - Vue d'ensemble du preset dont la section Améliorations a besoin
- [Tutoriel : Labyrinthe](Tutorial-Maze_fr) - Créer un jeu de navigation dans un labyrinthe
- [Tutoriel : Breakout](Tutorial-Breakout_fr) - Créer un jeu de casse-briques
- [Référence des Événements](Event-Reference_fr) - Documentation complète des événements
