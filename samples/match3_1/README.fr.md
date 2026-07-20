# Match-3 — Niveau 1

Un jeu de réflexion « aligner trois » (match-3) minimal mais complet. C'est le
premier exemple pygm2 **écrit nativement dans le format de projet de l'IDE** —
les exemples de labyrinthe et de plateforme ont été importés de fichiers `.gmk`
GameMaker 8.x ; celui-ci a été écrit directement pour le moteur pygm2.

Il est délibérément petit : une salle, un objet, aucun script, aucun son. Tout le
jeu tient dans quatre événements d'un unique objet contrôleur, ce qui en fait
l'exemple de référence pour l'action `execute_code` et pour le rendu par file
d'affichage. Des versions plus avancées (tuiles à base de sprites, son, niveaux)
sont prévues sous les noms `match3_2`, etc. — voir la *Feuille de route*
ci-dessous.

**Où ce niveau se situe :** `match3_*` est la dernière (et la plus différente)
des trois familles d'exemples — un paradigme différent, pas une étape
supplémentaire : aucune action intégrée, aucun objet par tuile, aucune tuile au
niveau de la salle. Tout (l'état de la grille, les collisions, le rendu) est
piloté directement depuis du Python dans `execute_code`, au lieu d'être composé
d'actions intégrées réparties sur de nombreux objets comme le font `maze_*` et
`plateforme_*`. Voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la progression complète.

**Sons et musique :** aucun — délibérément, pour la raison expliquée ci-dessus.
(Le son devient possible à partir de `match3_2`, grâce à la primitive de file
sonore introduite par cet exemple.)

## Comment jouer

- **Clique** sur une tuile pour la sélectionner (contour blanc), puis **clique
  sur une tuile voisine** pour échanger les deux.
- Si l'échange aligne **3 tuiles ou plus de la même couleur** en ligne ou en
  colonne, les tuiles alignées clignotent un instant, sont détruites, et les
  tuiles du dessus **glissent vers le bas** pour combler le trou ; de nouvelles
  tuiles tombent depuis le haut du plateau.
- Les réactions en chaîne (« cascades ») se résolvent vague après vague, chacune
  avec sa propre animation de clignotement et de glissement.
- Un échange qui ne produit aucun alignement est annulé immédiatement.
- Chaque tuile détruite vaut **10 points** ; atteins **500 points** pour gagner.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — fenêtre de 800×800, 60 images/s (`room_speed`), salle de démarrage `rm_match3` |
| `rooms/rm_match3.json` | L'unique salle ; contient une instance d'`obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | Tout le jeu : quatre événements, chacun contenant une seule action `execute_code` |
| `sprites/spr_red\|blue\|green\|yellow.*` | Carrés de tuiles 32×32 — **pas encore utilisés** ; réservés à la suite à base de sprites (voir `CREDITS.txt`) |

Il n'y a ni objet joueur, ni objet par tuile : le plateau est de la pure donnée
(une liste 6×6 d'indices de couleur) détenue par une unique instance de
contrôleur invisible, et tout ce qui apparaît à l'écran est dessiné par
l'événement `draw` de ce contrôleur, via la file d'affichage du moteur
(`self._draw_queue`).

## Comment le code fonctionne

Tout l'état est porté par l'instance du contrôleur (`self.…`), créé dans
l'événement `create` :

| Attribut | Signification |
|---|---|
| `grid` | Liste 6×6 d'entiers de 0 à 3 (indices dans `palette`) ; initialisée sans aucun alignement préexistant |
| `sel` | Case actuellement sélectionnée `(gx, gy)`, ou `None` |
| `marked` | Ensemble des cases actuellement alignées et clignotantes |
| `flash` / `flash_total` | Images restantes de la phase de clignotement / sa durée (36 images ≈ 0,6 s à 60 im/s) |
| `falling` | Dictionnaire `(gx, gy) → pixels` — de combien chaque tuile en train de glisser se trouve encore au-dessus de sa case de repos |
| `fall_speed` | Vitesse de glissement en pixels par image (12 → une rangée de 96 px en ≈ 0,13 s) |
| `score`, `target`, `won` | État du score (victoire à 500) |
| `find_matches` | Fonction utilitaire (définie dans `create` et rangée sur l'instance) qui parcourt la grille et renvoie l'ensemble des cases alignées |

Le jeu est un petit automate à états piloté par l'événement `step` :

```
repos ──(clic échange, alignement trouvé)──▶ CLIGNOTEMENT (36 images)
                                               │ tuiles détruites, score ajouté
                                               ▼
                                        CHUTE (les décalages diminuent de 12 px/image)
                                               │ tuiles posées → nouveau parcours de la grille
                          nouvel alignement ───┴─── aucun alignement
                                     │                      │
                                     ▼                      ▼
                             CLIGNOTEMENT                 repos
```

- **`create`** — construit la grille de départ (en retirant au hasard toute tuile
  qui compléterait un alignement immédiat), initialise l'état ci-dessus et
  définit `find_matches`.
- **`mouse_left_press`** — logique de sélection et de désélection ; sur un
  échange entre cases voisines, applique l'échange puis soit arme le clignotement
  (`marked`, `flash`), soit annule. Les clics sont ignorés pendant un
  clignotement ou une chute en cours, ainsi qu'une fois la partie gagnée.
- **`step`** — décompte le clignotement ; à son terme, crédite le score, réécrit
  chaque colonne touchée dans sa disposition finale, et enregistre un décalage en
  pixels dans `falling` pour chaque tuile qui a bougé (les tuiles survivantes
  reçoivent `rangées_descendues × 96` ; les tuiles de remplissage entrent par le
  haut du plateau). Tant que `falling` n'est pas vide, chaque décalage diminue de
  `fall_speed` ; quand tout est posé, la grille est reparcourue à la recherche
  d'alignements en cascade, et le clignotement est soit réarmé, soit l'on revient
  au repos.
- **`draw`** — dessine le panneau du plateau, puis chaque tuile à
  `position_de_repos − décalage_de_chute`. Les tuiles au-dessus du bord supérieur
  du plateau sont découpées (partiellement sorties) ou ignorées (totalement
  cachées), de sorte que les tuiles de remplissage semblent glisser depuis sous
  l'en-tête. Les tuiles marquées clignotent en blanc toutes les 6 images et
  portent un contour blanc ; la sélection, la ligne de score, les instructions et
  la bannière de victoire sont dessinées en dernier.

### À expérimenter

- Taille du plateau : `self.cols` / `self.rows` (les constantes de disposition
  `ox`, `oy` et `tile` en contrôlent le placement — un plateau 6×6 de tuiles de
  96 px tient dans la fenêtre de 800×800).
- Couleurs et types de tuiles : `self.palette` (ajoute un tuple pour obtenir une
  5e couleur ; la logique de tirage et le rendu la prennent en compte
  automatiquement, mais pense à mettre à jour les `random.randrange(4)` dans
  `create` et `step`).
- Difficulté : `self.target` (points pour gagner), `flash_total`, `fall_speed`.

## Feuille de route (versions avancées prévues)

- **[match3_2](../match3_2/README.md)** — fait : dessine les tuiles avec des
  sprites au lieu de rectangles colorés, ajoute des effets sonores pour les
  échanges, les alignements et les cascades, ainsi qu'une animation de
  glissement lors de l'échange.
- **[match3_3](../match3_3/README.md)** — fait : un nombre de coups limité, trois
  salles formant des niveaux aux objectifs croissants, et des tuiles spéciales
  issues des alignements de 4 ou 5. Clôt cette feuille de route.

Ces versions sont pensées pour refléter la progression de `maze_1` à `maze_3` :
chacune est une évolution lisible de la précédente.

## État de l'export

- **Test du jeu (F5) / bureau :** fonctionne — le jeu tourne sur le moteur pygame
  standard. Il est exercé sans affichage dans les tests automatiques, via
  `tools/smoke_run_samples.py`.
- **Android (.apk) / Mobile (Kivy) :** **pris en charge** (depuis le 03/07/2026).
  Le moteur Kivy exporté dessine la file d'affichage du jeu (rectangles et
  textes, avec l'axe y converti vers le repère de bas en haut de Kivy), transmet
  les appuis comme l'événement `mouse_left_press` avec des `mouse_x`/`mouse_y` en
  coordonnées de salle, aussi bien sur Android (en inversant la transformation de
  mise à l'échelle plein écran) que sur Kivy en version bureau, et — puisque ce
  jeu n'a aucun événement clavier — n'affiche pas la croix directionnelle
  virtuelle qui recouvrirait sinon le coin inférieur droit du plateau. Le jeu
  exporté est exercé sans affichage dans
  `tests/test_kivy_draw_queue_mouse_export.py`, qui joue un tour complet
  échange → clignotement → glissement à travers le code généré. Construire le
  véritable fichier `.apk` demande en plus buildozer (via WSL sous Windows) —
  voir [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md) pour le guide
  complet (installation, temps de compilation, mise en cache pour une salle de
  classe) ; les écarts de parité restants de l'export Kivy, qui n'affectent
  *pas* ce jeu, sont listés sous « Kivy/Android export » dans le `TODO.md` du
  dépôt.
- **Web (HTML5) :** **pris en charge** (depuis le 10/07/2026) — et c'est la
  meilleure voie vers les iPhone (aucune installation, aucune signature). La
  page exportée détecte que le jeu contient des événements `execute_code` en
  Python et charge le moteur Pyodide pour les exécuter avec la sémantique de
  l'IDE ; les clics et les appuis sont transmis comme l'événement d'appui du
  bouton gauche, et la file d'affichage est dessinée sur le canevas. Vérifié de
  bout en bout sous Chromium sans affichage (le plateau s'affiche, l'échange par
  clic, le clignotement, le glissement et le score fonctionnent). Une réserve :
  le moteur Python se charge depuis un CDN, la page a donc besoin d'un accès à
  Internet à son ouverture — les jeux composés uniquement d'actions (les exemples
  de labyrinthe et de plateforme) restent, eux, entièrement hors ligne.
- **Archive autonome :** non testée avec cet exemple.
