# Sky Strike — Niveau 1

Un shoot-'em-up à défilement vertical dans l'esprit des classiques
d'arcade comme *Xevious* : survolez le sol qui défile vers le nord,
abattez les avions ennemis avec des tirs, et bombardez les cibles au sol
que les tirs ne peuvent pas atteindre du tout — deux armes distinctes
pour deux types d'ennemis distincts.

**Aucune nouveauté n'a été ajoutée au moteur pour cet exemple.** Chaque
mécanique ici — le défilement du sol, les deux types d'armes, l'apparition
des vagues d'ennemis, la boucle victoire/défaite — est construite
entièrement à partir d'actions qui existaient déjà : la vitesse de
défilement/mosaïque de `set_background`, `create_instance`, `set_alarm`,
`set_hspeed`/`set_vspeed`, et de simples événements
`collision_with_<objet>`. C'est un bon exemple de tout ce que l'ensemble
d'actions existant permet, sans extension dédiée.

## Comment jouer

- **Flèches / WASD** déplacent le vaisseau (limité à l'écran — impossible
  de sortir par les bords).
- **Espace** tire des balles vers le haut. Maintenez la touche enfoncée
  pour un tir rapide (un court temps de recharge par tir, pas
  littéralement à chaque image). Les balles ne touchent que les
  **avions ennemis**.
- **Z** largue une bombe. Les bombes conservent l'élan du vaisseau —
  elles remontent l'écran (dans le sens de votre vol), plus lentement
  que les balles, vers la cible au sol qui se trouve devant vous au
  moment du largage. Un petit viseur dessiné devant le vaisseau indique
  la colonne que suivra votre prochaine bombe — alignez-le sur la
  position horizontale d'une cible au sol avant de larguer. Les bombes
  sont plus rares que les balles et ne touchent que les **cibles au
  sol** — les tourelles/bunkers qui défilent vers vous. Une balle ne
  fait rien à une cible au sol, et une bombe ne fait rien à un avion :
  il faut utiliser la bonne arme contre le bon ennemi.
- **Objectif :** marquez le plus de points possible avant de perdre
  toutes vos vies — les avions ennemis et les cibles au sol continuent
  d'apparaître indéfiniment (un jeu de score à l'arcade, pas un niveau
  avec une fin). Entrer en collision avec un avion ennemi coûte une vie
  et détruit l'avion. À court de vies, le message « Partie terminée ! »
  s'affiche et la partie recommence.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet |
| `rooms/room0.json` | L'unique salle de jeu, 480×640 |
| `objects/obj_player.json` | Le vaisseau — déplacement, tir/bombardement (avec temps de recharge), les deux alarmes d'apparition, la configuration du défilement du fond, l'affichage du score/des vies, et la collision avec les avions ennemis |
| `objects/obj_bullet.json` | Arme air-air — détruit `obj_enemy_plane` au contact (+50) |
| `objects/obj_bomb.json` | Arme air-sol — avance vers l'avant (remonte l'écran, `vspeed` négatif) pour atteindre une cible devant elle ; détruit `obj_ground_target` au contact (+100) |
| `objects/obj_enemy_plane.json` | Descend vers le joueur avec une légère dérive latérale aléatoire ; apparaît toutes les 40 étapes |
| `objects/obj_ground_target.json` | Défile vers le bas à la même vitesse que le fond, pour donner l'impression d'être fixée au terrain ; apparaît toutes les 70 étapes |
| `sprites/`, `backgrounds/bg_ground.png` | Graphismes originaux en aplats de couleur (voir `CREDITS.txt`), générés par `tools/gen_sky_strike_1_sprites.py`, y compris `spr_crosshair.png` (le viseur de bombardement) |

## Réglages à ajuster

- Cadence de tir : la valeur de réinitialisation de `fire_cooldown`
  d'`obj_player` (`8` étapes) et de `bomb_cooldown` (`24` étapes), toutes
  deux dans les gestionnaires de touches `space`/`z`.
- Fréquence d'apparition : le nombre d'étapes des deux `set_alarm` dans
  `game_start` (`40` pour les avions, `70` pour les cibles au sol) et dans
  le rappel de chaque gestionnaire d'alarme.
- Vitesse de défilement : le `vspeed` de `set_background` dans
  `game_start` (`2`) — le `vspeed` des cibles au sol est réglé pour
  correspondre dans leur événement `create`, donc modifier l'un sans
  l'autre fera dériver les cibles par rapport au terrain. La vitesse des
  bombes (`-4`, événement `create` d'`obj_bomb`) est indépendante des
  deux — elle doit simplement rester négative (vers l'avant/le haut) pour
  atteindre une cible devant, et plus rapide (plus négative) que le `+2`
  de la cible pour combler l'écart en un temps raisonnable.
- Dérive latérale des avions ennemis : `irandom(2) - 1` dans l'événement
  `create` d'`obj_enemy_plane` (actuellement -1, 0 ou 1 px/image).
- Position du viseur : le décalage fixe vers l'avant dans l'événement
  `draw` d'`obj_player` (`self.y - 89`, soit 80px devant le vaisseau plus
  la moitié de la hauteur du viseur lui-même) — c'est un décalage
  statique, pas un prédicteur physique exact, comme dans les jeux
  d'arcade classiques.

## Deux vrais bugs rencontrés en créant cet exemple

- **Apparaître entièrement hors champ causait une autodestruction
  immédiate.** Les avions ennemis et les cibles au sol apparaissaient à
  l'origine entièrement au-dessus de la salle (`y = -30` pour un avion de
  24px de haut, `y = -40` pour une cible de 28px) — entièrement hors des
  limites `0..640` de la salle dès leur création. L'événement
  `outside_room` du moteur se déclenche dès qu'un sprite d'instance est
  **entièrement** hors de la salle, y compris à l'image même de sa
  création, pas seulement lorsqu'il s'envole hors champ en cours de jeu —
  chaque ennemi apparu se détruisait donc lui-même avant même de devenir
  visible, et rien ne semblait jamais apparaître. Corrigé en faisant
  apparaître les instances quelques pixels *à l'intérieur* de la salle
  (`y = -20` / `y = -24`), pour qu'une partie du sprite soit toujours
  visible à l'écran dès la création. À retenir pour tout futur exemple
  qui fait apparaître des instances hors champ et compte sur
  `outside_room` pour les nettoyer ensuite.
- **Le sol qui défile ne défilait jamais réellement — un vrai bug du
  moteur, pas une erreur d'exemple.** Le champ `"backgrounds"` de
  `room0.json` avait été copié de la convention d'un autre exemple : une
  liste des 8 emplacements de calques de fond au format GMK, chacun
  `visible: false`. Le moteur de rendu sur ordinateur (`_render_room`)
  choisit le chemin multi-calques plutôt que le défilement simple hérité
  de `set_background` dès que cette liste est simplement *non vide* —
  peu importe si quoi que ce soit y est réellement visible — si bien que
  le `vspeed` de `set_background` s'incrémentait correctement à chaque
  image en interne, sans que rien n'atteigne jamais le code qui dessine
  réellement avec cette valeur. C'est un vrai bug du moteur (corrigé dans
  `runtime/game_runner.py`, `GameRoom._bg_layers_active`, désormais une
  vérification en direct qu'au moins un calque est réellement *visible*,
  plutôt que « la liste n'est pas vide ») — aucun autre exemple fourni ne
  l'avait rencontré auparavant, celui-ci étant le premier à réellement
  utiliser la fonction de défilement de `set_background` dans une vraie
  salle. `room0.json` a aussi été corrigé pour reprendre la valeur par
  défaut native de l'éditeur de salles (`"backgrounds": []`), celle
  qu'une salle qui ne touche jamais à la fonctionnalité multi-calques
  devrait avoir.

## État de l'export

Vérifié sur **ordinateur** (vraie boucle `GameRunner`, sans affichage,
avec des entrées simulées testant le déplacement, le tir, le
bombardement, les deux types de collision et la boucle fin de
partie/redémarrage — voir `tests/test_sky_strike_1_sample.py`).
**Pas encore essayé en HTML5 ni en Kivy** — tout ici utilise des actions
déjà prises en charge par les trois cibles, donc ça devrait fonctionner,
mais personne n'a encore réellement exporté et lancé cet exemple sur
l'une ou l'autre de ces cibles.

Disponible depuis l'onglet Accueil de l'IDE — choisissez
**« Sky Strike — Niveau 1 »** dans le menu déroulant *Choisir un
exemple* (ouvrir un exemple le copie dans vos Documents pour que
l'original fourni reste intact).
