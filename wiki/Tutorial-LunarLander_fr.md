# Tutoriel : Créer un Jeu d'Atterrissage Lunaire

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-LunarLander) | [Français](Tutorial-LunarLander_fr) | [Deutsch](Tutorial-LunarLander_de) | [Italiano](Tutorial-LunarLander_it) | [Español](Tutorial-LunarLander_es) | [Português](Tutorial-LunarLander_pt) | [Slovenščina](Tutorial-LunarLander_sl) | [Українська](Tutorial-LunarLander_uk) | [Русский](Tutorial-LunarLander_ru)

---

## Introduction

Dans ce tutoriel, vous créerez un **Jeu d'Atterrissage Lunaire** - un jeu d'arcade classique où vous contrôlez un vaisseau spatial descendant vers une plateforme d'atterrissage. Vous devez gérer votre poussée pour contrer la gravité et atterrir en douceur sans vous écraser. Ce jeu est parfait pour apprendre les concepts physiques comme la gravité, la poussée, la vélocité et la gestion du carburant.

**Ce que vous apprendrez :**
- Physique de la gravité et de la poussée
- Détection d'atterrissage basée sur la vélocité
- Système de gestion du carburant
- Contrôle de rotation ou directionnel
- Zones d'atterrissage sécurisées

**Difficulté :** Débutant
**Preset :** Preset Intermédiaire (la physique de poussée/carburant repose sur Execute Code tout au long, qui ne fait pas partie du Preset Débutant)

---

## Étape 1 : Comprendre le Jeu

### Mécaniques du Jeu
1. L'atterrisseur est attiré vers le bas par la gravité
2. Appuyer sur HAUT applique une poussée vers le haut (utilise du carburant)
3. GAUCHE/DROITE contrôlent la rotation ou le mouvement de l'atterrisseur
4. Atterrissez doucement sur la plateforme pour gagner
5. Crash si vous atterrissez trop vite ou ratez la plateforme
6. Plus de carburant = impossible de ralentir !

### Ce Dont Nous Avons Besoin

| Élément | Fonction |
|---------|----------|
| **Atterrisseur** | Le vaisseau que vous contrôlez |
| **Plateforme d'atterrissage** | Zone sûre pour atterrir |
| **Sol** | Terrain qui cause un crash |
| **Affichage Carburant** | Montre le carburant restant |
| **Affichage Vitesse** | Montre la vitesse actuelle |

---

## Étape 2 : Créer les Sprites

### 2.1 Sprite de l'Atterrisseur

1. Dans l'**Arbre des Ressources**, faites un clic droit sur **Sprites** et sélectionnez **Create Sprite**
2. Nommez-le `spr_lander`
3. Cliquez sur **Edit Sprite** pour ouvrir l'éditeur de sprite
4. Dessinez un vaisseau spatial simple (triangle ou forme d'atterrisseur classique)
5. Taille : 32x32 pixels
6. **Important :** réglez l'origine sur centre-bas pour un atterrissage correct

### 2.2 Sprite de la Plateforme d'Atterrissage

1. Créez un nouveau sprite nommé `spr_pad`
2. Dessinez une plateforme plate avec des marquages (comme un « H »)
3. Utilisez des couleurs vives (jaune/vert)
4. Taille : 64x16 pixels

### 2.3 Sprite du Sol

1. Créez un nouveau sprite nommé `spr_ground`
2. Dessinez un terrain rocheux/accidenté
3. Utilisez des couleurs grises/marron
4. Taille : 32x32 pixels

### 2.4 Sprite de Flamme (Optionnel)

1. Créez un nouveau sprite nommé `spr_flame`
2. Dessinez une petite flamme/un jet
3. Utilisez des couleurs orange/jaune
4. Taille : 16x16 pixels

![The Sprite Editor with spr_lander open, Origin set to Center-Bottom (X 16, Y 32); spr_lander, spr_pad, spr_ground and spr_flame in the resource tree](images/tutorial-lunarlander-02-sprites.png)

---

## Étape 3 : Créer l'Objet Sol

Le sol est un terrain dangereux qui provoque un crash.

1. Faites un clic droit sur **Objects** et sélectionnez **Create Object**
2. Nommez-le `obj_ground`
3. Définissez le sprite sur `spr_ground`
4. **Cochez la case "Solid"**
5. Aucun événement nécessaire

![obj_ground's Object Events panel: empty -- Solid checked is all it needs](images/tutorial-lunarlander-03-ground-object.png)

---

## Étape 4 : Créer l'Objet Plateforme d'Atterrissage

La plateforme d'atterrissage est l'endroit où le joueur doit se poser en sécurité.

1. Créez un nouvel objet nommé `obj_pad`
2. Définissez le sprite sur `spr_pad`
3. **Cochez la case "Solid"**
4. Aucun événement nécessaire (la collision est gérée par l'atterrisseur)

![obj_pad's Object Events panel: empty, with Solid checked](images/tutorial-lunarlander-04-pad-object.png)

---

## Étape 5 : Créer l'Objet Atterrisseur

L'atterrisseur est l'objet principal contrôlé par le joueur, avec de la
physique. Contrairement aux autres tutoriels de mouvement de ce wiki, ses
commandes doivent accumuler de la vitesse progressivement et suivre une
ressource de carburant, donc cet objet s'appuie davantage sur **Control**
→ **Execute Code** (du vrai Python — `self` est l'instance courante, `game`
est le moteur de jeu, `keyboard.check(nom)` indique si une touche est
maintenue) que sur les actions structurées seules. Partout où une action
structurée fait le travail, ce tutoriel en utilise quand même une.

1. Créez un nouvel objet nommé `obj_lander`
2. Définissez le sprite sur `spr_lander`

### 5.1 Gravité et Variables de Départ

**Événement : Create**
1. Ajoutez l'action **Move** → **Set Gravity** (Direction : `270`, Gravity : `0.05`)
   — une légère attraction vers le bas ; le moteur l'ajoute automatiquement
   à la vitesse verticale de l'atterrisseur à chaque pas, comme la gravité
   du tutoriel Plateforme, en plus faible.
2. Ajoutez l'action **Control** → **Execute Code** :

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Le système de mouvement de ce projet suit déjà la vélocité via
`self.hspeed`/`self.vspeed` et déplace l'instance de cette quantité à
chaque image (avec la collision solide intégrée) — inutile de créer des
variables `hsp`/`vsp` séparées comme le ferait une simulation physique
brute.

### 5.2 Événement Step — Poussée et Contrôles

**Événement : Step** — Ajoutez l'action **Control** → **Execute Code** :

```python
if not self.landed and not self.crashed:
    if keyboard.check('up') and self.fuel > 0:
        self.vspeed -= self.thrust_force
        self.fuel -= self.fuel_use
        if self.fuel < 0:
            self.fuel = 0

    if keyboard.check('left'):
        self.hspeed -= 0.05
    if keyboard.check('right'):
        self.hspeed += 0.05

    # Limite la vitesse maximale
    self.hspeed = max(-self.max_speed, min(self.max_speed, self.hspeed))
    self.vspeed = max(-self.max_speed, min(self.max_speed, self.vspeed))

    # Empêche l'atterrisseur de dériver hors des bords ou au-dessus de la room
    room = game.current_room
    if self.x < 16:
        self.x = 16
        self.hspeed = 0
    if self.x > room.width - 16:
        self.x = room.width - 16
        self.hspeed = 0
    if self.y < 16:
        self.y = 16
        self.vspeed = 0
```

Tout le bloc est entouré de `if not self.landed and not self.crashed:` pour
que la poussée et le pilotage s'arrêtent dès la fin de la partie — l'objet
`self` n'a pas de moyen d'interrompre un événement en cours de route (pas
de `exit` façon GML), donc un `if` autour du reste du code fait
l'équivalent.

### 5.3 Collision avec la Plateforme d'Atterrissage

**Événement : Collision avec obj_pad**
1. Ajoutez l'action **Control** → **Test Expression**
   - Expression : `(self.hspeed**2 + self.vspeed**2)**0.5 <= self.safe_speed`
     — la vitesse d'atterrissage est la longueur du vecteur vélocité
     (Pythagore), pas une variable `speed` (dans ce moteur, `speed` désigne
     la *vitesse d'animation du sprite*, pas la magnitude du mouvement — un
     vrai piège pour qui vient de GameMaker).
   - Then Actions :
     1. **Control** → **Set Variable** (Variable : `landed`, Value : `true`, Scope : `self`)
     2. **Move** → **Stop Movement**
     3. **Move** → **Set Gravity** (Direction : `270`, Gravity : `0`) — empêche
        la gravité de faire remonter discrètement la vitesse verticale d'un
        atterrisseur déjà posé
     4. **Output** → **Show Message** (Message : `Perfect Landing! You Win!`)
   - Else Actions :
     1. **Control** → **Set Variable** (Variable : `crashed`, Value : `true`, Scope : `self`)
     2. **Output** → **Show Message** (Message : `Crashed! Too fast!`)
     3. **Room** → **Restart Room**

Le texte de Show Message est une chaîne fixe — il ne peut pas intégrer la
vitesse réelle d'atterrissage. Le HUD (Étape 7) affiche déjà la vitesse en
direct jusqu'au moment du contact, donc le joueur a déjà vu le chiffre.

### 5.4 Collision avec le Sol

**Événement : Collision avec obj_ground**
1. Ajoutez l'action **Control** → **Set Variable** (Variable : `crashed`, Value : `true`, Scope : `self`)
2. Ajoutez l'action **Output** → **Show Message** (Message : `Crashed into terrain!`)
3. Ajoutez l'action **Room** → **Restart Room**

![obj_lander's Object Events panel: Create (Set Gravity + Execute Code), Step (Execute Code), Collision with obj_pad (the Test Expression landing check), Collision with obj_ground (Set Variable + Show Message + Restart Room)](images/tutorial-lunarlander-05-lander-object.png)

---

## Étape 6 : Créer l'Objet Flamme (Optionnel)

Retour visuel lors de la poussée.

1. Créez un nouvel objet nommé `obj_flame`
2. Définissez le sprite sur `spr_flame`

Il sera créé par l'atterrisseur lors de la poussée (fonctionnalité
avancée). Pour une approche plus simple, vous pouvez dessiner la flamme
dans l'événement Draw de l'atterrisseur.

![obj_flame's Object Events panel: empty -- it just needs the spr_flame sprite](images/tutorial-lunarlander-06-flame-object.png)

---

## Étape 7 : Créer le Contrôleur de Jeu

Le contrôleur de jeu affiche le carburant, la vélocité et les
instructions en les lisant sur l'instance de l'atterrisseur à chaque
image.

1. Créez un nouvel objet nommé `obj_game_controller`
2. Aucun sprite nécessaire

**Événement : Draw**
1. Ajoutez l'action **Control** → **Execute Code** — trouve l'atterrisseur
   et calcule les valeurs que les actions Draw ci-dessous afficheront :

```python
lander = None
for inst in game.current_room.instances:
    if inst.object_name == 'obj_lander':
        lander = inst
        break

if lander is not None:
    self.fuel_display = round(lander.fuel)
    self.speed_display = round((lander.hspeed ** 2 + lander.vspeed ** 2) ** 0.5, 2)
    self.too_fast = self.speed_display > lander.safe_speed
    self.no_fuel = lander.fuel <= 0
else:
    self.fuel_display = 0
    self.speed_display = 0.0
    self.too_fast = False
    self.no_fuel = False
```

2. Ajoutez l'action **Game** → **Set Draw Color** (Color : `#FFFFFF`)
3. Ajoutez l'action **Game** → **Draw Text** (Text : `LUNAR LANDER`, X : `10`, Y : `10`)
4. Ajoutez l'action **Game** → **Draw Text** (Text : `Fuel:`, X : `10`, Y : `30`)
5. Ajoutez l'action **Game** → **Draw Variable** (Variable : `self.fuel_display`, X : `70`, Y : `30`)
6. Ajoutez l'action **Game** → **Draw Text** (Text : `Speed:`, X : `10`, Y : `50`)
7. Ajoutez l'action **Game** → **Draw Variable** (Variable : `self.speed_display`, X : `70`, Y : `50`)
8. Ajoutez l'action **Game** → **Draw Text** (Text : `Safe Speed: < 2`, X : `10`, Y : `70`)

Puis les deux lignes d'avertissement, chacune conditionnée par **Control**
→ **Test Expression** (pas de Else nécessaire — rien ne se dessine quand la
condition est fausse) :

9. **Control** → **Test Expression** (Expression : `self.too_fast`)
   - Then Actions : **Game** → **Set Draw Color** (`#FF0000`), **Game** →
     **Draw Text** (`TOO FAST!`, X `10`, Y `90`)
   - Else Actions : **Game** → **Set Draw Color** (`#00FF00`), **Game** →
     **Draw Text** (`Speed OK`, X `10`, Y `90`)
10. **Control** → **Test Expression** (Expression : `self.no_fuel`)
    - Then Actions : **Game** → **Set Draw Color** (`#FF0000`), **Game** →
      **Draw Text** (`NO FUEL!`, X `10`, Y `110`)

11. Ajoutez l'action **Game** → **Set Draw Color** (Color : `#808080`)
12. Ajoutez l'action **Game** → **Draw Text** (Text : `UP: Thrust | LEFT/RIGHT: Move`,
    X : `10`, Y : `440`) — choisissez un Y proche du bas de la taille de
    room que vous utilisez à l'Étape 8.

![obj_game_controller's Object Events panel: a Draw event with 12 actions -- the Execute Code HUD-value calculation, then the Set Draw Color / Draw Text / Draw Variable chain and the two Test Expression warning blocks -- with no sprite set](images/tutorial-lunarlander-07-controller-object.png)

---

## Étape 8 : Concevoir Votre Niveau

1. Faites un clic droit sur **Rooms** et sélectionnez **Create Room**
2. Nommez-la `room_game`
3. Définissez la taille de la room (ex : 640x480)
4. Réglez la couleur de fond sur noir (l'espace)

### Placement des Objets

Construisez votre niveau en suivant ces indications :

1. **Sol** - Placez `obj_ground` le long du bas pour créer le terrain
2. **Plateforme d'atterrissage** - Placez `obj_pad` dans une ouverture du terrain
3. **Atterrisseur** - Placez `obj_lander` en haut de la room
4. **Contrôleur de jeu** - Placez `obj_game_controller` n'importe où

### Exemple de Disposition de Niveau

```
    L                          <- L'atterrisseur commence ici




GGG    GGG    PPPP    GGG    GGG
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

G = Sol    L = Atterrisseur    P = Plateforme d'atterrissage
```

![The Room Editor for room_game: a solid terrain row along the bottom with rocky chunks above it, a yellow landing pad in a clear gap, the white lander near the top-left, and the obj_game_controller marker near the top-right, all on a black space background](images/tutorial-lunarlander-08-room.png)

---

## Étape 9 : Testez Votre Jeu !

1. Cliquez sur **Exécuter** ou appuyez sur **F5** pour tester
2. Utilisez la flèche **HAUT** pour la poussée (surveillez votre carburant !)
3. Utilisez les flèches **GAUCHE/DROITE** pour piloter
4. Atterrissez doucement sur la plateforme (la vitesse doit être sous 2)
5. Évitez le terrain rocheux !

---

## Améliorations (Optionnel)

### Ajouter le Contrôle de Rotation

Au lieu du mouvement gauche/droite, faites tourner l'atterrisseur et
poussez dans la direction où il pointe. Les instances de ce moteur ont un
véritable attribut `rotation` (degrés, 0 = droite, croissant dans le sens
antihoraire) utilisé pour faire pivoter le sprite — pas besoin de
`image_angle`/`lengthdir_x`/`lengthdir_y`, puisque `math` est déjà
disponible dans Execute Code :

Remplacez le code de l'événement Create du 5.1 par :
```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
self.rotation = 90  # pointant vers le haut
self.rotation_speed = 3
```

Remplacez les lignes de pilotage du 5.2 (le bloc `left`/`right` →
`hspeed`) par :
```python
if keyboard.check('left'):
    self.rotation -= self.rotation_speed
if keyboard.check('right'):
    self.rotation += self.rotation_speed
```

Et remplacez les lignes de poussée par :
```python
if keyboard.check('up') and self.fuel > 0:
    rad = math.radians(self.rotation)
    self.hspeed += self.thrust_force * math.cos(rad)
    self.vspeed -= self.thrust_force * math.sin(rad)
    self.fuel -= self.fuel_use
    if self.fuel < 0:
        self.fuel = 0
```

(le `-=` sur `vspeed` correspond au code de gravité du moteur — l'axe Y de
l'écran augmente vers le bas, donc « haut » est une vitesse verticale
négative).

### Ajouter Plusieurs Plateformes d'Atterrissage

Créez des plateformes de tailles différentes avec des valeurs de points
différentes :
- Petite plateforme = 100 points (plus difficile)
- Grande plateforme = 50 points (plus facile)

### Ajouter des Réserves de Carburant

1. Créez `obj_fuel` qui flotte dans l'air
2. En cas de collision avec l'atterrisseur, ajoutez du carburant et détruisez-le

### Ajouter des Niveaux

Créez plusieurs rooms avec un terrain de plus en plus difficile et des
plateformes d'atterrissage plus petites.

### Ajouter du Vent

Ajoutez une petite poussée horizontale constante. Dans le code de
l'événement Create de `obj_lander`, ajoutez `self.wind_force = 0.02` ;
puis, en haut du bloc `if not self.landed and not self.crashed:` de
l'événement Step, ajoutez :
```python
self.hspeed += self.wind_force
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| L'atterrisseur tombe trop vite | Diminuez la valeur `Gravity` de Set Gravity, ou augmentez `thrust_force` dans le code de l'événement Create |
| Impossible de ralentir assez | Augmentez `thrust_force`, ou augmentez `safe_speed` |
| Le carburant s'épuise trop vite | Diminuez `fuel_use`, ou augmentez le `fuel` de départ |
| L'atterrisseur sort de l'écran | Vérifiez le bloc de limites à la fin du code de l'événement Step |
| L'atterrissage n'est pas détecté | Assurez-vous que `obj_pad` a "Solid" coché |

---

## Ce Que Vous Avez Appris

Félicitations ! Vous avez créé un jeu d'atterrissage lunaire ! Vous avez appris :

- **Physique de poussée** - Ajuster `self.vspeed` contre une attraction continue de Set Gravity
- **Gestion de vélocité** - Calculer la vitesse à partir de `hspeed`/`vspeed` avec le théorème de Pythagore
- **Système de carburant** - Gameplay de gestion de ressources avec une simple variable d'instance
- **Détection de collision** - Résultats différents pour la plateforme et le sol, choisis avec Test Expression
- **Affichage HUD** - Calculer les valeurs d'affichage dans Execute Code, puis les montrer avec Draw Text/Draw Variable

---

## Idées de Défis

1. **Rotation Réaliste** - Tourner et pousser dans la direction où l'on pointe
2. **Plusieurs Niveaux** - Terrain de plus en plus difficile
3. **Système de Score** - Points selon le carburant restant et la précision de l'atterrissage
4. **Astéroïdes** - Ajouter des dangers mobiles à éviter
5. **Mode Deux Joueurs** - Course pour atterrir en premier

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels de jeux
- [Preset Intermédiaire](Intermediate-Preset_fr) - Vue d'ensemble du preset dont ce tutoriel a besoin
- [Tutoriel : Plateforme](Tutorial-Platformer_fr) - Créer un jeu de saut de plateforme
- [Tutoriel : Labyrinthe](Tutorial-Maze_fr) - Créer un jeu de navigation dans un labyrinthe
- [Référence des Événements](Event-Reference_fr) - Documentation complète des événements
