# PyGameMaker — Tutoriel 2 : Votre premier jeu — Guide de l'enseignant·e

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Votre premier jeu : Attrape l'étoile**, 5 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 1 (projet, sprite, objet, salle, F5).

## Vue d'ensemble

Les élèves construisent un jeu complet et jouable en quatre phases, et le testent après chacune : un joueur qui se déplace, des étoiles qui tombent, attraper et marquer, et les finitions. Notions nouvelles : les **événements et actions** (clavier, création, alarme, collision, dessin, pas, hors de la salle), un objet **générateur** et le **score**.

> INFO: L'idée essentielle de la leçon est « un objet réagit à des événements ». Si un élève sait dire « quand la flèche est maintenue, la vitesse horizontale du joueur est réglée à -5 », il a compris.

## Durée suggérée (45 à 60 minutes)

Le tutoriel annonce 15 à 20 minutes pour un élève à l'aise ; en classe, prévoyez plus.

| Séquence | Durée | Ce qui se passe |
| Rappel et hypothèses | 5 min | Demandez : « Comment un objet pourrait-il bouger ? » Montrez le jeu terminé au projecteur |
| Phase 1 : joueur mobile | 10-15 min | Pages 1-2 ; vérifiez que chaque élève fait bouger le joueur |
| Phase 2 : étoiles qui tombent | 10-15 min | Page 3 ; le générateur est le plus difficile, circulez |
| Phase 3 : attraper et marquer | 10-15 min | Page 4 |
| Phase 4 et défis | 5-10 min | Page 5 ; les élèves rapides prennent les défis |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |

Pour une séance de 45 minutes, faites les phases 1 à 3 et laissez la phase 4 en devoir.

## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : joueur mobile**

- Les trois événements clavier doivent tous être sur `obj_player`. L'erreur la plus courante : les ajouter à la salle, ou oublier **Aucune touche**, ce qui fait glisser le joueur indéfiniment.
- *Définir la vitesse horizontale à -5* va à gauche, *5* va à droite. Demandez pourquoi l'une est négative.
- **Normal :** le joueur peut sortir de l'écran. Ne corrigez pas encore ; la phase 4 s'en charge.

**Phase 2 : étoiles qui tombent**

- L'événement Création de l'étoile règle la vitesse verticale à 3. Les élèves oublient souvent d'assigner le sprite à `obj_star`.
- Le générateur n'a **pas de sprite** et doit être placé dans la salle. Si aucune étoile n'apparaît, vérifiez cela en premier.
- L'événement Alarme doit relancer l'alarme à sa fin, sinon une seule étoile apparaît.
- À la cadence par défaut de 60 pas par seconde, *Définir l'alarme 0 à 60* crée **une étoile par seconde**. Demandez comment en obtenir 2 par seconde (régler 30).

**Phase 3 : attraper et marquer**

- Utilisez **Détruire l'autre instance**. Détruire « cette » instance supprime le joueur au lieu de l'étoile ; c'est une bonne erreur à provoquer exprès et à discuter.
- Le score est dessiné par un `obj_game_controller` séparé, qui doit être placé dans la salle. Deux objets qui « doivent être placés » (générateur et contrôleur) sont une source fréquente de « rien n'apparaît ».
- Les étoiles qui tombent en bas sont détruites par **Hors de la salle** ; sans cela, elles s'accumulent sans être vues.

**Phase 4 : finitions**

- La vérification des limites est l'étape la moins détaillée du tutoriel : elle dit « si x < 0, définir x = 0 ». Les élèves ont besoin d'un bloc conditionnel (tester une expression) avec la comparaison, puis d'une action « définir x ». Donnez un indice ou montrez-le une fois. Dans le projet de référence, le joueur peut dépasser d'un pas (5 pixels) avant d'être ramené ; c'est normal.
- Le tutoriel suggère un arrière-plan « couleur d'espace sombre ». Le texte du score est blanc, il reste donc lisible sur les couleurs sombres.

> TIP: **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`02_first_game_checkpoints.zip`) : un projet pour la fin de chaque phase. Donnez à un élève bloqué le projet de la phase précédente pour qu'il continue au lieu de prendre du retard.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| Événement | Quelque chose qui se passe (touche maintenue, alarme qui se déclenche, collision) |
| Action | Un bloc qui fait quelque chose quand un événement se produit |
| Alarme | Un minuteur ; quand il atteint 0, son événement s'exécute |
| Générateur | Un objet invisible dont le rôle est d'en créer d'autres |
| Instance | Une copie d'un objet dans une salle (chaque étoile est une instance de `obj_star`) |

## Questions de discussion

- Pourquoi le générateur est-il invisible ? (C'est un auxiliaire ; les joueurs n'ont pas à le voir.)
- Que changerait une alarme de 120 au lieu de 60 ?
- Pourquoi faut-il *Détruire l'autre instance* et pas simplement *Détruire* ?
- Comment le jeu sait-il qu'une étoile a touché le joueur ? (Événement de collision.)

## Différenciation

- **Soutien :** travail en binômes ; donnez le projet de la phase précédente ; laissez les élèves importer une image plutôt que dessiner.
- **Approfondissement :** les trois niveaux de défis de la fiche ; ajouter des vies, des étoiles plus rapides quand le score monte, ou une bombe.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-B, 4-A.

**Partie B :** 1. Clavier : Flèche gauche (maintenue). 2. Création (sur `obj_star`). 3. En collision avec `obj_star` (sur le joueur). 4. Hors de la salle (sur `obj_star`). 5. Dessin (sur le contrôleur).

**Partie C :**

1. Dans l'événement **Création** du générateur (pour lancer le minuteur) et à la fin de **Alarme 0** (pour le relancer, afin que les étoiles continuent d'arriver).
2. Une par seconde (60 pas à 60 pas par seconde). Régler l'alarme à 30 pour en avoir deux fois plus.
3. Le joueur serait détruit en touchant une étoile (le jeu semblerait s'arrêter) ; *Détruire l'autre instance* supprime l'étoile.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Attrape l'étoile

| Niveau | Ce que montre le jeu |
| 4 - Complet | Le joueur bouge et reste à l'écran ; les étoiles apparaissent à des endroits aléatoires ; attraper rapporte 10 et supprime l'étoile ; le score s'affiche ; les étoiles ratées sont nettoyées |
| 3 - Fonctionnel | Mouvement, étoiles et score fonctionnent ; un élément de finition manque (limites, nettoyage ou affichage) |
| 2 - À moitié | Le joueur bouge et les étoiles tombent, mais attraper ou marquer ne fonctionne pas |
| 1 - Commencé | Le joueur bouge ; pas d'étoiles ni de score |

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 3 (une étoile peut être attrapée)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
