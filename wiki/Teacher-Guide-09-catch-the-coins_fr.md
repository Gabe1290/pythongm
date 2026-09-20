# PyGameMaker — Tutoriel 9 : Attrape les pièces — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-09-catch-the-coins_fr.pdf) · [ODT](downloads/Teacher-Guide-09-catch-the-coins_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/09_catch_the_coins_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Attrape les pièces : gagner et perdre**, 5 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 2 (événements, collisions, score). C'est la meilleure première leçon de « jeu complet » : elle a une victoire et une défaite bien nettes.

## Vue d'ensemble

Les élèves construisent un jeu à deux fins en quatre phases : un joueur qui se déplace ; des pièces et un ennemi ; attraper, s'écraser et le score ; et une vérification de victoire. Notions nouvelles : les **transitions de salle** (aller à une salle de victoire ou de Game Over), le **comptage d'instances** (*Si le nombre de obj_coin égale 0*), le **modèle de projet** « Avec écran Game Over », et **Redémarrer le jeu**.

> **Info:** Demandez « comment le jeu sait-il que j'ai gagné ? » La réponse, « il compte les pièces qui restent », est l'idée clé de la leçon.

## Durée suggérée (45 minutes)

Le tutoriel annonce 15 à 20 minutes pour un élève à l'aise ; prévoyez du temps en plus pour le modèle et la salle de victoire.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Montrez le jeu terminé ; demandez comment un jeu décide de « gagner » ou « perdre » |
| Phase 1 : joueur mobile | 5-10 min | Pages 1-2 (créer le projet à partir du modèle) |
| Phase 2 : pièces et ennemi | 10 min | Page 3 |
| Phase 3 : attraper et s'écraser | 10 min | Page 4 |
| Phase 4 : gagner | 10 min | Page 5 |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : joueur mobile**

- Le projet doit être créé avec le modèle **« Avec écran Game Over »** ; il fournit `room_gameover`, que l'événement de crash utilise plus tard. Un projet créé sans lui n'a pas de salle Game Over.
- Trois événements clavier sur le joueur, comme au Tutoriel 2. Le joueur peut sortir de l'écran ; c'est normal.

**Phase 2 : pièces et ennemi**

- Les pièces et l'ennemi tombent tout droit (*Définir la vitesse verticale 3* dans **Création**).
- **Les pièces ratées doivent revenir.** Une pièce qui tombe hors du bas de la salle n'est pas détruite : elle existe toujours, loin sous l'écran, donc le nombre de pièces n'atteint jamais 0 et le jeu devient impossible à gagner (dans le projet de référence, une pièce ratée reste en vie indéfiniment). Le tutoriel donne donc à la pièce et à l'ennemi un événement **Hors de la salle** avec *Définir variable y = 0* : tout ce qui est raté réapparaît en haut. Effet secondaire : l'ennemi revient sans cesse, ce qui maintient la tension.
- Le nombre de pièces placées est le nombre que le joueur doit attraper. Cinq est un bon début.

**Phase 3 : attraper et s'écraser**

- Collision avec une pièce : *Ajouter au score 1* et **Détruire l'autre instance** (la pièce). *Détruire cette instance* supprimerait le joueur.
- Collision avec l'ennemi : *Aller à la salle* `room_gameover`. Le nom de la salle doit correspondre exactement.
- Le score est mis à 0 dans l'événement **Création** du joueur et dessiné par un événement **Dessin** sur le joueur.

**Phase 4 : gagner**

- Un événement **Pas** sur le joueur vérifie *Si le nombre de obj_coin égale 0*, puis va à `room_win`. Il s'exécute à chaque image : dès que la dernière pièce est attrapée, la salle de victoire apparaît.
- **S'il n'y a aucune pièce dans la salle, le nombre vaut 0 immédiatement** et le jeu affiche YOU WIN! dès la première image. C'est l'erreur classique de la « victoire instantanée ».
- `obj_win_text` dessine le message à des coordonnées fixes dans une salle de taille par défaut (1024×768), et redémarre le jeu sur ESPACE. La salle Game Over du modèle redémarre de la même façon.
- Le texte de la salle de victoire est dessiné dans la couleur par défaut (noir), lisible sur l'arrière-plan vif suggéré par le tutoriel. Sur un fond sombre, utilisez *Définir la couleur de dessin* en blanc.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`09_catch_the_coins_checkpoints.zip`) : un projet pour la fin de chaque phase. Dans le projet de référence, `room_gameover` est une petite salle faite à la main, pas celle du modèle. Donnez à un élève bloqué la phase précédente.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| État de victoire / de défaite | Les deux fins possibles du jeu |
| Transition de salle | Passer à une autre salle avec *Aller à la salle* |
| Nombre d'instances | Le nombre de copies d'un objet qui existent, testé avec *Si le nombre de* |
| Modèle | Un projet prêt à l'emploi pour commencer |
| Événement Pas | S'exécute à chaque image ; utilisé ici pour vérifier la victoire |


## Questions de discussion

- Comment le jeu sait-il que le joueur a gagné ?
- Que se passerait-il si une pièce restait en vie sous le bas de l'écran ?
- Comment rendre la victoire plus difficile ? (Plus de pièces, chute plus rapide, plus d'ennemis.)
- Quels autres jeux ont pour but « tout ramasser » ?

## Différenciation

- **Soutien :** donnez le projet de la phase 2 ; utilisez moins de pièces.
- **Approfondissement :** des vies ; un chronomètre ; un second ennemi ; des pièces de valeurs différentes ; une salle « niveau suivant » au lieu de la salle de victoire.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-B, 4-A.

**Partie B :** 1. `obj_player`, En collision avec `obj_coin`. 2. `obj_player`, En collision avec `obj_enemy`. 3. `obj_player`, Pas. 4. `obj_coin` (et `obj_enemy`), Hors de la salle. 5. `obj_win_text` (et l'objet de la salle Game Over), Touche pressée : espace.

**Partie C :**

1. Le nombre vaut déjà 0, donc le jeu passe à la salle de victoire dès le premier pas (une victoire instantanée).
2. Non. La pièce ratée existe toujours hors de l'écran, donc le nombre n'atteint jamais 0. C'est pourquoi les pièces ratées sont renvoyées en haut.
3. Changer *Ajouter au score 1* dans l'événement **En collision avec obj_coin** du joueur en 5 (ou utiliser un second objet pièce avec sa propre valeur).

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Attrape les pièces

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Le joueur bouge ; pièces et ennemi tombent et reviennent quand ils sont ratés ; attraper rapporte des points et supprime la pièce ; l'ennemi mène au Game Over ; le score est affiché ; attraper toutes les pièces mène à une salle de victoire ; ESPACE recommence |
| 3 - Fonctionnel | Déplacement, capture et crash fonctionnent ; la vérification de victoire ou l'affichage du score manque |
| 2 - À moitié | Le joueur bouge et les pièces tombent, mais la capture ou le crash ne fonctionne pas |
| 1 - Commencé | Le joueur existe et bouge ; rien ne tombe |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 3 (une pièce peut être attrapée et l'ennemi termine la partie)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
