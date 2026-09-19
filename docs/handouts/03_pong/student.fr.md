# PyGameMaker — Tutoriel 3 : Pong classique

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > Pong classique : Jeu à deux joueurs** (4 pages, environ 20 à 25 minutes). Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e. Il te faudra un ou une partenaire pour jouer à la fin !

## Ce que tu vas créer

Le jeu d'arcade classique : deux raquettes, une balle qui rebondit, des buts invisibles derrière chaque raquette, et un score à l'écran. Le joueur 1 utilise **W** et **S** ; le joueur 2 utilise les flèches **Haut** et **Bas**.

## Phase 1 : Raquettes et balle

- [ ] **1.** Crée trois sprites : `spr_ball` (16×16, cercle blanc), `spr_paddle` (16×64, rectangle haut) et `spr_wall` (32×32, bloc gris).
- [ ] **2.** Crée les objets : `obj_wall` (sprite `spr_wall`, **Solide**), `obj_paddle_left` et `obj_paddle_right` (sprite `spr_paddle`, **Solide**), et `obj_ball` (sprite `spr_ball`, **pas** solide).
- [ ] **3.** Raquette gauche : **Clavier : W (maintenue)** avec *Définir la vitesse verticale à -8*, **Clavier : S (maintenue)** avec *Définir la vitesse verticale à 8*, **Clavier : Aucune touche** avec *Arrêter le mouvement*, et **En collision avec obj_wall** avec *Arrêter le mouvement*.
- [ ] **4.** Raquette droite : les quatre mêmes événements, mais avec **Flèche haut** et **Flèche bas**.
- [ ] **5.** Balle : **Création** avec *Commencer à se déplacer dans la direction 45 à la vitesse 6* ; et trois événements de collision (avec `obj_wall`, `obj_paddle_left`, `obj_paddle_right`), chacun avec *Rebondir contre les objets solides*.
- [ ] **6.** Crée `room_pong` (640×480). Place des murs en haut et en bas, une raquette près de chaque bord latéral, et la balle au centre.

> DONE: **Tu dois voir :** appuie sur **F5**. Les deux raquettes bougent avec leurs touches et s'arrêtent aux murs. La balle part en haut à droite, rebondit sur les murs et les raquettes, et si tu la rates elle sort sur le côté de l'écran. C'est normal pour l'instant.

## Phase 2 : Buts et score

- [ ] **7.** Crée un sprite `spr_goal` (32×32, de la couleur que tu veux).
- [ ] **8.** Crée `obj_goal_left` et `obj_goal_right` (sprite `spr_goal`, **Visible décoché**, **Solide** coché).
- [ ] **9.** Dans `obj_ball`, ajoute **En collision avec obj_goal_left** : *Définir variable* `global.p2score` *relative* +1, puis *Sauter à la position de départ*. Ajoute **En collision avec obj_goal_right** : la même chose avec `global.p1score`.
- [ ] **10.** Dans la salle, empile `obj_goal_left` le long du bord gauche et `obj_goal_right` le long du bord droit, derrière les raquettes.

> DONE: **Tu dois voir :** appuie sur **F5**. Quand la balle dépasse une raquette, elle retourne au centre. Tu ne vois pas encore le score.

## Phase 3 : Affichage du score

- [ ] **11.** Crée `obj_score` (sans sprite). Son événement **Création** met `global.p1score` et `global.p2score` à 0.
- [ ] **12.** Son événement **Dessin** : d'abord *Définir la couleur de dessin* en blanc (`#ffffff`) ; puis *Dessiner texte* « Joueur 1 : » à x 10, y 40 ; *Dessiner variable* `global.p1score` à x 100, y 40 ; *Dessiner texte* « Joueur 2 : » à x 10, y 60 ; *Dessiner variable* `global.p2score` à x 100, y 60.
- [ ] **13.** Place `obj_score` n'importe où dans la salle.

> DONE: **Tu dois voir :** appuie sur **F5** et joue un point avec ton ou ta partenaire. Les scores s'affichent en haut à gauche et augmentent quand l'autre joueur rate la balle.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Une raquette traverse le mur | La raquette n'a pas d'événement **En collision avec obj_wall**, ou `obj_wall` n'est pas Solide | Ajoute l'événement (avec *Arrêter le mouvement*) ; coche **Solide** sur `obj_wall` |
| La balle traverse les murs ou les raquettes | Les événements de rebond manquent, ou les murs et raquettes ne sont pas Solides | Ajoute **Rebondir contre les objets solides** pour chaque collision ; coche **Solide** |
| La balle ne va que sur le côté | La direction n'est pas celle attendue | Vérifie *Commencer à se déplacer dans la direction 45* dans l'événement **Création** de la balle |
| La balle reste au milieu | L'événement **Création** de la balle manque, ou la balle n'est pas dans la salle | Ajoute l'événement ; place la balle dans la salle |
| La balle ne marque jamais | Les buts ne sont pas dans la salle, ou ne sont pas Solides | Place les buts derrière les raquettes ; coche **Solide** |
| Le score ne s'affiche pas | `obj_score` n'est pas dans la salle, il n'y a pas d'événement **Dessin**, ou le texte est noir sur la salle noire | Place-le ; ajoute l'événement Dessin ; ajoute d'abord *Définir la couleur de dessin* en blanc |
| Le score reste à 0 | Les variables n'ont pas le même nom partout | Utilise exactement `global.p1score` et `global.p2score` partout |
| Les touches des deux joueurs bougent la même raquette | Les deux raquettes ont les mêmes touches | Gauche : W et S. Droite : Haut et Bas |

## Défis

- **Essaie (5 minutes) :** change la vitesse de la balle, ou celle des raquettes.
- **Va plus loin :** ajoute une ligne pointillée au milieu, ou fais accélérer la balle à chaque contact avec une raquette.
- **Invente :** termine la partie quand un joueur atteint 10 points et affiche qui a gagné, ou change l'angle de la balle selon l'endroit où elle touche la raquette.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Solide | Un objet sur lequel les autres peuvent rebondir ou qui les arrête |
| Rebond | Inverser la direction du mouvement après un choc |
| Variable globale | Une valeur partagée par tous les objets, écrite `global.nom` |
| Événement Dessin | L'événement qui dessine à l'écran à chaque image |
| But | Un objet (invisible) qui détecte que la balle est passée |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi les buts ont-ils **Visible** décoché mais **Solide** coché ?
2. Que signifie `global.` dans `global.p1score`, et pourquoi en avons-nous besoin ici ?
3. Après un but, la balle est remise au milieu. Dans quelle direction part-elle, et pourquoi ?

## Mes notes

[[notes:10]]
