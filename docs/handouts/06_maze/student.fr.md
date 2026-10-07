# PyGameMaker — Tutoriel 6 : Labyrinthe

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Labyrinthe : Trouvez la Sortie** (5 pages, 4 de base + 1 bonus facultatif, environ 20 à 25 minutes pour le jeu de base). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un jeu de labyrinthe : tu diriges un personnage dans des couloirs avec les flèches du clavier, tu ramasses des pièces pour gagner des points, et tu atteins la sortie pour gagner.

## Phase 1 : Joueur et labyrinthe

- [ ] **1.** Crée deux sprites (32×32) : `spr_player` et `spr_wall`.
- [ ] **2.** Crée `obj_wall` (sprite `spr_wall`, **Solide** coché) et `obj_player` (sprite `spr_player`, pas solide).
- [ ] **3.** Dans `obj_player`, ajoute cinq événements : **Clavier : Flèche droite (maintenue)** avec *Définir la vitesse horizontale à 4* ; **Flèche gauche (maintenue)** avec *-4* ; **Flèche bas (maintenue)** avec *Définir la vitesse verticale à 4* ; **Flèche haut (maintenue)** avec *-4* ; et **Clavier : Aucune touche** avec *Arrêter le mouvement*.
- [ ] **4.** Crée quatre sprites de plus, `spr_player_up`/`_down`/`_left`/`_right`, et ajoute un bloc *Définir le sprite* à chacun des quatre événements de touches fléchées de l'étape 3, pour que l'image du joueur corresponde à la direction où il se déplace.
- [ ] **5.** Ajoute **En collision avec obj_wall** avec *Arrêter le mouvement*.
- [ ] **6.** Crée `room_maze` (640×480) et active **Aligner sur la grille** 32×32. Place des murs sur le bord et à l'intérieur pour faire des couloirs, et place le joueur en haut à gauche. Chaque couloir doit faire au moins une case de large.

> DONE: **Tu dois voir :** appuie sur **F5**. Les flèches déplacent le joueur, son image regarde dans la direction où il se déplace, il s'arrête aux murs, et il s'arrête quand tu relâches.

## Phase 2 : Pièces et sortie

- [ ] **7.** Crée les sprites `spr_coin` et `spr_exit` (32×32).
- [ ] **8.** Crée `obj_coin` et `obj_exit`, chacun avec son sprite et **pas** solide.
- [ ] **9.** Dans `obj_coin`, ajoute **En collision avec obj_player** : *Ajouter au score 10*, puis *Détruire cette instance*.
- [ ] **10.** Dans `obj_exit`, ajoute **En collision avec obj_player** : *Afficher un message* « Vous avez gagné ! », puis *Recommencer la salle*.
- [ ] **11.** Dans la salle, éparpille des pièces le long des couloirs et mets la sortie aussi loin que possible du départ.

> DONE: **Tu dois voir :** appuie sur **F5**. Les pièces disparaissent quand tu les touches. Atteindre la sortie affiche « Vous avez gagné ! » et la salle recommence.

## Phase 3 : Affichage du score

- [ ] **12.** Crée `obj_game_controller` (sans sprite, pas solide).
- [ ] **13.** Événement **Création** : *Définir le score à 0*. Événement **Dessin** : *Afficher le score à x 10, y 10*.
- [ ] **14.** Place `obj_game_controller` n'importe où dans la salle.

> DONE: **Tu dois voir :** « Score : 0 » en haut à gauche, qui augmente de 10 pour chaque pièce. Après « Vous avez gagné ! », les pièces reviennent et le score est de nouveau à 0.

## Phase 4 : Passer en 2.5D (bonus facultatif, page 5)

Ton jeu est terminé après la Phase 3 — ceci est seulement pour ceux qui veulent essayer quelque chose en plus. Pas besoin d'un nouveau labyrinthe.

- [ ] **B1.** Dans `obj_player`, ajoute un événement **Création** avec *Activer la vue Raycast* (Cell Size 32).
- [ ] **B2.** Ajoute un bloc *Définir l'angle de vue* à chacun des quatre mêmes événements de touches fléchées des étapes 3/4 : Droite = 0, Gauche = 180, Haut = 90, Bas = 270.

> DONE: **Tu dois voir :** appuie sur **F5**. Le labyrinthe apparaît maintenant à la première personne au lieu d'être vu de dessus, texturé avec ta propre image `spr_wall`, et tourner suit la flèche que tu maintiens — exactement comme l'image de ton joueur à la Phase 1.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Le joueur ne bouge pas | Les événements sont sur le mauvais objet, ou le joueur n'est pas dans la salle | Vérifie les cinq événements de `obj_player` ; vérifie la salle |
| Le joueur glisse sans s'arrêter | L'événement **Aucune touche** manque | Ajoute **Clavier : Aucune touche** avec *Arrêter le mouvement* |
| L'image du joueur ne change jamais | Un bloc **Définir le sprite** manque sur l'un des quatre événements de touches fléchées | Ajoute-le, en faisant correspondre la direction |
| Le joueur traverse les murs | `obj_wall` n'est pas Solide, ou le joueur n'a pas **En collision avec obj_wall** | Coche **Solide** ; ajoute l'événement avec *Arrêter le mouvement* |
| Le joueur reste coincé dans les couloirs | Les murs ou le joueur n'ont pas été placés sur la grille | Active **Aligner sur la grille** 32×32 et replace-les |
| Les pièces ne font rien | La pièce n'a pas d'événement **En collision avec obj_player** | Ajoute-le à `obj_coin` |
| Tout le jeu se fige à la sortie | *Afficher un message* attend un clic | Clique sur OK dans le message |
| Pas de score à l'écran | `obj_game_controller` n'est pas dans la salle | Place-le dans la salle |
| Le score ne revient pas à 0 après la victoire | *Définir le score à 0* manque dans l'événement **Création** du contrôleur | Ajoute-le |
| (Bonus) Le labyrinthe reste vu de dessus | *Activer la vue Raycast* manque, ou l'extension 2.5D Raycast View n'est pas cochée dans **Fichier > Paramètres du projet... > Extensions** | Ajoute l'événement Création ; coche l'extension |
| (Bonus) La caméra ne tourne pas | Un bloc *Définir l'angle de vue* manque sur l'un des quatre événements de touches fléchées | Ajoute-le, selon le tableau de l'étape B2 |

## Défis

- **Essaie (5 minutes) :** change la vitesse du joueur, ou la valeur d'une pièce.
- **Va plus loin :** fais un second labyrinthe dans une autre salle et utilise **Aller à la salle suivante** à la sortie.
- **Invente :** ajoute un ennemi qui patrouille, un compte à rebours, ou une clé à ramasser avant que la sortie fonctionne.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Solide | Un objet qui bloque le mouvement |
| Objet à ramasser | Un objet qui disparaît quand le joueur le touche |
| Sortie | Un objet qui termine ou fait avancer le niveau |
| Aligner sur la grille | Placer les objets exactement sur une grille régulière |
| Conception de niveau | Planifier le labyrinthe pour qu'il soit équitable et résoluble |
| Direction regardée | Le sens vers lequel un personnage est tourné ; sert à choisir une image (Phase 1) ou un angle de caméra (bonus) |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi le joueur a-t-il besoin d'un événement **Aucune touche** avec *Arrêter le mouvement* ?
2. Pourquoi la pièce détruit-elle *cette* instance, et qu'aurait fait *Détruire l'autre instance* dans l'événement de la pièce ?
3. Pourquoi place-t-on les objets sur une grille quand on construit le labyrinthe ?

## Mes notes

[[notes:10]]
