# Lancer de rayons — Niveau 3

Le troisième niveau à la première personne façon Doom ou Wolfenstein, construit
sur le même **moteur de lancer de rayons 2,5D** que
[`raycast_1`](../raycast_1/README.fr.md) et
[`raycast_2`](../raycast_2/README.fr.md) — complet sur les trois cibles d'export
(bureau, HTML5, natif/Kivy) : murs texturés, ciel défilant, lancer de sol
texturé en basse résolution et sprites en panneaux face à la caméra.

Là où `raycast_1` enseigne *la vue à la première personne elle-même* et où
`raycast_2` y ajoute *des choses qui se passent dans la vue* (gemmes, ennemi en
patrouille, sortie verrouillée), `raycast_3` porte sur **l'état que tu peux voir
en jouant** : les monstres coûtent des **points de vie** plutôt qu'une vie
entière, les trousses de secours en redonnent, et un **affichage tête haute**
composé par-dessus la vue 3D montre en permanence le score, les vies et une
barre de vie.

Cet affichage est la raison d'être de cet exemple. Jusqu'au 20/07/2026, le
moteur dessinait la vue à la première personne puis s'arrêtait : le score et les
vies d'un jeu en lancer de rayons n'apparaissaient que dans la barre de titre de
la fenêtre, sur bureau — donc invisibles sur les exports HTML5 et Kivy. Voir
[`docs/RAYCAST_HUD_PLAN.md`](../../docs/RAYCAST_HUD_PLAN.md) pour ce travail et
[`docs/RAYCAST_2_5D_PLAN.md`](../../docs/RAYCAST_2_5D_PLAN.md) pour le moteur.

Un jeu complet en deux niveaux : traverse chaque labyrinthe à la première
personne, ramasse toutes les gemmes en survivant aux monstres et atteins la
sortie verrouillée par les gemmes — la première salle (brique chaude) mène à une
seconde (caverne de cristal), et la terminer gagne la partie. Disponible depuis
l'onglet d'accueil de l'IDE (« Lancer de rayons — Niveau 3 »).

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Haut / Bas** — avance ou recule dans la direction où tu regardes (déplacement
  continu, pas case par case ; les murs te bloquent).
- **Gauche / Droite** — pivote sur place (modifie `facing_angle`, indépendamment
  du déplacement : tu peux tourner à l'arrêt).
- **Ramasse les gemmes** — chacune ajoute 10 au score, affiché en haut à gauche.
- **Évite les monstres** — en toucher un coûte **25 points de vie**, et non une
  vie entière. Après un coup, tu bénéficies d'une courte invulnérabilité
  (45 pas), pour qu'un monstre qui te traverse ne vide pas toute la barre d'un
  coup.
- **Prends les trousses de secours** — les boîtes à croix rouge rendent
  **40 points de vie**, sans jamais dépasser le maximum.
- **Si tes points de vie tombent à zéro**, tu perds une vie, la barre se remplit
  et la salle recommence. Si tu n'as **plus de vies**, la partie recommence.
- **Objectif** — ramasse *toutes* les gemmes d'une salle, puis atteins sa sortie.
  Y arriver trop tôt affiche seulement un rappel.

## L'affichage tête haute

C'est `obj_hud` qui le dessine, en **espace écran**, par-dessus l'image 3D
terminée :

| Élément | Coin | Action |
|---|---|---|
| Score | en haut à gauche | `draw_score` |
| Vies | en haut à droite | `draw_text` et `draw_lives` |
| Barre de vie | en bas à gauche | `draw_health_bar` |
| Minicarte | en bas à droite | `draw_minimap` |

Le score et la barre de vie sont dans des coins **opposés**, volontairement :
une barre de vie est large et un score s'allonge au fil de la partie, les
empiler inviterait à une collision.

### La minicarte

`draw_minimap` dessine une carte des murs de la salle **orientée au nord**, avec
un repère indiquant où tu te trouves et dans quelle direction tu regardes. Elle
ne tourne pas : la carte reste fixe et c'est le repère qui pivote, ce qui est
plus facile à lire qu'une carte qui tournoie.

Elle n'a besoin d'aucune donnée propre : elle lit les mêmes arêtes de murs que
la vue à la première personne a déjà déduites des instances solides de la salle,
elle reste donc juste si tu remanies le labyrinthe. Elle n'affiche **que les
murs** — ni gemmes ni monstres — pour que le labyrinthe garde son intérêt.

**Non implémenté (volontairement) :** le brouillard de guerre, un mode orienté
selon le regard, et l'affichage des objets ou des ennemis. Voir
[`docs/RAYCAST_MINIMAP_PLAN.md`](../../docs/RAYCAST_MINIMAP_PLAN.md) pour les
raisons de chaque choix.

**`obj_hud` est en `visible: true`, et ce détail compte.** GameMaker n'exécute
pas l'événement `draw` d'une instance invisible — l'affichage ne peut donc pas
simplement être porté par le contrôleur de caméra invisible
(`obj_cam0`/`obj_cam1`). Si tu construis ton propre affichage et que rien
n'apparaît, vérifie d'abord cet indicateur.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste — fenêtre de 640×480, les deux salles, copies intégrées des ressources |
| `rooms/room0.json` | Labyrinthe de brique chaude : 15×15 cases / 480×480, 8 gemmes, 3 monstres, 3 trousses |
| `rooms/room1.json` | Labyrinthe de cristal : la moitié la plus difficile — 10 gemmes, 5 monstres, 2 trousses seulement |
| `objects/obj_person.json` | Joueur et caméra — déplacement, dégâts avec alarme d'invulnérabilité, gestion de la mort |
| `objects/obj_hud.json` | L'affichage tête haute (voir plus haut) |
| `objects/obj_cam0.json`, `obj_cam1.json` | Contrôleurs de caméra par salle, chacun portant le thème de textures de sa salle |
| `objects/obj_gem.json` | Objet à ramasser, +10 au score |
| `objects/obj_medkit.json` | Rend 40 points de vie |
| `objects/obj_monster.json` | Ennemi en panneau, en patrouille |
| `objects/obj_goal.json`, `obj_goal_final.json` | Sorties verrouillées par les gemmes : avancer, et gagner |
| `objects/obj_wall_h.json`, `obj_wall_v.json` | Segments de murs fins (32×8 et 8×32) |
| `sprites/` | 13 sprites, repris de `raycast_2` plus `spr_medkit` |

## Le labyrinthe est généré, pas placé à la main

`tools/gen_raycast_3_maze.py` construit les deux salles avec un labyrinthe
« retour sur trace » récursif, passé par le placement en murs fins de
`raycast_1` — des cloisons de 8 px centrées sur les limites de cases, et non des
blocs de 32 px remplissant une case. Relancer le script reproduit exactement les
salles livrées, et un test vérifie qu'elles n'ont pas divergé : la conception des
niveaux reste donc relisible et modifiable, au lieu d'être une donnée opaque.
(Le labyrinthe de `raycast_2` venait d'un script jetable jamais versionné, ses
salles ne peuvent donc pas être régénérées — celui-ci corrige ce défaut.)

Les graines sont **choisies, pas arbitraires** : `check_start()` vérifie que la
case de départ s'ouvre vers l'est (le joueur y apparaît en regardant vers l'est,
donc un départ muré revient à commencer le nez contre un mur) et que toutes les
cases sont accessibles.

## À expérimenter

- **Dégâts et soins :** le `-25` dans l'événement `collision_with_obj_monster`
  d'`obj_person`, le `+40` dans l'événement `destroy` d'`obj_medkit`.
- **Fenêtre d'invulnérabilité :** les `45` pas de `alarm_0`. Plus courte, le jeu
  devient plus rude ; supprime-la et un monstre qui te chevauche à répétition
  déchiquettera la barre.
- **Équilibrage :** les `counts` de chaque salle dans le générateur — le rapport
  monstres / trousses est le principal réglage.
- **Disposition de l'affichage :** les coordonnées dans l'événement `draw`
  d'`obj_hud`. Garde le score et la barre de vie dans des coins opposés.
- **Minicarte :** le paramètre `size` de `draw_minimap` met toute la salle à
  l'échelle dans ce carré — une valeur plus grande donne donc simplement une
  carte plus lisible ; `wall_color` et `player_color` en règlent l'apparence.
- **Thèmes :** les paramètres de textures sur `obj_cam0`/`obj_cam1`.

## Une note sur le moment des collisions

Le moteur déclenche un événement de collision quand deux instances **commencent**
à se chevaucher, et non à chaque image où elles se chevauchent encore. Rester
dans un monstre coûte donc un seul coup, et non un coup par image.
L'alarme d'invulnérabilité garde tout son intérêt : elle couvre les
touchers/détachements répétés d'un monstre qui te *traverse*, c'est-à-dire le cas
que l'on rencontre réellement en jouant.

## État de l'export

Fonctionne sur les trois cibles. Couvert par la suite de tests automatiques
(`tools/smoke_run_samples.py`) et par `tests/test_raycast_3_sample.py`, qui
exerce la vraie boucle de jeu : les dégâts, l'ouverture et la fermeture de la
fenêtre d'invulnérabilité, la mort coûtant exactement une vie, le soin de la
trousse et son plafond, la sortie verrouillée par les gemmes, le passage à la
salle au thème de glace, et l'affichage dessiné par-dessus la vue à la première
personne dans les **deux** salles.

Il a été vérifié que les exports Kivy et HTML5 emportent bien toute la boucle —
`no_more_health`, `alarm_0`, `draw_health_bar`, `obj_hud` et `spr_medkit`
survivent tous à la génération de code — mais le test *visuel* sur chaque cible
mérite d'être fait de visu avant une publication.
