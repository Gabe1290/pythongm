# Lancer de rayons — Niveau 1

Une vue à la première personne, à la manière de Doom ou Wolfenstein, du **même
tracé de labyrinthe que `maze_1`** — mêmes salles, même arrivée, mêmes chemins de
résolution. Là où `maze_1` montre le labyrinthe vu de dessus avec des blocs de
murs occupant une case entière, cet exemple le dessine en projection par lancer
de rayons, avec des **murs fins posés sur les arêtes** (des cloisons de 8 px
placées sur les limites de cases, et non des blocs de 32 px remplissant une
case) — de vrais couloirs aux proportions de Wolfenstein, et non une simple
caméra à la première personne greffée sur l'ancien tracé en gros blocs. Les
fichiers `rooms/room0.json` et `room1.json` ont été régénérés à partir du tracé
d'origine de `maze_1` par une conversion qui préserve la topologie (mêmes
connexions, même solvabilité, géométrie de murs différente) : ils n'ont pas été
redessinés à la main. Voir
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) à la racine du
dépôt pour le plan technique complet, et notamment la section « Complete
rethink » qui explique pourquoi les murs pleine case ne laissaient pas assez de
place pour tourner.

**C'est de la 2,5D, pas de la 3D** — la logique de jeu est rigoureusement
identique à celle de `maze_1` (même position 2D en `x`/`y`, mêmes collisions avec
les murs solides) ; seule l'*image* est truquée pour paraître en trois
dimensions. Il n'y a pas de regard vertical (pas d'inclinaison), les couloirs
doivent être alignés sur la grille, et il n'y a pas de vraie superposition de
salles. C'est une limitation assumée et délibérée, pas une fonctionnalité
manquante — voir la note pédagogique « why raycasting » du plan.

**État — entièrement texturé (murs, ciel, sol, panneaux publicitaires) sur les
trois cibles : bureau (pygame), HTML5 et natif (Kivy).** Les murs
échantillonnent une **texture de brique** (`spr_wall_texture`, via
`wall_texture`) : chaque colonne de l'écran prélève une bande verticale à
l'endroit touché par le rayon, mise à l'échelle selon la distance, la face de mur
opposée étant assombrie de moitié — un indice de profondeur gratuit. Le plafond
est un **ciel à la manière de DOOM** (`spr_sky`, via `sky_texture`) : un panorama
qui défile horizontalement quand on tourne (un tour complet de 360° le fait
défiler une fois) et qui ne recule *pas* avec la distance, ce qui le fait lire
comme un horizon infiniment lointain. Le sol est une **texture de pierre projetée**
(`spr_floor`, via `floor_texture`) — un lancer de sol en basse résolution (le
calcul pixel par pixel en pleine résolution était environ 13 fois trop lent en
Python pur ; `floor_cast_res` règle le sous-échantillonnage, 4 ≈ 5 ms) qui se
répète par case de grille et rejoint la base des murs sans raccord visible.
`obj_goal` est dessiné comme un panneau publicitaire face à la caméra (mis à
l'échelle selon la distance, masqué par les murs) — voir « Ce qu'il y a de
nouveau ici ». Pour revenir à l'aspect plat, vide
`wall_texture`, `sky_texture` et `floor_texture` sur l'action
`enable_raycast_view`.

## Comment jouer

- **Haut / Bas** avancent et reculent dans la direction où l'on regarde
  (déplacement continu, non aligné sur la grille — les murs bloquent toujours,
  via la collision habituelle du moteur avec les instances solides, inchangée par
  rapport à `maze_1`).
- **Gauche / Droite** font tourner sur place (font pivoter `facing_angle`,
  indépendamment du déplacement — on peut tourner à l'arrêt).
- **Objectif :** trouver l'arrivée. La toucher fait passer à la salle suivante
  s'il en existe une (même logique d'`obj_goal` que `maze_1`, fichier identique
  octet par octet).

## Ce qu'il y a de nouveau ici, côté moteur

- `GameInstance.facing_angle` — direction du regard, persistante (convention
  d'angle GameMaker : 0 = droite, 90 = haut, 180 = gauche, 270 = bas), définie
  par la nouvelle action `set_facing_angle`. Contrairement à la propriété
  `direction` existante (déduite de `hspeed`/`vspeed`, donc toujours à 0 à
  l'arrêt), celle-ci survit à l'immobilité — indispensable pour des commandes de
  FPS « tourner sur place ».
- `enable_raycast_view` — bascule la salle courante vers la caméra à lancer de
  rayons (liée à l'instance appelante, ici l'événement `create` d'`obj_person`),
  ou revient au rendu normal vu de dessus.
- La carte des murs est **déduite des instances solides déjà présentes dans la
  salle**, et non d'un format de création séparé — mais depuis la refonte en murs
  fins, elle est déduite sous forme de vraies arêtes
  (`GameRoom._build_raycast_walls`), et non d'une occupation grossière case par
  case : le rapport largeur/hauteur du sprite d'une instance solide détermine
  s'il s'agit d'un segment de mur horizontal ou vertical (une forme à peu près
  carrée retombe sur le blocage d'une case entière, pour rester compatible avec
  les contenus sans murs fins). C'est ce qui fait que l'épaisseur de 8 px
  d'`obj_wall_h`/`obj_wall_v` compte réellement, tant pour le rendu que pour la
  place nécessaire aux virages, et pas seulement visuellement — voir la section
  « Complete rethink » du plan.
- **Panneaux publicitaires (billboards).** Toute instance visible, non solide et
  dotée d'un sprite (ici `obj_goal`) est dessinée comme un sprite 2D face à la
  caméra dans la vue en lancer de rayons, mise à l'échelle selon la distance et
  centrée verticalement sur l'horizon, comme une bande de mur. Le masquage est un
  vrai découpage colonne par colonne, comparé aux distances des murs déjà
  calculées pour la passe des murs de cette image : une arrivée située derrière
  un mur est donc correctement cachée, au lieu de transparaître. C'est une
  première version de la phase 6 du plan (les murs ne dessinent que les instances
  solides, les panneaux uniquement les non solides, rien n'est donc dessiné deux
  fois) — sans fusion des transparences partielles, sans rotation pour suivre
  l'orientation propre du sprite : juste la mise à l'échelle et le découpage à
  plat qu'un moteur à la Wolfenstein utilisait pour les objets et les ennemis.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet |
| `rooms/room0.json`, `rooms/room1.json` | Même *topologie* de labyrinthe que `maze_1`, régénérée avec des murs fins sur les arêtes (voir l'algorithme de conversion du plan) |
| `objects/obj_person.json` | Joueur et caméra — `create` active la vue en lancer de rayons, les événements `keyboard` gèrent la rotation et l'avance/le recul, et il enregistre `collision_with_obj_wall_h`/`_v` |
| `objects/obj_goal.json` | Objet d'arrivée — identique octet par octet à celui de `maze_1` |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segments de murs fins (32×8 et 8×32) — ils remplacent l'unique `obj_wall` pleine case de `maze_1` |
| `sprites/` | `spr_person` et `spr_goal` (repris de `maze_1`), plus les `spr_wall_h`/`spr_wall_v` propres à cet exemple (fins, de couleur unie, servant de substituts — jamais dessinés en vue à la première personne, seules leurs dimensions comptent pour les collisions et le lancer de rayons) |

## À expérimenter

- La vitesse de rotation est de `3`°/image (`room_speed: 30`, soit 90°/s) et la
  vitesse de déplacement de `3` px/image — les deux sont écrites en dur dans les
  événements `keyboard` d'`obj_person`.
- Champ de vision de `66`°, `render_distance` de `20` cases, `cell_size` de
  `32` — tous des paramètres d'`enable_raycast_view` dans l'événement `create`
  d'`obj_person`.
- Les couleurs des murs, du sol et du plafond sont également des paramètres
  d'`enable_raycast_view` — c'est l'aspect plat de repli quand la texture
  correspondante est vidée.
- L'épaisseur des murs est de `8` px, écrite en dur dans la conversion qui a
  généré les `rooms/*.json` (ce n'est pas un paramètre d'exécution) — pour la
  changer, il faut régénérer les salles.
- `spr_person` fait **16×16** avec une boîte de collision `(4,4)-(12,12)` — la
  taille du joueur a été divisée par deux par rapport à l'ancien 32×32 (et
  recentrée dans sa case de départ, pour que la caméra reste au centre de la
  case), parce qu'un joueur de taille normale rendait les couloirs d'une case
  très étriqués ; un gabarit plus petit laisse beaucoup plus de place pour se
  déplacer. La **texture de brique** des murs a été affinée de la même façon
  (briques à demi-échelle) pour que les murs paraissent plus éloignés — les deux
  réglages échangent l'effet « collé au nez » contre une meilleure sensation
  d'espace.

## État de l'export

La vue à la première personne **complète** s'affiche désormais sur **les trois
cibles** — bureau (pygame), **HTML5**
(`export/HTML5/templates/engine.js`) et **natif/Kivy**
(`export/Kivy/kivy_exporter.py`) — avec les commandes de regard par angle
d'orientation, les murs texturés et plats, le ciel défilant, le lancer de sol
texturé en basse résolution et les panneaux publicitaires découpés selon le
masquage. Les trois moteurs de rendu ne partagent aucun code (trois copies
écrites à la main) : leur cœur DDA est donc verrouillé par
`tests/test_raycast_export_parity.py` (égalité numérique exacte entre bureau et
Kivy sur une matrice de 260 rayons ; parité structurelle pour le HTML5,
faute de moteur JavaScript dans l'intégration continue).

Le lancer de sol utilise la même approche « calculer en basse résolution puis
agrandir » sur toutes les cibles (`floor_cast_res`, 4 par défaut) ; des mesures
de temps sur le matériel réel ont confirmé que cela tient dans le budget
(navigateur ≈ 0,4 ms à res=2 ; Kivy sur AMD 840M ≈ 5 ms à res=4). Un projet peut
toujours vider `floor_texture` pour obtenir un sol plat en `floor_color`.

Disponible depuis l'onglet d'accueil de l'IDE — choisis **« Lancer de rayons —
Niveau 1 »** dans la liste déroulante *Choisir un exemple* (ouvrir un exemple le
copie dans tes Documents, l'original fourni reste donc intact).
