# PyGameMaker — Tutoriel 6 : Labyrinthe

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Labyrinthe : Trouvez la Sortie** (4 pages, environ 20 à 25 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un jeu de labyrinthe : tu diriges un personnage dans des couloirs avec les flèches du clavier, tu ramasses des pièces pour gagner des points, et tu atteins la sortie pour gagner.

## Phase 1 : Joueur et labyrinthe

- [ ] **1.** Crée deux sprites (32×32) : `spr_player` et `spr_wall`.
- [ ] **2.** Crée `obj_wall` (sprite `spr_wall`, **Solide** coché) et `obj_player` (sprite `spr_player`, pas solide).
- [ ] **3.** Dans `obj_player`, ajoute cinq événements : **Clavier : Flèche droite (maintenue)** avec *Définir la vitesse horizontale à 4* ; **Flèche gauche (maintenue)** avec *-4* ; **Flèche bas (maintenue)** avec *Définir la vitesse verticale à 4* ; **Flèche haut (maintenue)** avec *-4* ; et **Clavier : Aucune touche** avec *Arrêter le mouvement*.
- [ ] **4.** Ajoute **En collision avec obj_wall** avec *Arrêter le mouvement*.
- [ ] **5.** Crée `room_maze` (640×480) et active **Aligner sur la grille** 32×32. Place des murs sur le bord et à l'intérieur pour faire des couloirs, et place le joueur en haut à gauche. Chaque couloir doit faire au moins une case de large.

> DONE: **Tu dois voir :** appuie sur **F5**. Les flèches déplacent le joueur, il s'arrête aux murs, et il s'arrête quand tu relâches.

## Phase 2 : Pièces et sortie

- [ ] **6.** Crée les sprites `spr_coin` et `spr_exit` (32×32).
- [ ] **7.** Crée `obj_coin` et `obj_exit`, chacun avec son sprite et **pas** solide.
- [ ] **8.** Dans `obj_coin`, ajoute **En collision avec obj_player** : *Ajouter au score 10*, puis *Détruire cette instance*.
- [ ] **9.** Dans `obj_exit`, ajoute **En collision avec obj_player** : *Afficher un message* « Vous avez gagné ! », puis *Recommencer la salle*.
- [ ] **10.** Dans la salle, éparpille des pièces le long des couloirs et mets la sortie aussi loin que possible du départ.

> DONE: **Tu dois voir :** appuie sur **F5**. Les pièces disparaissent quand tu les touches. Atteindre la sortie affiche « Vous avez gagné ! » et la salle recommence.

## Phase 3 : Affichage du score

- [ ] **11.** Crée `obj_game_controller` (sans sprite, pas solide).
- [ ] **12.** Événement **Création** : *Définir le score à 0*. Événement **Dessin** : *Afficher le score à x 10, y 10*.
- [ ] **13.** Place `obj_game_controller` n'importe où dans la salle.

> DONE: **Tu dois voir :** « Score : 0 » en haut à gauche, qui augmente de 10 pour chaque pièce. Après « Vous avez gagné ! », les pièces reviennent et le score est de nouveau à 0.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Le joueur ne bouge pas | Les événements sont sur le mauvais objet, ou le joueur n'est pas dans la salle | Vérifie les cinq événements de `obj_player` ; vérifie la salle |
| Le joueur glisse sans s'arrêter | L'événement **Aucune touche** manque | Ajoute **Clavier : Aucune touche** avec *Arrêter le mouvement* |
| Le joueur traverse les murs | `obj_wall` n'est pas Solide, ou le joueur n'a pas **En collision avec obj_wall** | Coche **Solide** ; ajoute l'événement avec *Arrêter le mouvement* |
| Le joueur reste coincé dans les couloirs | Les murs ou le joueur n'ont pas été placés sur la grille | Active **Aligner sur la grille** 32×32 et replace-les |
| Les pièces ne font rien | La pièce n'a pas d'événement **En collision avec obj_player** | Ajoute-le à `obj_coin` |
| Tout le jeu se fige à la sortie | *Afficher un message* attend un clic | Clique sur OK dans le message |
| Pas de score à l'écran | `obj_game_controller` n'est pas dans la salle | Place-le dans la salle |
| Le score ne revient pas à 0 après la victoire | *Définir le score à 0* manque dans l'événement **Création** du contrôleur | Ajoute-le |

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

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi le joueur a-t-il besoin d'un événement **Aucune touche** avec *Arrêter le mouvement* ?
2. Pourquoi la pièce détruit-elle *cette* instance, et qu'aurait fait *Détruire l'autre instance* dans l'événement de la pièce ?
3. Pourquoi place-t-on les objets sur une grille quand on construit le labyrinthe ?

## Mes notes

[[notes:10]]
