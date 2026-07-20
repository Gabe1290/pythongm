# Match-3 — Niveau 3

La suite de [`match3_2`](../match3_2/README.md) avec nombre de coups limité,
niveaux multiples et tuiles spéciales, promise dans la feuille de route d'origine
de `match3_1` — la dernière des trois versions prévues de match3. Même
architecture d'un bout à l'autre : aucun script, tout le jeu tient encore dans
quatre événements `execute_code` sur un unique objet contrôleur, simplement placé
dans trois salles au lieu d'une.

**Où ce niveau se situe :** il fait partie de la famille `match3_*` — du pur
script dans `execute_code`, aucune action intégrée, aucune tuile au niveau de la
salle ; il clôt la progression décrite dans
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays).

**Sons et musique :** 5 fichiers sonores — les 3 de `match3_2`
(`snd_swap`/`match`/`cascade`) plus 2 nouveaux (`snd_special`, `snd_level_up`),
tous réellement utilisés via `self._sound_queue`.

## Comment jouer

Mêmes règles d'échange, d'alignement et de cascade que dans `match3_1` et
`match3_2`, plus :

- Tu disposes d'un **nombre de coups limité** par niveau. Un coup n'est consommé
  que par un échange qui produit réellement un alignement — un échange invalide
  (qui repart en glissant) peut être retenté sans rien coûter.
- Atteins le **score cible** du niveau avant d'être à court de coups pour passer
  à la salle suivante. Si les coups s'épuisent d'abord, le niveau se termine —
  **clique n'importe où pour recommencer** le même niveau depuis le début.
- **Aligne 4 tuiles** (exactement 4) et l'une des quatre devient une **tuile
  spéciale « nettoyage de ligne »** : une barre blanche la signale. Aligne-la de
  nouveau plus tard (dans n'importe quel autre alignement) et elle nettoie sa
  **ligne ou sa colonne entière** — selon la direction dans laquelle courait
  l'alignement de 4 d'origine.
- **Aligne 5 tuiles ou plus** et l'une d'elles devient une **tuile spéciale
  « bombe de couleur »** : un anneau blanc la signale. Aligne-la de nouveau plus
  tard et elle nettoie **toutes les tuiles d'une même couleur** sur tout le
  plateau.
- Il y a **3 niveaux**, chacun dans sa propre salle, avec un objectif plus élevé
  et un nombre de coups plus serré. Termine le niveau 3 pour gagner la partie.

## Ce qui change par rapport à `match3_2`

| `match3_2` | `match3_3` |
|---|---|
| Une salle, coups illimités, victoire à un score fixe | **3 salles** (une par niveau), un **nombre de coups limité** par niveau, et un **objectif croissant** à chaque niveau |
| Un alignement est toujours entièrement détruit | Un alignement de **4** ou de **5 et plus** laisse derrière lui une **tuile spéciale** au lieu de détruire toutes les cases |
| Aucune progression d'un niveau à l'autre | Atteindre l'objectif appelle `self.advance_level()`, qui règle `self.goto_room_target` sur la salle suivante (ou `self.won` au dernier niveau) |

L'automate central d'échange, de clignotement, de chute et de cascade, le dessin
des tuiles par sprites et les déclenchements de la file sonore sont par ailleurs
inchangés depuis `match3_2` — voir le guide de cet exemple pour la description
complète de `swap_off`, `falling` et `find_matches`.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — fenêtre de 800×800, 60 images/s, salle de démarrage `rm_level1`, `room_order` = les 3 niveaux |
| `rooms/rm_level1\|2\|3.json` | Une salle par niveau, chacune contenant sa propre instance d'`obj_GridManager` en (0, 0) |
| `objects/obj_GridManager.json` | Tout le jeu : quatre événements, chacun contenant une seule action `execute_code` |
| `sprites/`, `sounds/` | Tuiles de gemmes et effets, repris pour l'essentiel de `match3_2` (voir `CREDITS.txt`) ; `snd_special` et `snd_level_up` sont nouveaux |

Il n'y a toujours ni objet par tuile ni script — une instance de contrôleur par
salle, recréée à neuf (par la règle habituelle de GameMaker « chaque salle a ses
propres instances ») à chaque entrée dans une salle, ce qui donne gratuitement à
chaque niveau un départ propre.

## Comment le code fonctionne

### Mise en place des niveaux (nouveau dans `create`)

```python
self.room_order = ['rm_level1', 'rm_level2', 'rm_level3']
level_config = {
    'rm_level1': (300, 20),   # (score cible, nombre de coups)
    'rm_level2': (500, 18),
    'rm_level3': (800, 16),
}
```

`create` lit `game.current_room.name`, le range dans `self.room_name`
(indispensable, car une simple variable locale définie dans un événement
`execute_code` ne **survit pas** jusqu'à un événement ultérieur — voir la note
sur le piège ci-dessous), et règle `self.target`, `self.moves` et
`self.level_num` d'après la table ci-dessus.

### Coups et défaite (nouveau dans `mouse_left_press`)

Un échange ne consomme un coup que si `find_matches` indique qu'il produira
réellement un alignement (`if marks: self.moves = self.moves - 1`) ; un échange
refusé qui repart en glissant est donc gratuit. Quand `self.moves` atteint 0 sans
que l'objectif soit atteint, `step` met `self.lost = True` ; `mouse_left_press`
vérifie cet indicateur **en premier**, avant le contrôle d'entrée habituel, et
transforme n'importe quel clic en `self.restart_room_flag = True` (le même
indicateur qu'utilise `restart_room`), ce qui reconstruit la salle — et avec
elle, une nouvelle instance d'`obj_GridManager` dont l'événement `create`
réinitialise tout.

### Tuiles spéciales (nouveau dans `step`)

`find_matches` renvoie désormais `(marks, runs)` au lieu du seul `marks` — chaque
suite est un `(cases_dans_l_ordre, 'h' ou 'v')`. À l'expiration du clignotement,
**avant** le décompte des points :

1. Pour chaque suite de longueur ≥ 4, la **case du milieu** devient une tuile
   spéciale au lieu d'être détruite : les suites de 4 donnent `('row',)` ou
   `('col',)` (selon l'orientation de la suite) ; les suites de 5 et plus donnent
   `('color', <indice de couleur>)`.
2. Pour chaque case déjà marquée qui figure dans `self.special` (c'est-à-dire une
   tuile spéciale prise dans *cet* alignement), son effet se déclenche une fois :
   une tuile `row`/`col` ajoute toute sa ligne ou sa colonne aux cases à
   nettoyer ; une tuile `color` ajoute toutes les cases du plateau ayant la
   couleur qu'elle a mémorisée. C'est une passe **unique et non récursive** — si
   le souffle d'une tuile spéciale en attrape une autre, celle-ci est détruite
   mais ne déclenche **pas** son propre effet en chaîne. (C'est une
   simplification, pas un bug — cela garde l'effet borné et facile à suivre.)
3. Les cases spéciales nouvellement créées sont protégées de la destruction dans
   la même vague, même si un souffle de l'étape 2 les aurait attrapées.
4. `self.special` est reconstruit de zéro à chaque vague, en suivant les tuiles
   survivantes pendant leur chute (la boucle de chute par colonne porte désormais
   un troisième élément dans son tuple — le type de spécialité de la tuile, ou
   `None` — à côté de sa rangée et de sa couleur), de sorte qu'une tuile spéciale
   pas encore alignée descend avec la gravité comme n'importe quelle autre.

### Passage au niveau suivant (nouveau dans `create`, utilisé depuis `step`)

```python
def advance_level():
    idx = self.room_order.index(self.room_name)
    if idx + 1 < len(self.room_order):
        self.goto_room_target = self.room_order[idx + 1]
        self._sound_queue.append('snd_level_up')
    else:
        self.won = True
self.advance_level = advance_level
```

`self.goto_room_target` est le même indicateur d'instance que règle l'action
intégrée `goto_room` — la boucle principale du jeu le consulte déjà à chaque
image, il suffit donc de le régler directement depuis `execute_code` pour
déclencher un véritable changement de salle, sans avoir besoin d'action
structurée. `step` appelle `self.advance_level()` dès que
`self.score >= self.target`, et saute tout nouveau parcours de cascade pour le
reste de cette image si un changement de salle (ou une victoire finale) est
désormais en attente : une salle que l'on quitte ne continue donc pas à s'animer.

### Piège : les fermetures sur de simples variables locales ne survivent pas d'un événement à l'autre

L'environnement d'exécution d'`execute_code` passe des dictionnaires de
variables globales et locales **distincts** (`exec(code, exec_globals,
exec_locals)`), ce qui le fait se comporter comme l'intérieur d'une fonction :
une simple affectation au premier niveau (`room_name = ...`) atterrit dans le
dictionnaire des *locales*, mais une fonction définie par `def` à ce même premier
niveau résout ses variables libres à travers le dictionnaire des *globales* au
moment où elle est **appelée** — ce qui, pour une fonction imbriquée rangée sur
`self` (comme `find_matches`, `arm_swap` et maintenant `advance_level`), se
produit toujours depuis un **autre** appel d'`execute_code`, avec son propre
dictionnaire de locales tout neuf. Une simple variable locale référencée par une
telle fonction provoque un `NameError` la première fois que la fonction est
réellement appelée depuis un autre événement — tout semble correct dans
l'événement où elle est définie, et l'échec ne se manifeste que plus tard, au
déclenchement. Le remède est celui que les `find_matches` de `match3_1` et
`arm_swap` de `match3_2` illustraient déjà sans le dire explicitement : ne
fermer que sur `self` (toujours présent dans les globales de chaque événement) ou
sur des **attributs d'instance** (`self.room_name`, et non un simple
`room_name`) — jamais sur une simple variable locale. Détecté par l'étape de
validation en banc d'essai autonome pendant le développement (voir les notes de
méthodologie d'audit dans le `CLAUDE.md` du dépôt) ; il existe désormais un test
de non-régression pour ce cas (`tests/test_match3_3_sample.py`).

### `draw`

Même dessin du panneau, du plateau, de la sélection, de la ligne de score et de
la bannière de victoire que dans `match3_2`, plus : une ligne d'affichage pour le
numéro de niveau et les coups restants, une barre ou un anneau blanc superposé au
sprite d'une tuile spéciale (omis pendant le clignotement de la tuile), et une
bannière « OUT OF MOVES — click to retry » quand `self.lost` est vrai.

### À expérimenter

- Difficulté de chaque niveau : la table `level_config` dans `create` (score
  cible, nombre de coups) — ajoute une quatrième entrée et une quatrième salle
  pour prolonger la série.
- Portée du souffle des tuiles spéciales : les branches `row`/`col`/`color` de la
  boucle d'activation dans `step`.
- Tout ce que `match3_2` exposait déjà (taille du plateau, vitesse d'échange et
  de chute, volumes sonores).

## Feuille de route

Cet exemple clôt la feuille de route d'origine en trois parties de `match3_1`
(`match3_1` → `match3_2` → `match3_3`). Aucune autre version n'est prévue.

## État de l'export

- **Test du jeu (F5) / bureau :** fonctionne — vérifié de bout en bout avec une
  vraie exécution de `GameRunner` injectant un véritable clic de souris par le
  circuit d'événements pygame standard : alignement de 4 forcé → tuile spéciale
  créée → objectif atteint → **la salle est réellement passée à `rm_level2`**
  avec une nouvelle instance (`level_num == 2`, score et coups réinitialisés).
- **Android (.apk) / Mobile (Kivy) :** repose sur la même machinerie
  (`asset_paths.py`, `_drain_sound_queue`, résolution des sprites par nom) que
  `match3_2` a ajoutée et vérifiée — cet exemple n'exerce rien de nouveau sur ce
  plan (aucun nouveau type de commande d'affichage, aucun nouveau type d'action ;
  le `goto_room` par indicateur fonctionne à l'identique dans la boucle de scène
  exportée vers Kivy, qui consulte déjà les mêmes indicateurs d'instance à chaque
  image). Construire le véritable fichier `.apk` demande en plus buildozer (via
  WSL sous Windows) — voir
  [`docs/ANDROID_EXPORT.md`](../../docs/ANDROID_EXPORT.md).
- **Web (HTML5) :** même raisonnement — aucune nouvelle primitive de file
  d'affichage ou de file sonore au-delà de ce que `match3_2` avait déjà validé
  sur cette cible.
- **Archive autonome :** non testée avec cet exemple.
