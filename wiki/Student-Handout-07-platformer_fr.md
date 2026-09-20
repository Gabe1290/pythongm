# PyGameMaker — Tutoriel 7 : Jeu de plateforme

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Student-Handout-07-platformer_fr.pdf) · [ODT](downloads/Student-Handout-07-platformer_fr.odt)

---

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Platformer : Courez, Sautez, Collectez** (4 pages, environ 25 à 30 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un jeu de plateforme : ton personnage tombe avec la gravité, court et saute entre des plateformes, ramasse des pièces, évite des pics (chaque contact coûte une vie) et atteint un drapeau pour gagner.

## Phase 1 : Un joueur qui saute

- [ ] **1.** Crée deux sprites (32×32) : `spr_player` et `spr_ground`.
- [ ] **2.** Crée `obj_ground` (sprite `spr_ground`, **Solide**) et `obj_player` (sprite `spr_player`).
- [ ] **3.** Dans `obj_player`, événement **Création** : *Définir la gravité* direction **270**, force **0.5**.
- [ ] **4.** Ajoute **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale à -4* et **Flèche droite (maintenue)** avec *4*.
- [ ] **5.** Ajoute **Clavier : Aucune touche** avec *Définir la vitesse horizontale à 0*. N'utilise **pas** *Arrêter le mouvement* ici : il annulerait aussi la gravité.
- [ ] **6.** Ajoute **Touche pressée : Flèche haut** avec *Définir la vitesse verticale à -10*.
- [ ] **7.** Ajoute **En collision avec obj_ground** avec *Arrêter le mouvement*.
- [ ] **8.** Crée `room_level1` (800×480, arrière-plan bleu clair, Aligner sur la grille 32×32). Place le sol en bas, des plateformes en l'air, et le joueur debout sur le sol à gauche. **Laisse de la place libre au-dessus du joueur** pour qu'il puisse sauter.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Le joueur tombe sur le sol, court à gauche et à droite, et la flèche haut le fait sauter d'environ trois cases de haut. Il atterrit sur les plateformes.

## Phase 2 : Pièces et dangers

- [ ] **9.** Crée les sprites `spr_coin`, `spr_spike` et `spr_flag` et les objets `obj_coin`, `obj_spike` et `obj_flag` (aucun événement dessus).
- [ ] **10.** Dans `obj_player`, ajoute **En collision avec obj_coin** : *Ajouter au score 10*, puis *Détruire l'autre instance*.
- [ ] **11.** Ajoute **En collision avec obj_spike** : *Recommencer la salle*.
- [ ] **12.** Ajoute **En collision avec obj_flag** : *Afficher un message* « You Win! ».
- [ ] **13.** Dans la salle, place des pièces sur les plateformes, des pics près des trous, et le drapeau à l'extrémité droite.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Les pièces disparaissent et valent 10. Un pic recommence le niveau. Le drapeau affiche « You Win! ».

## Phase 3 : Contrôleur de jeu

- [ ] **14.** Crée `obj_game_controller` (sans sprite).
- [ ] **15.** Événement **Game Start** (dans *Autres événements*) : *Définir le score à 0* et *Définir les vies à 3*.
- [ ] **16.** Événement **Dessin** : *Afficher le score à x 10, y 10* et *Afficher les vies à x 200, y 10*.
- [ ] **17.** Dans la collision avec les pics de `obj_player`, ajoute *Ajouter aux vies -1* **avant** *Recommencer la salle*.
- [ ] **18.** Place `obj_game_controller` n'importe où dans la salle.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Le score et les vies sont affichés. Chaque pic coûte une vie et recommence la salle, et les vies restent plus basses.

> **Astuce:** **Game Start, pas Création.** Un événement Création se relance à chaque redémarrage de la salle. Si les vies étaient réglées à 3 dans Création, chaque pic te les rendrait et tu n'en manquerais jamais.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
|---|---|---|
| Le joueur traverse le sol | `obj_ground` n'est pas Solide, ou le joueur n'a pas **En collision avec obj_ground** | Coche **Solide** ; ajoute l'événement avec *Arrêter le mouvement* |
| Le joueur ne tombe pas du tout | L'action **Définir la gravité** manque dans **Création**, ou **Aucune touche** utilise *Arrêter le mouvement* | Ajoute la gravité ; change **Aucune touche** en *Définir la vitesse horizontale à 0* |
| Le joueur ne saute pas | L'événement Haut est *maintenue* au lieu de *Touche pressée*, ou un objet solide est juste au-dessus du joueur | Utilise **Touche pressée : Flèche haut** ; laisse la place libre au-dessus |
| Le joueur saute sans arrêt tant que je maintiens Haut | C'est un événement Clavier (maintenue) | Utilise **Touche pressée** pour un saut par appui |
| Les pièces ne font rien | L'événement de pièce est sur la pièce au lieu du joueur, ou manque | Mets **En collision avec obj_coin** sur `obj_player` |
| Les pics ne coûtent jamais de vies | Les vies sont réglées dans **Création** au lieu de **Game Start**, ou *Ajouter aux vies -1* manque | Déplace les actions dans **Game Start** ; ajoute l'action avant *Recommencer la salle* |
| Le score et les vies ne s'affichent pas | `obj_game_controller` n'est pas dans la salle | Place-le dans la salle |
| Le drapeau ne fait rien | Pas de **En collision avec obj_flag** sur le joueur | Ajoute-le |


## Défis

- **Essaie (5 minutes) :** change la gravité (0.5) ou la vitesse de saut (-10) et vois comment le saut change.
- **Va plus loin :** ajoute une plateforme mobile ou un ennemi qui patrouille ; fais aller le drapeau à la salle suivante.
- **Invente :** ajoute un double saut, ou un message Game Over quand les vies atteignent 0.

## Vocabulaire

| Terme | Ce que cela veut dire |
|---|---|
| Gravité | Une force qui tire un objet vers le bas (direction 270) à chaque pas |
| Vitesse verticale | La rapidité avec laquelle quelque chose monte (négatif) ou descend (positif) |
| Touche pressée | Un événement qui se produit une fois quand une touche est enfoncée |
| Danger | Quelque chose qui blesse le joueur, comme un pic |
| Game Start | Un événement qui s'exécute une fois, au début de toute la partie |


## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi utilise-t-on *Définir la vitesse horizontale à 0* et non *Arrêter le mouvement* pour **Aucune touche** ?
2. Pourquoi la vitesse de saut est-elle négative ?
3. Pourquoi le score et les vies sont-ils réglés dans **Game Start** et non dans **Création** ?

## Mes notes

<br>

<br>

<br>

<br>

<br>

<br>

