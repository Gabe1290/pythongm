# Vues — Niveau 2

Une démonstration de **coopération en écran partagé** : la salle de 2400×800 est
affichée par deux caméras côte à côte dans une seule fenêtre de 800×600. La
**moitié gauche** (vue 0) suit le **joueur 1** (orange, touches fléchées) ; la
**moitié droite** (vue 1) suit le **joueur 2** (turquoise, touches WASD). Chaque
joueur explore la salle commune dans son propre couloir et ramasse des pièces —
et l'on voit les deux à la fois.

**Où ce niveau se situe :** c'est le second niveau de la quatrième famille
d'exemples. `views_1` introduisait une caméra unique qui défile ; `views_2`
introduit **plusieurs fenêtrages simultanés** — l'autre grande possibilité des
vues de GameMaker. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la progression complète. Le déplacement reprend le principe de grille de
`maze_1` et `views_1`.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Joueur 1 (orange) :** les touches fléchées — se déplace dans la vue de
  **gauche**.
- **Joueur 2 (turquoise) :** `W` `A` `S` `D` — se déplace dans la vue de
  **droite**.
- Les deux avancent d'une case de la grille (32 px) à la fois ; les murs
  (`obj_wall`) sont solides. Une cloison centrale percée d'ouvertures sépare les
  deux couloirs.
- **Objectif :** ramasser les 18 pièces (`obj_coin`) — n'importe lequel des deux
  joueurs peut prendre n'importe quelle pièce ; chacune vaut 10 points (affichés
  dans le titre de la fenêtre).

## Pourquoi les deux joueurs s'arrêtent indépendamment (un vrai piège)

Le déplacement sur grille s'arrête normalement sur l'événement `nokey` (déclenché
quand *aucune* touche n'est enfoncée). Mais l'état des touches est suivi
globalement, pour toutes les instances : avec deux joueurs, `nokey` ne se
déclenche donc que lorsque **les deux** ont tout relâché — le joueur 2
continuerait de glisser tant que le joueur 1 maintient une touche. Chaque joueur
s'arrête donc plutôt via **`keyboard_release`** sur **ses propres** touches
(les flèches pour J1, WASD pour J2), qui se déclenche par touche et par objet.
C'est la différence avec le joueur unique de `views_1`, qui peut utiliser `nokey`
sans risque.

## Comment l'écran partagé est configuré

Un contrôleur invisible, `obj_camera`, configure les deux vues dans son événement
**create** (les actions intégrées `enable_views` et deux `set_view`), et la même
configuration est inscrite dans le bloc `views` de la salle pour que tout soit
correct dès la première image à l'export :

- **vue 0** — `view` et `port` de `400×600`, `port_x` à 0 (moitié gauche),
  `follow` = `obj_player1`.
- **vue 1** — `view` et `port` de `400×600`, `port_x` à 400 (moitié droite),
  `follow` = `obj_player2`.

Les deux vues sont à l'échelle **1:1** (taille de la vue = taille du port) et le
partage se fait **gauche/droite** (`port_y` à 0, pleine hauteur). C'est important
pour la cohérence entre cibles : le bureau et le HTML5 dessinent chaque vue en
1:1 (ils découpent et décalent, ils ne **mettent pas** une vue à l'échelle de son
port), et un partage gauche/droite évite l'inversion du `port_y` entre Kivy
(axe y vers le haut) et bureau/HTML5 (axe y vers le bas). Une minicarte dézoomée
(vue plus grande que son port) n'est délibérément **pas** utilisée ici — elle ne
serait mise à l'échelle correctement que sous Kivy.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste — réglages de fenêtre et de salle, ressources intégrées, et la configuration `views` à deux vues |
| `rooms/room0.json` | La salle de 2400×800 (284 instances : caméra, murs, 2 joueurs, 18 pièces) et son bloc `views` |
| `objects/obj_camera.json` | Contrôleur invisible : `enable_views` et deux `set_view` dans l'événement `create` |
| `objects/obj_player1.json` | Joueur 1 (touches fléchées) ; déplacement sur grille et arrêt par `keyboard_release` |
| `objects/obj_player2.json` | Joueur 2 (WASD) ; déplacement sur grille et arrêt par `keyboard_release` |
| `objects/obj_coin.json` | Objet à ramasser — détruit par l'un ou l'autre joueur, ajoute 10 points |
| `objects/obj_wall.json` | Mur fixe et solide |
| `sprites/` | `spr_player1.png` (orange), `spr_player2.png` (turquoise), `spr_wall.png`, `spr_coin.png` et leurs métadonnées `.json` |
| `CREDITS.txt` | Mentions de licence des ressources |

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_camera` | Contrôleur invisible ; active et configure les deux vues | `create` (`enable_views`, 2× `set_view`) |
| `obj_player1` | Joueur de la vue de gauche (flèches) | `keyboard` (haut/bas/gauche/droite/aucune touche), `keyboard_release` (par touche), `collision_with_obj_wall` |
| `obj_player2` | Joueur de la vue de droite (WASD) | `keyboard` (w/a/s/d/aucune touche), `keyboard_release` (par touche), `collision_with_obj_wall` |
| `obj_coin` | Objet à ramasser valant 10 points | `collision_with_obj_player1`, `collision_with_obj_player2`, `destroy` (`set_score` +10) |
| `obj_wall` | Mur fixe et solide, limite de la caméra | (aucun — simple obstacle passif) |

## Ressources

4 sprites (`spr_player1`, `spr_player2`, `spr_wall`, `spr_coin`, chacun 32×32,
une seule image, collision au pixel près), 0 son. Tous sont de simples graphismes
de couleur unie en CC0, créés pour cet exemple — voir `CREDITS.txt`.

## À expérimenter

- **Sens du partage** — l'exemple utilise un partage gauche/droite (`port_x` à 0
  et 400, `port_y` à 0, pleine hauteur). Un partage haut/bas placerait les deux
  moitiés à des `port_y` différents ; attention, cela s'affiche à une position
  verticale différente sous Kivy (axe y vers le haut) et sous bureau/HTML5 (axe y
  vers le bas) : le partage gauche/droite est donc le choix portable.
- **Largeur des vues** — chaque vue fait `400` de large (la moitié de la
  fenêtre). Élargis la fenêtre ou rétrécis les vues pour changer la portion de
  salle que voit chaque joueur.
- **Bordures** — `hborder` à 120 et `vborder` à 150 définissent la zone morte de
  chaque caméra.

## État de l'export

- **Bureau (pygame) :** la référence — `tests/test_views_2_sample.py` charge
  l'exemple, exécute l'événement `create` d'`obj_camera` et vérifie que les deux
  caméras défilent **indépendamment** (déplacer un joueur ne bouge pas la vue de
  l'autre) et se bloquent au bord de la salle, en plus du score des pièces et de
  l'arrêt par `keyboard_release` propre à chaque joueur.
- **Web (HTML5) :** `engine.js` dessine chaque vue visible (découpage par vue et
  translation en 1:1) ; la configuration à deux vues se retrouve fidèlement dans
  l'export.
- **Mobile (Kivy/Android) :** l'exportateur dessine la salle dans un Fbo puis
  recopie la zone visible de chaque vue dans son port à l'écran
  (`tests/test_kivy_views.py` couvre le rendu multi-vues). Les actions
  `enable_views` et `set_view` sont bien émises : la configuration à deux vues
  fonctionne donc aussi bien depuis l'événement `create` d'`obj_camera` que
  depuis la configuration inscrite dans la salle. Limitation résiduelle (comme
  dans `views_1`) : la cible de rendu est construite à la création de la salle,
  il faut donc que `views_enabled` figure dans la configuration de la salle
  (c'est le cas ici) pour que la caméra s'affiche sous Kivy.
- La concordance du calcul de défilement entre les cibles est verrouillée par
  `tests/test_views_export_parity.py`.

Présent dans l'onglet d'accueil de l'IDE sous le nom « Vues — Niveau 2 »
(`widgets/welcome_tab.py`).
