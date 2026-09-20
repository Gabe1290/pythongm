# PyGameMaker — Tutoriel 14 : 2.5D, ATH et minicarte — Guide de l'enseignant·e

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > 2.5D : ATH et minicarte**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves poursuivent le jeu du Tutoriel 13. Les leçons 2.5D sont **masquées dans l'édition débutant** : changez d'abord l'édition. C'est la dernière leçon de la série.

## Vue d'ensemble

Les élèves ajoutent un ATH au jeu à la première personne en trois phases : texte du score et des vies, une minicarte, et une barre d'état façon DOOM. Notions nouvelles : l'**événement Dessin par-dessus la vue 3D**, pourquoi l'objet de l'ATH doit être **visible**, des actions d'aide en un bloc (**Dessiner la mini-carte**, **Dessiner l'ATH DOOM**), et le cadre **Viewport Height**.

## Durée suggérée (45 minutes)

| Séquence | Durée | Ce qui se passe |
| Rappel et hypothèses | 5 min | Montrez le tableau de bord d'un tir classique ; demandez quelles informations il montre |
| Phase 1 : score et vies | 10 min | Pages 1-2 |
| Phase 2 : minicarte | 10 min | Page 3 |
| Phase 3 : barre d'état | 15 min | Page 4 |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : score et vies**

- La vue 3D ne dessine que le monde. Tout ce qui se superpose vient d'un événement **Dessin**, ici sur le joueur.
- **L'objet de l'ATH doit être visible.** Son événement Dessin ne s'exécute que tant que l'objet est visible. Le joueur (caméra) n'est jamais dessiné dans la vue 3D mais est bien « visible » : son événement Dessin fonctionne donc. Un objet d'ATH invisible ne dessine silencieusement rien.
- **Couleur de dessin.** *Dessiner du texte* est **noir** par défaut, *Dessiner le score* est **blanc**. Une scène sombre cache le texte noir : commencez donc l'événement Dessin par *Définir la couleur de dessin* en blanc. (Dans le projet de référence, le texte du score s'affiche en blanc sur la vue et les icônes de vies se trouvent en haut à droite.)
- Une icône par vie restante est dessinée à partir d'un sprite (celui du joueur).

**Phase 2 : la minicarte**

- Une seule action dessine toute la carte. Elle a le **nord en haut** (la carte ne tourne pas ; la flèche oui) et montre **uniquement les murs et le joueur**, exprès : une carte qui montre chaque gemme rend un jeu « tout ramasser » trop facile.
- Positionnez-la avec X, Y (coin supérieur gauche, en pixels d'écran) et Size ; dans le projet de référence, une carte de taille 80 en X 230, Y 10 se dessine dans le coin supérieur droit et nulle part ailleurs.
- Les trois couleurs ont de bonnes valeurs par défaut.

**Phase 3 : la barre d'état**

- La barre a besoin de place. **Viewport Height** sur *Activer la vue Raycast* comprime la vue 3D dans la bande du haut ; la valeur par défaut 0 utilise toute la fenêtre (et la barre en cacherait une partie). Pour une salle de 320 pixels et une barre de 64 pixels, Viewport Height = 320 - 64 = 256.
- *Dessiner l'ATH DOOM* : **Y = -1** signifie le bas de la fenêtre, **Width = 0** signifie pleine largeur, et **Height** doit correspondre à la bande réservée (64). Elle affiche une barre de santé avec un nombre, le score et les vies.
- **Santé :** réglez-la dans **Game Start** (*Définir la santé* 100) ; sinon la barre est vide.
- L'Objective Label et le Face Sprite de la barre servent aux défis ; les valeurs par défaut montrent « Keys » et aucun visage.

> TIP: **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`14_raycast_hud_minimap_checkpoints.zip`) : le projet au début de la leçon (le résultat du Tutoriel 13) et le jeu terminé avec la barre d'état et la minicarte. Dans le projet terminé, le texte du score et des vies est remplacé par la barre, comme dans le tutoriel.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| ATH | Les informations dessinées par-dessus la vue du jeu |
| Minicarte | Une petite carte des murs avec le nord en haut |
| Zone d'affichage (viewport) | La partie de la fenêtre utilisée par la vue 3D |
| Barre d'état | Un panneau en bas (santé, score, vies) |
| Cadre (letterbox) | Comprimer la vue pour laisser une bande à autre chose |

## Questions de discussion

- De quelles informations un joueur a-t-il besoin à chaque instant ?
- Pourquoi la minicarte a-t-elle le nord en haut ? Que changerait une rotation ?
- Pourquoi la carte ne doit-elle pas montrer les gemmes ?
- Comment concevriez-vous un ATH pour un autre type de jeu ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 et ajoutez un élément d'ATH à la fois.
- **Approfondissement :** une carte qu'on active avec M ; un visage dans la barre ; des monstres qui retirent 25 de santé ; un compteur d'objectif.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-B, 4-A.

**Partie B :** 1. Dessiner le score. 2. Définir la couleur de dessin (blanc). 3. Dessiner la mini-carte. 4. Viewport Height sur Activer la vue Raycast. 5. Dessiner l'ATH DOOM.

**Partie C :**

1. Viewport Height 480 - 60 = 420 ; la Height de la barre est 60.
2. La flèche tourne ; les murs et la carte ne tournent pas (le nord reste en haut).
3. La couleur du texte est noire sur une scène sombre (pas de Définir la couleur de dessin), ou l'objet est invisible ou n'a pas d'événement Dessin.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : 2.5D, ATH et minicarte

| Niveau | Ce que montre le projet |
| 4 - Complet | Score et vies (ou la barre d'état) sont visibles et corrects ; une minicarte avec une flèche ; un Viewport Height correct avec une barre d'état qui ne cache pas la vue ; la santé est réglée |
| 3 - Fonctionnel | Le texte de l'ATH et la minicarte fonctionnent ; la barre d'état manque ou cache une partie de la vue |
| 2 - À moitié | Seul le score est affiché |
| 1 - Commencé | L'objet d'ATH existe mais rien n'est dessiné |

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a vu l'ATH par-dessus la vue 3D
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
