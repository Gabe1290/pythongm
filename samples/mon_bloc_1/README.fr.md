# Mes Blocs — Leçon 1

Un petit jeu de collecte de pièces dont l'intérêt n'est pas le jeu
lui-même, mais la leçon qu'il contient : **« My Blocks »** (« Mes
Blocs »), la fonctionnalité de Blockly qui permet de créer son propre
bloc personnalisé (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md, Fonctionnalité 2,
dans la documentation technique de ce projet). C'est un projet pygm2
natif, créé directement dans l'IDE (pas d'import `.gmk`, pas
d'`execute_code`) — tout ici est construit avec des blocs d'action
ordinaires.

**Son et musique :** aucun — ce projet ne contient aucun fichier son.

## Comment jouer

- Les **flèches directionnelles** (haut/bas/gauche/droite) déplacent le
  joueur d'une case de grille (32 px) à la fois.
- Marcher sur une pièce la ramasse : les pièces **bronze** valent 5
  points, les pièces **argent** 10, les pièces **or** 25. Le score
  s'affiche en haut à gauche.
- Il n'y a ni mur, ni but, ni condition de victoire — juste trois types
  de pièces à collecter pendant que vous regardez comment le jeu est
  construit (voir ci-dessous).

## La leçon : repérer la répétition, puis l'éliminer

Ouvrez `obj_joueur` dans l'éditeur d'objets et passez à son onglet
**Blockly**. Vous y verrez trois événements de collision — un par
couleur de pièce — et chacun fait *exactement la même chose*, avec un
seul nombre qui change :

| Événement | Action 1 | Action 2 |
|---|---|---|
| `collision_with_obj_piece_bronze` | « Destroy other instance » | Ajouter au score : **5** |
| `collision_with_obj_piece_argent` | « Destroy other instance » | Ajouter au score : **10** |
| `collision_with_obj_piece_or` | « Destroy other instance » | Ajouter au score : **25** |

C'est exactement le genre de répétition que tout programmeur apprend à
repérer : quand on se retrouve à recopier les mêmes blocs encore et
encore en changeant seulement une valeur, c'est le signe qu'il est temps
d'en faire **son propre bloc**. Voici comment, étape par étape :

1. Ouvrez la catégorie **My Blocks** en bas de la boîte à outils Blockly
   (elle est toujours là, même vide au départ) et cliquez sur **Make a
   Block**.
2. Nommez-le `donner_points` et ajoutez une entrée — cliquez sur le **+**
   bleu de la fenêtre de configuration, nommez le nouveau paramètre
   `montant`, puis fermez la fenêtre.
3. Vous avez maintenant un bloc « define donner_points (montant) » sur
   le plan de travail. Glissez-y les blocs **« Destroy other
   instance »** et « Add to score » — les deux mêmes blocs que vous
   avez vus répétés trois fois ci-dessus.
4. Glissez le paramètre `montant` (il apparaît comme une petite pièce de
   puzzle sur le bloc « define » lui-même, la même forme que celle
   utilisée par le bloc « Set Variable » pour sa propre valeur) dans la
   case numérique d'« Add to score », à la place du `5`/`10`/`25` que
   vous auriez sinon dû taper trois fois.
5. Retournez aux trois événements de collision. Dans chacun, supprimez
   la paire « Destroy other instance » + « Add to score » et
   remplacez-la par un seul bloc **call `donner_points`** (lui aussi
   dans la catégorie My Blocks) — en tapant `5` pour le bronze, `10`
   pour l'argent, `25` pour l'or dans son unique case d'entrée.

Le jeu se joue exactement de la même façon après — mais désormais, la
logique « que se passe-t-il quand on ramasse une pièce » n'existe qu'en
**un seul endroit** : corriger un bug dedans (ou ajouter une quatrième
action, comme un son) ne sera plus jamais à faire qu'une fois.

**Envie d'aller plus loin ?** Un bloc personnalisé peut aussi *renvoyer
une valeur* au lieu de simplement exécuter des actions — dans la fenêtre
« Make a Block », cochez « with output » à la création, puis branchez
une simple expression arithmétique dans sa case `return` (pas
d'actions, juste un calcul). Ce genre de bloc peut alors se glisser
directement dans une case numérique ailleurs, de la même façon que
`donner_points` est ici appelé comme une instruction. Ce projet n'en
utilise pas — la leçon ci-dessus se limite volontairement, dans un
premier temps, au genre de bloc le plus simple : celui qui exécute des
actions.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre/salle et copies intégrées de toutes les ressources |
| `rooms/room0.json` | La seule salle : départ du joueur + 2 pièces de chaque couleur |
| `objects/obj_joueur.json` | Objet joueur — déplacement sur grille + les trois événements de collision répétés qui sont le sujet de cette leçon |
| `objects/obj_piece_bronze.json`, `obj_piece_argent.json`, `obj_piece_or.json` | Les trois types de pièces — purement passifs ; c'est `obj_joueur` qui fait tout le travail lors de la collision |
| `objects/obj_hud.json` | Objet contrôleur invisible qui affiche le score |
| `sprites/` | `spr_joueur.png` + trois sprites de pièces, générés par `tools/gen_mon_bloc_1_sprites.py` |
| `CREDITS.txt` | Mention de licence des ressources de ce projet |

## Objets

| Objet | Rôle | Événements clés |
|---|---|---|
| `obj_joueur` | Personnage contrôlé par le joueur ; déplacement sur grille, collecte les pièces | keyboard (up, down, left, right, nokey), collision_with_obj_piece_bronze/argent/or |
| `obj_piece_bronze` / `obj_piece_argent` / `obj_piece_or` | Pièce collectible, valant 5/10/25 points | (aucun — passif, détruit par le gestionnaire de collision du joueur) |
| `obj_hud` | Invisible ; affiche le score en continu | draw |

## Ressources

4 sprites (`spr_joueur` 24×24, trois sprites de pièces 16×16, tous en une
seule image), 0 son. Toutes ces images sont des formes en couleurs
unies générées par `tools/gen_mon_bloc_1_sprites.py`, placées dans le
domaine public (CC0) — voir `CREDITS.txt`.

## Statut export

Couvert par la suite de tests de fumée (`tools/smoke_run_samples.py`,
qui liste `mon_bloc_1`) ; non vérifié individuellement par cible
d'export (HTML5/Kivy) — le jeu lui-même n'utilise que des actions déjà
anciennes et déjà couvertes (`set_score`, `destroy_instance`,
déplacement sur grille, `draw_score`), donc rien n'est spécifique à une
cible d'export dans ce projet. Présenté dans l'onglet d'accueil de l'IDE
sous le nom « My Blocks — Lesson 1 » (`widgets/welcome_tab.py`). **Volontairement
non couvert** : la fonctionnalité « My Blocks » elle-même n'existe qu'au
moment de la création dans Blockly (docs/BLOCKLY_SCRATCH_PARITY_PLAN.md)
— un bloc personnalisé est développé en actions ordinaires avant même
d'être enregistré, donc il n'y a rien qu'une cible d'export aurait à
prendre en charge de toute façon.
