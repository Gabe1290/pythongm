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
**Preset :** Preset Débutant

---

## Étape 1 : Comprendre le Jeu

### Mécaniques du Jeu
1. L'atterrisseur est attiré vers le bas par la gravité
2. Appuyer sur HAUT applique une poussée vers le haut (utilise du carburant)
3. GAUCHE/DROITE contrôlent la rotation ou le mouvement
4. Atterrissez doucement sur la plateforme pour gagner
5. Crash si vous atterrissez trop vite ou ratez la plateforme
6. Plus de carburant = impossible de ralentir !

### Ce Dont Nous Avons Besoin

| Élément | Fonction |
|---------|----------|
| **Atterrisseur** | Le vaisseau que vous contrôlez |
| **Plateforme** | Zone sûre pour atterrir |
| **Sol** | Terrain qui cause un crash |
| **Affichage Carburant** | Montre le carburant restant |
| **Affichage Vitesse** | Montre la vitesse actuelle |

---

## Étape 2 : Créer les Sprites

### Sprites
- `spr_lander` (32x32 pixels) - vaisseau spatial simple
- `spr_pad` (64x16 pixels) - plateforme d'atterrissage
- `spr_ground` (32x32 pixels) - terrain rocheux
- `spr_flame` (16x16 pixels) - flamme de propulsion (optionnel)

---

## Étape 3-4 : Créer les Objets Sol et Plateforme

**obj_ground** et **obj_pad** : Définissez le sprite, cochez "Solide"

---

## Étape 5 : Créer l'Objet Atterrisseur

L'atterrisseur est l'objet le plus complexe : ses commandes doivent
accumuler de la vitesse progressivement et suivre une ressource de
carburant. Cet objet utilise donc davantage **Control** → **Execute Code**
(du vrai Python — `self` est l'instance courante, `game` est le moteur de
jeu, `keyboard.check(nom)` indique si une touche est maintenue) que les
tutoriels de mouvement précédents de ce wiki, tout en gardant une action
structurée partout où c'est possible.

### 5.1 Gravité et Variables de Départ

**Événement Create**
1. Action : **Move** → **Set Gravity** (Direction : `270`, Gravity : `0.05`)
   — une légère attraction vers le bas ; le moteur l'ajoute automatiquement
   à la vitesse verticale à chaque image, comme dans le tutoriel Plateforme,
   en plus faible.
2. Action : **Control** → **Execute Code** :

```python
self.thrust_force = 0.1
self.max_speed = 5
self.fuel = 100
self.fuel_use = 0.5
self.landed = False
self.crashed = False
self.safe_speed = 2
```

Le système de mouvement de ce moteur suit déjà la vélocité via
`self.hspeed`/`self.vspeed` et déplace l'instance de cette quantité à
chaque image (avec la collision solide intégrée) — inutile de créer des
variables `hsp`/`vsp` séparées comme le ferait une simulation physique
manuelle.

### 5.2 Événement Step — Poussée et Contrôles

**Événement Step** — Action : **Control** → **Execute Code** :

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
n'a pas de moyen d'interrompre un événement en cours de route (pas de
`exit` façon GML) ; un `if` autour du reste du code fait l'équivalent.

### 5.3 Collision avec la Plateforme

**Événement : Collision avec obj_pad**
1. Action : **Control** → **Test Expression**
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
     4. **Output** → **Show Message** (Message : `Atterrissage Parfait ! Vous Gagnez !`)
   - Else Actions :
     1. **Control** → **Set Variable** (Variable : `crashed`, Value : `true`, Scope : `self`)
     2. **Output** → **Show Message** (Message : `Crash ! Trop rapide !`)
     3. **Room** → **Restart Room**

Le texte de Show Message est une chaîne fixe — il ne peut pas afficher la
vitesse réelle d'atterrissage. Le HUD (Étape 7) affiche déjà la vitesse en
direct jusqu'au moment du contact, donc le joueur a déjà vu le chiffre.

### 5.4 Collision avec le Sol

**Événement : Collision avec obj_ground**
1. Action : **Control** → **Set Variable** (Variable : `crashed`, Value : `true`, Scope : `self`)
2. Action : **Output** → **Show Message** (Message : `Crash dans le terrain !`)
3. Action : **Room** → **Restart Room**

---

## Étape 6-7 : Contrôleur de Jeu

**obj_game_controller** — Événement Draw : trouve l'atterrisseur via une
boucle sur `game.current_room.instances` (même schéma que le compteur de
pièces du tutoriel Labyrinthe), calcule le carburant/la vitesse arrondis
dans une **Execute Code**, puis les affiche avec **Draw Text**/**Draw
Variable** ; voir la [version anglaise](Tutorial-LunarLander) pour le détail
complet action par action.

---

## Étape 8 : Concevoir Votre Niveau

1. Créez `room_game` (640x480)
2. Fond noir (espace)
3. Placez le sol en bas avec une ouverture
4. Placez la plateforme dans l'ouverture
5. Placez l'atterrisseur en haut
6. Placez le contrôleur de jeu

---

## Ce Que Vous Avez Appris

- **Physique de poussée** - Ajuster `self.vspeed` contre une gravité continue (Set Gravity)
- **Gestion de vélocité** - Calculer la vitesse à partir de `hspeed`/`vspeed` avec Pythagore
- **Système de carburant** - Gestion de ressources avec une simple variable d'instance
- **Détection de collision** - Résultats différents pour la plateforme et le sol, choisis avec Test Expression

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels
- [Tutoriel : Platformer](Tutorial-Platformer_fr) - Créer un jeu de plateforme
