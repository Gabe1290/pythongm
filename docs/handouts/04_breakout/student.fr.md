# PyGameMaker — Tutoriel 4 : Casse-briques

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Breakout : Casse-Briques** (7 pages, environ 25 à 30 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Le casse-briques classique : une raquette en bas, une balle qui rebondit sur les murs et la raquette, quatre rangées de briques colorées à détruire, trois vies et un score. Tu vas utiliser un **objet parent** pour qu'une seule règle de collision fonctionne pour toutes les couleurs de briques.

## Phase 1 : Une balle qui rebondit

- [ ] **1.** Crée quatre sprites : `spr_ball` (16×16), `spr_paddle` (64×16), `spr_wall` (32×32) et `spr_death_zone` (32×32). Dessine-les ou importe les images d'exemple de `Tutorials/04_breakout/assets/`.
- [ ] **2.** Crée les objets : `obj_wall_side` et `obj_wall_top` (sprite `spr_wall`, **Solide**), `obj_paddle` (**Solide**), `obj_ball` (**pas** solide), et `obj_death_zone` (sprite `spr_death_zone`, **Visible décoché**).
- [ ] **3.** Raquette : **Clavier : Flèche gauche (maintenue)** avec *Définir la vitesse horizontale à -8*, **Clavier : Flèche droite (maintenue)** avec *Définir la vitesse horizontale à 8*, **Clavier : Aucune touche** avec *Arrêter le mouvement*, et **En collision avec obj_wall_side** avec *Arrêter le mouvement*.
- [ ] **4.** Balle : **Création** avec *Définir la vitesse horizontale à 3* et *Définir la vitesse verticale à -3*.
- [ ] **5.** Collisions de la balle : avec `obj_wall_side` → *Inverser le mouvement horizontal* ; avec `obj_wall_top` → *Inverser le mouvement vertical* ; avec `obj_paddle` → *Inverser le mouvement vertical* ; avec `obj_death_zone` → *Sauter à x : 320 y : 100*.
- [ ] **6.** Crée `room_breakout` (640×480). Place des murs latéraux sur les deux bords, des murs du haut le long du haut, la zone de mort le long du **bas** (il n'y a pas de mur en bas), la raquette près du centre en bas et la balle juste au-dessus.

> DONE: **Tu dois voir :** appuie sur **F5**. La raquette bouge avec les flèches et s'arrête aux murs. La balle rebondit partout ; si elle passe sous la raquette, elle revient en haut.

## Phase 2 : Première rangée de briques

- [ ] **7.** Crée un sprite `spr_brick_red` (32×16).
- [ ] **8.** Crée `obj_brick_parent` (sans sprite, **Solide**) — un modèle. Puis crée `obj_brick_red` (sprite `spr_brick_red`, **Parent** `obj_brick_parent`, **Solide**).
- [ ] **9.** Dans `obj_ball`, ajoute **En collision avec obj_brick_parent** : *Inverser le mouvement vertical*, *Détruire l'autre instance*, *Ajouter au score 10*.
- [ ] **10.** Dans la salle, remplis une rangée de `obj_brick_red` près du haut (active **Aligner sur la grille** 32×16).

> DONE: **Tu dois voir :** appuie sur **F5**. La balle détruit les briques et rebondit. Chaque brique vaut 10 points (tu ne vois pas encore le score).

## Phase 3 : Plus de rangées de briques

- [ ] **11.** Crée les sprites `spr_brick_orange`, `spr_brick_yellow` et `spr_brick_green` (32×16).
- [ ] **12.** Crée `obj_brick_orange`, `obj_brick_yellow` et `obj_brick_green`, chacun avec son sprite, **Parent** `obj_brick_parent` et **Solide**. Ne modifie **pas** la balle.
- [ ] **13.** Remplis quatre rangées : rouge, orange, jaune, vert.

> DONE: **Tu dois voir :** appuie sur **F5**. Les briques de toutes les couleurs se cassent quand la balle les touche.

## Phase 4 : Contrôleur de jeu

- [ ] **14.** Crée `obj_game_controller` (sans sprite). **Création** : *Définir les vies à 3*, *Définir le score à 0*. **Dessin** : *Afficher le score à x 10, y 10* et *Afficher les vies à x 200, y 10*.
- [ ] **15.** Dans `obj_ball`, dans l'événement **En collision avec obj_death_zone**, ajoute *Ajouter aux vies -1* **avant** le saut.
- [ ] **16.** Dans `obj_game_controller`, ajoute l'événement **Autres événements > Plus de vies** avec *Afficher un message « Game Over ! »*, puis *Afficher le tableau des meilleurs scores*, puis *Terminer le jeu*.
- [ ] **17.** Place `obj_game_controller` n'importe où dans la salle.

> DONE: **Tu dois voir :** le score et les vies s'affichent en haut. Chaque chute coûte une vie. Après la troisième chute, tu obtiens un message Game Over, le tableau des meilleurs scores, et le jeu se ferme.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| La balle sort de la salle | Un mur manque ou n'est pas Solide, ou la balle n'a pas d'événement de rebond pour lui | Vérifie les murs ; vérifie les événements de collision de la balle |
| La balle rebondit mais les briques restent | L'événement de collision de brique est sur le mauvais objet, ou les briques n'ont pas de parent | Mets l'événement sur `obj_ball` pour `obj_brick_parent` ; règle le **Parent** de chaque brique |
| Seules les briques rouges se cassent | Les nouvelles briques n'ont pas de **Parent** | Règle **Parent** sur `obj_brick_parent` pour orange, jaune et vert |
| La raquette traverse les murs latéraux | Pas d'événement **En collision avec obj_wall_side** sur la raquette | Ajoute-le avec *Arrêter le mouvement* |
| La balle n'est jamais perdue / les vies ne baissent pas | La zone de mort manque, ou *Ajouter aux vies -1* n'a pas été ajouté | Place la zone de mort en bas ; ajoute l'action |
| Ni score ni vies à l'écran | `obj_game_controller` n'est pas dans la salle | Place-le dans la salle |
| Les vies commencent à 0 ou le jeu s'arrête tout de suite | *Définir les vies à 3* manque | Ajoute-le à l'événement **Création** du contrôleur |
| La balle traverse une brique sans la casser | La brique n'est pas Solide ou n'est pas bien placée dans la salle | Coche **Solide** sur les objets briques |

## Défis

- **Essaie (5 minutes) :** change la vitesse de la balle ou de la raquette.
- **Va plus loin :** donne un score différent à chaque couleur (rouge 40, orange 30, jaune 20, vert 10), ou accélère la balle quand les briques disparaissent.
- **Invente :** construis un second niveau avec une autre disposition de briques, ou joue un son à la fin de la partie.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Objet parent | Un objet modèle ; les objets qui l'utilisent héritent de ses événements |
| Objet enfant | Un objet qui a un parent (chaque couleur de brique) |
| Zone de mort | Un objet invisible qui détecte que la balle est perdue |
| Vies | Le nombre de fois où tu peux perdre la balle |
| Meilleurs scores | Les meilleurs résultats, gardés dans un tableau |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi l'événement de collision est-il écrit pour `obj_brick_parent` et non pour chaque couleur ?
2. Pourquoi n'y a-t-il pas de mur en bas de la salle ?
3. Que fait *Inverser le mouvement vertical*, et pourquoi l'utilise-t-on pour le mur du haut et la raquette mais *Inverser le mouvement horizontal* pour les murs latéraux ?

## Mes notes

[[notes:10]]
