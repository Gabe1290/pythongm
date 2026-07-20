# Labyrinthe — Niveau 1

Un jeu de labyrinthe en vue de dessus, sur une grille : guide le personnage à
travers un labyrinthe bordé de murs jusqu'à la case d'arrivée, qui fait passer à
la salle suivante. C'est un projet pygm2 natif (pas de fichier `.gmk` associé —
ses ressources proviennent à l'origine d'un import GameMaker 8.x, voir
CREDITS.txt, mais le projet lui-même est écrit et enregistré au format JSON de
pygm2).

**Où ce niveau se situe :** `maze_*` est la première des trois familles
d'exemples, classées selon une progression des techniques de création (objets et
sprites intégrés → arrière-plans en tuiles de `plateforme_*` → jeux entièrement
scriptés avec `execute_code` de `match3_*`) — voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la vue d'ensemble. Cet exemple n'utilise que des objets et des sprites :
aucune image d'arrière-plan, aucune tuile au niveau de la salle.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Les flèches** (haut/bas/gauche/droite) déplacent le joueur d'une case de la
  grille (32 px) à la fois ; le déplacement est aligné sur la grille grâce à
  `test_alignment` / `snap_to_grid` (grille de 32×32).
- Les murs (`obj_wall`) sont solides — foncer dedans arrête le joueur et le
  réaligne sur la grille.
- **Objectif :** atteindre la case d'arrivée (`obj_goal`). La toucher fait passer
  à la salle suivante s'il en existe une, sinon la partie recommence.
- **Raccourcis de test :** appuyer sur `N` sur l'arrivée saute à la salle
  suivante (s'il y en a une) ; `P` revient à la précédente — même logique que
  toucher l'arrivée.
- Cet exemple ne gère ni vies, ni score, ni santé (la santé est réinitialisée par
  `set_health` au changement de salle, mais n'est jamais affichée).

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, et copies intégrées de toutes les ressources |
| `rooms/room0.json` | Tracé du labyrinthe de la salle 0 (131 instances : murs, départ du joueur, arrivée) |
| `rooms/room1.json` | Tracé du labyrinthe de la salle 1 (130 instances) |
| `objects/obj_person.json` | Définition de l'objet joueur (référence ; identique à la copie intégrée dans `project.json`) |
| `objects/obj_goal.json` | Définition de l'objet d'arrivée |
| `objects/obj_wall.json` | Définition de l'objet mur |
| `sprites/` | `spr_person.png`, `spr_wall.png`, `spr_goal.png` et leurs métadonnées `.json` |
| `CREDITS.txt` | Mentions de licence des ressources de cet exemple |

Les fichiers annexes `objects/*.json` ont été comparés aux copies intégrées dans
`project.json` : ils sont identiques dans cet exemple, aucun décalage constaté.

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_person` | Personnage contrôlé par le joueur ; déplacement sur la grille | création implicite via le clavier, `keyboard` (bas, droite, haut, gauche, aucune touche), `collision_with_obj_wall` |
| `obj_goal` | Sortie du niveau ; fait avancer ou recommencer au contact ou par touche de test | `collision_with_obj_person`, `keyboard_press` (p, n) |
| `obj_wall` | Mur fixe et solide, bloque le déplacement | (aucun — simple obstacle passif) |

## Ressources

3 sprites (`spr_person`, `spr_wall`, `spr_goal`, chacun 32×32, une seule image,
collision au pixel près), 0 son. Licences : `spr_person.png` et `spr_wall.png`
sont en CC0 (domaine public), réalisés par l'auteur de pygm2 ; l'origine de
`spr_goal.png` n'est pas encore documentée — voir `CREDITS.txt` dans ce dossier
et `docs/ASSET_LICENSES.md` à la racine du dépôt.

## À expérimenter

- La vitesse de déplacement du joueur est de `4` (cases par pas) alors que
  l'arrêt contre un mur utilise la vitesse `8` — les deux sont écrits en dur dans
  les paramètres d'action de chaque touche, dans `obj_person`.
- La taille de la grille est `32` (comme les sprites 32×32) ; la changer impose
  d'ajuster aussi les appels à `snap_to_grid` / `test_alignment` et le tracé des
  salles.
- Les salles font `480×480` avec `room_speed: 30` — de petits labyrinthes tenant
  sur un écran, sans défilement.
- Les touches de test `N` / `P` sur `obj_goal` permettent de passer d'une salle à
  l'autre sans toucher l'arrivée : pratique pour tester, mais facile à déclencher
  par accident en jouant.

## État de l'export

Couvert par la suite de tests automatiques (`tools/smoke_run_samples.py`, qui
inclut `maze_1` et le fait tourner environ 180 images avec des appuis de touches
simulés) ; non revérifié individuellement pour chaque cible d'export (Kivy/Web).
Présent dans l'onglet d'accueil de l'IDE sous le nom « Labyrinthe — Niveau 1 »
(`widgets/welcome_tab.py`).
