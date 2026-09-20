# PyGameMaker — Tutoriel 5 : Sokoban

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Student-Handout-05-sokoban_fr.pdf) · [ODT](downloads/Student-Handout-05-sokoban_fr.odt)

---

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Sokoban : Puzzle Pousse-Caisses** (4 pages, environ 20 à 25 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un puzzle classique : tu te déplaces sur une grille, une case à la fois, et tu pousses des caisses sur des cibles. Une caisse devient verte quand elle est sur une cible, et tu peux appuyer sur **R** pour recommencer le niveau.

## Phase 1 : Joueur et murs

- [ ] **1.** Crée deux sprites (32×32) : `spr_player` et `spr_wall`.
- [ ] **2.** Crée `obj_wall` (sprite `spr_wall`, **Solide**) et `obj_player` (sprite `spr_player`).
- [ ] **3.** Dans `obj_player`, ajoute quatre événements **Touche pressée** (flèches droite, gauche, haut, bas). Chacun fait *Déplacer grille* dans sa direction avec une taille de **32**.
- [ ] **4.** Ajoute **En collision avec obj_wall** avec *Arrêter le mouvement*.
- [ ] **5.** Crée `room_sokoban` (320×320, une grille de 10×10), active l'accrochage à la grille 32×32, place des murs sur le bord et quelques-uns à l'intérieur, et place le joueur.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Chaque appui sur une touche te déplace d'exactement une case. Les murs t'arrêtent.

## Phase 2 : Pousser des caisses

- [ ] **6.** Crée un sprite `spr_crate` et un objet `obj_crate` (sprite `spr_crate`, **Solide**).
- [ ] **7.** Dans `obj_player`, ajoute **En collision avec obj_crate** : *Si peut pousser (facing)* puis *Pousser l'autre instance 32*.
- [ ] **8.** Dans `obj_crate`, ajoute **En collision avec obj_wall** avec *Arrêter le mouvement*.
- [ ] **9.** Place 2 ou 3 caisses dans la salle, chacune avec de la place pour bouger (pas dans un coin !).

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Avance vers une caisse et elle bouge d'une case. Elle ne bouge pas s'il y a un mur ou une autre caisse derrière.

## Phase 3 : Cibles et contrôleur

- [ ] **10.** Crée les sprites `spr_target` et `spr_crate_ok` (une caisse verte).
- [ ] **11.** Crée `obj_target` (sprite `spr_target`) — **pas Solide**, pour que les caisses et le joueur puissent passer dessus.
- [ ] **12.** Dans `obj_crate`, ajoute un événement **Pas** : *Si en collision avec obj_target*, *Définir le sprite à spr_crate_ok* ; *Sinon*, *Définir le sprite à spr_crate*.
- [ ] **13.** Crée `obj_controller` (sans sprite). Événement **Dessin** : *Dessiner du texte* « Poussez les caisses sur les cibles ! » à x 10, y 10. **Touche pressée R** : *Recommencer la salle*.
- [ ] **14.** Dans la salle, place d'abord les cibles, puis **supprime le joueur et les caisses et replace-les**. Place `obj_controller` n'importe où. Le nombre de cibles doit être égal au nombre de caisses.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Pousse une caisse sur une cible et elle devient verte ; pousse-la ailleurs et elle redevient brune. **R** remet tout en place.

> **Astuce:** **Pourquoi placer les cibles d'abord ?** Le jeu dessine les éléments dans l'ordre où tu les as placés. Une cible placée après une caisse ou le joueur est dessinée par-dessus, et une caisse sur une cible resterait cachée sous la marque rouge.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
|---|---|---|
| Je bouge de plusieurs cases d'un coup, ou pas du tout | Les événements sont *Clavier* (maintenue) au lieu de *Touche pressée*, ou la taille de *Déplacer grille* n'est pas 32 | Utilise des événements **Touche pressée** et *Déplacer grille* avec la taille 32 |
| Je traverse les murs | `obj_wall` n'est pas Solide, ou le joueur n'a pas d'événement **En collision avec obj_wall** | Coche **Solide** ; ajoute l'événement avec *Arrêter le mouvement* |
| La caisse ne bouge pas | Le joueur n'a pas d'événement de collision avec la caisse, ou la caisse n'est pas Solide | Ajoute **En collision avec obj_crate** avec *Si peut pousser* ; coche **Solide** sur la caisse |
| La caisse traverse les murs | La caisse n'a pas d'événement **En collision avec obj_wall** | Ajoute-le avec *Arrêter le mouvement* |
| La caisse ne devient jamais verte | L'événement Pas manque, ou la cible est dessinée par-dessus la caisse | Ajoute l'événement Pas ; place d'abord les cibles, puis replace les caisses |
| Je ne peux pas pousser une caisse sur une cible | `obj_target` est Solide | Décoche **Solide** sur `obj_target` |
| La caisse est coincée dans un coin dès le début | Elle a été placée dans un coin | Place les caisses avec de la place pour bouger |
| Le texte est difficile à lire | C'est du texte noir sur la salle sombre | Regarde la rangée du haut, ou demande à ton enseignant·e au sujet de *Définir la couleur de dessin* |


## Défis

- **Essaie (5 minutes) :** dessine un joueur ou une caisse plus jolis.
- **Va plus loin :** conçois un niveau plus difficile avec des couloirs plus étroits ; vérifie d'abord que tu peux le résoudre toi-même.
- **Invente :** compte les déplacements avec une variable, ou crée plusieurs salles et passe à la suivante quand toutes les caisses sont sur des cibles.

## Vocabulaire

| Terme | Ce que cela veut dire |
|---|---|
| Déplacement sur grille | Se déplacer par pas fixes (ici 32 pixels) au lieu de glisser |
| Touche pressée | Un événement qui se produit une fois quand une touche est enfoncée |
| Solide | Un objet qui bloque le mouvement |
| Cible | Une marque au sol ; pas solide |
| Recommencer la salle | Remettre le niveau comme au départ |


## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi utilise-t-on des événements **Touche pressée** et non *Clavier* (maintenue) pour un joueur de Sokoban ?
2. Pourquoi les cibles ne doivent-elles pas être Solides ?
3. Pourquoi une caisse n'est-elle pas poussée s'il y a une autre caisse derrière ?

## Mes notes

<br>

<br>

<br>

<br>

<br>

<br>

