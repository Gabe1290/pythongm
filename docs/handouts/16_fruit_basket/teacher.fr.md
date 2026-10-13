# PyGameMaker — Tutoriel 16 : Panier de fruits — Guide de l'enseignant·e

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Panier de Fruits : Attrape et Évite !**, 6 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Aucun tutoriel précédent n'est nécessaire &mdash; c'est le bon premier projet pour un·e élève qui n'est pas encore prêt·e pour la variable « se souvenir de ce qu'on tient » du Tutoriel 15. Chaque action de ce jeu est un bloc unique et déjà prêt ; rien n'est créé, nommé, ou relu par l'élève.

## Vue d'ensemble

Les élèves construisent un jeu complet de ramassage et d'évitement sans jamais toucher à l'idée de variable. Un panier se déplace le long du bas de la salle ; les fruits et les bombes sont placés une fois pour toutes et ne bougent ni ne réapparaissent jamais, donc il n'y a rien à recycler ni à se souvenir d'une image à l'autre. Quatre phases : un panier mobile ; placer les fruits et les bombes sans aucun comportement encore ; relier les collisions (ramasser un fruit rapporte des points, toucher une bombe redémarre la salle) ; et une vérification de victoire une fois tous les fruits disparus.

> INFO: Si un·e élève demande « comment le jeu sait-il que j'ai ramassé tous les fruits », la réponse honnête est : il compte, à chaque image, combien d'instances de `obj_fruit` existent encore dans la salle &mdash; le bloc **Si le nombre de**. Rien n'est stocké ou mémorisé exprès ; le nombre est juste relu à chaque fois.

## Durée suggérée (30 à 35 minutes)

Le tutoriel annonce 10 à 15 minutes pour un·e élève à l'aise ; prévoyez du temps en plus pour le tout premier événement de collision et le tout premier redémarrage de salle, car ce sont de nouvelles idées même si aucune des deux n'a besoin de variable.

| Séquence | Durée | Ce qui se passe |
| Rappel et hypothèses | 5 min | Montrez le jeu terminé ; demandez ce qui se passe si on touche une bombe |
| Phase 1 : panier mobile | 5 min | Page 2 |
| Phase 2 : fruits et bombes | 5 min | Page 3 (placement seulement, aucun comportement encore) |
| Phase 3 : ramasser et éviter | 10 min | Page 4 (deux nouveaux événements de collision) |
| Phase 4 : gagner | 5-10 min | Page 5 |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : panier mobile**

- Trois événements clavier, exactement comme au Tutoriel 2 / Tutoriel 9 / Tutoriel 15. Le panier peut sortir de l'écran ; c'est normal et pas corrigé dans ce tutoriel.

**Phase 2 : fruits et bombes**

- L'erreur de placement la plus courante : un fruit placé trop près de l'endroit où démarre le panier, de sorte que le panier le « ramasse » juste en existant, avant même que l'élève appuie sur une touche. Faites vérifier la boîte de départ du panier par rapport à la position de chaque fruit si cela arrive.
- Rien ne tombe ni ne bouge ici &mdash; un·e élève venant du Tutoriel 9 ou du Tutoriel 15 peut s'attendre à un événement **Création** qui définit une vitesse de chute. Il n'y en a pas ; c'est le but.

**Phase 3 : ramasser et éviter**

- Le gestionnaire de collision de `obj_fruit` vit sur `obj_player`, pas sur le fruit lui-même &mdash; le même schéma **Détruire l'autre instance** que tous les autres tutoriels de ramassage (Tutoriel 2, 9, 15). Un·e élève qui écrit *Détruire cette instance* détruit le panier à la place.
- **Redémarrer la salle** est un nouveau vocabulaire introduit par ce tutoriel. Ce n'est volontairement PAS une punition avec des vies ou un écran de fin de partie &mdash; assurez-vous que les élèves remarquent que cela remet simplement la salle actuelle à zéro, fruits compris, donc toucher une bombe coûte un peu de temps, pas la partie.
- Un·e élève qui oublie l'événement **Dessin** aura quand même un jeu qui fonctionne &mdash; seul le score n'est pas visible. C'est facile à remarquer et à corriger sans tout réexpliquer.

**Phase 4 : gagner**

- La vérification de victoire est un événement **Pas** sur `obj_player`, exactement le schéma du Tutoriel 9 (*Si le nombre de obj_coin* devient *Si le nombre de obj_fruit*) &mdash; un·e élève ayant fait le Tutoriel 9 le reconnaîtra immédiatement.
- Si un·e élève a placé zéro fruit à la Phase 2 (rare, mais ça arrive), la salle de victoire apparaît dès le début de la partie. C'est un bon moment pour rappeler que le nombre est vraiment vérifié à chaque image, pas stocké.

> TIP: **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`16_fruit_basket_checkpoints.zip`) : un projet pour la fin de chaque phase. Donnez à un·e élève bloqué·e la phase précédente plutôt que de dépanner ses collisions à partir de rien.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| Collision | Un événement qui se déclenche au moment où deux objets se touchent |
| Nombre d'instances | Combien de copies d'un objet existent en ce moment |
| Redémarrer la salle | Une action qui remet la salle actuelle exactement comme au début |
| Événement Pas | S'exécute à chaque image ; utilisé ici pour vérifier la victoire |

## Questions de discussion

- Pourquoi `obj_fruit` n'a-t-il besoin d'aucun événement, alors que `obj_coin` du Tutoriel 9 avait besoin d'un événement Création et d'un événement Hors de la salle ?
- Quelle est la différence entre **Redémarrer la salle** et **Redémarrer le jeu** ? Quand voudrait-on l'un plutôt que l'autre ?
- Pourquoi la vérification de victoire de la Phase 4 peut-elle « simplement compter » au lieu d'avoir besoin de se souvenir de quoi que ce soit d'une image précédente ?
- Quels autres jeux laissent « juste réessayer » au lieu de punir une erreur avec un écran de fin de partie ?

## Différenciation

- **Soutien :** donnez le projet de la phase 2, pour qu'un·e élève en difficulté n'ait qu'à relier les deux événements de collision des phases 3 et 4.
- **Approfondissement :** un second type de fruit qui vaut plus de points ; un chronomètre qui montre la vitesse à laquelle la salle a été vidée ; un panier qui peut aussi se déplacer vers le haut et le bas pour atteindre une deuxième rangée de fruits.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-B, 3-A, 4-D.

**Partie B :** 1. `obj_player`, En collision avec `obj_fruit`. 2. `obj_player`, En collision avec `obj_bomb`. 3. `obj_player`, Pas. 4. `obj_win_text`, Dessin. 5. `obj_win_text`, Touche pressée : espace.

**Partie C :**

1. `obj_fruit` ne bouge jamais et ne change jamais &mdash; il reste simplement dans la salle en attendant d'être touché. Tout le *comportement* (« que se passe-t-il quand on me touche ») vit sur les événements de collision de `obj_player` à la place, de la même façon que `obj_coin` au Tutoriel 9 n'avait besoin que d'une vitesse de chute, et `obj_fruit` ici n'a besoin de rien du tout, puisqu'il ne tombe même pas.
2. Le jeu vérifierait combien de bombes restent au lieu de combien de fruits restent &mdash; comme les bombes ne sont jamais détruites par quoi que ce soit dans ce jeu, ce nombre n'atteindrait jamais zéro, donc la salle de victoire n'apparaîtrait jamais.
3. Si une bombe était proche d'un fruit, un·e élève visant le fruit pourrait toucher la bombe par accident en se positionnant pour le ramassage, transformant « tout ramasser » en un défi d'évitement précis au lieu du jeu « se diriger vers ce qu'on veut » prévu.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Panier de fruits

| Niveau | Ce que montre le jeu |
| 4 - Complet | Le panier se déplace ; les fruits et les bombes sont placés dans la salle ; ramasser un fruit ajoute 10 au score et le supprime ; toucher une bombe redémarre la salle ; ramasser tous les fruits affiche YOU WIN! et ESPACE redémarre |
| 3 - Fonctionnel | Le déplacement et le ramassage des fruits fonctionnent ; le redémarrage par bombe ou l'écran de victoire est manquant ou incorrect |
| 2 - À moitié | Le panier se déplace et les fruits/bombes sont placés, mais ramasser ou éviter ne fonctionne pas correctement |
| 1 - Commencé | Le panier existe et se déplace ; rien d'autre n'est encore placé |

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la Phase 3 (ramasser un fruit fonctionne de bout en bout)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
