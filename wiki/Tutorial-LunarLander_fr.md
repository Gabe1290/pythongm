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

### Événement Create
```gml
gravity_force = 0.05;
thrust_force = 0.1;
max_speed = 5;
hsp = 0;
vsp = 0;
fuel = 100;
fuel_use = 0.5;
landed = false;
crashed = false;
safe_speed = 2;
```

### Événement Step
```gml
if (landed || crashed) exit;

vsp += gravity_force;

if (keyboard_check(vk_up) && fuel > 0) {
    vsp -= thrust_force;
    fuel -= fuel_use;
    if (fuel < 0) fuel = 0;
}

if (keyboard_check(vk_left)) hsp -= 0.05;
if (keyboard_check(vk_right)) hsp += 0.05;

hsp = clamp(hsp, -max_speed, max_speed);
vsp = clamp(vsp, -max_speed, max_speed);

x += hsp;
y += vsp;

if (x < 16) { x = 16; hsp = 0; }
if (x > room_width - 16) { x = room_width - 16; hsp = 0; }
if (y < 16) { y = 16; vsp = 0; }
```

### Collision avec obj_pad
```gml
var total_speed = sqrt(hsp*hsp + vsp*vsp);

if (total_speed <= safe_speed) {
    landed = true;
    hsp = 0;
    vsp = 0;
    show_message("Atterrissage Parfait ! Vous Gagnez !");
} else {
    crashed = true;
    show_message("Crash ! Trop rapide !");
    room_restart();
}
```

### Collision avec obj_ground
```gml
crashed = true;
show_message("Crash dans le terrain !");
room_restart();
```

---

## Étape 6-7 : Contrôleur de Jeu

**obj_game_controller** - Événement Draw : Afficher carburant, vitesse, instructions

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

- **Physique de poussée** - Contrer la gravité
- **Gestion de vélocité** - Contrôler la vitesse
- **Système de carburant** - Gestion des ressources
- **Détection de collision** - Différents résultats

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels
- [Tutoriel : Platformer](Tutorial-Platformer_fr) - Créer un jeu de plateforme

