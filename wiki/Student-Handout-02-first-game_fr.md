# PyGameMaker — Tutoriel 2 : Ton premier jeu — Attrape l'étoile

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Student-Handout-02-first-game_fr.pdf) · [ODT](downloads/Student-Handout-02-first-game_fr.odt)

---

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Votre premier jeu : Attrape l'étoile** (5 pages, environ 15 à 20 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase avant de continuer. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un petit jeu complet : tu déplaces un vaisseau à gauche et à droite en bas de l'écran, des étoiles tombent du ciel, et chaque étoile attrapée te rapporte 10 points.

## Phase 1 : Un joueur qui se déplace

- [ ] **1.** Crée un nouveau projet nommé `CatchTheStar` (**Fichier > Nouveau projet**).
- [ ] **2.** Crée un sprite `spr_player` (32×32) et dessine un vaisseau, un personnage ou un panier. Enregistre avec **Ctrl+S**.
- [ ] **3.** Crée un objet `obj_player` et donne-lui le sprite `spr_player`.
- [ ] **4.** Crée une salle `room_game` et place `obj_player` près du centre, en bas.
- [ ] **5.** Dans `obj_player`, ouvre l'onglet **Blockly** et ajoute trois événements : **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale à -5*, **Clavier : Flèche droite (maintenue)** avec *Définir la vitesse horizontale à 5*, et **Clavier : Aucune touche** avec *Arrêter le mouvement*.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Les flèches déplacent ton joueur à gauche et à droite, et il s'arrête quand tu relâches. Il peut sortir de l'écran — c'est normal pour l'instant.

## Phase 2 : Des étoiles qui tombent

- [ ] **6.** Crée un sprite `spr_star` (32×32) et un objet `obj_star` qui l'utilise.
- [ ] **7.** Dans `obj_star`, ajoute un événement **Création** avec *Définir la vitesse verticale à 3*.
- [ ] **8.** Crée un objet `obj_spawner` **sans sprite**. Son événement **Création** fait *Définir l'alarme 0 à 60*. Son événement **Alarme 0** fait *Créer une instance de obj_star à x : aléatoire, y : 0*, puis *Définir l'alarme 0 à 60* de nouveau.
- [ ] **9.** Place `obj_spawner` n'importe où dans `room_game`.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Environ une étoile par seconde apparaît en haut, à un endroit différent chaque fois, et tombe. Les étoiles traversent ton joueur — c'est normal pour l'instant.

## Phase 3 : Attraper et marquer

- [ ] **10.** Dans `obj_player`, ajoute **En collision avec obj_star** : *Ajouter au score 10*, puis *Détruire l'autre instance*.
- [ ] **11.** Crée `obj_game_controller` (sans sprite). Son événement **Création** fait *Définir le score à 0* ; son événement **Dessin** fait *Dessiner le score à x : 10, y : 10*.
- [ ] **12.** Dans `obj_star`, ajoute un événement **Hors de la salle** avec *Détruire cette instance*.
- [ ] **13.** Place `obj_game_controller` n'importe où dans la salle.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Attrape une étoile : elle disparaît et le score en haut à gauche augmente de 10. Les étoiles que tu rates disparaissent en bas.

## Phase 4 : Finitions

- [ ] **14.** Dans `obj_player`, ajoute un événement **Pas** qui garde le joueur à l'écran : si x est inférieur à 0, mets x à 0 ; si x est supérieur à la largeur de la salle moins la largeur du sprite, mets x à cette valeur.
- [ ] **15.** Donne à `room_game` une couleur d'arrière-plan que tu aimes.

> **Réussi:** **Tu dois voir :** le joueur s'arrête aux deux bords de la fenêtre, et ton jeu terminé est prêt à être joué.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
|---|---|---|
| Le joueur ne bouge pas | Les événements sont sur le mauvais objet, ou `obj_player` n'est pas dans la salle | Ouvre `obj_player` et vérifie les trois événements Clavier ; ouvre la salle et vérifie que le joueur y est placé |
| Le joueur glisse encore quand je relâche | L'événement **Aucune touche** manque | Ajoute **Clavier : Aucune touche** avec *Arrêter le mouvement* |
| Aucune étoile n'apparaît | `obj_spawner` n'est pas dans la salle, ou son événement Création ne règle pas l'alarme | Place le générateur ; vérifie *Définir l'alarme 0 à 60* dans son événement **Création** |
| Une seule étoile apparaît | L'alarme n'est pas relancée à la fin de **Alarme 0** | Ajoute *Définir l'alarme 0 à 60* comme dernière action de **Alarme 0** |
| Le score ne s'affiche pas | `obj_game_controller` n'est pas dans la salle, ou il n'a pas d'événement Dessin | Place-le ; ajoute *Dessiner le score* dans un événement **Dessin** |
| Le score n'augmente jamais | L'événement Collision est sur le mauvais objet ou n'a pas *Ajouter au score* | Mets **En collision avec obj_star** sur `obj_player` |
| Mon joueur disparaît quand il touche une étoile | J'ai utilisé *Détruire cette instance* au lieu de *Détruire l'autre instance* | Utilise **Détruire l'autre instance** |


## Défis

- **Essaie (5 minutes) :** change la vitesse de chute de l'étoile, ou le nombre de points d'une étoile.
- **Va plus loin :** fais tomber les étoiles plus vite quand le score monte, ou ajoute une seconde sorte d'étoile qui vaut plus de points.
- **Invente :** ajoute un objet « bombe » qui termine le jeu si tu l'attrapes, ou des vies que tu perds quand une étoile atteint le bas.

## Vocabulaire

| Terme | Ce que cela veut dire |
|---|---|
| Événement | Quelque chose qui se passe dans le jeu (une touche est pressée, deux objets se touchent) |
| Action | Ce qu'un objet fait quand un événement se produit |
| Alarme | Un minuteur ; il décompte puis déclenche son événement Alarme |
| Générateur | Un objet invisible qui crée d'autres objets |
| Collision | Quand deux objets se touchent |


## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Que fait une **alarme**, et pourquoi le générateur la relance-t-il à la fin ?
2. Quelle est la différence entre *Détruire cette instance* et *Détruire l'autre instance* dans l'événement de collision ?
3. Quel objet dessine le score, et pourquoi n'est-ce pas le joueur ?

## Mes notes

<br>

<br>

<br>

<br>

<br>

<br>

