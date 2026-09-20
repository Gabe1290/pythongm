# PyGameMaker — Tutoriel 8 : Alunissage

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Lunar Lander : Atterrir sur la Lune** (4 pages, environ 20 à 25 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un jeu d'alunissage : ton vaisseau tombe lentement sous la faible gravité de la Lune. Tu utilises les flèches pour pousser et diriger, et tu dois te poser sur l'aire verte. Si tu touches le sol rocheux, tu t'écrases.

## Phase 1 : Un atterrisseur qui vole

- [ ] **1.** Crée deux sprites (32×32) : `spr_lander` et `spr_ground`.
- [ ] **2.** Crée `obj_ground` (sprite `spr_ground`, **Solide**) et `obj_lander` (sprite `spr_lander`).
- [ ] **3.** Dans `obj_lander`, événement **Création** : *Définir la gravité* direction **270**, force **0.05**. (La gravité de la Lune vaut environ un sixième de celle de la Terre, donc la valeur est petite.)
- [ ] **4.** **Clavier : Flèche haut (maintenue)** avec *Définir la vitesse verticale -2*.
- [ ] **5.** **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale -2* et **Flèche droite (maintenue)** avec *2*.
- [ ] **6.** **Clavier : Aucune touche** avec *Définir la vitesse horizontale 0*. Ne remets pas la vitesse verticale à zéro, sinon la gravité ne fonctionne plus.
- [ ] **7.** Crée `room_game` (640×480, arrière-plan **noir**, Aligner sur la grille 32×32). Place du sol sur la rangée du bas et l'atterrisseur près du haut.

> DONE: **Tu dois voir :** appuie sur **F5**. L'atterrisseur tombe lentement. Maintiens **Haut** pour monter, **Gauche** et **Droite** pour diriger. Relâche tout et il dérive vers le bas. (Il traverse le sol pour l'instant : pas encore d'événement de collision.)

## Phase 2 : Atterrir et s'écraser

- [ ] **8.** Crée `spr_pad` (un rectangle vert plat) et `obj_pad` (sprite `spr_pad`, **Solide**).
- [ ] **9.** Dans `obj_lander`, ajoute **En collision avec obj_pad** : *Arrêter le mouvement*, puis *Définir la gravité* direction 270 force **0**, puis *Afficher un message* « Landing successful! ».
- [ ] **10.** Ajoute **En collision avec obj_ground** : *Afficher un message* « Crashed! », puis *Recommencer la salle*.
- [ ] **11.** Modifie la salle : rends le sol irrégulier avec des collines, laisse un trou dans la rangée du bas, et place `obj_pad` dans le trou (un ou deux blocs).

> DONE: **Tu dois voir :** appuie sur **F5**. Touche l'aire et tu obtiens « Landing successful! » une seule fois. Touche le sol et tu obtiens « Crashed! » et le niveau recommence. Utilise de courts appuis sur **Haut** pour contrôler ta chute.

## Phase 3 : Contrôleur de jeu

- [ ] **12.** Crée `obj_game_controller` (sans sprite). Événement **Création** : *Définir le score à 0*.
- [ ] **13.** Événement **Dessin** : d'abord *Définir la couleur de dessin* en blanc (`#ffffff`), puis *Dessiner du texte* « Lunar Lander » à x 10, y 10 et *Dessiner du texte* « Land on the green pad! » à x 10, y 30.
- [ ] **14.** Place `obj_game_controller` n'importe où dans la salle.

> DONE: **Tu dois voir :** appuie sur **F5**. Le titre et les instructions s'affichent en haut à gauche, en blanc.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| L'atterrisseur ne tombe pas | L'action de gravité manque dans **Création**, ou **Aucune touche** utilise *Arrêter le mouvement* | Ajoute la gravité ; fais de **Aucune touche** un *Définir la vitesse horizontale 0* |
| L'atterrisseur tombe très vite | La force de gravité est trop grande (par exemple 5 au lieu de 0.05) | Règle la force à 0.05 |
| L'atterrisseur traverse le sol | Pas de **En collision avec obj_ground**, ou `obj_ground` n'est pas Solide | Ajoute l'événement ; coche **Solide** |
| « Landing successful! » réapparaît sans arrêt | La gravité n'est pas coupée après l'atterrissage | Ajoute *Définir la gravité* force 0 à l'événement de l'aire |
| Je m'écrase toujours, même sur l'aire | L'aire manque, ou elle est trop petite ou trop haute pour être atteinte | Vérifie que `obj_pad` est dans la salle et Solide ; utilise un ou deux blocs |
| L'atterrisseur reste collé au sol après un crash | *Recommencer la salle* manque | Ajoute-le après *Afficher un message* |
| Le texte ne s'affiche pas | Le texte est noir sur la salle noire | Ajoute *Définir la couleur de dessin* en blanc avant le texte |
| L'atterrisseur est difficile à contrôler | De longs appuis sur Haut le font monter vite | Appuie sur Haut par petites impulsions |

## Défis

- **Essaie (5 minutes) :** change la gravité ou la poussée et vois comment le jeu se comporte.
- **Va plus loin :** rends l'aire plus petite, ou construis un second niveau plus difficile dans une autre salle.
- **Invente :** ajoute un compteur de carburant qui baisse quand tu pousses et coupe la poussée à 0, ou fais qu'un atterrissage trop rapide compte comme un crash.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Poussée | Une impulsion qui lutte contre la gravité (ici, régler la vitesse verticale à -2) |
| Gravité | Une force qui tire vers le bas un peu plus à chaque pas |
| Vitesse verticale / horizontale | La rapidité de l'atterrisseur de haut en bas / de gauche à droite |
| Aire d'atterrissage | Le seul endroit où toucher le sol est une réussite |
| ATH | Du texte à l'écran qui informe le joueur |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi la gravité vaut-elle 0.05 et non 0.5 comme dans le jeu de plateforme ?
2. Pourquoi **Aucune touche** ne remet-il à zéro que la vitesse horizontale ?
3. Pourquoi faut-il couper la gravité quand l'atterrisseur se pose sur l'aire ?

## Mes notes

[[notes:10]]
