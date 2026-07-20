# Labyrinthe — Niveau 4

Le plus gros des exemples de labyrinthe : **21 salles** d'énigmes sur grille avec
des **tapis roulants**, trois sortes de **monstres**, des **bombes et explosions**
qui percent les murs, un **anneau de pouvoir** qui effraie les monstres, et des
objets à ramasser (diamants, anneaux, cœurs). C'est un projet pygm2 natif importé
depuis `maze_4.gmk` (GameMaker 8.x), puis écrit et enregistré au format JSON de
pygm2.

**Où ce niveau se situe :** c'est le quatrième niveau `maze_*` et le plus riche
en mécaniques — il superpose le déplacement par tapis roulants, plusieurs types
d'ennemis, une boucle « effrayer puis manger » et une bombe qui détruit les murs
au déplacement de base sur grille de `maze_1` à `maze_3`. Il avait été retiré en
rc.12 à cause de bugs d'import GMK, puis **réintégré après la fiabilisation de
l'importateur** (16/07/2026) ; voir
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
et [`../../docs/maze_4_testing_pass.md`](../../docs/maze_4_testing_pass.md).

**Sons et musique :** 10 effets sonores sont fournis. Une ancienne piste d'époque
GM8 (`sound_background`) est dans un format que pygame ne sait pas charger et est
ignorée à l'exécution (comme dans `maze_2` et `maze_3`) ; le jeu n'en est pas
affecté.

## Comment jouer

- **Les flèches** déplacent le joueur d'une case à la fois ; les murs bloquent le
  passage.
- **Les tapis roulants** (flèches dessinées au sol) entraînent automatiquement le
  joueur dans leur direction tant qu'il est dessus.
- **Les monstres** existent en trois sortes (`monster_all` se déplace librement,
  `monster_ud` patrouille verticalement, `monster_lr` horizontalement) — en
  toucher un coûte une vie et relance la salle.
- Ramasse un **anneau** et tous les monstres deviennent **effrayés** (leur sprite
  change, ils se figent) pendant une dizaine de secondes — touche-les alors pour
  les manger et marquer des points ; ils redeviennent normaux à la fin du minuteur.
- **Les bombes** explosent en un souffle qui **détruit les murs alentour** —
  utile pour ouvrir des sections autrement inaccessibles.
- Ramasse les **diamants, anneaux et cœurs** ; atteins l'**arrivée** pour avancer.
  L'affichage (score et vies) est dessiné en bas de l'écran par
  `controller_main`.

## Une note sur la correction manuelle (documentation honnête)

Dans pygm2, un déplacement bloqué *glisse jusqu'au contact* du mur, alors que
GameMaker 8 *annule* le déplacement et revient à la position précédente — ce
comportement d'origine gardait gratuitement le joueur aligné sur la grille. Sans
lui, pousser contre un mur laissait le joueur à quelques pixels de la grille de
32, et les vérifications de déplacement et de tapis roulants, qui dépendent de
cet alignement, se bloquaient. `obj_person` porte donc une **correction manuelle
de gameplay** délibérée : `snap_to_grid(32)` sur ses événements de collision
`wall_corner` / `wall_horizontal` / `wall_vertical`. C'est la même correction que
celle livrée dans `maze_1` : il s'agit d'un correctif, pas d'une modification de
fidélité — un nouvel import depuis le `.gmk` ne l'inclura pas (voir plus bas).

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste — réglages de fenêtre et de salle, ressources intégrées et ordre des salles |
| `rooms/*.json` | 21 salles ; ordre de jeu `room_start` puis en ordre décroissant (`room14`, `room13`, …) — l'ordre du jeu d'origine, importé fidèlement |
| `objects/*.json` | 24 définitions d'objets (référence ; fusionnées par-dessus les copies intégrées au chargement) |
| `sprites/` | 24 images PNG et leurs métadonnées `.json` |
| `sounds/` | 10 effets sonores |
| `backgrounds/` | 2 arrière-plans |
| `CREDITS.txt` | Mentions de licence des ressources |

## Objets (24)

Joueur et affichage : `obj_person`, `controller_main` (dessine score et vies),
`controller_start`.
Murs : `wall_horizontal`, `wall_vertical`, `wall_corner`, `block`.
Ennemis : `monster_all`, `monster_ud`, `monster_lr`.
Bonus et objets : `ring` (effraie), `bomb` + `explosion` (détruisent les murs),
`obj_diamond`, `heart`, `bonus`, `obj_door`, `obj_goal`, `trigger`, `hole`.
Tapis roulants : `move_up`, `move_down`, `move_left`, `move_right`.

## Ressources

24 sprites, 10 sons, 2 arrière-plans, 1 police — tous importés depuis
`maze_4.gmk`. Voir `CREDITS.txt` et
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) pour l'origine.

## À expérimenter

- **Vitesse des tapis et du joueur** — les tapis déplacent à la vitesse `8`, le
  clavier à `4` (paramètres par action sur `obj_person`).
- **Durée de la frayeur** — l'alarme posée par l'anneau (`set_alarm`) est de
  `300` pas sur `monster_all`.
- **Ordre des salles** — les salles s'enchaînent dans l'ordre des clés du
  dictionnaire de salles de `project.json` ; réorganise-les dans l'IDE (par
  glisser-déposer dans l'arbre des ressources) et le test du jeu suivra.

## État de l'export

Couvert par la suite de tests automatiques (`tools/smoke_run_samples.py`, qui
inclut `maze_4`) et par la suite de non-régression d'import
(`tests/test_gmk_treasure_maze4_import.py`). Vérifié lors d'une session de test
manuelle pendant la fiabilisation de l'importateur en juillet 2026 (voir le
document de test). Présent dans l'onglet d'accueil sous le nom
**« Labyrinthe — Niveau 4 »**.

## Régénérer depuis le `.gmk` d'origine

Le fichier voisin `../maze_4.gmk` est la source GameMaker 8.x :

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/maze_4.gmk', '/tmp/maze_4_reimport')"
```

Un nouvel import est fidèle au jeu d'origine, **à l'exception** de la correction
manuelle `snap_to_grid` décrite plus haut — pense à la réappliquer (ajouter
`snap_to_grid` avec `grid_size` 32 aux trois événements de collision avec les
murs d'`obj_person`) après régénération.
