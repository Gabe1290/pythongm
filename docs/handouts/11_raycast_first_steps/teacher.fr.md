# PyGameMaker — Tutoriel 11 : 2.5D, premiers pas — Guide de l'enseignant·e

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > 2.5D : Premiers pas**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 2 et, idéalement, le Tutoriel 6 (murs solides). C'est la première des quatre leçons 2.5D (11 à 14).

> INFO: Les leçons 2.5D sont **masquées dans l'édition débutant**. Changez l'édition dans les préférences avant la leçon, sinon les élèves ne les verront pas dans la liste des tutoriels.

## Vue d'ensemble

Les élèves construisent une salle entourée de murs et la regardent à la première personne, comme dans Wolfenstein 3D. Notions nouvelles : une **vue raycast (2.5D)**, l'**objet caméra** (ici le joueur), l'**angle de vue**, la marche dans la direction du regard, et des **blocs solides qui deviennent des murs**. C'est de la 2.5D, pas de la 3D : tout a encore une position 2D normale et les murs fonctionnent comme n'importe quel objet solide.

## Durée suggérée (45 minutes)

| Séquence | Durée | Ce qui se passe |
| Introduction et démonstration | 5 min | Montrez la vue terminée ; demandez comment une salle plate peut sembler en 3D |
| Phase 1 : salle et murs | 15 min | Pages 1-2 ; plus de 30 blocs à placer (glisser pour placer plus vite) |
| Phase 2 : caméra et commandes | 15 min | Page 3 |
| Phase 3 : tester et régler | 5-10 min | Page 4 ; un réglage à la fois |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : salle et murs**

- Tout se place sur une **grille de 32×32**. Le sprite du mur doit faire exactement 32×32 : un bloc solide à peu près carré bloque les quatre côtés de sa case.
- La salle fait 320×320 (10×10 cases). **La fenêtre du jeu prend la taille de la salle** : une petite salle donne donc une petite fenêtre.
- Les murs doivent être **Solides** ; le joueur n'est **pas** solide. Des blocs hors de la grille créent des trous et des bords de mur bizarres.
- Le sprite du joueur (16×16) n'est jamais vu, mais chaque objet doit en avoir un.

**Phase 2 : caméra et commandes**

- L'objet joueur exécute *Activer la vue Raycast* dans son événement **Quand créé** : Field of View 66, Cell Size 32, Render Distance 20. Laissez Camera Object vide (= cet objet).
- Rotation : *Définir l'angle de vue* 3 et -3 avec **Relatif** activé (s'ajoute à l'angle actuel). La gauche est une rotation positive.
- La marche utilise *Définir direction et vitesse* avec la direction `facing_angle` (avant) ou `facing_angle+180` (arrière), vitesse 3 ; **Aucune touche** règle la direction 0 et la vitesse 0.
- **N'oubliez pas le Quand collision avec obj_wall vide.** Un objet solide n'arrête qu'un autre objet qui a un événement de collision pour lui, même vide. Sans lui, le joueur sort de la salle (dans le projet de référence, il s'est retrouvé à plus de 400 pixels dehors). Avec lui, le joueur reste retenu à l'intérieur.
- Les murs sont lus une seule fois au démarrage de la salle : ils sont donc fixes.

**Phase 3 : tester et régler**

- Suggérez de changer un réglage à la fois (Field of View, Render Distance, les trois couleurs, Columns). Demandez aux élèves de prévoir avant de lancer.
- Columns : moins de colonnes se dessinent plus vite mais paraissent plus grossières.

> TIP: **Projets de référence.** Téléchargez le projet terminé de la leçon sur le wiki (`11_raycast_first_steps_checkpoints.zip`). Donnez à un élève bloqué le projet terminé pour qu'il se compare.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| Raycast / 2.5D | Une image à la première personne dessinée à partir d'une salle 2D |
| Caméra | L'objet à partir duquel la vue est dessinée |
| Angle de vue | La direction du regard, en degrés (0 droite, 90 haut, 180 gauche, 270 bas) |
| Champ de vision | La largeur de la vue |
| Solide | Objets qui bloquent le mouvement (les murs) |

## Questions de discussion

- Pourquoi appelle-t-on ce jeu 2.5D et non 3D ?
- Pourquoi l'image reste-t-elle correcte quand on tourne alors que la salle est plate ?
- Que change un champ de vision très large ? Très étroit ?
- À quelle ancienne leçon la collision avec les murs vous fait-elle penser ?

## Différenciation

- **Soutien :** donnez le projet terminé et laissez les élèves ne changer que les réglages.
- **Approfondissement :** une salle plus grande avec des couloirs ; changer la vitesse de rotation ; une couleur de mur différente par salle.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-B, 3-D, 4-A.

**Partie B :** 1. Définir l'angle de vue (une valeur positive tourne à gauche). 2. Définir direction et vitesse avec la direction `facing_angle`. 3. Render Distance (la diminuer). 4. Les couleurs de mur, de sol et de plafond (plus sombres). 5. Cocher Solide sur l'objet du bloc.

**Partie C :**

1. Chaque objet a besoin d'un sprite dans ce moteur, même s'il n'est jamais dessiné.
2. Que `obj_wall` est Solide, et que le joueur a un événement **Quand collision avec obj_wall** (il peut être vide).
3. 180 est la gauche. Marcher en arrière utilise **Clavier : Flèche bas (maintenue)** avec la direction `facing_angle+180`.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : 2.5D, premiers pas

| Niveau | Ce que montre le projet |
| 4 - Complet | Une salle entourée de murs alignés sur la grille ; la vue raycast est activée ; tourner et marcher fonctionnent dans la direction du regard ; les murs arrêtent le joueur ; l'élève a essayé au moins deux réglages |
| 3 - Fonctionnel | La vue et les commandes fonctionnent, mais les murs n'arrêtent pas le joueur ou quelques blocs sont hors de la grille |
| 2 - À moitié | La salle et les murs existent, mais la vue à la première personne n'est pas activée |
| 1 - Commencé | Les objets existent, mais il n'y a pas de salle ou pas de mur |

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a vu la vue à la première personne
- [ ] Notez qui aura besoin du projet terminé la prochaine fois
