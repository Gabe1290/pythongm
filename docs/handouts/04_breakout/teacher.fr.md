# PyGameMaker — Tutoriel 4 : Casse-briques — Guide de l'enseignant·e

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Breakout : Casse-Briques**, 7 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé les Tutoriels 2 et 3 (événements, collisions, score, dessin, objets solides).

## Vue d'ensemble

Les élèves construisent le casse-briques en quatre phases, en testant après chacune : une balle qui rebondit, une rangée de briques, quatre rangées, et un contrôleur de jeu avec des vies. Notions nouvelles : les **objets parent et enfant** (une seule règle de collision pour plusieurs types de briques), une **zone de mort** au lieu d'un mur du bas, les **vies**, et un **Game Over avec tableau des meilleurs scores**.

> INFO: L'idée clé est l'héritage : « une brique rouge *est une* brique, elle reçoit donc tout ce que reçoit une brique ». Demandez aux élèves de prévoir ce qui se passe quand le parent n'est pas réglé sur la nouvelle couleur.

## Durée suggérée (60 à 90 minutes)

Le tutoriel annonce 25 à 30 minutes pour un élève à l'aise. Il compte sept pages et beaucoup d'objets : prévoyez une double période ou deux séances.

| Séquence | Durée | Ce qui se passe |
| Rappel et hypothèses | 5 min | Montrez le jeu terminé ; demandez « de quels objets a-t-on besoin ? » |
| Sprites (page 2) | 10 min | Laissez les élèves importer les images d'exemple de `Tutorials/04_breakout/assets/` pour gagner du temps |
| Raquette, balle et salle (pages 3-4) | 20 min | Phase 1 ; tout le monde joue avec une balle qui rebondit |
| Briques (pages 5-6) | 20 min | Phases 2-3 ; l'objet parent |
| Contrôleur, vies, Game Over (page 7) | 15 min | Phase 4 |
| Feuille d'exercices / ticket de sortie | 5-10 min | Parties A à C |

Pour une séance de 45 minutes, faites les sprites et la phase 1 lors de la première séance, le reste lors d'une seconde.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : balle qui rebondit**

- Deux objets mur (côté et haut) existent pour que la balle inverse la bonne direction : le mur latéral inverse l'horizontale, le mur du haut et la raquette inversent la verticale.
- **Solide** est nécessaire pour les murs et la raquette ; la balle n'est *pas* Solide. Chaque rebond est un événement de collision séparé sur la balle.
- La raquette a besoin de son propre événement **En collision avec obj_wall_side** avec *Arrêter le mouvement* ; sinon elle traverse les murs latéraux.
- **Il n'y a pas de mur en bas, exprès.** La zone de mort invisible en bas attrape la balle et la renvoie en (320, 100). Les élèves placent souvent un mur en bas ; demandez « comment la balle pourrait-elle alors être perdue ? ».
- La balle rebondit indéfiniment entre les murs et la raquette ; c'est **normal**. La raquette sert seulement à empêcher la balle de tomber.

**Phases 2-3 : briques et objet parent**

- `obj_brick_parent` n'a pas de sprite et est Solide. Chaque couleur a besoin de **Parent = obj_brick_parent** et de **Solide**. Oublier le parent sur une nouvelle couleur est l'erreur classique : cette couleur devient un mur qui ne casse jamais.
- L'événement de brique de la balle est uniquement sur `obj_brick_parent`. Montrez qu'ajouter une cinquième couleur ne demande **aucun** changement à la balle.
- Chaque brique rapporte 10 points quelle que soit sa couleur (le tutoriel laisse les scores différents en défi).
- Utilisez **Aligner sur la grille** (32×16) pour placer les briques, sinon les rangées sont irrégulières.

**Phase 4 : contrôleur de jeu**

- Le contrôleur doit être **placé dans la salle**, comme celui du Tutoriel 2.
- Les vies sont réglées dans l'événement **Création** du contrôleur ; la balle retire une vie dans son événement de zone de mort (*Ajouter aux vies -1* avant le saut).
- **Plus de vies** est un événement qui se déclenche automatiquement quand les vies atteignent zéro. Le tutoriel demande *Afficher un message*, *Afficher le tableau des meilleurs scores*, *Terminer le jeu* dans cet ordre et prévient que l'ordre compte. Sur le lecteur de bureau, le tableau s'affiche dans les deux cas, mais gardez l'ordre du tutoriel : c'est le plus sûr.
- Le score et les vies sont dessinés en blanc à y 10, sur la rangée de murs gris du haut ; ils restent lisibles.

> TIP: **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`04_breakout_checkpoints.zip`) : un projet pour la fin de chaque phase. Donnez à un élève bloqué la phase précédente pour qu'il continue.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| Objet parent | Un modèle ; les enfants héritent de ses événements |
| Objet enfant | Un objet dont le champ Parent nomme un autre objet |
| Zone de mort | Un objet invisible en bas qui attrape la balle |
| Vies | Un compteur du nombre de fois où la balle peut être perdue |
| Tableau des meilleurs scores | Une liste enregistrée des meilleurs résultats |

## Questions de discussion

- Pourquoi écrire un seul événement de collision pour le parent plutôt qu'un par couleur ?
- Pourquoi la balle inverse-t-elle le mouvement *vertical* sur une brique ?
- Que pourrait-on changer pour rendre le jeu plus difficile ou plus équitable ? (Vitesse, taille de la raquette, angle de rebond.)
- Quelles parties du jeu sont des événements, et lesquelles sont des actions ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 et commencez aux briques ; importez les sprites d'exemple au lieu de les dessiner.
- **Approfondissement :** points différents par couleur ; balle qui accélère ; un second niveau avec une autre disposition ; un son à la fin.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-A, 3-B, 4-D.

**Partie B :** 1. Inverser le mouvement horizontal. 2. Détruire l'autre instance. 3. Ajouter aux vies -1 (définir les vies, relatif -1). 4. Afficher un message. 5. Terminer le jeu.

**Partie C :**

1. Régler son **Parent** sur `obj_brick_parent` (et Solide). Non, l'événement de la balle pour le parent la couvre déjà.
2. Vers le haut et vers la droite. À l'écran, y augmente vers le bas ; une vitesse verticale négative signifie donc vers le haut.
3. Afficher le tableau des meilleurs scores doit venir avant Terminer le jeu, car le tutoriel indique que terminer d'abord le jeu peut empêcher le tableau de s'afficher. (Sur le lecteur de bureau, les deux ordres fonctionnent ; l'ordre sûr reste préférable.)

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Casse-briques

| Niveau | Ce que montre le jeu |
| 4 - Complet | Raquette et balle fonctionnent ; les briques de toutes les couleurs se cassent par un seul événement parent et donnent des points ; vies et score sont affichés ; Game Over, meilleurs scores et fin fonctionnent |
| 3 - Fonctionnel | Raquette, balle et briques fonctionnent ; les vies ou le Game Over manquent |
| 2 - À moitié | Raquette et balle fonctionnent ; les briques ne cassent pas, ou une seule couleur casse |
| 1 - Commencé | Les objets existent, mais la balle ne rebondit pas ou la raquette ne bouge pas |

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 2 (une brique peut être cassée)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
