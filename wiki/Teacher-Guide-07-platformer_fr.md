# PyGameMaker — Tutoriel 7 : Jeu de plateforme — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-07-platformer_fr.pdf) · [ODT](downloads/Teacher-Guide-07-platformer_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/07_platformer_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Platformer : Courez, Sautez, Collectez**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé les Tutoriels 2 et 6 (événements, collisions, objets solides, score).

## Vue d'ensemble

Les élèves construisent un jeu de plateforme en trois phases : gravité, course et saut ; pièces, pics et drapeau ; et un affichage du score et des vies. Notions nouvelles : la **gravité**, le **saut** par une impulsion de vitesse verticale, les **dangers**, et des vies qui survivent à un redémarrage de la salle.

> **Info:** La gravité est un bon moment pour demander « que fait l'ordinateur à chaque pas ? » : ajouter 0.5 à la vitesse verticale, puis déplacer. Un saut n'est qu'une grande vitesse vers le haut que la gravité annule peu à peu.

## Durée suggérée (60 minutes)

Le tutoriel annonce 25 à 30 minutes pour un élève à l'aise ; la construction du niveau ajoute du temps.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Demandez quelles forces agissent sur un personnage qui saute |
| Phase 1 : gravité, course, saut | 15-20 min | Pages 1-2 ; le plan du niveau prend du temps |
| Phase 2 : pièces, pics, drapeau | 15 min | Page 3 |
| Phase 3 : contrôleur et vies | 10 min | Page 4 |
| Jouer et régler | 5 min | Changez la gravité et la vitesse de saut ; jouez les niveaux des autres |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


Pour une séance de 45 minutes, faites les phases 1 et 2 et laissez la phase 3 en devoir.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : gravité, course, saut**

- La gravité est réglée une fois dans l'événement **Création** du joueur : direction **270** (vers le bas), force **0.5**. Les angles commencent à 0 (droite) et vont dans le sens inverse des aiguilles d'une montre ; 90 est le haut.
- **Aucune touche** doit être *Définir la vitesse horizontale à 0*, **pas** *Arrêter le mouvement*. Arrêter le mouvement efface aussi la vitesse verticale que la gravité accumule, et le joueur reste suspendu (dans le projet de référence, il dérive d'environ 15 pixels en une demi-seconde au lieu de tomber de plus de 100). C'est la cause la plus fréquente de « le joueur ne tombe pas ».
- Le saut est sur **Touche pressée** (une fois par appui), pas sur *Clavier (maintenue)*.
- Le sol doit être **Solide**, et le joueur a besoin de **En collision avec obj_ground** avec *Arrêter le mouvement* ; sinon il traverse le sol.
- **Laissez de la place libre au-dessus du joueur** en le plaçant. Une plateforme juste au-dessus de la position de départ bloque le saut et donne l'impression que « le saut ne marche pas ». Le saut du projet de référence fait environ 95 pixels (trois cases) de haut.
- Les joueurs doivent être placés debout sur le sol (ou au-dessus). Aligner sur la grille 32×32 facilite cela.

**Phase 2 : pièces, dangers et drapeau**

- Toutes les interactions sont des événements de collision **sur le joueur** ; les objets pièce, pic et drapeau n'ont besoin d'aucun événement.
- Le pic utilise *Recommencer la salle*. En phase 2, rien n'est retenu entre les redémarrages ; les pièces reviennent.
- Le drapeau affiche un message ; il n'y a pas encore de niveau suivant.

**Phase 3 : contrôleur de jeu et vies**

- Le contrôleur doit être placé dans la salle.
- **Réglez le score et les vies dans Game Start, pas dans Création.** Un événement Création se relance à chaque redémarrage de la salle, et un pic redémarre la salle : avec Création, les vies étaient remises à 3 après chaque pic et ne pouvaient jamais s'épuiser. (Le tutoriel utilisait Création jusqu'à sa correction ; si l'écran d'un élève indique « Création », c'est une ancienne copie des instructions.) Game Start ne s'exécute qu'une fois, au tout début de la partie.
- Avec Game Start, le score est aussi conservé entre les redémarrages : un élève peut donc ramasser les mêmes pièces après chaque mort. Demandez si c'est équitable ; remettre le score à zéro dans l'événement du pic est un bon changement.
- Rien de spécial ne se passe quand les vies atteignent 0 (pas de Game Over) : c'est un défi à la fin du tutoriel.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`07_platformer_checkpoints.zip`) : un projet pour la fin de chaque phase, avec un petit niveau. Donnez à un élève bloqué la phase précédente.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Gravité | S'ajoute à la vitesse verticale à chaque pas, dans la direction donnée |
| Vitesse verticale | Vers le haut est négatif, vers le bas est positif |
| Impulsion | Un changement unique de vitesse, comme le saut |
| Danger | Un objet qui nuit au joueur (pic) |
| Game Start | Un événement qui s'exécute une fois au début de la partie, pas aux redémarrages de salle |


## Questions de discussion

- Pourquoi la vitesse de saut est-elle négative ?
- Que devient le saut si l'on double la gravité ? Si l'on divise la vitesse de saut par deux ?
- Pourquoi le joueur a-t-il besoin d'un événement de collision avec le sol en plus du sol Solide ?
- Pourquoi ne peut-on pas régler les vies dans Création ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 et laissez les élèves construire le niveau par-dessus ; gardez un petit niveau.
- **Approfondissement :** plateformes mobiles ; ennemis qui patrouillent ; double saut ; Game Over à 0 vie ; une seconde salle depuis le drapeau.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-A, 4-B.

**Partie B :** 1. Création (Définir la gravité). 2. Touche pressée : Flèche haut. 3. En collision avec `obj_coin` (sur le joueur). 4. Game Start (sur le contrôleur). 5. Dessin (sur le contrôleur).

**Partie C :**

1. Environ 20 pas (10 ÷ 0.5 = 20).
2. *Arrêter le mouvement* dans **Aucune touche** ; ce devrait être *Définir la vitesse horizontale à 0*.
3. La salle recommence et l'événement Création s'exécute de nouveau : les vies sont remises à 3 après chaque pic et ne s'épuisent jamais. Il faut Game Start.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Jeu de plateforme

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Gravité, course et un saut par appui fonctionnent ; les plateformes sont solides ; les pièces rapportent des points et disparaissent ; les pics coûtent une vie qui reste perdue ; le drapeau affiche un message ; score et vies sont affichés |
| 3 - Fonctionnel | Mouvement, saut, pièces et pics fonctionnent ; les vies ou l'affichage manquent |
| 2 - À moitié | Le joueur tombe, court et saute, mais les pièces ou les dangers ne fonctionnent pas |
| 1 - Commencé | Le joueur et le sol existent, mais le joueur traverse le sol ou ne peut pas bouger |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 1 (courir et sauter)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
