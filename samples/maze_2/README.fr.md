# Labyrinthe — Niveau 2

Un jeu de labyrinthe en vue de dessus avec deux labyrinthes jouables et un écran
titre : ramasse des bonbons pour marquer des points, puis atteins la sortie pour
avancer. Il reprend la boucle labyrinthe/arrivée de `maze_1` en y ajoutant un
écran de démarrage, un objet à ramasser (le bonbon, qui rapporte des points) et
une porte verrouillée qui ne s'ouvre qu'une fois tous les bonbons de la salle
récupérés. C'est un projet pygm2 natif (pas de fichier `.gmk` associé — ses
ressources proviennent à l'origine d'un import GameMaker 8.x, voir
`CREDITS.txt`, mais le projet lui-même est écrit et enregistré au format JSON de
pygm2).

**Où ce niveau se situe :** il fait partie de la famille `maze_*` — objets et
sprites, plus (contrairement à `maze_1`) une **image d'arrière-plan** fixe par
salle (`background_main`), sans tuiles au niveau de la salle. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la comparaison avec `plateforme_*` (qui ajoute les arrière-plans en tuiles)
et `match3_*` (entièrement scripté, sans actions intégrées).

**Sons et musique :** 4 fichiers sonores sont fournis (`sound_background.mid`,
`sound_diamond`/`door`/`goal.wav`) mais **aucun n'est réellement utilisé** —
aucun objet n'appelle `play_sound` ni `play_music`, le jeu est donc silencieux en
pratique malgré la présence de ces ressources. (À comparer avec `maze_3`, où le
même ensemble de sons est bel et bien joué.)

## Comment jouer

- **Écran titre (`room_start`) :** appuie sur **ESPACE** pour commencer
  (l'action `keyboard_press` de `controller_start` appelle `next_room`).
- **Les flèches** (haut/bas/gauche/droite) déplacent le joueur d'une case de la
  grille (32 px) à la fois ; le déplacement est aligné sur la grille grâce à
  `test_alignment` / `snap_to_grid` (grille de 32×32), comme dans `maze_1`.
- **Objectif :** ramasser les bonbons (`obj_diamond`, sprite `sprite_bonbon`)
  disséminés dans chaque labyrinthe — chacun vaut +10 points — puis atteindre
  l'arrivée (`obj_goal`). Dans `room2`, la sortie est en plus bloquée par une
  porte verrouillée (`obj_door`) qui ne se détruit qu'une fois tous les
  `obj_diamond` de la salle disparus.
- Toucher l'arrivée fait passer à la salle suivante (+100 points) s'il en existe
  une ; la toucher dans la dernière salle (`room2`) rapporte +100 points, ouvre
  l'écran de saisie du meilleur score et termine la partie.
- **Aucune condition de défaite :** aucune action touchant aux vies ou à la santé
  n'apparaît dans les objets de cet exemple — `starting_lives: 3` est bien défini
  dans les réglages du projet, mais n'est jamais affiché ni décrémenté.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, et copies intégrées de toutes les ressources |
| `rooms/room_start.json` | Écran titre — 1 instance (`controller_start`) |
| `rooms/room1.json` | Premier labyrinthe — 134 instances (murs, joueur, arrivée, 4 bonbons, `controller_main`) |
| `rooms/room2.json` | Second labyrinthe — 112 instances (murs, joueur, arrivée, 21 bonbons, porte verrouillée, `controller_main`) |
| `objects/*.json` | 9 définitions d'objets — comparées aux copies intégrées dans `project.json` et identiques dans cet exemple (aucun décalage) |
| `sprites/` | 7 sprites (`sprite_person`, `sprite_bonbon`, `sprite_door`, `sprite_goal`, `sprite_wall_corner`, `sprite_wall_horizontal`, `sprite_wall_vertical`) et leurs métadonnées ; `tiles.json` est un fichier orphelin (non déclaré dans `project.json`, image absente — inutilisé) |
| `backgrounds/` | `background_start.png` (écran titre), `background_tiles.png` (sol du labyrinthe) |
| `sounds/` | 4 fichiers sonores (voir « Ressources » ci-dessous) |
| `CREDITS.txt` | Mentions de licence des ressources de cet exemple |

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_person` | Personnage contrôlé par le joueur ; déplacement sur la grille | `keyboard` (bas, droite, haut, gauche, aucune touche), `collision_with_wall_corner` |
| `wall_corner` | Mur solide de base ; objet parent des deux autres types de murs | (aucun — simple obstacle passif) |
| `wall_horizontal` | Segment de mur horizontal solide (hérite de `wall_corner`) | (aucun — simple obstacle passif) |
| `wall_vertical` | Segment de mur vertical solide (hérite de `wall_corner`) | (aucun — simple obstacle passif) |
| `obj_diamond` | Bonbon à ramasser ; ajoute des points au passage | `destroy`, `collision_with_obj_person` |
| `obj_door` | Porte de sortie verrouillée (salle 2 uniquement) ; s'ouvre quand tous les bonbons ont disparu | `step` |
| `obj_goal` | Sortie du niveau ; fait passer à la salle suivante ou termine la partie | `collision_with_obj_person` |
| `controller_start` | Contrôleur de l'écran titre ; attend que le joueur commence | `create`, `keyboard_press` (ESPACE) |
| `controller_main` | Contrôleur d'affichage dans le labyrinthe ; dessine le score | `draw` |

## Ressources

7 sprites (32×32, une seule image, collision au pixel près sauf `sprite_goal`
qui n'a pas d'indicateur `precise` explicite), 2 arrière-plans, 4 sons
(`sound_background.mid`, `sound_diamond.wav`, `sound_door.wav`,
`sound_goal.wav`). L'origine et la licence de toutes les ressources de cet
exemple sont **non documentées** — voir `CREDITS.txt` dans ce dossier, qui
renvoie à la tâche « Remaining maze assets » de `docs/ASSET_LICENSES.md`. Ne
suppose pas que ces fichiers sont en CC0 ni sous une autre licence.

## À expérimenter

- La vitesse de déplacement du joueur est de `4` (cases par pas) alors que
  l'arrêt contre un mur utilise la vitesse `8` — les deux sont écrits en dur dans
  les paramètres d'action de chaque touche, dans `obj_person`, comme dans
  `maze_1`.
- Les 4 fichiers sonores fournis ne sont référencés nulle part — aucun objet
  n'appelle `play_sound` ; en brancher un sur le ramassage d'un bonbon,
  l'ouverture de la porte ou l'arrivée serait une suite naturelle.
- Les salles font de `480×480` à `480×512` avec `room_speed: 30` — de petits
  labyrinthes tenant sur un écran, sans défilement.
- `sprites/tiles.json` est un fichier résiduel non déclaré comme ressource du
  projet (son `sprites/tiles.png` n'existe pas) — on peut l'ignorer ou le
  supprimer sans risque.

## État de l'export

Couvert par la suite de tests automatiques (`tools/smoke_run_samples.py`, qui
inclut `maze_2` et le fait tourner environ 180 images avec des appuis de touches
simulés) ; non revérifié individuellement pour chaque cible d'export (Kivy/Web).
Présent dans l'onglet d'accueil de l'IDE sous le nom « Labyrinthe — Niveau 2 »
(`widgets/welcome_tab.py`).
