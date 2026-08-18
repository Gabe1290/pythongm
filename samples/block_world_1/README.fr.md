# Monde de Blocs — Niveau 1

Un petit monde en voxels construit sur l'extension **Monde de Blocs**
(`extensions/block_world/`) — le même territoire « inspiré de, pas copié
sur » que Luanti/Minetest occupent, construit de zéro avec un ensemble de
textures CC0 (voir `extensions/block_world/ASSETS.md`), et non un clone
d'un jeu existant.

**Le but :** grimper l'escalier jusqu'au bloc doré au sommet de la
terrasse. C'est tout — s'y rendre suffit pour gagner. Vous pouvez aussi
creuser et construire n'importe où dans le monde en chemin ; rien dans la
victoire ne l'exige.

## Contrôles

|  | |
|---|---|
| `W` `A` `S` `D` | Se déplacer (nord/sud/ouest/est — voir la remarque ci-dessous) |
| Flèche gauche / droite | Tourner le regard à gauche/droite |
| Flèche haut / bas | Regarder vers le haut/bas |
| `Espace` | Casser le bloc visé |
| `Maj` | Placer un bloc depuis votre barre d'outils |
| `Q` / `E` | Faire défiler votre sélection dans la barre d'outils |
| `H` | Afficher ou masquer les commandes (affichées au démarrage) |

**Le déplacement suit la carte, pas le regard.** Appuyer sur `D` vous
déplace toujours vers l'est, quelle que soit la direction dans laquelle
vous regardez — tourner la caméra (les flèches) ne change que ce que vous
*voyez*, pas la direction dans laquelle `WASD` vous déplace. C'est une
simplification voulue : orienter une touche de déplacement vers l'endroit
où pointe la caméra nécessite de la trigonométrie que les expressions
simples de paramètres d'action de ce moteur ne prennent pas encore en
charge, et « regarder librement autour de soi, se déplacer selon les
points cardinaux de la carte » est un schéma de contrôle tout à fait
normal pour beaucoup de vrais jeux — pas un raccourci pris pour livrer cet
exemple plus vite.

## Ce que cela démontre

- **Empiler des blocs et grimper dessus** — c'est toute la raison pour
  laquelle le personnage joué a un corps haut de deux blocs
  (`eye_height`) : depuis le sol, vous pouvez voir le sommet d'un bloc
  juste à côté de vous et construire vers le haut. L'escalier que vous
  grimpez pour atteindre le bloc doré est préconstruit, mais vous êtes
  libre d'y ajouter vos propres constructions.
- **Casser et placer** des blocs, liés à de vraies touches, avec votre
  sélection actuelle suivie par une barre d'outils (`Q`/`E` pour en faire
  défiler le contenu).
- **Un monde chargé depuis des données**, pas placé à la main :
  `blocks/room0.json` (généré par le script `tools/gen_block_world_1_room.py`
  versionné dans le dépôt) est chargé dans la salle par une action
  `load_block_world` dans l'événement `game_start` du joueur.

## Pourquoi le but ne demande pas de placer un bloc précis

Une version antérieure de cet exemple demandait de *construire* un pont
au-dessus d'une fosse pour atteindre le but. Il fallait alors regarder
nettement vers le bas, à exactement la bonne distance, pour placer des
blocs au niveau des pieds — un mécanisme réel et fonctionnel (`Haut`/`Bas`
pour regarder, puis `Maj` pour placer), mais qui rendait la réussite de
l'exemple dépendante d'une combinaison délicate d'angle et de distance que
la plupart des joueurs trouveraient frustrante dès leur première tentative.
Grimper un escalier préconstruit en marchant fonctionne à coup sûr et
montre quand même les mécanismes d'empilement et d'ascension du moteur —
construire vos propres ajouts est là pour explorer, pas pour finir.

## État du moteur

Cet exemple fonctionne sur les trois cibles de Monde de Blocs — le bureau
(pygame), HTML5 et Kivy (export Android/application de bureau). Les moteurs
HTML5 et Kivy dessinent chaque face de bloc en couleur unie (la couleur
moyenne de la texture de chaque type de bloc) plutôt qu'avec les vraies
textures par pixel du bureau — une réduction de portée délibérée et
documentée pour les exports (voir les notes de la phase 6 dans
`docs/VOXEL_WORLD_PLAN.md`) ; tout le reste — le monde, le but, le
déplacement, casser/placer, la barre d'outils et le réticule — fonctionne
à l'identique sur les trois cibles.
