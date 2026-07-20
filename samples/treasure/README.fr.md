# Trésor

Une course-poursuite dans un labyrinthe à la manière de Pac-Man : l'**explorateur**
parcourt un labyrinthe bordé de murs pour ramasser des **points de trésor**,
poursuivi par des **monstres** qui choisissent une nouvelle direction à chaque
croisement. Ramasse une **pastille de pouvoir** (`pil`) et la situation
s'inverse : tous les monstres deviennent **effrayés** et peuvent être mangés pour
des points bonus, jusqu'à ce que l'effet se dissipe. C'est un projet pygm2 natif
importé depuis `treasure.gmk` (GameMaker 8.x) ; le projet lui-même est écrit et
enregistré au format JSON de pygm2.

**Où ce niveau se situe :** `treasure` se place aux côtés de la famille `maze_*` —
construit à partir d'objets et d'actions intégrées, via l'éditeur d'événements
visuel — mais il y ajoute un **script au niveau du projet** (`adapt_direction`,
l'intelligence des monstres aux croisements) et une boucle d'états
**« poursuite / pouvoir / fuite »** à la manière de GameMaker, répartie sur ses
objets. C'était l'un des deux exemples retirés en rc.12 à cause de bugs d'import
GMK, puis **réintégrés après la fiabilisation de l'importateur** (16/07/2026) ;
voir
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
et [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Sons et musique :** 6 effets sonores sont fournis (ramassage, pastille de
pouvoir, monstre mangé, mort, …). Une ancienne piste d'époque GM8 (`music`) est
dans un format que pygame ne sait pas charger et est ignorée à l'exécution —
comme les musiques d'ambiance des autres exemples de labyrinthe ; le jeu n'en est
pas affecté.

## Comment jouer

- **Les flèches** déplacent l'explorateur dans le labyrinthe ; les murs bloquent
  le passage.
- Ramasse tous les **points de trésor** pour terminer le niveau (4 salles au
  total).
- **Les monstres** te poursuivent ; en toucher un coûte normalement une vie.
- Ramasse une **pastille de pouvoir** et les monstres deviennent **effrayés**
  (leur sprite change) pendant quelques secondes — touche alors un monstre
  effrayé pour le **manger** (+points ; il est téléporté à son point de départ et
  redevient un monstre normal). L'effet se dissipe au bout d'un minuteur.

## L'intelligence des monstres (le script `adapt_direction`)

Chaque monstre appelle le script de projet `adapt_direction` depuis ses
événements `step` et de collision. C'est du vrai code Python pygm2 : à chaque
croisement possible, le monstre envisage aléatoirement de tourner, et vérifie
`game.check_collision_at_position(...)` pour détecter un mur avant de s'engager —
les monstres errent donc dans le labyrinthe au lieu de filer tout droit. Ouvre la
ressource **Scripts** pour le lire ; l'action `execute_script` dans les
événements du monstre montre où il est appelé.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste — réglages de fenêtre et de salle, ressources intégrées, le script `adapt_direction` et l'ordre des salles |
| `rooms/room0..3.json` | Les quatre niveaux de labyrinthe (instances de chaque salle) |
| `objects/*.json` | Les 7 définitions d'objets (référence ; fusionnées par-dessus les copies intégrées au chargement) |
| `sprites/` | 10 images PNG et leurs métadonnées `.json` |
| `sounds/` | 6 effets sonores |
| `backgrounds/` | 1 arrière-plan |
| `CREDITS.txt` | Mentions de licence des ressources |

## Objets

| Objet | Rôle |
|---|---|
| `explorer` | Personnage du joueur ; ramasse les trésors, mange les monstres effrayés, meurt au contact des monstres normaux |
| `monster` | Poursuivant ; erre grâce à `adapt_direction` ; se transforme en `scared` sur une pastille de pouvoir |
| `scared` | Un monstre en état de fuite ; comestible ; redevient un `monster` au bout d'un minuteur |
| `pil` | Pastille de pouvoir — effraie tous les monstres quand elle est ramassée |
| `point` | Trésor à ramasser |
| `bonus` | Objet bonus supplémentaire |
| `wall` | Mur de labyrinthe fixe et solide |

## Ressources

10 sprites, 6 sons, 1 arrière-plan — tous importés depuis `treasure.gmk`. Voir
`CREDITS.txt` et
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md) pour l'origine.

## À expérimenter

- **Durée de la frayeur** — l'alarme de la pastille de pouvoir est de `160` pas,
  dans l'événement `collision_with_pil` d'`explorer` ; augmente-la pour une phase
  de fuite plus longue.
- **Probabilité de virage des monstres** — les tests `random.random() * 3 < 1` du
  script `adapt_direction` déterminent la fréquence à laquelle les monstres
  tournent à un croisement.
- **Valeur des points** — les points de trésor et de monstre mangé sont des
  actions `set_score` (en mode relatif) sur les événements de collision
  correspondants.

## État de l'export

Couvert par la suite de tests automatiques (`tools/smoke_run_samples.py`, qui
inclut `treasure`) et par la suite de non-régression d'import
(`tests/test_gmk_treasure_maze4_import.py` et `tests/test_gmk_applies_to.py`).
Vérifié lors d'une session de test manuelle pendant la fiabilisation de
l'importateur en juillet 2026 (voir le document de test). Présent dans l'onglet
d'accueil sous le nom **« Trésor »**.

## Régénérer depuis le `.gmk` d'origine

Le fichier voisin `../treasure.gmk` est la source GameMaker 8.x. Pour le
régénérer :

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Un nouvel import est fidèle au jeu d'origine depuis la fiabilisation de
l'importateur de juillet 2026 (aucune correction manuelle n'a été appliquée à cet
exemple).
