# PyGameMaker — Tutoriel 9 : Attrape les pièces

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Attrape les pièces : gagner et perdre** (5 pages, environ 15 à 20 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un jeu complet avec une façon de gagner et une façon de perdre : des pièces tombent du ciel et tu glisses à gauche et à droite pour les attraper. Attrape toutes les pièces et tu gagnes. Touche l'ennemi et c'est Game Over. Depuis chaque fin, ESPACE recommence.

## Phase 1 : Un joueur qui se déplace

- [ ] **1.** Crée un nouveau projet `CatchTheCoins` et choisis le modèle **Avec écran Game Over**. Il te donne une salle Game Over déjà prête.
- [ ] **2.** Crée un sprite `spr_player` (32×32) et un objet `obj_player` avec ce sprite.
- [ ] **3.** Crée une salle `room_main` et place `obj_player` près du centre, en bas.
- [ ] **4.** Dans `obj_player` : **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale à -5* ; **Flèche droite (maintenue)** avec *5* ; **Clavier : Aucune touche** avec *Arrêter le mouvement*.

> DONE: **Tu dois voir :** appuie sur **F5**. Gauche et Droite déplacent le joueur, et il s'arrête quand tu relâches. Il peut sortir de l'écran pour l'instant.

## Phase 2 : Pièces et ennemi

- [ ] **5.** Crée les sprites `spr_coin` (24×24, cercle jaune) et `spr_enemy` (32×32, carré rouge).
- [ ] **6.** Crée `obj_coin` et `obj_enemy`, chacun avec son sprite. Chacun reçoit un événement **Création** : *Définir la vitesse verticale à 3*.
- [ ] **7.** Donne aux **deux** objets un événement **Hors de la salle** avec *Définir variable* `y` à 0, pour que tout ce qui tombe hors du bas revienne en haut.
- [ ] **8.** Dans `room_main`, place 5 à 8 pièces en haut et un ennemi entre elles.

> DONE: **Tu dois voir :** appuie sur **F5**. Les pièces et l'ennemi tombent. Les toucher ne fait rien pour l'instant. Tout ce que tu rates revient en haut.

## Phase 3 : Attraper et s'écraser

- [ ] **9.** Dans `obj_player`, événement **Création** : *Définir le score à 0*.
- [ ] **10.** Ajoute **En collision avec obj_coin** : *Ajouter au score 1*, puis *Détruire l'autre instance* (la pièce, pas le joueur !).
- [ ] **11.** Ajoute **En collision avec obj_enemy** : *Aller à la salle* `room_gameover`.
- [ ] **12.** Ajoute un événement **Dessin** : *Afficher le score à x 10, y 10*.

> DONE: **Tu dois voir :** appuie sur **F5**. Attraper une pièce ajoute 1 et la pièce disparaît. Toucher l'ennemi affiche l'écran Game Over, et ESPACE recommence.

## Phase 4 : Gagner la partie

- [ ] **13.** Crée `obj_win_text`. Événement **Dessin** : *Dessiner du texte* « YOU WIN! » à x 412, y 320 et « Press SPACE to play again » à x 340, y 400. **Touche pressée : espace** : *Redémarrer le jeu*.
- [ ] **14.** Crée `room_win` avec une couleur d'arrière-plan vive, et place-y un `obj_win_text`.
- [ ] **15.** Dans `obj_player`, ajoute un événement **Pas** : *Si le nombre de* `obj_coin` *égale 0* alors *Aller à la salle* `room_win`.

> DONE: **Tu dois voir :** appuie sur **F5**. Attrape toutes les pièces et la salle YOU WIN! apparaît. Touche l'ennemi et tu obtiens Game Over. ESPACE lance une nouvelle partie depuis chacune.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Le jeu affiche YOU WIN! tout de suite | Il n'y a aucune pièce dans `room_main` (le nombre est déjà 0) | Place au moins une pièce dans la salle |
| J'attrape toutes les pièces mais rien ne se passe | L'événement Pas ou le nom de la salle est faux | Vérifie *Si le nombre de obj_coin égale 0* et le nom de salle `room_win` |
| Une pièce ratée rend le jeu impossible à gagner | La pièce ou l'ennemi n'a pas d'événement **Hors de la salle** | Ajoute *Définir variable* `y` à 0 sur les deux |
| Mon joueur disparaît quand il attrape une pièce | J'ai utilisé *Détruire cette instance* | Utilise **Détruire l'autre instance** |
| Toucher l'ennemi ne fait rien | Pas de **En collision avec obj_enemy**, ou le nom de salle est mal écrit | Ajoute-le ; utilise exactement le nom de la salle Game Over |
| L'écran Game Over est absent | Le projet n'a pas été créé avec le modèle « Avec écran Game Over » | Crée un nouveau projet à partir du modèle |
| Le score ne s'affiche pas | Pas d'événement **Dessin** sur le joueur | Ajoute *Afficher le score* dans un événement Dessin |
| ESPACE ne fait rien sur l'écran de fin | La salle de fin n'a pas d'objet avec un événement **Touche pressée : espace** | Ajoute l'événement et place l'objet dans la salle |

## Défis

- **Essaie (5 minutes) :** change la vitesse de chute, ou le nombre de pièces.
- **Va plus loin :** ajoute un second ennemi, ou fais tomber pièces et ennemi à des vitesses différentes.
- **Invente :** ajoute des vies, un chronomètre, ou une pièce qui vaut plus d'un point.

## Vocabulaire

| Terme | Ce que cela veut dire |
| État de victoire | Ce qui se passe quand le joueur gagne |
| État de défaite | Ce qui se passe quand le joueur perd |
| Transition de salle | Passer d'une salle à une autre (ici, vers la salle Game Over ou de victoire) |
| Nombre d'instances | Combien de copies d'un objet existent en ce moment |
| Modèle | Un projet de départ déjà prêt |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Comment le jeu sait-il que toutes les pièces ont été attrapées ?
2. Pourquoi les pièces ratées ont-elles besoin d'un événement **Hors de la salle** ?
3. Quelle est la différence entre la salle de victoire et la salle Game Over ?

## Mes notes

[[notes:10]]
