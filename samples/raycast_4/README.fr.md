# Lancer de rayons — Niveau 4

Le quatrième niveau à la première personne façon Doom ou Wolfenstein, et le
premier construit **autour d'une barre d'état permanente en bas de l'écran** —
l'esthétique DOOM plutôt que les affichages en coin de `raycast_3`. La vue 3D
est volontairement **plus courte** (en letterbox) pour laisser la place à la
barre ; cela fait partie du rendu, ce n'est pas un défaut.

Là où `raycast_3` a validé un affichage en coin et la santé comme ressource,
`raycast_4` montre les deux fonctions du moteur conçues pour une barre DOOM :

- **`viewport_height`** sur `enable_raycast_view` rétrécit la vue à la première
  personne vers le haut de la fenêtre et réserve la bande en dessous.
- **`draw_doom_hud`** remplit cette bande : une barre de vie et son nombre, un
  **portrait qui réagit à la santé**, le score, les vies et un compteur de
  clés — le tout à partir de commandes de dessin ordinaires, si bien que la
  barre s'affiche aussi bien sur bureau, HTML5 que natif (Kivy).

Voir [`docs/RAYCAST_DOOM_HUD_PLAN.md`](../../docs/RAYCAST_DOOM_HUD_PLAN.md) pour
la partie technique, et [`raycast_3`](../raycast_3/README.fr.md) pour l'affichage
en coin que ce niveau ne réintègre volontairement pas.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Haut / Bas** — avance ou recule dans la direction où tu regardes.
- **Gauche / Droite** — pivote sur place.
- **Ramasse les clés** — chacune rapporte 25 points et incrémente le compteur
  **KEYS** de la barre. Il y en a trois.
- **Évite les monstres** — en toucher un coûte **25 points de vie** (avec une
  courte invulnérabilité ensuite). Surveille le **visage** : il grimace à mesure
  que ta santé baisse, avant même que tu aies lu le nombre.
- **Plus de vie** → tu perds une vie, la santé se remplit, la salle recommence.
  **Plus de vies** → la partie recommence.
- **Atteins la sortie** une fois les **trois clés** trouvées. La toucher trop tôt
  t'indique seulement que la porte est verrouillée.

## La barre d'état (`draw_doom_hud`)

C'est `obj_person` qui la dessine à chaque image, en espace écran, par-dessus la
vue 3D terminée. De gauche à droite :

| Zone | Contenu |
|---|---|
| Gauche | l'étiquette `HEALTH` + une barre de vie proportionnelle + le nombre |
| Centre | le **portrait**, une bande de 4 images qui réagit à la santé |
| Droite | `SCORE` au-dessus de `LIVES` |
| Extrême droite | le compteur `KEYS` |

Le visage est tout l'intérêt de l'exemple. Son image est choisie par une
répartition en tranches égales selon la santé — l'image 0 (calme) proche du
plein, la dernière (mourant) proche du vide — de sorte que le portrait te dit où
tu en es avant le nombre, exactement comme la barre de DOOM.

**`obj_person` est à la fois la caméra *et* le dessinateur de l'affichage.** Et
c'est voulu : le compteur de clés est alors une simple variable d'instance sur
`obj_person` (`keys`), donc l'expression d'objectif de `draw_doom_hud` lit la
même valeur à l'identique sur les trois cibles d'export. Un objet caméra
invisible séparé (comme dans `raycast_3`) ne pourrait pas porter une variable
dont l'affichage visible a besoin.

## Le letterbox (`viewport_height`)

`enable_raycast_view` s'exécute dans l'événement `create` d'`obj_person` avec
`viewport_height: 400` dans une fenêtre de 640×480 — la vue 3D fait donc 400 px
de haut et les **80 px** du bas sont réservés, remplis de noir par le moteur, et
recouverts par la barre. Mets `viewport_height` à `0` (la valeur par défaut) et
la vue remplit toute la fenêtre sans bande réservée, exactement comme
`raycast_1` à `3`.

L'horizon remonte avec la vue plus courte, et les murs, le ciel et le sol se
mettent tous à son échelle — c'est un vrai letterbox, pas une barre posée sur une
vue pleine hauteur. (Sous Kivy, dont l'axe y est vers le haut, la bande réservée
est malgré tout en bas de la fenêtre ; le moteur gère l'inversion.)

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste — fenêtre de 640×480, une salle |
| `rooms/room0.json` | Le labyrinthe : 15×15 cases, 3 clés, 4 monstres, une sortie verrouillée par les clés |
| `objects/obj_person.json` | Joueur + caméra + barre d'état — déplacement, santé, clés, `draw_doom_hud` |
| `objects/obj_key.json` | Une clé (passive ; c'est la collision d'`obj_person` qui la gère) |
| `objects/obj_monster.json` | Ennemi en panneau, en patrouille |
| `objects/obj_goal.json` | Sortie verrouillée (s'ouvre quand il ne reste aucune `obj_key`) |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segments de murs fins |
| `sprites/` | Graphismes de murs/ciel/sol/personnage/monstre réutilisés, plus les nouveaux `spr_face` (portrait de 4 images) et `spr_key` |

## Le labyrinthe est généré

`tools/gen_raycast_4_maze.py` construit la salle en **déléguant au générateur
versionné de `raycast_3`** — même labyrinthe « retour sur trace » récursif,
mêmes murs fins sur les arêtes, même discipline de graine choisie (le départ
s'ouvre vers l'est, toutes les cases accessibles). Il ne diffère que par ce qui
est disséminé (des clés, et non des gemmes ou des trousses) et par le fait
qu'`obj_person` est la caméra. Relancer le script reproduit la salle livrée ; un
test le vérifie.

## À expérimenter

- **Hauteur de la barre et du viewport :** la `height` de `draw_doom_hud` (80)
  doit correspondre à la bande réservée (`640×480 − viewport_height 400 = 80`).
  Change l'une, change l'autre.
- **Réactivité du visage :** `face_frames` (4) répartit la santé sur la bande.
  Une bande de 5 images avec `face_frames: 5` donne des expressions plus fines.
- **Dégâts / clés :** le `-25` dans l'événement `collision_with_obj_monster`
  d'`obj_person` ; les 3 clés et 4 monstres dans les `counts` du générateur.
- **Couleurs et libellés de la barre :** les paramètres de `draw_doom_hud` dans
  l'événement `draw` d'`obj_person`.

## État de l'export

Fonctionne sur les trois cibles. Couvert par la suite de tests automatiques
(`tools/smoke_run_samples.py`) et par `tests/test_raycast_4_sample.py`, qui
exerce la vraie boucle : la barre affiche toutes ses parties par-dessus la vue
rétrécie, alignée en bas dans la bande réservée ; l'**image du visage suit la
santé** (100/75/50/25 → 0/1/2/3) ; le ramassage d'une clé la compte, la marque
et la détruit.

Il a été vérifié que les exports Kivy et HTML5 emportent bien l'ensemble — le
`viewport_height` du letterbox dans la configuration de la caméra,
`draw_doom_hud`, le visage à plusieurs images — mais le test **visuel** sur
chaque cible reste la dernière étape et mérite d'être fait de visu : c'est le
premier exemple en lancer de rayons dont la *forme de la vue* change, donc celui
qu'il vaut le plus la peine de regarder s'afficher dans un navigateur et sur
Android.
