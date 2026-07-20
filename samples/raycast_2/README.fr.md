# Lancer de rayons — Niveau 2

Un jeu complet à deux niveaux : parcours chaque labyrinthe à la première
personne, ramasse toutes les gemmes en évitant les monstres qui patrouillent, et
atteins la sortie — verrouillée tant qu'il reste des gemmes. La première salle
(briques chaudes) mène à une seconde salle (caverne de cristal), et la terminer
gagne la partie. Disponible depuis l'onglet d'accueil de l'IDE
(*« Lancer de rayons — Niveau 2 »*) et exportable vers les trois cibles
(bureau, HTML5, natif/Kivy).

Ce niveau est construit sur le même **moteur de lancer de rayons 2.5D** que
[`raycast_1`](../raycast_1/README.md) : murs texturés, ciel panoramique,
placage du sol par lancer de rayons basse résolution, et sprites *billboard*
orientés vers la caméra.

## Comment jouer

- **Haut / Bas** — avance ou recule dans la direction où tu regardes
  (déplacement continu, pas case par case ; les murs te bloquent).
- **Gauche / Droite** — pivote sur place (modifie `facing_angle`, indépendant du
  déplacement : tu peux tourner à l'arrêt).
- **Ramasse les gemmes** disséminées dans le labyrinthe — chacune ajoute 10 au
  score, affiché dans la **barre de titre** de la fenêtre.
- **Évite les monstres** — ils patrouillent les couloirs (et rebondissent sur les
  murs) et se dessinent comme des *billboards* face à la caméra. Les toucher
  coûte une vie et relance la salle ; tu commences avec 3 vies.
- **Objectif :** ramasse **toutes** les gemmes d'une salle, puis atteins sa
  sortie. Y arriver trop tôt affiche seulement un rappel — la sortie ne s'ouvre
  qu'une fois la dernière gemme prise.

## Les messages du jeu

Les messages (« Collect all the gems before you leave! » et « Well done!… »)
sont écrits **en anglais** dans l'exemple, avec l'action standard
**Afficher un message** (`show_message`). C'est volontaire : ce sont des actions
programmables ordinaires, donc tu peux ouvrir l'objet `obj_goal` (ou
`obj_goal_final`), double-cliquer sur l'action et **réécrire le texte dans ta
propre langue** — exactement comme tu le ferais dans ton propre jeu. Ce guide,
lui, est traduit ; les messages du jeu restent à toi.

## Géométrie des salles

`rooms/room0.json` et `rooms/room1.json` sont des labyrinthes de 15×15 cases
(480×480) générés par un algorithme de *retour sur trace* (labyrinthe parfait :
toutes les cases sont accessibles), puis convertis vers le modèle de **murs
fins** de `raycast_1` : chaque frontière entre une case ouverte et un mur devient
un segment `obj_wall_h` (32×8) ou `obj_wall_v` (8×32) posé sur la ligne de la
grille. Chaque salle utilise une graine différente : les deux niveaux ont donc
des tracés distincts.

## Thème par salle

Les textures de la vue 3D sont **propres à chaque salle** : l'action
`enable_raycast_view` est placée sur un petit objet contrôleur invisible posé
dans chaque salle — `obj_cam0` (briques chaudes) dans room0, `obj_cam1` (caverne
de cristal, textures teintées en bleu) dans room1. Chaque contrôleur désigne
`obj_person` comme caméra via le paramètre `camera_object`, si bien que c'est
toujours le *joueur* qui voit, même si c'est le *contrôleur* qui déclenche
l'action. C'est ce qui permet à la seconde salle d'avoir une autre ambiance.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet |
| `rooms/room0.json`, `rooms/room1.json` | Les deux labyrinthes (données d'instances de référence) |
| `objects/obj_person.json` | Joueur/caméra — les événements `keyboard` gèrent la rotation et l'avance ; `game_start` initialise score et vies ; gère les collisions avec les murs et les monstres |
| `objects/obj_cam0.json`, `obj_cam1.json` | Contrôleurs de caméra, un par salle, avec leur jeu de textures |
| `objects/obj_gem.json` | Gemme à ramasser — la collision la détruit, son événement `destroy` ajoute 10 au score |
| `objects/obj_monster.json` | Monstre *billboard* qui patrouille et rebondit sur les murs |
| `objects/obj_goal.json`, `obj_goal_final.json` | Sortie de room0 (→ salle suivante) et de room1 (→ victoire) ; les deux exigent toutes les gemmes |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segments de mur fins (32×8 et 8×32) |
| `sprites/` | Repris de `raycast_1` (joueur, sortie, mur, ciel, sol), plus `spr_gem`, `spr_monster` et le jeu de textures `*_ice` de la salle 2 |

## À retenir

Tout ce niveau a été construit **sans modifier le moteur** : uniquement de la
conception de salles et de gameplay au-dessus du moteur de lancer de rayons
existant. Deux pièges rencontrés en le construisant, utiles pour tes propres
jeux :

- L'événement **`create` est rejoué à chaque redémarrage de salle**. Initialiser
  le score et les vies dans `create` les remettait à zéro à chaque mort : c'est
  `game_start` qu'il faut utiliser (il ne se déclenche qu'une fois).
  `enable_raycast_view`, à l'inverse, doit rester dans `create`, car la caméra
  doit être réarmée à chaque entrée dans une salle.
- L'**origine du sprite** compte : une origine centrée décalait les *billboards*
  d'une demi-image, pile sur les lignes de la grille où se trouvent les murs —
  les gemmes apparaissaient coupées en deux.
