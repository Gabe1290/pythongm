# PyGameMaker — Tutoriel 11 : 2.5D, premiers pas

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > 2.5D : Premiers pas** (4 pages, environ 20 à 25 minutes). Cette leçon n'est pas dans l'édition débutant : ton enseignant·e devra peut-être changer d'abord l'édition. Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Une petite salle que tu explores **à la première personne**, comme dans le jeu classique Wolfenstein 3D. C'est toujours une salle 2D ordinaire (les murs ont un x et un y normaux) ; seule l'image à l'écran est dessinée comme si tu te tenais à l'intérieur. Tu tournes avec les flèches, tu avances et tu recules, et tu heurtes de vrais murs.

## Phase 1 : La salle et les murs

- [ ] **1.** Crée un projet `FirstPerson` avec le modèle **Projet vide**.
- [ ] **2.** Crée le sprite `spr_wall` (**32×32**, gris ou briques) et le sprite `spr_player` (16×16, de la couleur que tu veux ; tu ne le verras jamais).
- [ ] **3.** Crée `obj_wall` (sprite `spr_wall`) et coche **Solide**. Crée `obj_player` (sprite `spr_player`), **pas** solide.
- [ ] **4.** Crée `room_main` avec une largeur et une hauteur de **320**, et affiche la grille (32 par défaut, donc les blocs s'alignent).
- [ ] **5.** Place des murs dans chaque case du bord : rangée du haut de x 0 à 288 (y 0), rangée du bas (y 288), colonnes de gauche et de droite entre les coins, et trois blocs à l'intérieur en (128, 128), (160, 128) et (128, 160).
- [ ] **6.** Place `obj_player` en (48, 48).

> DONE: **Tu dois voir :** une grille de 10×10 cases avec un anneau de blocs de mur et trois blocs à l'intérieur. (Tu ne vois pas encore la vue 3D.)

## Phase 2 : La caméra et les commandes

- [ ] **7.** Dans `obj_player`, **Quand créé** : *Activer la vue Raycast* avec Field of View (champ de vision) **66**, Cell Size (taille de case) **32**, Render Distance (distance d'affichage) **20**. Laisse Camera Object vide (cela veut dire « cet objet »).
- [ ] **8.** **Clavier : Flèche gauche (maintenue)** : *Définir l'angle de vue* **3**, Relatif activé. **Flèche droite (maintenue)** : *Définir l'angle de vue* **-3**, Relatif activé.
- [ ] **9.** **Flèche haut (maintenue)** : *Définir direction et vitesse* direction `facing_angle`, vitesse **3**. **Flèche bas (maintenue)** : direction `facing_angle+180`, vitesse **3**. **Aucune touche** : direction 0, vitesse 0.
- [ ] **10.** Ajoute **Quand collision avec obj_wall** et laisse-le **vide**. Ne l'oublie pas : sans lui, le joueur traverse les murs.

> DONE: **Tu dois voir :** appuie sur **F5**. La salle apparaît à la première personne : murs gris, plafond bleu et sol sombre. Les flèches te font tourner et marcher, et tu ne peux pas sortir de la salle.

## Phase 3 : Tester et régler

- [ ] **11.** Change un réglage à la fois de *Activer la vue Raycast* et appuie sur **F5** : Field of View 40 et 100 ; Render Distance 3 ; Wall Color, Floor Color, Ceiling Color (couleurs) ; Columns (colonnes).
- [ ] **12.** Note dans tes notes ce que chaque changement a fait.

> DONE: **Tu dois voir :** une vue étroite pour 40, une vue large et un peu déformée pour 100, des murs lointains qui disparaissent pour une Render Distance courte, et de nouvelles couleurs.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Je vois la salle normale vue du dessus | L'action *Activer la vue Raycast* manque, ou elle est sur un objet qui n'est pas dans la salle | Mets-la dans **Quand créé** de `obj_player` et place le joueur dans la salle |
| Je traverse les murs | Le **Quand collision avec obj_wall** vide manque, ou `obj_wall` n'est pas Solide | Ajoute l'événement (laisse-le vide) ; coche **Solide** |
| Les murs paraissent bizarres ou ont des trous | Un mur est hors de la grille de 32 pixels, ou Cell Size n'est pas 32 | Utilise l'alignement sur la grille ; règle Cell Size sur 32 |
| Je tourne dans le mauvais sens | Le 3 et le -3 sont inversés | Inverse-les sur les deux événements de rotation |
| Je peux tourner mais pas avancer | Haut et Bas n'ont pas *Définir direction et vitesse*, ou la direction n'est pas `facing_angle` | Vérifie exactement le texte de la direction |
| Je continue d'avancer quand je relâche | L'événement **Aucune touche** manque | Ajoute direction 0, vitesse 0 |
| La fenêtre est minuscule | La fenêtre prend la taille de la salle (320×320) | Fais une salle plus grande, en gardant les murs sur la grille |
| Rien n'est visible sur les murs | Le sprite du mur est entièrement transparent | Dessine un sprite 32×32 rempli |

## Défis

- **Essaie (5 minutes) :** fabrique un donjon ou une base sur Mars avec les trois réglages de couleur.
- **Va plus loin :** construis une salle plus grande avec des couloirs (garde chaque mur sur la grille de 32 pixels).
- **Invente :** rends la rotation plus rapide ou plus lente en changeant le 3 et le -3.

## Vocabulaire

| Terme | Ce que cela veut dire |
| 2.5D (raycast) | Une image à la première personne dessinée à partir d'une salle 2D, comme dans Wolfenstein 3D |
| Caméra | L'objet à partir duquel la vue est dessinée (ici, le joueur) |
| Angle de vue | La direction dans laquelle tu regardes, en degrés (0 = droite, 90 = haut) |
| Champ de vision | La largeur de la vue, en degrés |
| Taille de case | La taille d'une case de la grille (32 pixels) ; les murs doivent être sur cette grille |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi appelle-t-on cela 2.5D et non 3D ?
2. Pourquoi le joueur a-t-il besoin d'un événement **Quand collision avec obj_wall** sans aucune action ?
3. Que signifie *Relatif* quand on règle l'angle de vue ?

## Mes notes

[[notes:10]]
