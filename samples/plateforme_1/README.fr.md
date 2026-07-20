# Plateforme — Niveau 1

Un jeu de plateformes minimal à défilement latéral, importé de GameMaker 8.x
(`samples/plateforme_1.gmk`). La balle contrôlée par le joueur (`obj_balle`)
grimpe un écran de plateformes en briques (`obj_brique`) à l'aide de sondes
`if_collision` à la manière de GameMaker : elle avance par pas de 4 px par image
et ne tombe sous l'effet de la gravité que lorsqu'il n'y a rien de solide
directement en dessous — un système de déplacement AABB écrit à la main plutôt
que la physique intégrée du moteur.

**Où ce niveau se situe :** il fait partie de la famille `plateforme_*`, mais
dans sa version la plus dépouillée — contrairement à `plateforme_2` et
`plateforme_3`, ce niveau n'a ni image d'arrière-plan ni **arrière-plan en
tuiles** (le tableau `tiles` de la salle est vide) ; il n'est construit qu'avec
des objets et des sprites, comme `maze_1`. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour situer la famille entière par rapport à `maze_*` et `match3_*`.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Flèches gauche / droite** — déplacent la balle de 4 px par appui, bloquée par
  les briques solides.
- **Flèche haut** — saut (met `vspeed` à -10), uniquement quand la balle repose
  sur une brique solide.
- Ce niveau n'a ni objectif, ni pièce, ni sortie — c'est un labyrinthe vertical
  de briques à escalader. Il n'y a pas non plus de monstre ni de danger, donc
  aucune condition de défaite : c'est une exploration libre de la mécanique de
  collision et de gravité.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, copies intégrées des ressources (voir la note ci-dessous). |
| `rooms/niveau_01.json` | L'unique salle : 800×640, 120 instances (surtout des murs et plateformes `obj_brique`, plus une `obj_balle`). |
| `objects/obj_balle.json` | Logique de la balle du joueur (déplacement, gravité, saut). |
| `objects/obj_brique.json` | Brique solide fixe, sans événement. |
| `sprites/` | `spr_balle.png` (la balle) et `spr_32x32_noir.png` (la brique), chacun avec son fichier `.json`. |

`objects/*.json` et `rooms/niveau_01.json` sont les fichiers annexes courants ;
leur contenu correspond à ce qui est intégré dans `project.json` pour cet exemple
(aucune divergence constatée), mais par convention du dépôt, ce sont les fichiers
annexes qui font référence en cas de désaccord.

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_balle` | Balle contrôlée par le joueur ; gravité, déplacement tenant compte des collisions, saut | `create` (vide), `step`, `collision_with_obj_brique`, `keyboard` (gauche, droite, haut) |
| `obj_brique` | Tuile de plateforme/mur solide et fixe | *(aucun — pas d'événement défini)* |

## Ressources

2 sprites (`spr_balle`, `spr_32x32_noir`), 0 son. Les deux sprites sont des
œuvres dérivées des graphismes du jeu Pingus, sous licence GPL-3.0-or-later —
voir `CREDITS.txt` dans ce dossier pour la mention complète et le crédit des
artistes d'origine ; ne les considère pas comme couverts par la licence MIT de
l'IDE.

## À expérimenter

- Événement `step` d'`obj_balle` : la gravité vaut `0,45` px/image² et la
  `vspeed` est plafonnée à `24` — augmente ou diminue l'une ou l'autre pour
  changer le poids de la chute et la vitesse limite.
- L'impulsion de saut est un simple `vspeed = -10` (touche « haut ») — une valeur
  plus grande en valeur absolue fait sauter plus haut.
- Le pas horizontal est de `4` px par appui (touches « gauche » / « droite ») —
  des pas plus grands donnent des déplacements plus vifs, mais peuvent faire
  traverser les passages étroits.
- La salle fait 800×640 avec `room_speed: 30` ; la disposition des briques dans
  `rooms/niveau_01.json` peut être réorganisée librement, puisque `obj_brique`
  n'a aucune logique propre.

## État de l'export

Cet exemple figure dans la liste `SAMPLES` de `tools/smoke_run_samples.py` : il
est donc couvert par les tests automatiques (qui exécutent la vraie boucle de jeu
pendant environ 180 images avec des appuis de touches simulés). Il n'a pas été
vérifié séparément pour les cibles d'export Kivy ou Web. Il est présent dans
l'onglet d'accueil de l'IDE sous le nom **« Plateforme — Niveau 1 »**
(`widgets/welcome_tab.py`).
