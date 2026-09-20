# PyGameMaker — Tutoriel 6 : Labyrinthe — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-06-maze_fr.pdf) · [ODT](downloads/Teacher-Guide-06-maze_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/06_maze_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Labyrinthe : Trouvez la Sortie**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 2 (événements, actions, collisions, score).

## Vue d'ensemble

Les élèves construisent un jeu de labyrinthe en trois phases : un joueur et des murs, des pièces et une sortie, et un affichage du score. Notions nouvelles : le **mouvement fluide avec des touches maintenues**, les **murs solides**, les **objets à ramasser**, une **sortie qui recommence la salle**, et la **conception de niveau**.

> **Info:** Le plan du labyrinthe est la partie créative. Demandez aux élèves de le dessiner d'abord sur papier quadrillé (le tutoriel propose un exemple de 20×15) et de vérifier qu'il peut être résolu avant de le construire.

## Durée suggérée (45 à 60 minutes)

Le tutoriel annonce 20 à 25 minutes pour un élève à l'aise ; la construction du labyrinthe est ce qui prend le plus de temps.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Montrez un labyrinthe terminé ; demandez de quels objets il a besoin |
| Phase 1 : joueur et labyrinthe | 15-20 min | Pages 1-2 ; la majeure partie du temps sert à placer les murs |
| Phase 2 : pièces et sortie | 10-15 min | Page 3 |
| Phase 3 : affichage du score | 5-10 min | Page 4 |
| Échange et jeu | 5 min | Les élèves jouent les labyrinthes des autres |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


Pour une séance de 45 minutes, donnez le plan des murs sur papier, ou faites importer les sprites d'exemple, pour gagner du temps.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : joueur et labyrinthe**

- Cinq événements sur le joueur : quatre flèches maintenues plus **Aucune touche** avec *Arrêter le mouvement*. Sans **Aucune touche**, le joueur ne s'arrête jamais.
- `obj_wall` **doit être Solide** et le joueur a besoin de **En collision avec obj_wall** avec *Arrêter le mouvement*. Les deux sont nécessaires.
- **Tout placer sur la grille.** Activez **Aligner sur la grille** 32×32. Le joueur avance de 4 pixels par pas ; si le joueur ou un mur est ne serait-ce que de quelques pixels hors de la grille, le joueur se coince à l'entrée des couloirs d'une case (un joueur placé 8 pixels à côté ne peut pas du tout descendre un couloir). « Coincé dans les couloirs » signifie presque toujours un placement hors grille ; supprimez et replacez avec l'alignement.
- Chaque couloir doit faire au moins une case de large, et le labyrinthe doit être résoluble. Le labyrinthe d'exemple du tutoriel fait 20×15 et est résoluble ; le projet de référence l'utilise.

**Phase 2 : pièces et sortie**

- Les pièces et la sortie ne sont **pas Solides** ; elles ne réagissent qu'à la collision avec le joueur. La pièce utilise *Détruire cette instance* (la pièce). *Détruire l'autre instance* supprimerait le joueur.
- *Afficher un message* met le jeu en pause jusqu'au clic sur OK ; les élèves croient parfois que le jeu s'est figé.
- La sortie utilise *Recommencer la salle* : les pièces reviennent. Pour plusieurs niveaux, utilisez plutôt **Aller à la salle suivante**.
- Mettez la sortie loin du départ (dans le labyrinthe de référence, c'est la case accessible la plus éloignée).

**Phase 3 : affichage du score**

- Le contrôleur doit être placé dans la salle. Son événement **Création** met le score à 0 ; comme la sortie recommence la salle, le score se remet à zéro automatiquement.
- Le score est dessiné en blanc en haut à gauche, sur la rangée de murs du bord, et reste lisible.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`06_maze_checkpoints.zip`) : un projet pour la fin de chaque phase, avec le labyrinthe d'exemple du tutoriel plus cinq pièces et une sortie. Donnez à un élève bloqué la phase précédente.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Touche maintenue | Un événement actif tant que la touche est enfoncée |
| Solide | Objets qui bloquent les autres (les murs) |
| Objet à ramasser | Un objet détruit quand le joueur le touche |
| Recommencer la salle | Relancer le niveau depuis le début |
| Aligner sur la grille | Option de l'éditeur qui aligne les objets sur une grille |


## Questions de discussion

- Pourquoi tous les objets doivent-ils être sur la grille dans ce jeu ?
- Qu'est-ce qui rend un labyrinthe injuste ? (Pièces inaccessibles, aucun chemin vers la sortie.)
- Comment le score revient-il à 0 après la victoire ?
- Qu'ajouteriez-vous pour rendre le jeu plus difficile ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 et laissez les élèves construire leur labyrinthe par-dessus ; importez les sprites d'exemple.
- **Approfondissement :** plus de niveaux avec **Aller à la salle suivante** ; un compte à rebours ; des ennemis qui patrouillent ; des clés et des portes.

## Corrigé de la feuille d'exercices

**Partie A :** 1-D, 2-B, 3-A, 4-C.

**Partie B :** 1. `obj_player`. 2. `obj_coin`. 3. `obj_exit`. 4. `obj_game_controller`. 5. `obj_wall` (parce qu'il est Solide).

**Partie C :**

1. 32 ÷ 4 = 8 pas.
2. La salle recommence, donc toutes les pièces reviennent, et le score revient à 0 parce que l'événement Création du contrôleur s'exécute de nouveau et le remet à zéro.
3. Si le joueur et les murs ont été placés sur la grille (Aligner sur la grille 32×32).

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Labyrinthe

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Le joueur bouge et s'arrête correctement ; les murs bloquent ; les pièces donnent des points et disparaissent ; la sortie affiche un message et recommence ; le score est affiché ; le labyrinthe est résoluble et toutes les pièces sont accessibles |
| 3 - Fonctionnel | Mouvement, murs, pièces et sortie fonctionnent ; l'affichage du score manque, ou un petit défaut de conception |
| 2 - À moitié | Le joueur bouge et les murs bloquent, mais les pièces ou la sortie ne fonctionnent pas |
| 1 - Commencé | Joueur et murs existent ; le joueur traverse les murs ou ne peut pas bouger |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 2 (une pièce peut être ramassée)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
