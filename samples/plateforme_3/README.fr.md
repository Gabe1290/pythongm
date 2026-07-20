# Plateforme — Niveau 3

Un jeu de plateformes à défilement latéral importé de GameMaker 8.x
(`samples/plateforme_3.gmk`). C'est de loin le plus gros des trois exemples de
plateforme : 2 objets (`plateforme_1`) → 4 objets (`plateforme_2`) → **15 objets**
ici, avec l'ajout de monstres terrestres et volants en patrouille (que l'on peut
tuer en leur sautant dessus, et dont les cadavres et les éclaboussures
apparaissent à l'exécution), un danger invisible qui tue instantanément, deux
types d'objets à ramasser, et un objet de sortie qui fait passer à la salle
suivante ou affiche le tableau des meilleurs scores avant de recommencer.

**Où ce niveau se situe :** il fait partie de la famille `plateforme_*` — comme
`plateforme_2`, il utilise un **arrière-plan en tuiles** (125 morceaux de tuiles
sous les briques solides, plus l'image en dégradé `fond_degrade`), l'étape que
cette famille ajoute par rapport à `maze_*`. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la progression complète.

**Sons et musique :** 4 fichiers sonores, réellement branchés : 7 appels à
`play_sound` pour `son_bonus` (ramassage), `son_monstre_mort` (monstre écrasé),
`son_personnage_mort` (mort du joueur) et `son_niveaufini` (niveau terminé).

## Comment jouer

- **Flèches gauche / droite** — déplacent Pingus (`obj_pingus`) vers la gauche ou
  la droite.
- **Flèche haut** — saut, mais uniquement quand le joueur repose sur quelque
  chose de solide (vérifié un pixel plus bas).
- **Objectif** — ramasser les `obj_bonus` (+5 points) et les `obj_power`
  (+20 points) en traversant `niveau_01` jusqu'à l'`obj_sortie` ; le toucher joue
  un petit air, puis fait passer à la salle suivante (il n'y en a pas dans cet
  exemple, on retombe donc sur la branche « meilleurs scores et recommencer ») ou
  affiche le tableau des meilleurs scores et relance la partie.
- **Les monstres** — atterrir sur un `obj_monstre` ou un `obj_monstre_volant`
  (`vspeed > 0` et au-dessus du monstre) le tue et rapporte 50 points ; le
  toucher de côté ou par en dessous coûte une vie et relance la salle. À noter :
  la collision avec `obj_monstre_volant` ne fait rien (le monstre volant ne peut
  ni blesser ni être blessé) tant qu'un `obj_power` n'a pas été ramassé — voir
  « À expérimenter ».
- **Condition de défaite** — toucher un `obj_mortel` (une zone invisible qui tue
  instantanément) ou un monstre du mauvais côté coûte une vie et relance la
  salle ; arriver à court de vies (`no_more_lives`) affiche le tableau des
  meilleurs scores et relance toute la partie. Vies au départ : 3 (réglages de
  `project.json`).

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, copies intégrées des ressources. |
| `rooms/niveau_01.json` | L'unique salle : 800×640, 194 instances et 125 tuiles d'arrière-plan. C'est la référence pour le contenu de la salle (la liste `instances` intégrée dans `project.json` est vide, comme dans `plateforme_2`). |
| `objects/*.json` | Fichiers annexes des 15 objets ; identiques aux copies intégrées dans `project.json` à ce jour (vérifié octet par octet, contrairement au fichier de salle de `plateforme_2`). |
| `sprites/` | 18 sprites (bandes de marche et de vol, sprites de mort, blocs de plateforme, objets à ramasser, sortie, marqueur). |
| `sounds/` | 4 effets sonores (mort d'un monstre, mort du joueur, ramassage d'un bonus, niveau terminé). |
| `backgrounds/` | Jeu de tuiles enneigées (`tuiles_neige.png`, source des 125 tuiles automatiques de la salle) et un dégradé vertical (`fond_degrade.png`) en arrière-plan de la salle. |
| `CREDITS.txt` | Mentions de licence des graphismes (voir « Ressources » ci-dessous). |

## Objets

15 objets, regroupés par rôle. Le nombre d'instances placées (sur 194) est
indiqué quand l'objet apparaît dans `niveau_01` ; les objets « créés à
l'exécution » n'apparaissent qu'en cours de partie, via `change_instance`.

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_pingus` | Joueur — déplacement, saut, gravité, et toute la gestion des collisions, des défaites et de la victoire | `create`, `step`, `keyboard` (gauche/droite/haut), `keyboard_release`, `collision_with_obj_brique`/`obj_monstre`/`obj_monstre_volant`/`obj_mortel`/`obj_bonus`/`obj_power`/`obj_sortie`/`obj_marqueur`, `game_start`, `no_more_lives` |
| `obj_brique` | Bloc de plateforme solide de base, 32×32 (109 placés) | (aucun — seulement l'indicateur « solide ») |
| `obj_brique_h` | Variante large de plateforme, 32×16, enfant d'`obj_brique` (15 placés) | (aucun) |
| `obj_brique_v` | Variante étroite de plateforme, 16×32, enfant d'`obj_brique` ; définie mais non placée dans `niveau_01` | (aucun) |
| `obj_brique_c` | Petite variante de plateforme, 16×16, enfant d'`obj_brique` (1 placé) | (aucun) |
| `obj_monstre` | Monstre terrestre — patrouille de gauche à droite, fait demi-tour au contact d'un mur (3 placés) | `create`, `collision_with_obj_brique` |
| `obj_monstre_mort` | Cadavre de monstre créé à l'exécution après un écrasement ; hérite d'`obj_brique` (devient une marche solide) | `create` |
| `obj_monstre_volant` | Monstre volant — patrouille vers la droite, rebondit sur les murs (2 placés) | `create`, `collision_with_obj_brique` |
| `obj_monstre_volant_mort` | Cadavre de monstre volant créé à l'exécution ; tombe avec une gravité plafonnée, se pose sur les plateformes et les marqueurs | `step`, `collision_with_obj_brique`, `collision_with_obj_marqueur` |
| `obj_mortel` | Zone de danger invisible qui tue instantanément (4 placées) | (aucun — géré depuis l'événement de collision d'`obj_pingus`) |
| `obj_splat` | Animation de mort du joueur créée à l'exécution ; relance la salle à la fin de l'animation | `create`, `animation_end` |
| `obj_bonus` | Petit objet à ramasser, +5 points, image de repos aléatoire (52 placés) | `create` |
| `obj_power` | Gros objet à ramasser, +20 points ; détermine aussi si les monstres volants peuvent blesser ou être tués (1 placé) | `create` |
| `obj_sortie` | Sortie du niveau — joue un petit air, puis salle suivante ou meilleurs scores et relance (1 placée) | (aucun — géré depuis l'événement de collision d'`obj_pingus`) |
| `obj_marqueur` | Marqueur de conception invisible et non solide ; les collisions ne font explicitement rien (5 placés) | (aucun) |

## Ressources

18 sprites, 4 sons, 2 arrière-plans. Les graphismes des sprites et des
arrière-plans sont adaptés du projet Pingus (GPL-3.0-or-later) — voir
`CREDITS.txt` pour la mention complète et les termes de la licence ; ce guide ne
reformule ni n'étend ces mentions.

## À expérimenter

- Le test d'écrasement entre `obj_pingus` et `obj_monstre`/`obj_monstre_volant`
  était autrefois `vspeed > 0 and y < other.y+8`, que la chute pouvait dépasser
  si elle était rapide (la fenêtre de 8 px était comparée à la position
  *après* déplacement) — cela coûtait une vie sur ce qui ressemblait pourtant à
  un écrasement réussi. C'est désormais `vspeed > 0 and y - vspeed < other.y+8`,
  qui compare la fenêtre à la position *avant* déplacement.
- L'objet `obj_power` conditionne silencieusement toute interaction avec
  `obj_monstre_volant` (via un `if_object_exists(obj_power, not_flag=true)`
  autour de la logique d'écrasement et de mort dans `obj_pingus`) — il vaudrait
  la peine de rendre cela visible pour les joueurs (par un changement de sprite
  ou de couleurs, par exemple) plutôt que d'en faire une règle invisible.
- La vitesse horizontale du joueur est un simple `hspeed = 4` ; l'impulsion de
  saut vaut `vspeed = -10` ; la gravité de chute est de `0,5` avec une vitesse
  limite plafonnée à `vspeed = 24`.
- La salle fait 800×640 avec `room_speed = 30`.

## État de l'export

Cet exemple figure dans la liste `SAMPLES` de `tools/smoke_run_samples.py` : il
est donc couvert par les tests automatiques (la vraie boucle de jeu est exécutée
pendant environ 180 images avec des appuis de touches simulés) à chaque passage
de ce banc d'essai. Aucune vérification n'a été faite spécifiquement pour cet
exemple sur les cibles d'export (Kivy/Web). Il est présent dans l'onglet
d'accueil de l'IDE sous le nom **« Plateforme — Niveau 3 »**
(`widgets/welcome_tab.py`).
