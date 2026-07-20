# Labyrinthe — Niveau 3

Une exploration de donjon en cinq labyrinthes précédée d'un écran titre — le plus
gros des trois exemples de labyrinthe (17 objets / 6 salles, contre 9 objets /
3 salles pour `maze_2`). Il conserve la boucle « ramasser les diamants puis
atteindre l'arrivée » de `maze_2` ainsi que la porte verrouillée par les
diamants, et y ajoute trois mécaniques qui apparaissent progressivement au fil
des salles : un casse-tête de caisses à pousser dans des trous (salle 5), trois
types de monstres en patrouille qui tuent au contact (salles 3 à 5) et un piège à
bombe caché dont l'explosion a un rayon d'action (salle 4). Contrairement à
`maze_1` et `maze_2`, cet exemple **est** un import brut de GameMaker 8.x : le
fichier `samples/maze_3.gmk` est présent dans le dépôt (il n'en existe pas pour
`maze_1`/`maze_2`), et le projet pygm2 à côté en est le résultat converti.

**Où ce niveau se situe :** il fait partie de la famille `maze_*` — objets et
sprites, plus une **image d'arrière-plan** fixe par salle (comme `maze_2`), sans
tuiles au niveau de la salle. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la comparaison avec `plateforme_*` (qui ajoute les arrière-plans en tuiles)
et `match3_*` (entièrement scripté, sans actions intégrées).

**Sons et musique :** 8 fichiers sonores, et — contrairement à l'ensemble fourni
mais muet de `maze_2` — réellement utilisés : 11 appels à `play_sound` /
`play_music` répartis sur `sound_background` (musique), `sound_diamond`,
`sound_door`, `sound_goal`, `sound_dead`, `sound_explode`, `sound_hole` et
`sound_push`.

## Comment jouer

- **Écran titre (`room_start`) :** appuie sur **ESPACE** pour commencer.
- **Les flèches** déplacent le joueur d'une case de 32 px à la fois
  (`test_alignment` / `snap_to_grid`, comme dans `maze_1` et `maze_2`).
- **Objectif :** ramasser les diamants (`obj_diamond`, +5 points chacun) et
  atteindre l'`obj_goal` de chaque salle. Les salles 2 à 4 bloquent en plus la
  sortie derrière une porte verrouillée (`obj_door`) qui ne se détruit qu'une
  fois tous les diamants de la salle ramassés (la salle 3 possède 4 portes qui
  s'ouvrent toutes ensemble). La salle 5 remplace les diamants par un casse-tête
  de poussée : marche contre un `obj_block` pour le faire glisser d'une case, ou
  pousse-le dans un `obj_hole` pour combler le trou (les deux sont alors
  détruits).
- **Dangers :** trois types de monstres patrouillent dans les salles 3 à 5 et
  tuent au contact — `monster_all` rebondit sur les murs dans les 4 directions,
  `monster_lr` et `monster_ud` patrouillent sur un seul axe et font demi-tour
  contre un mur. La salle 4 cache aussi une plaque `obj trigger` qui, une fois
  touchée, transforme une `obj_bomb` voisine en `obj_explosion` : son explosion
  de 16 images détruit toute instance non solide (y compris le joueur) dans un
  rayon de 64 px.
- **Condition de défaite :** toucher un monstre coûte une vie (`sound_dead` +
  `set_lives -1` + `restart_room`) ; arriver à 0 vie affiche l'écran de saisie du
  meilleur score et relance la partie. Toucher l'arrivée de la dernière salle
  affiche au contraire un message de félicitations, rapporte +100 points et
  termine la partie de la même façon.
- **Touches de test** sur `controller_main` : **R** coûte immédiatement une vie
  et relance la salle ; **N** et **P** sautent directement à la salle suivante ou
  précédente — pratique pour tester, mais c'est aussi un moyen de sauter un
  niveau sur lequel un joueur peut tomber par hasard.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, et copies intégrées des ressources. Les copies d'objets correspondent exactement à leurs fichiers annexes, mais **les copies de salles sont périmées** : chaque salle intégrée contient 0 instance et un marqueur `_external_file` — les vraies données d'instances ne se trouvent que dans `rooms/*.json` |
| `rooms/room_start.json` | Écran titre — 1 instance (`controller_start`) |
| `rooms/room1.json` | Labyrinthe 1 — 134 instances (murs, 4 diamants, arrivée, joueur, contrôleur) |
| `rooms/room2.json` | Labyrinthe 2 — 96 instances (+20 diamants, 1 porte verrouillée) |
| `rooms/room3.json` | Labyrinthe 3 — 105 instances (+16 diamants, 4 portes verrouillées, les 3 types de monstres, 6 monstres au total) |
| `rooms/room4.json` | Labyrinthe 4 — 95 instances (+14 diamants, 1 porte, 4 `monster_lr`, 2 paires plaque/bombe) |
| `rooms/room5.json` | Labyrinthe 5 — 99 instances (4 caisses poussables, 3 trous, 2 arrivées, 2 `monster_lr` — ni diamants ni porte) |
| `objects/*.json` | 17 définitions d'objets — comparées aux copies intégrées dans `project.json` et identiques (aucun décalage). À noter : le nom de fichier `objects/obj trigger.json` contient une espace |
| `sprites/` | 16 sprites et leurs métadonnées (voir « Ressources ») |
| `sounds/` | 8 fichiers sonores, tous référencés par au moins un objet |
| `backgrounds/` | 2 arrière-plans (`background_start.png` pour l'écran titre, `background_main.png` pour les labyrinthes) |
| `CREDITS.txt` | Mentions de licence des ressources de cet exemple |

## Objets

**Joueur et contrôleurs**

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_person` | Personnage contrôlé par le joueur ; déplacement sur la grille | `keyboard` (haut/bas/gauche/droite/aucune touche), `collision_with_obj_block`, `collision_with_monster_all/_lr/_ud`, `collision_with_wall_corner` |
| `controller_start` | Contrôleur de l'écran titre ; règle score et vies, lance la musique | `create`, `keyboard` (ESPACE) |
| `controller_main` | Affichage en jeu et touches de test ; dessine score et vies, termine la partie à 0 vie | `keyboard` (R : relance), `no_more_lives`, `draw`, `keyboard_press` (N/P : changement de salle) |

**Murs**

| Objet | Rôle | Événements principaux |
|---|---|---|
| `wall_corner` | Mur solide de base ; parent des deux autres types | (aucun — obstacle passif) |
| `wall_horizontal` | Segment de mur horizontal (hérite de `wall_corner`) | (aucun) |
| `wall_vertical` | Segment de mur vertical (hérite de `wall_corner`) | (aucun) |

**Objets à ramasser, portes, arrivées et casse-tête de poussée (salle 5)**

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_diamond` | À ramasser ; +5 points | `destroy`, `collision_with_obj_person` |
| `obj_door` | Porte verrouillée ; se détruit quand tous les diamants de la salle ont disparu | `step` |
| `obj_goal` | Sortie du niveau ; change de salle ou termine la partie dans la dernière | `collision_with_obj_person` |
| `obj_block` | Caisse poussable ; glisse d'une case quand on marche dessus, ou tombe dans un trou | `collision_with_obj_person` |
| `obj_hole` | Trou ; se détruit avec toute caisse poussée dedans | `collision_with_obj_block` |

**Monstres et piège à bombe (salle 4)**

| Objet | Rôle | Événements principaux |
|---|---|---|
| `monster_all` | Rebondit sur les murs dans les 4 directions | `create`, `collision_with_wall_corner` |
| `monster_lr` | Patrouille de gauche à droite, fait demi-tour au contact d'un mur | `create`, `collision_with_wall_corner` |
| `monster_ud` | Patrouille de haut en bas, fait demi-tour au contact d'un mur | `create`, `collision_with_wall_corner` |
| `obj trigger` | Plaque cachée ; au contact, joue le son d'explosion, transforme l'`obj_bomb` associée en `obj_explosion` et se détruit | `collision_with_obj_person` |
| `obj_bomb` | Objet inerte qui tient lieu de bombe armée jusqu'au déclenchement | (aucun) |
| `obj_explosion` | Explosion de 16 images ; à l'apparition, détruit les instances non solides dans un rayon de 64 px, puis se détruit en fin d'animation | `create`, `animation_end` |

## Ressources

16 sprites (majoritairement 32×32, une seule image, collision au pixel près ;
`sprite_explosion` est une bande de 1536×96 en 16 images, sans indicateur
`precise`), 2 arrière-plans, 8 sons — les 8 sons sont référencés par au moins un
objet, contrairement à `maze_2` où aucun n'était branché. L'origine et la licence
des ressources de cet exemple sont **non documentées** — voir `CREDITS.txt` dans
ce dossier, qui renvoie à la tâche « Remaining maze assets » de
`docs/ASSET_LICENSES.md`. Ne suppose pas que ces fichiers sont en CC0 ni sous une
autre licence.

## À expérimenter

- `sprite_lives` (16×16) est une ressource déclarée mais jamais dessinée :
  l'action `draw_lives` de `controller_main` utilise en réalité `sprite_person` à
  l'échelle 0,7, ce qui laisse `sprite_lives` orphelin (même cas que le
  `tiles.json` de `maze_2`).
- L'explosion du piège (événement `create` d'`obj_explosion`) détruit le joueur
  par un simple `destroy_instance` dans son test de rayon, en contournant le
  parcours `sound_dead` / `set_lives` / `restart_room` utilisé par les
  monstres — attraper le joueur laisse donc la partie dans un état bancal plutôt
  que dans une mort propre suivie d'une relance.
- La vitesse des monstres est écrite en dur à `32/6` px par pas pour les trois
  types, tandis que le joueur avance à `4` — les monstres ne sont pas alignés sur
  la grille comme le joueur, leur déplacement ne reste donc pas calé sur les
  cases au fil du temps.
- Les touches de test `R` / `N` / `P` de `controller_main` sont actives dans le
  contrôleur livré (voir « Comment jouer ») — il vaudrait la peine de les
  conditionner à un mode de débogage si cet exemple était retravaillé.

## État de l'export

Couvert par la suite de tests automatiques (`tools/smoke_run_samples.py`, qui
inclut `maze_3` et le fait tourner un nombre fixe d'images avec des appuis de
touches simulés) ; non revérifié individuellement pour chaque cible d'export
(Kivy/Web). Présent dans l'onglet d'accueil de l'IDE sous le nom
« Labyrinthe — Niveau 3 » (`widgets/welcome_tab.py`).
