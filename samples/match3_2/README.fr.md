# Match-3 — Niveau 2

La suite animée et à base de sprites de [`match3_1`](../match3_1/README.md),
promise dans la feuille de route de cet exemple : même plateau, même score, mais
dessiné avec de vrais sprites de gemmes au lieu de rectangles colorés, avec une
animation de glissement lors de l'échange et des effets sonores pour l'échange,
l'alignement et la cascade. Toujours une salle, un objet, aucun script — tout le
jeu tient encore dans quatre événements `execute_code` sur un unique objet
contrôleur.

**Où ce niveau se situe :** il fait partie de la famille `match3_*` — du pur
script dans `execute_code`, aucune action intégrée, aucune tuile au niveau de la
salle. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour comprendre ce qui le distingue de l'approche multi-objets à actions
intégrées de `maze_*` et `plateforme_*`.

**Sons et musique :** 3 fichiers sonores (`snd_swap`, `snd_match`,
`snd_cascade`), tous réellement utilisés — mis en file depuis `execute_code` via
`self._sound_queue` (voir plus bas), et non par l'action `play_sound`.

## Comment jouer

Comme dans `match3_1` :

- **Clique** sur une tuile pour la sélectionner (contour blanc), puis **clique
  sur une tuile voisine** pour échanger les deux. L'échange **glisse** désormais
  en place au lieu de se faire instantanément.
- Si l'échange aligne **3 tuiles ou plus de la même couleur** en ligne ou en
  colonne, les tuiles alignées clignotent un instant, sont détruites, et les
  tuiles du dessus **glissent vers le bas** pour combler le trou ; de nouvelles
  tuiles tombent depuis le haut du plateau. Les réactions en chaîne
  (« cascades ») se résolvent vague après vague.
- Un échange qui ne produit aucun alignement **revient en glissant** à sa
  position d'origine, au lieu de se remettre en place d'un coup.
- Chaque tuile détruite vaut **10 points** ; atteins **500 points** pour gagner.
- Chaque tentative d'échange joue un clic ; un alignement réussi joue un
  carillon, et chaque cascade supplémentaire du même enchaînement joue un
  carillon plus clair et plus aigu.

## Ce qui change par rapport à `match3_1`

| `match3_1` | `match3_2` |
|---|---|
| Tuiles dessinées comme des rectangles de couleur pleine | Tuiles dessinées comme des **sprites** de gemmes (commande de file d'affichage à la manière de `draw_sprite`), avec une forme par couleur pour l'accessibilité aux daltoniens |
| L'échange s'applique instantanément, les alignements sont évalués aussitôt | L'échange **glisse** d'abord en place (≈ 4 images) ; un échange sans alignement repart en glissant au lieu de se replacer d'un coup |
| Aucun son | **Effets sonores** pour l'échange, l'alignement et la cascade, mis en file depuis `execute_code` via la nouvelle primitive `self._sound_queue` (voir plus bas) |

La logique du plateau elle-même (modèle de grille, recherche d'alignements, chute
en cascade, score, condition de victoire) est inchangée par rapport à
`match3_1` — c'est une véritable évolution lisible, pas une réécriture.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — fenêtre de 800×800, 60 images/s, salle de démarrage `rm_match3` |
| `rooms/rm_match3.json` | L'unique salle ; contient une instance d'`obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | Tout le jeu : quatre événements, chacun contenant une seule action `execute_code` |
| `sprites/spr_gem_red\|blue\|green\|yellow.png` | Tuiles de gemmes en 88×88 (voir `CREDITS.txt`) — dimensionnées pour se placer exactement là où se trouvait le remplissage rectangulaire de `match3_1`, puisque `draw_sprite` dessine à la taille native, sans mise à l'échelle |
| `sounds/snd_swap\|match\|cascade.wav` | Courtes tonalités synthétisées (voir `CREDITS.txt`) |

## Comment le code fonctionne

L'état et l'automate du `step` sont les mêmes que dans `match3_1` (`grid`, `sel`,
`marked`, `flash`/`flash_total`, `falling`/`fall_speed`, `score`, `target`,
`won`, `find_matches`) — voir ce guide pour la description complète. État ajouté
dans cette version :

| Attribut | Signification |
|---|---|
| `sprite_names` | `['spr_gem_red', 'spr_gem_blue', 'spr_gem_green', 'spr_gem_yellow']`, indexés de la même façon que `palette` l'était dans `match3_1` |
| `swap_off` | Dictionnaire `(gx, gy) → (dx, dy)` : décalage en pixels du glissement d'échange en cours ; il décroît jusqu'à `(0, 0)` à raison de `swap_speed` px/image — la même technique de retour au repos que `falling` utilisait déjà pour les cascades, généralisée à deux axes |
| `swap_phase` | `None` / `'forward'` (glissement vers la position échangée) / `'back'` (échange refusé, glissement de retour vers les cases d'origine) |
| `last_swap` | `(gx, gy, sx, sy)` — les deux cases concernées par l'échange en cours, pour que `step` puisse les remettre en place sans avoir besoin d'un état de fermeture |
| `pending_marks` | L'ensemble des alignements calculé juste après un échange, conservé jusqu'à la fin de l'animation d'entrée pour que le clignotement ne démarre pas au milieu du glissement |
| `arm_swap(a, b)` | Fonction utilitaire (définie dans `create` et rangée sur l'instance comme `find_matches`) qui règle `swap_off` pour les deux cases à partir de leurs seules positions — la rappeler avec les deux mêmes cases produit l'animation inverse, ce qui donne gratuitement le glissement de retour |

Déroulement mis à jour :

```
clic sur une tuile voisine
  → grille échangée immédiatement (les données), pending_marks calculé
  → swap_off armé (aller) — les tuiles glissent vers leurs nouvelles cases
       │
       ▼ (le glissement se termine)
  pending_marks ?
    oui → armer le clignotement (clignote → détruit → chute → nouveau parcours,
          comme dans match3_1)
    non → rééchanger la grille, réarmer swap_off avec les MÊMES deux cases
          (phase = 'back')
             │
             ▼ (le glissement se termine)
          repos
```

- **`create`** — même initialisation de grille que `match3_1`, plus
  `sprite_names`, `swap_off`/`swap_speed`/`swap_phase`/`last_swap`/
  `pending_marks` et la fonction `arm_swap`.
- **`mouse_left_press`** — la logique de sélection est inchangée ; un échange
  valide entre cases voisines applique désormais l'échange dans la grille,
  calcule `pending_marks`, arme le glissement aller et met `snd_swap` en file.
- **`step`** — les blocs de clignotement et de chute sont inchangés par rapport à
  `match3_1` (ils mettent toujours `snd_cascade` en file lors d'un nouvel
  alignement enchaîné) ; un nouveau bloc `elif self.swap_off:` fait décroître le
  glissement puis, une fois celui-ci terminé, arme le clignotement (en mettant
  `snd_match` en file) ou lance le glissement de retour.
- **`draw`** — même dessin du panneau, du plateau, de la sélection, du score, des
  instructions et de la bannière de victoire que `match3_1`, mais chaque tuile
  est désormais une commande de file d'affichage
  `{'type': 'sprite', 'sprite_name': ..., 'x': ..., 'y': ...}` au lieu d'un
  rectangle plein (toujours remplacée par un simple rectangle blanc pendant le
  clignotement des tuiles marquées, exactement comme le faisait `match3_1`),
  décalée par `swap_off` combiné à `falling`.

### La primitive `self._sound_queue`

`execute_code` ne dispose d'un objet `game` vivant que sur le moteur pygame en
version bureau — le moteur exporté vers Kivy et celui du Web/Pyodide lient tous
deux `game = None` dans cette portée, si bien que `game.sounds[...].play()` (la
solution qui vient naturellement à l'esprit) ne fonctionne que sur bureau. C'est
cet exemple qui a motivé l'ajout d'une vraie primitive multiplateforme :
l'`execute_code` de n'importe quel événement peut écrire

```python
self._sound_queue.append('snd_swap')
# ou, pour un volume différent de celui par défaut :
self._sound_queue.append({'sound': 'snd_swap', 'volume': 0.5})
```

et cela se joue de façon identique sur les trois cibles :

- **Bureau** — `ActionExecutor.execute_event` vide la file et la joue (via
  `game.sounds[...]`) juste après chaque événement, et pas seulement après
  `draw`.
- **Export Kivy** — `GameObject._drain_sound_queue` (généré dans
  `base_object.py`) résout le nom via un `asset_paths.py` généré (`SOUND_PATHS`)
  et appelle la fonction `play_sound()` existante ; la file est vidée une fois
  par image et par instance vivante, depuis la boucle `update()` de la scène, ce
  qui fonctionne donc même pour les objets sans événement `draw`.
- **Web (Pyodide)** — l'amorçage Python renvoie les sons mis en file dans le
  correctif JSON, aux côtés de la file d'affichage ; `engine.js` les joue comme
  de vrais éléments `<audio>`, par le même circuit audio mutualisé que celui déjà
  utilisé par l'action structurée `play_sound`.

Le même défaut de résolution par nom existait pour les commandes à la manière de
`draw_sprite` émises depuis un `execute_code` brut (le rendu des tuiles de cet
exemple) : le moteur de file d'affichage de Kivy ne savait auparavant résoudre un
sprite qu'à partir d'un `sprite_path` inscrit à la génération du code pour les
actions *structurées*, si bien qu'un dictionnaire
`{'type': 'sprite', 'sprite_name': ...}` écrit à la main n'y était silencieusement
pas dessiné. Corrigé de la même façon : `asset_paths.py` porte aussi
`SPRITE_PATHS`, et le cas `'sprite'` de la file d'affichage de Kivy s'y rabat par
nom lorsqu'aucun chemin préalablement résolu n'est présent.

### À expérimenter

Les mêmes réglages que dans `match3_1` (`self.cols`/`self.rows`, `self.palette`,
`self.target`, `flash_total`, `fall_speed`), plus :

- Vitesse de l'animation d'échange : `self.swap_speed` (px/image ; 24 ≈ 4 images
  par glissement avec `tile=96`).
- Volume des sons : passe un dictionnaire `{'sound': ..., 'volume': ...}` au lieu
  d'un simple nom à `self._sound_queue.append(...)`.

## Feuille de route

**[match3_3](../match3_3/README.md)** — fait : un nombre de coups limité, trois
salles formant des niveaux aux objectifs croissants, et des tuiles spéciales
(bonus d'alignement de 4 ou 5). Clôt la feuille de route d'origine de `match3_1`.

## État de l'export

- **Test du jeu (F5) / bureau :** fonctionne — vérifié de bout en bout avec une
  vraie exécution de `GameRunner` injectant un véritable clic de souris par le
  circuit d'événements pygame standard (échange → alignement → cascade → score,
  avec de vrais appels à `pygame.mixer.Sound.play()` observés).
- **Android (.apk) / Mobile (Kivy) :** **pris en charge.** Il a été vérifié que
  l'export se compile proprement, qu'`asset_paths.py` porte les bons
  `SPRITE_PATHS` et `SOUND_PATHS`, et que les images des sprites et les fichiers
  sonores sont bien copiés dans `assets/images` et `assets/sounds`. Construire le
  véritable fichier `.apk` demande en plus buildozer (via WSL sous Windows) —
  voir [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5) :** **pris en charge.** L'amorçage Pyodide de la page exportée
  vide `self._sound_queue` dans le même aller-retour JSON que la file
  d'affichage ; il a été vérifié que l'amorçage généré se compile et transmet
  correctement les commandes d'affichage comme les sons mis en file, sous CPython
  ordinaire (aucun navigateur n'est nécessaire pour cette vérification — le
  démarrage de Pyodide dans le navigateur n'est pas lui-même couvert par la suite
  automatique, même réserve que pour `match3_1`). Nécessite un accès à Internet
  au premier chargement (Pyodide se charge depuis un CDN).
- **Archive autonome :** non testée avec cet exemple.
