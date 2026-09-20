# PyGameMaker — Tutoriel 13 : 2.5D, objectifs, gemmes et monstres — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-13-raycast-goals-monsters_fr.pdf) · [ODT](downloads/Teacher-Guide-13-raycast-goals-monsters_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/13_raycast_goals_monsters_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > 2.5D : Objectifs, gemmes et monstres**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves poursuivent leur salle du Tutoriel 11 (les textures du Tutoriel 12 sont facultatives). Les leçons 2.5D sont **masquées dans l'édition débutant** : changez d'abord l'édition.

## Vue d'ensemble

Les élèves transforment la salle à la première personne en jeu en trois phases : gemmes et score, un monstre qui patrouille et des vies, et une sortie conditionnée aux gemmes. Notions nouvelles : les **panneaux** (billboards : les objets non solides avec un sprite sont dessinés comme des images qui font face au joueur, cachées derrière les murs), le **score et les vies** avec **Game Start**, et la condition **Tester le nombre d'instances**.

## Durée suggérée (45 à 60 minutes)

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Demandez : comment une image plate peut-elle représenter un objet dans un monde 3D ? |
| Phase 1 : gemmes et score | 15 min | Pages 1-2 |
| Phase 2 : monstre et vies | 15 min | Page 3 |
| Phase 3 : la sortie | 10-15 min | Page 4 |
| Jouer et échanger | 5 min | Les élèves jouent les labyrinthes des autres |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : gemmes et score**

- Tout objet **visible et non solide** avec un sprite est dessiné automatiquement comme un panneau, mis à l'échelle selon la distance et **caché derrière les murs**. Une gemme solide deviendrait un mur. Le joueur est la caméra et n'est jamais dessiné comme un panneau.
- L'événement **En collision avec obj_player** de la gemme la détruit ; son événement **Destroy** ajoute 10 au score. Dans le projet de référence, une gemme donne 10 points et disparaît.
- **Le score et les vies vont dans Game Start, pas dans Création.** Création se relance à chaque redémarrage de la salle, et le monstre redémarre la salle. Avec Création, les vies seraient remises à fond après chaque mort. (Game Start ne s'exécute qu'une fois.) C'est le même piège qu'au Tutoriel 7.
- Le score n'est pas encore affiché : la vue 3D ne dessine que le monde. Cela vient au Tutoriel 14.
- Placez les gemmes hors des murs ; une gemme inaccessible rendra la sortie impossible plus tard.

**Phase 2 : le monstre et les vies**

- Le monstre est non solide. **Quand créé** : *Commencer à bouger (direction)* gauche et droite, vitesse 2. **Quand collision avec obj_wall** : *Inverser horizontalement*. Placez-le dans un long couloir droit. Dans le projet de référence, il reste dans son couloir et fait demi-tour à chaque bout.
- **En collision avec obj_monster** sur le joueur : *Définir les vies à -1* (relatif) et *Redémarrer la salle*. Une collision se déclenche quand les objets **commencent** à se toucher : rester sur un monstre coûte donc une vie, pas une par image. **No More Lives** : *Redémarrer le jeu*.
- Le redémarrage de la salle remet les gemmes en place, mais les vies et le score sont conservés (réglés dans Game Start).
- Un redémarrage peut causer un second contact si le monstre est juste au départ ; gardez le monstre loin du départ du joueur.

**Phase 3 : la sortie**

- Le but a deux vérifications : *Tester le nombre d'instances de obj_gem égal à 0* (victoire) et *supérieur à 0* (avertissement). Avec des gemmes restantes, la sortie ne fait que protester ; sans gemme, elle termine le jeu. Le paramètre « nombre » est un nombre (0).
- **Afficher un message** attend un clic ; les élèves croient parfois que le jeu s'est figé.
- Une seconde salle avec **Salle suivante** à la sortie est le principal défi du tutoriel : donnez à cette salle son propre objet caméra (avec d'autres textures) et réglez son Camera Object sur `obj_player`.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`13_raycast_goals_monsters_checkpoints.zip`) : le projet au début de la leçon (issu du Tutoriel 11) et le jeu terminé avec une gemme, un monstre et la sortie. Donnez à un élève bloqué le projet terminé pour qu'il se compare.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Panneau (billboard) | Une image qui fait toujours face à la caméra ; utilisée pour les objets non solides |
| Occlusion | Quelque chose de caché derrière un mur |
| Game Start | Un événement qui s'exécute une fois au début de la partie, pas aux redémarrages |
| Nombre d'instances | Le nombre de copies d'un objet, testé avec *Tester le nombre d'instances* |
| Patrouiller | Aller et venir |


## Questions de discussion

- Comment le moteur décide-t-il ce qui est un mur et ce qui est un panneau ?
- Pourquoi un monstre dans un couloir peut-il « surgir » derrière un angle ?
- Pourquoi faut-il régler les vies dans Game Start ?
- Qu'est-ce qui rend un labyrinthe équitable ? (Des gemmes accessibles, un monstre qu'on peut esquiver.)

## Différenciation

- **Soutien :** donnez le projet terminé et laissez les élèves changer les positions et les valeurs ; gardez un seul monstre.
- **Approfondissement :** un second monstre, plus rapide ; une gemme trésor à 50 ; une seconde salle avec ses propres textures ; un chronomètre.

## Corrigé de la feuille d'exercices

**Partie A :** 1-B, 2-D, 3-C, 4-A.

**Partie B :** 1. `obj_gem`, Destroy. 2. `obj_monster`, En collision avec `obj_wall`. 3. `obj_player`, En collision avec `obj_monster`. 4. `obj_goal`, En collision avec `obj_player` (Tester le nombre d'instances de `obj_gem`). 5. `obj_player`, Game Start.

**Partie C :**

1. Non : les panneaux sont cachés derrière les murs tant que rien ne dégage la ligne de vue.
2. Une vie : l'événement de collision se déclenche quand les objets commencent à se toucher, pas à chaque image.
3. La salle recommence et Création s'exécute de nouveau : les vies repassent à 3, tu n'en manques jamais. Il faut Game Start.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : 2.5D, objectifs, gemmes et monstres

| Niveau | Ce que montre le projet |
|---|---|
| 4 - Complet | Les gemmes donnent des points et disparaissent ; le monstre patrouille et coûte une vie qui reste perdue ; la sortie vérifie le nombre de gemmes et gagne ou avertit ; score et vies sont réglés dans Game Start |
| 3 - Fonctionnel | Gemmes, monstre et sortie fonctionnent ; les vies sont remplies par les redémarrages, ou la sortie n'est pas conditionnée |
| 2 - À moitié | Les gemmes fonctionnent, mais pas le monstre ni la sortie |
| 1 - Commencé | Les objets existent mais n'apparaissent pas dans la vue à la première personne |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 1 (une gemme peut être ramassée)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
