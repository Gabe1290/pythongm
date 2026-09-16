# PyGameMaker — Tutoriel 1 : Premiers pas — Guide de l'enseignant·e

Document d'accompagnement pour guider les élèves à travers le tutoriel
intégré (**Aide > Tutoriels > Premiers pas**, 4 pages) et la fiche élève
correspondante. Aucune expérience de programmation n'est nécessaire, ni
pour vous ni pour les élèves.

## Vue d'ensemble

Ce premier tutoriel est une visite guidée de l'interface suivie d'un
projet pratique. À la fin, chaque élève aura un projet avec un sprite, un
objet et une salle, et aura appuyé sur **F5** pour le voir fonctionner.

> INFO: L'objet placé par les élèves ne bougera pas encore et ne réagira
> à rien — les événements et les comportements sont introduits au
> Tutoriel 2 (« Premier jeu »). Si un·e élève demande « pourquoi il ne
> se passe rien ? », c'est le résultat attendu et correct pour cette
> leçon, pas une erreur.

## Durée suggérée (environ 45 minutes)

Ce sont des points de départ — adaptez librement selon votre classe et
votre salle informatique.

| Étape | Durée | Déroulement |
| Accueil et discussion | 5 min | Ouvrez le panneau de tutoriel (page 1), présentez ce que couvre la série |
| Visite de l'interface | 10 min | Page 2 — montrez les 3 zones en direct sur votre écran / au projecteur |
| Pratique : premier projet | 20-25 min | Page 3 — les 6 étapes ci-dessous, circulez dans la salle |
| Test et célébration | 5 min | Chaque élève appuie sur F5 et voit son objet apparaître |
| Conclusion / la prochaine fois | 5 min | Page 4 — aperçu de ce qu'apporte le Tutoriel 2 |

## Déroulé étape par étape et difficultés fréquentes

1. **Nouveau projet** (`Fichier > Nouveau projet`, `Ctrl+N`) — Demandez
aux élèves d'enregistrer dans un endroit qu'ils retrouveront facilement
(leur propre dossier / le lecteur partagé de la classe). Décidez de cette
convention avant le cours.
2. **Créer un sprite** (`spr_player`) — Le préfixe `spr_` est une
convention de nommage de PyGameMaker, pas une obligation, mais
l'adopter dès maintenant garde les projets suivants bien organisés. Les
élèves peuvent importer une image ou dessiner la leur ; dessiner prend
plus de temps, donc fixez une limite (par ex. « 2 minutes, juste une
forme rapide ») si le temps est compté.
3. **Créer un objet** (`obj_player`) — **Erreur la plus fréquente** :
oublier d'assigner le sprite à l'objet. Si le personnage d'un·e élève
n'apparaît pas plus tard, c'est presque toujours la raison — vérifiez
d'abord le champ Sprite de l'objet.
4. **Créer une salle** (`room_game`) — Rien de visuel ne se passe à
cette étape ; c'est normal, ce n'est pas une erreur.
5. **Placer l'objet** — **Erreur fréquente** : ouvrir l'éditeur de
salle mais oublier de réellement sélectionner `obj_player` dans la
liste des objets avant de cliquer dans la salle, donc rien n'est placé.
Il n'y a pas de « bonne » position pour cet exercice — n'importe où
dans la salle convient.
6. **Tester le jeu** (`F5` ou `Compilation > Tester le jeu`) — Une
fenêtre s'ouvre montrant la salle et le sprite placé. Il ne bougera pas
et ne réagira pas aux touches pour l'instant — ce sera la prochaine
leçon.

> TIP: La fenêtre de test du jeu. Quand un·e élève appuie sur F5, la
> fenêtre de PyGameMaker se réduit automatiquement pendant la durée du
> test et revient dès que l'élève ferme la fenêtre du jeu. Cela évite
> que la fenêtre du jeu ne se retrouve cachée derrière l'éditeur. Sur la
> plupart des postes, l'éditeur revient aussi automatiquement au premier
> plan ; sur certaines configurations Linux, il peut seulement clignoter
> dans la barre des tâches au lieu de revenir au premier plan — dans ce
> cas, dites aux élèves de simplement cliquer dessus une fois.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
| Ressource (Asset) | Tout élément de votre projet : un sprite, un son, un objet ou une salle |
| Sprite | Une image (ou animation) utilisée pour dessiner quelque chose à l'écran |
| Objet | Une entité de jeu — ce qui apparaît et se comporte réellement dans une salle |
| Salle | Un niveau ou un écran de jeu ; l'endroit où l'on place les objets |

## S'il reste du temps / aperçu

D'après la page « Prochaines étapes » du tutoriel : la prochaine leçon
ajoute le **mouvement** (un événement Clavier) et présente la
programmation visuelle **Blockly**. Si un·e élève termine en avance et
demande ce qui suit, vous pouvez le mentionner sans hésiter, mais il
n'est pas nécessaire de le faire essayer aujourd'hui — il n'y a pas
encore d'événement auquel l'accrocher.

## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a appuyé sur F5 et a vu son objet apparaître dans la salle
- [ ] Notez qui souhaite continuer à explorer — de bons binômes pour
aider un·e camarade en difficulté la prochaine fois

> INFO: Série complète des tutoriels : `Aide > Tutoriels` dans
> PyGameMaker. Documentation écrite et exemples de projets
> supplémentaires : le wiki du projet.
