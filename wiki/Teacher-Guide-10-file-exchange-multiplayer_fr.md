# PyGameMaker — Tutoriel 10 : Multijoueur au tour par tour par échange de fichiers — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-10-file-exchange-multiplayer_fr.pdf) · [ODT](downloads/Teacher-Guide-10-file-exchange-multiplayer_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/10_file_exchange_multiplayer_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Multijoueur au tour par tour : Morpion par échange de fichiers**, 5 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 4 ou 6 et être à l'aise avec les variables, les conditions et l'événement Dessin. C'est le tutoriel le plus exigeant de la série et le seul qui demande deux ordinateurs.

## Vue d'ensemble

Les élèves construisent un morpion pour deux ordinateurs en quatre phases : le plateau (un seul joueur), héberger et rejoindre, de vrais tours de jeu, et gagner et rejouer. Notions nouvelles : le **multijoueur au tour par tour via un dossier partagé** (pas de connexion en direct, donc cela passe à travers les pare-feu scolaires), les **variables globales renseignées par le réseau** (`global.player_id`, `global.round_number`, `global.waiting_for_players`), les **variables partagées**, **Terminer le tour**, et l'événement **Manche résolue**.

> **Info:** La note historique du tutoriel (jeux par correspondance, VGA Planets) fait une bonne introduction : le jeu échange des fichiers exactement comme les joueurs échangeaient jadis des lettres.

## Durée suggérée (75 à 90 minutes, de préférence sur deux séances)

Le tutoriel annonce 25 à 30 minutes pour un élève à l'aise ; les neuf tests de cases répétés, les huit lignes gagnantes et la mise en place du laboratoire prennent beaucoup plus de temps.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Introduction et binômes | 10 min | Expliquez l'idée ; formez les binômes ; préparez le dossier partagé |
| Phase 1 : le plateau | 20 min | Pages 1-2 ; les neuf tests répétés sont fastidieux mais identiques |
| Phase 2 : héberger et rejoindre | 15 min | Page 3 ; premier vrai test entre deux ordinateurs |
| Phase 3 : les tours | 20 min | Page 4 |
| Phase 4 : gagner | 15 min | Page 5 ; huit lignes gagnantes |
| Feuille d'exercices / ticket de sortie | 5-10 min | Parties A à C de la feuille |


La phase 1 n'a pas besoin d'un second ordinateur. Bon découpage : séance 1 = phase 1 (et phase 2 s'il reste du temps), séance 2 = le reste avec le laboratoire préparé.

## Mise en place du laboratoire (à faire avant la leçon)

- **Le dossier partagé est tout le principe.** Les deux ordinateurs d'un binôme doivent lire et écrire dans le *même* dossier. Options : un lecteur réseau mappé ou un chemin UNC sur le serveur de l'école (le mieux : `\\serveur\partage\tictactoe` ou une lettre de lecteur), ou un dossier synchronisé (Dropbox, OneDrive). Donnez à chaque binôme son **propre sous-dossier** (par exemple `tictactoe_binome3`) pour que les binômes n'interfèrent pas.
- Les deux ordinateurs doivent saisir le **chemin de dossier exactement identique** dans les actions Héberger et Rejoindre. Une lettre de lecteur qui ne désigne pas la même chose sur chaque ordinateur est un piège courant ; un chemin UNC est le plus sûr.
- Le jeu consulte le dossier environ **une fois par seconde** : un coup met donc à peu près une seconde (parfois deux) pour apparaître sur l'autre écran. Avec un dossier cloud synchronisé, les délais de synchronisation s'y ajoutent.
- **Test en solo sur un ordinateur :** utilisez un simple nom de dossier (`tictactoe_files`) et lancez deux fenêtres Tester le jeu, l'une avec H et l'autre avec J. L'exemple fourni `fichier_1` fonctionne de la même façon et est une version terminée à laquelle les élèves peuvent se comparer.
- Le jeu ne se fige jamais si le dossier est inaccessible : il continue en mode solo (et « Waiting for opponent... » reste simplement affiché).
- L'hôte n'attend le coup de l'autre joueur que jusqu'à la **limite de manche** (30 secondes par défaut) ; ensuite, un joueur absent est ignoré pour cette manche.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : le plateau**

- Tout vit sur un seul objet, `obj_game`. Les neuf cases sont neuf variables simples (`cell_colonne_rangée`), chacune avec un nom fixe, car ce moteur ne permet pas de construire un nom de variable à partir d'autres valeurs.
- Les neuf tests de clic et les neuf tests de dessin ont la même forme ; les tableaux du tutoriel donnent les rectangles. Les élèves font souvent des fautes de frappe dans les nombres. Pensez à faire travailler en binôme ou à donner les tableaux sur papier.
- **Réglez d'abord la couleur de dessin en blanc.** Le tutoriel dessine en noir par défaut et une nouvelle salle est noire : sans *Définir la couleur de dessin*, tout le plateau est invisible (le projet de référence n'affiche rien du tout tant que la couleur n'est pas réglée). Le tutoriel inclut maintenant ce bloc.

**Phase 2 : héberger et rejoindre**

- H héberge et devient X ; J rejoint et devient O. Les deux ordinateurs exécutent le même projet. Si les deux appuient sur H, les deux disent « You are X » et rien ne fonctionne.
- `global.waiting_for_players` reste à 1 tant que l'hôte n'a pas autant de joueurs que le réglage Joueurs maximum (2). Aucun comptage n'est nécessaire.

**Phase 3 : de vrais tours de jeu**

- La manche 1 est celle de X ; les manches impaires sont à X, les paires à O. Le joueur qui n'a *pas* la main doit quand même soumettre quelque chose, pour que le jeu n'attende pas la limite : l'événement Pas envoie un **Terminer le tour** vide une fois par manche (la variable `last_round_acted` l'empêche de se déclencher à chaque image).
- Le gestionnaire de clic écrit la marque avec **Définir une variable partagée** en utilisant le *nom littéral* de la case, puis **Terminer le tour**. La marque n'apparaît sur les deux écrans qu'à la résolution de la manche, environ une seconde plus tard ; les élèves pensent que « ça n'a pas marché » et cliquent de nouveau.
- Les marques sont dessinées à partir de `global.cell_*`. Une variable partagée que personne n'a définie vaut le nombre **0**, pas un texte vide ; les tests de dessin comparent donc avec 0.
- Dans le projet de référence, un clic fait hors tour est ignoré, et les deux ordinateurs affichent toujours le même plateau.

**Phase 4 : gagner et rejouer**

- L'événement **Manche résolue** s'exécute sur les deux ordinateurs après chaque manche confirmée : les deux calculent donc eux-mêmes le gagnant.
- Huit lignes, huit blocs **Si** : rangées, colonnes, deux diagonales. Un nom de case faux dans une ligne signifie que cette ligne ne gagne jamais.
- **Ce que le jeu terminé ne fait pas :** il n'arrête pas la partie après une victoire (l'autre joueur peut encore placer des marques ; le message du gagnant reste), et il n'annonce pas de match nul quand le plateau est plein. Ce sont de bonnes tâches d'approfondissement.
- **Espace** exécute **Quitter la partie**, qui termine proprement la session de cet ordinateur. Pour une revanche propre, les élèves appuient de nouveau sur H et J ; remettre à zéro les cases et `winner` est le « essayez ensuite » du tutoriel.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`10_file_exchange_multiplayer_checkpoints.zip`) : un projet pour la fin de chaque phase, construit exactement comme le décrit le tutoriel. Les projets des phases 2 à 4 utilisent un simple nom de dossier (`tictactoe_files`) ; remplacez-le par votre dossier partagé dans les actions Héberger et Rejoindre avant de les utiliser sur deux ordinateurs.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Héberger / rejoindre | Les deux rôles : l'hôte fait tourner les manches ; les autres joueurs rejoignent |
| Dossier partagé | L'endroit où les coups sont échangés sous forme de petits fichiers |
| Manche | Un tour de jeu, résolu par l'hôte |
| Variable partagée | Une valeur écrite par un joueur et lisible par tous sous la forme `global.nom` |
| Passer | Terminer son tour sans jouer de coup |


## Questions de discussion

- Pourquoi ce jeu utilise-t-il des fichiers plutôt qu'une connexion en direct ? (Pas de problème de pare-feu ni de ports ; fonctionne de façon asynchrone.)
- Quels en sont les inconvénients ? (Plus lent, il faut un dossier partagé.)
- Pourquoi les deux ordinateurs doivent-ils exécuter le même projet ?
- Comment deux joueurs pourraient-ils jouer à des moments différents de la journée avec ce système ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 ; formez des binômes mêlant élèves à l'aise et en difficulté ; fournissez les tableaux de cases sur papier.
- **Approfondissement :** réinitialisation pour la revanche ; détection du match nul ; arrêt du jeu après une victoire ; un score sur plusieurs parties ; un écran-titre à la place des touches H/J.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-B, 3-D, 4-A.

**Partie B :** 1. Héberger une partie (échange de fichiers). 2. Définir une variable partagée (échange de fichiers). 3. Terminer le tour (échange de fichiers). 4. Quitter la partie (échange de fichiers). 5. L'événement Manche résolue.

**Partie C :**

1. Avantage : cela passe à travers les pare-feu et n'exige aucune connexion en direct (les joueurs peuvent même jouer à des moments différents). Inconvénient : un coup met environ une seconde ou plus à apparaître, et les deux ordinateurs ont besoin d'un dossier partagé.
2. La manche 5 est impaire : c'est donc le tour de X. Le jeu teste si `global.round_number` est impair (X) ou pair (O) et le compare à `my_mark`.
3. La marque n'apparaît qu'une fois la manche confirmée par l'hôte et publiée, ce qui prend environ une seconde (davantage sur un lecteur partagé lent).

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Morpion par échange de fichiers

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Le plateau et les marques fonctionnent ; héberger et rejoindre relient deux ordinateurs ; seul le joueur dont c'est le tour peut jouer et les deux écrans concordent ; une victoire s'affiche sur les deux ; les joueurs peuvent quitter et recommencer |
| 3 - Fonctionnel | Deux ordinateurs se connectent et jouent à tour de rôle ; la vérification de victoire ou la revanche manque |
| 2 - À moitié | Le plateau fonctionne et les ordinateurs se connectent, mais les coups n'arrivent pas à l'autre ordinateur |
| 1 - Commencé | Le plateau de la phase 1 fonctionne sur un seul ordinateur |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque binôme s'est connecté au moins une fois (H et J)
- [ ] Les sous-dossiers partagés sont nettoyés ou réutilisables la prochaine fois
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
