# PyGameMaker — Tutoriel 16 : Panier de fruits

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Panier de Fruits : Attrape et Évite !** (6 pages, environ 10 à 15 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un panier qui glisse à gauche et à droite le long du bas de la salle. Des fruits et des bombes sont déjà posés dans la salle — rien ne tombe, rien ne bouge tout seul. Fais marcher le panier sur un fruit et il disparaît, en ajoutant au score. Marche sur une bombe et la salle recommence. Ramasse tous les fruits et tu gagnes !

## Phase 1 : Le panier mobile

- [ ] **1.** Crée un nouveau projet `FruitBasket`.
- [ ] **2.** Crée un sprite `spr_basket` (56x40, un panier marron) et un objet `obj_player` avec ce sprite.
- [ ] **3.** Renomme la salle de départ du projet (`room0`) en `room_main`, règle sa **largeur à 640** et sa **hauteur à 480** dans ses propriétés, et place `obj_player` près du centre, en bas.
- [ ] **4.** Dans `obj_player` : **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale à -5* ; **Flèche droite (maintenue)** avec *5* ; **Clavier : Aucune touche** avec *Arrêter le mouvement*.

> DONE: **Tu dois voir :** appuie sur **F5**. Gauche et Droite déplacent le panier, et il s'arrête quand tu relâches.

## Phase 2 : Fruits et bombes

- [ ] **5.** Crée un sprite `spr_fruit` (26x26, un cercle vert) et un objet `obj_fruit` avec ce sprite. Aucun événement nécessaire.
- [ ] **6.** Crée un sprite `spr_bomb` (26x26, un cercle sombre) et un objet `obj_bomb` avec ce sprite. Aucun événement nécessaire ici non plus.
- [ ] **7.** Dans `room_main`, place **5 fruits** en bas avec des espaces entre eux (mais pas juste à l'endroit où le panier démarre), et **2 bombes**, une près du bord gauche et une près du bord droit, bien à l'écart de tout fruit.

> DONE: **Tu dois voir :** appuie sur **F5**. Les fruits et les bombes restent immobiles. Le panier peut se déplacer parmi eux, mais les toucher ne fait rien encore.

![L'éditeur de salles montrant room_main avec le panier, 5 fruits et 2 bombes placés](room_phase2_layout.png)

## Phase 3 : Ramasser et éviter

- [ ] **8.** Dans `obj_player`, événement **Création** : *Définir le score à 0*. Événement **Dessin** : *Afficher le score à x 10, y 10*.
- [ ] **9.** Ajoute **En collision avec obj_fruit** : *Ajouter 10 au score*, puis *Détruire l'autre instance* (le fruit, pas le panier !).
- [ ] **10.** Ajoute **En collision avec obj_bomb** : *Redémarrer la salle*.

> DONE: **Tu dois voir :** appuie sur **F5**. Ramasser un fruit ajoute 10 au score et le fruit disparaît. Toucher une bombe remet tout exactement comme au début, score compris.

## Phase 4 : Gagner

- [ ] **11.** Crée `obj_win_text`. Événement **Dessin** : *Dessiner du texte* « YOU WIN! » à x 412, y 320 et « Press SPACE to play again » à x 340, y 400. **Touche pressée : espace** : *Redémarrer le jeu*.
- [ ] **12.** Crée `room_win` avec une couleur d'arrière-plan vive, et place-y un `obj_win_text`.
- [ ] **13.** Dans `obj_player`, ajoute un événement **Pas** : *Si le nombre de* `obj_fruit` *égale 0* alors *Aller à la salle* `room_win`.

> DONE: **Tu dois voir :** appuie sur **F5**. Ramasse tous les fruits et la salle YOU WIN! apparaît. ESPACE lance une nouvelle partie.

![L'écran de victoire : YOU WIN! après avoir ramassé tous les fruits](gameplay_win_screen.png)

## Bonus (facultatif) : Importer des images toutes faites

La page 6 du tutoriel montre comment remplacer tes propres dessins par des
images toutes faites, si tu préfères ne pas dessiner. Ton jeu fonctionne
exactement de la même façon dans les deux cas &mdash; ceci ne vaut la peine
que lorsque tout ce qui précède fonctionne déjà.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Le panier ramasse un fruit dès le début de la partie | Un fruit a été placé trop près de l'endroit où démarre le panier | Éloigne ce fruit, ou déplace la position de départ du panier |
| Mon panier disparaît quand il ramasse un fruit | J'ai utilisé *Détruire cette instance* | Utilise **Détruire l'autre instance** |
| Toucher une bombe ne fait rien | Pas de **En collision avec obj_bomb** sur `obj_player`, ou la mauvaise action est utilisée | Ajoute la collision et utilise **Redémarrer la salle** |
| Le score ne s'affiche pas | Pas d'événement **Dessin** sur le panier | Ajoute *Afficher le score* dans un événement Dessin |
| Le jeu affiche YOU WIN! tout de suite | Il n'y a aucun fruit dans `room_main` (le nombre est déjà 0) | Place au moins un fruit dans la salle |
| Je ramasse tous les fruits mais rien ne se passe | L'événement Pas ou le nom de la salle est faux | Vérifie *Si le nombre de obj_fruit égale 0* et le nom de salle `room_win` |
| L'écran de victoire est vide | `obj_win_text` n'a pas été placé dans `room_win`, ou son événement Dessin est manquant | Place une instance ; vérifie que l'événement Dessin existe |
| ESPACE ne fait rien sur l'écran de victoire | La salle de victoire n'a pas d'objet avec un événement **Touche pressée : espace** | Ajoute l'événement à `obj_win_text` |

## Défis

- **Essaie (5 minutes) :** ajoute quelques fruits de plus, ou rapproche les bombes.
- **Va plus loin :** ajoute une deuxième rangée de fruits plus haut (il faudra laisser le panier se déplacer aussi vers le haut et le bas, ou ajouter un objet en forme d'échelle).
- **Invente :** donne des valeurs de points différentes aux fruits en créant un second objet fruit qui vaut plus.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Collision | Un événement qui se déclenche au moment où deux objets se touchent |
| Nombre d'instances | Combien de copies d'un objet existent en ce moment |
| Redémarrer la salle | Une action qui remet la salle actuelle exactement comme au début |
| Événement Pas | Un événement qui s'exécute à chaque image du jeu, encore et encore |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi le fruit n'a-t-il jamais besoin de ses propres événements, contrairement au panier ?
2. Qu'arrive-t-il à ton score si tu touches une bombe ? Pourquoi ?
3. Comment le jeu sait-il que tu as ramassé tous les fruits ?

## Mes notes

[[notes:10]]
