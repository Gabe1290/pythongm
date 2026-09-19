# PyGameMaker — Tutoriel 3 : Pong classique — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-03-pong_fr.pdf) · [ODT](downloads/Teacher-Guide-03-pong_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/03_pong_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Pong classique : Jeu à deux joueurs**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 2 (événements, actions, collisions, score, dessin).

## Vue d'ensemble

Les élèves construisent Pong en trois phases : raquettes et balle qui rebondit, buts invisibles, et affichage du score. Notions nouvelles : **deux joueurs sur un même clavier**, **objets solides et rebonds**, **variables globales** (`global.p1score`) et affichage de la valeur d'une variable.

> **Info:** Pong est un bon moment pour parler de *règles*. Chaque règle est un événement plus des actions sur un objet : « quand la balle touche le but gauche, ajouter 1 au score du joueur 2 et remettre la balle en place ».

## Durée suggérée (45 à 60 minutes)

Le tutoriel annonce 20 à 25 minutes pour un élève à l'aise ; en classe, prévoyez plus.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Demandez : « De quels objets Pong a-t-il besoin ? » Laissez les élèves les lister avant de commencer |
| Phase 1 : raquettes et balle | 15-20 min | Pages 1-2 ; la phase la plus longue, beaucoup d'objets |
| Phase 2 : buts et score | 10 min | Page 3 |
| Phase 3 : affichage du score | 5-10 min | Page 4 |
| Jouer et échanger | 5 min | Les binômes jouent l'un contre l'autre, puis changent d'ordinateur |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


Pour une séance de 45 minutes, faites les phases 1 et 2 en classe, la phase 3 en devoir.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : raquettes et balle**

- Les élèves créent six objets ici. Proposez une liste au tableau : mur, deux raquettes, balle, puis plus tard deux buts et un objet de score.
- **Solide** est important. Les murs et les raquettes doivent être Solides pour que *Rebondir contre les objets solides* ait quelque chose sur quoi rebondir. La balle n'est *pas* Solide.
- Chaque raquette a besoin de son propre événement **En collision avec obj_wall** avec *Arrêter le mouvement*. Sans lui, un mur solide n'arrête pas une raquette qui n'a pas d'événement de collision avec lui.
- La balle a besoin d'un événement de rebond **pour chaque objet** sur lequel elle doit rebondir (mur, raquette gauche, raquette droite). Les élèves n'ajoutent souvent que le mur.
- Dans cette phase, la balle sort de l'écran sur les côtés ; c'est **normal**.
- Si la balle ne va que sur le côté : le champ direction de *Commencer à se déplacer dans la direction* doit valoir 45 (vers le haut et la droite ; 0 est la droite et 90 le haut).

**Phase 2 : buts et score**

- Les buts sont **invisibles** mais **Solides** : invisibles pour que les joueurs ne les voient pas, présents pour que l'événement de collision de la balle se déclenche.
- Les variables de score sont **globales** : `global.p1score`, `global.p2score`. Une faute de frappe à un endroit (par exemple `global.p1Score`) crée une seconde variable différente, et le score semble bloqué à 0.
- Le but gauche fait marquer le **joueur 2**, le but droit le **joueur 1** (le joueur qui n'a pas raté).
- Après un but, la balle revient à sa position de départ mais garde sa direction, et se dirige donc à nouveau vers le même but. C'est normal ; cela fait un bon défi (« inverser la direction de la balle après chaque but »).

**Phase 3 : affichage du score**

- `obj_score` n'a pas de sprite et doit être placé dans la salle, comme le contrôleur du Tutoriel 2.
- Le texte dessiné est **noir par défaut** et l'arrière-plan d'une nouvelle salle est noir : sans *Définir la couleur de dessin*, le score est invisible. La page du tutoriel inclut ce bloc. Le texte est placé à y 40 et 60, sous la rangée de murs de 32 pixels, pour ne pas chevaucher le mur du haut.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`03_pong_checkpoints.zip`) : un projet pour la fin de chaque phase. Donnez à un élève bloqué la phase précédente pour qu'il continue.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Solide | Objets qui bloquent ou font rebondir les autres (murs, raquettes) |
| Rebond | Une action qui inverse la direction du mouvement après une collision |
| Variable globale | Une valeur nommée partagée par tous les objets ; toujours écrite avec `global.` |
| Événement Dessin | S'exécute à chaque image ; sert à afficher texte et nombres |
| Position de départ | L'endroit où un objet a été placé dans la salle |


## Questions de discussion

- De quels objets Pong a-t-il besoin, et lesquels sont invisibles ?
- Pourquoi garde-t-on le score dans une variable globale ?
- Que se passerait-il si les buts n'étaient pas Solides ?
- Le jeu est-il équitable ? (La balle garde sa direction après un but.) Comment corriger cela ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 et commencez à la phase 2 ; formez des binômes mêlant élèves à l'aise et en difficulté.
- **Approfondissement :** accélérer la balle à chaque contact avec une raquette ; terminer la partie à 10 points ; changer l'angle de rebond selon l'endroit où la balle touche la raquette.

## Corrigé de la feuille d'exercices

**Partie A :** 1-D, 2-C, 3-A, 4-B.

**Partie B :** 1. `obj_paddle_left`. 2. `obj_ball`. 3. La balle (son événement de collision avec un but ajoute au score). 4. `obj_score`. 5. L'événement En collision avec `obj_wall` de la raquette.

**Partie C :**

1. Un événement de collision appartient à un autre objet précis ; le jeu n'exécute le rebond que pour les objets qui ont un événement.
2. Le but gauche est derrière la raquette du joueur 1 ; quand la balle y arrive, le joueur 1 a raté, donc le joueur 2 marque.
3. Le score doit survivre à la remise en place de la balle, et plusieurs objets l'utilisent (la balle l'augmente, l'objet de score l'affiche) ; il vit donc dans une variable globale partagée.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Pong

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Les deux raquettes bougent et sont retenues par les murs ; la balle rebondit sur les murs et les raquettes ; les buts font marquer le bon joueur et remettent la balle en place ; les deux scores sont affichés |
| 3 - Fonctionnel | Raquettes, balle et score fonctionnent ; l'affichage du score ou un rebond manque |
| 2 - À moitié | Les raquettes bougent et la balle rebondit, mais les buts ne font pas marquer |
| 1 - Commencé | Certains objets existent, mais la balle ne rebondit pas ou une raquette ne bouge pas |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque binôme a joué au moins un point
- [ ] Notez qui aura besoin du projet de la phase 1 la prochaine fois
