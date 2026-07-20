# Vues — Niveau 1

Une démonstration de caméra à défilement : la salle (2400×800) est **trois fois
plus large que la fenêtre de 800×600**, un seul écran ne peut donc pas tout
montrer. La caméra (vue 0) suit le joueur qui avance vers la droite, dévoilant le
niveau écran par écran — c'est tout l'intérêt des **vues** à la manière de
GameMaker. Explore la grande salle et ramasse les 18 pièces.

**Où ce niveau se situe :** c'est la quatrième famille d'exemples, distincte des
trois familles classées par technique de création (`maze_*` → `plateforme_*` →
`match3_*`). Ce qu'elle introduit n'est pas un nouveau *style* de création, mais
une nouvelle possibilité du moteur : une **salle plus grande que la fenêtre**
avec une **caméra qui défile**. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la progression complète. Sur le plan des mécaniques, cet exemple reprend le
déplacement sur grille de `maze_1` (les actions intégrées `test_alignment`,
`snap_to_grid` et `start_moving_direction`) et n'ajoute qu'une seule chose
nouvelle : la caméra, activée depuis l'événement **create** du joueur avec les
actions `enable_views` et `set_view`.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Les flèches** déplacent le joueur d'une case de la grille (32 px) à la fois
  (déplacement aligné sur la grille, comme dans `maze_1`).
- Les murs (`obj_wall`) bordent la salle et forment quelques piliers à
  l'intérieur ; ils sont solides et arrêtent le joueur.
- **La caméra suit le joueur** : approche-toi d'un bord de l'écran et la vue
  défile pour te garder dans le cadre, en se bloquant aux limites de la salle
  pour que l'on ne voie jamais au-delà de la bordure de murs.
- **Objectif :** ramasser les 18 pièces (`obj_coin`). Chacune vaut 10 points
  (affichés dans le titre de la fenêtre).

## Comment la caméra est configurée

L'événement **create** du joueur exécute deux actions intégrées (aucun
`execute_code` brut) :

1. `enable_views` — active le système de vues pour la salle.
2. `set_view` — configure la **vue 0** : `view_w`/`view_h` de `800×600`, port
   placé en `(0,0)` et de taille `800×600`, `follow` = `obj_player`, `hborder` à
   240 et `vborder` à 180 (la zone morte avant que la caméra ne défile), sans
   limite de vitesse de défilement. La même configuration est aussi inscrite dans
   le bloc `views` de la salle, pour que la caméra soit correcte dès la première
   image sur toutes les cibles d'export.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, copies intégrées des ressources, et la configuration `views` de la salle |
| `rooms/room0.json` | La salle de 2400×800 (245 instances : bordure de murs et piliers, joueur, 18 pièces) et son bloc `views` |
| `objects/obj_player.json` | Joueur : déplacement sur grille et mise en place de la caméra dans l'événement `create` |
| `objects/obj_coin.json` | Objet à ramasser : détruit au contact du joueur, ajoute 10 au score |
| `objects/obj_wall.json` | Mur fixe et solide |
| `sprites/` | `spr_player.png`, `spr_wall.png`, `spr_coin.png` et leurs métadonnées `.json` |
| `CREDITS.txt` | Mentions de licence des ressources |

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_player` | Personnage du joueur ; déplacement sur grille et activation/configuration de la caméra | `create` (`enable_views`, `set_view`), `keyboard` (bas/droite/haut/gauche/aucune touche), `collision_with_obj_wall` |
| `obj_coin` | Objet à ramasser valant 10 points | `collision_with_obj_player` (`destroy_instance` sur soi-même), `destroy` (`set_score` +10) |
| `obj_wall` | Mur fixe et solide, limite de blocage de la caméra | (aucun — simple obstacle passif) |

## Ressources

3 sprites (`spr_player`, `spr_wall`, `spr_coin`, chacun 32×32, une seule image,
collision au pixel près), 0 son. Les trois sont de simples graphismes de couleur
unie en CC0, créés pour cet exemple — voir `CREDITS.txt`.

## À expérimenter

- **Taille de la salle** (`2400×800` dans `rooms/room0.json`) — agrandis-la en
  largeur ou en hauteur pour faire défiler plus loin ; la caméra s'adapte à la
  taille de la salle.
- **Bordures** (`hborder` 240 / `vborder` 180, dans l'action `set_view` *et* dans
  le bloc `views` de la salle) — des bordures plus petites laissent le joueur
  s'approcher davantage du bord avant que la caméra ne bouge ; des bordures plus
  grandes le maintiennent plus au centre.
- **Vitesse de défilement** — `hspeed` et `vspeed` valent `-1` (suivi
  instantané). Mets-y une valeur positive en pixels par pas pour obtenir une
  caméra plus douce, qui traîne légèrement.
- **Pièces** — ajoute ou retire des instances d'`obj_coin` dans
  `rooms/room0.json`.

## État de l'export

- **Bureau (pygame) :** la cible de référence — vérifiée par
  `tests/test_views_1_sample.py`, qui charge cet exemple, exécute l'événement
  `create` du joueur et vérifie que la caméra défile et se bloque correctement
  quand le joueur parcourt toute la largeur.
- **Web (HTML5) :** le fichier `engine.js` exporté embarque la même caméra à
  8 vues (`tests/test_html5_views.py`, vérifié sous Chromium pendant le
  développement) ; la configuration `views` de cet exemple et le `set_view` de
  l'événement `create` se retrouvent tous deux fidèlement dans l'export.
- **Mobile (Kivy/Android) :** la scène exportée dessine toute la salle dans un
  Fbo puis recopie la zone visible de chaque vue dans son port à l'écran, la
  fenêtre du système étant dimensionnée selon la vue (et non selon la salle) —
  la caméra montre donc une vraie tranche défilante et gère plusieurs
  fenêtrages (`tests/test_kivy_views.py`). Les actions `enable_views` et
  `set_view` sont bien émises, la reconfiguration de la caméra à l'exécution
  fonctionne donc aussi. *Une limitation subsiste :* la cible de rendu
  multi-vues est construite à la création de la salle, il faut donc que la salle
  ait `views_enabled` dans sa configuration (comme c'est le cas ici) pour que la
  caméra s'affiche — activer les vues uniquement via un `enable_views` à
  l'exécution, sur une salle qui n'en avait pas au départ, ne fonctionnera pas
  sous Kivy.
- La concordance du calcul de défilement entre les cibles est verrouillée par
  `tests/test_views_export_parity.py`.

Présent dans l'onglet d'accueil de l'IDE sous le nom « Vues — Niveau 1 »
(`widgets/welcome_tab.py`).
