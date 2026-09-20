# PyGameMaker — Tutoriel 10 : Multijoueur au tour par tour par échange de fichiers

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Multijoueur au tour par tour : Morpion par échange de fichiers** (5 pages, environ 25 à 30 minutes). Garde le tutoriel ouvert sur une moitié de ton écran ; il donne tous les détails de chaque étape. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. À partir de la phase 2, il te faut un ou une partenaire et un **dossier partagé** que les deux ordinateurs peuvent utiliser. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un morpion pour deux joueurs sur deux ordinateurs, sans connexion en direct : chaque coup est écrit sous forme d'un petit fichier dans un dossier partagé, et l'autre ordinateur le lit. Un ordinateur **héberge** (touche H) et joue X ; l'autre **rejoint** (touche J) et joue O.

## Phase 1 : Le plateau

- [ ] **1.** Crée un projet `TicTacToeFiles` avec le modèle **Projet vide**. Crée `obj_game` (sans sprite) et une salle `room_board`, et place un `obj_game` dedans.
- [ ] **2.** Dans `obj_game`, événement **Création** : mets neuf variables à un texte vide : `cell_0_0`, `cell_1_0`, `cell_2_0`, `cell_0_1`, `cell_1_1`, `cell_2_1`, `cell_0_2`, `cell_1_2`, `cell_2_2` (colonne d'abord, puis rangée).
- [ ] **3.** Événement **Dessin** : d'abord *Définir la couleur de dessin* en blanc. Puis quatre actions *Dessiner une ligne* pour la grille : x 270 et 370 de y 90 à 390, et y 190 et 290 de x 170 à 470.
- [ ] **4.** **Souris : Bouton gauche pressé** : neuf **Si**, un par case, comme `cell_0_0 == "" and mouse_x >= 170 and mouse_x < 270 and mouse_y >= 90 and mouse_y < 190` alors *Définir la variable* `cell_0_0` à X.
- [ ] **5.** Dans l'événement **Dessin** : pour chaque case, *Si* la variable n'est pas vide, *Dessiner du texte* dans la case (ajoute 100 à x par colonne et à y par rangée).

> DONE: **Tu dois voir :** appuie sur **F5**. Une grille blanche apparaît. Cliquer sur une case y met un X ; cliquer de nouveau ne fait rien.

## Phase 2 : Héberger une partie / rejoindre une partie

- [ ] **6.** Choisis un dossier que les deux ordinateurs peuvent utiliser (un lecteur réseau, ou un dossier synchronisé). Pour tester seul·e, un simple nom de dossier comme `tictactoe_files` convient.
- [ ] **7.** **Touche pressée H** : *Héberger une partie (échange de fichiers)* avec ce dossier, 2 joueurs maximum, nom « Player 1 » ; puis mets `my_mark` à X. **Touche pressée J** : *Rejoindre une partie (échange de fichiers)* avec le même dossier et le nom « Player 2 » ; puis mets `my_mark` à O.
- [ ] **8.** Dans l'événement **Dessin**, avant la grille : *Si* `global.waiting_for_players == 1` alors dessine « Waiting for opponent... » et *Quitter l'événement* ; sinon dessine « You are » + `my_mark`.

> DONE: **Tu dois voir :** lance le jeu sur les deux ordinateurs. Appuie sur H sur l'un et sur J sur l'autre. « Waiting for opponent... » disparaît et chaque écran indique « You are X » ou « You are O ».

## Phase 3 : De vrais tours de jeu

- [ ] **9.** **Création** : mets `last_round_acted` et `my_turn` à 0.
- [ ] **10.** **Pas** : si c'est mon tour (`global.round_number` impair et je suis X, ou pair et je suis O), mets `my_turn` à 1, sinon à 0. Ensuite : si `my_turn == 0` et `last_round_acted != global.round_number`, *Terminer le tour (échange de fichiers)* et mets `last_round_acted` à `global.round_number` (un « passe »).
- [ ] **11.** Réécris les neuf tests de clic : ajoute `my_turn == 1`, et au lieu de définir la variable, *Définir une variable partagée (échange de fichiers)* avec le nom propre de la case et la valeur `my_mark`, puis *Terminer le tour (échange de fichiers)*.
- [ ] **12.** Dans l'événement **Dessin**, dessine chaque case à partir de `global.cell_0_0` etc. (seulement si elle n'est pas 0 ; une variable partagée jamais définie vaut 0).

> DONE: **Tu dois voir :** seul le joueur dont c'est le tour peut placer une marque. Une marque apparaît sur **les deux** écrans un instant après le clic, et les tours alternent X, O, X.

## Phase 4 : Gagner et rejouer

- [ ] **13.** Dans `obj_game`, ajoute l'événement **Manche résolue** avec huit **Si**, un par ligne (trois rangées, trois colonnes, deux diagonales) : si les trois `global.cell_*` sont égales et différentes de 0, mets `winner` à cette marque.
- [ ] **14.** **Création** : mets `winner` à un texte vide. **Dessin** (en dernier) : si `winner != ""`, dessine `winner + " wins! Press SPACE to play again."`.
- [ ] **15.** **Touche pressée Espace** : si `winner != ""`, *Quitter la partie (échange de fichiers)*. Appuie de nouveau sur H et J pour une nouvelle partie.

> DONE: **Tu dois voir :** aligne trois marques et les deux écrans affichent qui a gagné.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| L'écran est vide | Le dessin est noir sur la salle noire | Ajoute *Définir la couleur de dessin* en blanc en haut de l'événement **Dessin** |
| « Waiting for opponent... » reste affiché | Les deux ordinateurs utilisent des dossiers différents, ou un ordinateur ne peut pas atteindre le dossier | Utilise exactement le même chemin ; vérifie que les deux peuvent y créer un fichier |
| Les deux ordinateurs disent « You are X » | Les deux ont appuyé sur H | L'un appuie sur H, l'autre sur J |
| Un clic ne fait rien | Ce n'est pas ton tour, la case est déjà prise, ou `my_turn` n'est pas défini | Attends ton tour ; vérifie l'événement **Pas** |
| Ma marque n'apparaît qu'après un instant | C'est normal : elle apparaît quand la manche est résolue (environ une seconde) | Attends environ une seconde |
| La marque d'un joueur n'apparaît jamais | Il a oublié *Terminer le tour* après le clic | Ajoute *Terminer le tour (échange de fichiers)* au gestionnaire de clic |
| Personne ne gagne même avec trois alignés | Il manque une ligne dans **Manche résolue**, ou les noms sont faux | Vérifie les huit lignes et les noms de cases |
| Les noms des cases ne correspondent pas | Une faute de frappe, par exemple `cell_1_0` au lieu de `cell_0_1` | Les noms de cases sont colonne d'abord, puis rangée |

## Défis

- **Essaie (5 minutes) :** change les noms des joueurs, ou le dossier.
- **Va plus loin :** remets les neuf cases et `winner` à zéro en quittant la partie, pour une revanche sans redémarrer.
- **Invente :** affiche un message quand le plateau est plein sans gagnant, ou garde un score sur plusieurs parties avec une autre variable partagée.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Hôte | L'ordinateur qui fait tourner la partie et décide de chaque manche |
| Dossier partagé | Un dossier que les deux ordinateurs peuvent lire et écrire |
| Variable partagée | Une valeur que chaque joueur peut lire sous la forme `global.nom` |
| Manche | Un tour de jeu, résolu par l'hôte |
| Au tour par tour | Les joueurs agissent l'un après l'autre, pas en même temps |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Comment un coup passe-t-il d'un ordinateur à l'autre ?
2. Pourquoi le joueur dont ce n'est pas le tour doit-il quand même « passer » avec *Terminer le tour* ?
3. Pourquoi la marque est-elle dessinée à partir de `global.cell_0_0` et non de la variable locale ?

## Mes notes

[[notes:10]]
