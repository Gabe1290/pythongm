# PyGameMaker — Tutoriel 15 : Fusion de Fruits — Feuille d'exercices

Nom : ______________________________   Date : ______________

Fais cette feuille après avoir gagné et perdu... en fait, tu ne peux pas perdre ! Fais-la après avoir gagné la partie au moins une fois.

## Partie A : Les mots

Associe chaque mot à sa signification. Écris la lettre à côté du numéro.

1. Fusion ____
2. Fruit tenu ____
3. Si / Sinon ____
4. Générateur ____

- **A.** Un bloc qui fait une chose quand quelque chose est vrai, et une autre chose sinon
- **B.** Un objet invisible dont le seul rôle est de créer d'autres objets selon une minuterie
- **C.** Attraper un fruit qui correspond pour qu'il devienne le fruit suivant, plus gros
- **D.** Le fruit que le panier porte actuellement, dont on se souvient dans `held_level`

## Partie B : Quel objet et quel événement ?

Écris l'objet et l'événement pour chaque règle.

1. Devenir une fraise quand une cerise correspondante est attrapée : ______________________
2. Créer une nouvelle cerise toutes les 90 pas : ______________________
3. Retirer un fruit qui tombe sans avoir été attrapé par le panier : ______________________
4. Afficher le message VOUS AVEZ GAGNÉ ! : ______________________
5. Redémarrer le jeu quand ESPACE est pressé sur l'écran de victoire : ______________________

## Partie C : Réfléchis

1. `held_level` commence à 1 (une cerise). Pourquoi attraper une cerise alors que `held_level` est déjà à 3 (une orange) ne donne que 1 point au lieu de fusionner ?

[[notes:3]]

2. Que se passerait-il si l'action *Aller à la salle room_win* de la collision avec l'orange était placée par erreur dans la branche *Sinon* au lieu de la branche *Si* ?

[[notes:3]]

3. Pourquoi chaque type de fruit a-t-il besoin de son propre générateur, plutôt qu'un seul générateur qui choisirait un type de fruit au hasard ?

[[notes:3]]

## Partie D : Essaie-le

- [ ] Le panier se déplace et s'arrête
- [ ] Attraper une cerise correspondante transforme le panier en fraise et ajoute 10 points
- [ ] Attraper une fraise correspondante transforme le panier en orange et ajoute 20 points
- [ ] Attraper une orange correspondante transforme le panier en pastèque, ajoute 50 points, et affiche VOUS AVEZ GAGNÉ !
- [ ] Une capture qui ne correspond pas ajoute seulement 1 point et ne change rien d'autre

## Partie E : Regarde en arrière

1. Ce dont je suis le plus fier ou la plus fière : ______________________________________
2. Un bug que j'ai trouvé et corrigé : ______________________________________
3. Ce que j'ajouterais ensuite : ______________________________________
