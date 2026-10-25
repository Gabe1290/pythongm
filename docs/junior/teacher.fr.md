# PyGameMaker Junior : guide de l'enseignant

## Ce qu'est Junior

Junior est une édition simplifiée de PyGameMaker pour des élèves d'environ
8 à 9 ans. C'est le même programme et les mêmes fichiers de projet que les
autres éditions. Elle ne fait que masquer des éléments : un projet créé en
Junior s'ouvre normalement en Débutant, Avancé ou Développement, et
inversement.

## L'activer

1. Ouvre **Outils > Préférences > Général > Édition de l'IDE** et choisis **Junior**.
2. Clique sur OK, puis **redémarre l'IDE**. L'apparence, la police et les
   menus s'appliquent au démarrage.
3. Pour revenir en arrière, refais les mêmes étapes et choisis une autre
   édition. Les Préférences restent dans le menu Outils en Junior pour cette raison.

Remarques :
- **Ordinateurs partagés :** l'édition est un réglage par utilisateur. Pour
  configurer plusieurs machines, mets `"edition": "junior"` dans
  `.pygamemaker/config.json` dans le dossier personnel de l'utilisateur.
- **Thème et police :** si quelqu'un a déjà changé le thème ou la police
  dans les Préférences d'une machine, ce choix l'emporte sur la police plus
  grande et le thème contrasté de Junior. Réinitialise-les dans les
  Préférences si la machine ne change pas d'aspect.
- **Boîte à outils Blockly :** l'ensemble de blocs de Junior s'applique aux
  **nouveaux** projets. Un projet existant garde l'ensemble de blocs avec
  lequel il a été enregistré. Changer d'édition dans les Préférences applique
  aussi le nouvel ensemble de blocs au projet ouvert.
- **Catégories de la barre latérale :** Sprites, Sounds, Backgrounds, Objects
  et Rooms restent en anglais dans l'arborescence des ressources, même en
  français. Un élève qui suit sa fiche verra donc **Rooms** dans la liste à
  gauche, pas « Salles » (la fiche de l'élève utilise maintenant « Room »
  pour cette raison).

## Ce que voient les élèves

| Zone | En Junior |
|---|---|
| Apparence | Police plus grande, icônes plus grandes, thème contrasté |
| Menu Fichier | Nouveau, Ouvrir, Enregistrer, Enregistrer le projet sous, Fermer le projet, Récents, **Exporter en HTML5**, Quitter |
| Menu Ressources | Importer sprite, son, arrière-plan ; **Créer un sprite**, Créer objet, salle |
| Menu Compiler | **Tester le jeu** |
| Menu Outils | Préférences, Restaurer les ressources supprimées, Langue |
| Éditeur d'objet | **Blockly seulement.** Pas d'onglet Liste d'événements, pas d'onglet Éditeur de code |
| Boîte à outils Blockly | 46 blocs, exactement ceux utilisés par les tutoriels Junior |
| Clic droit dans Blockly | Dupliquer et Supprimer sur les blocs ; Annuler, Rétablir et Nettoyer sur l'espace de travail |
| Export | HTML5 seulement |

Masqués volontairement : les autres exports (bureau, Android, Kivy, zip),
l'import GameMaker, les réglages de sauvegarde automatique, les Paramètres du
projet, Rechercher et remplacer, les scripts et les polices, les paquets
d'objets et de salles, Déboguer et Compiler, Configurer les blocs d'action et
les outils de maintenance.

Toujours visible : le petit panneau « Standard » des événements, à gauche de
l'éditeur d'objet. Il affiche les événements construits par Blockly. Les
élèves peuvent l'ignorer.

## Plan de leçon suggéré (environ 60 minutes)

| Temps | Activité |
|---|---|
| 0-10 | Visite : barre d'outils, ressources, bouton de lecture. Ouvrir un exemple depuis l'onglet Bienvenue et appuyer sur F5 |
| 10-25 | Fiche de l'élève, parties 1 à 3 : créer un projet, puis dessiner un sprite |
| 25-45 | Parties 4 et 5 : faire bouger un objet, construire une salle, jouer |
| 45-55 | Partie 6 : exporter en HTML5 et l'ouvrir dans le navigateur |
| 55-60 | Partage, et les questions « Réfléchis » comme ticket de sortie |

Pour une période de 45 minutes, fais les parties 1 à 5 et garde l'export pour
la fois suivante.

**Partie 7 (bonus, optionnelle) : ramasse des fruits.** Pour les élèves qui
finissent vite : un objet `obj_fruit` que le héros ramasse par collision,
avec un score affiché. Pas dans le minutage ci-dessus, propose-la plutôt
comme activité libre une fois la partie 6 terminée, ou en devoir si le
temps manque.

Leçons suivantes : les tutoriels Junior sous **Aide > Tutoriels** :
Premiers pas, Attrapez l'étoile, Pong, Breakout, Fusion de Fruits,
Panier de Fruits. Chacun a sa propre fiche de l'élève et son guide de
l'enseignant.

## Problèmes courants

| Symptôme | Cause et solution |
|---|---|
| L'objet ne bouge pas | Aucun bloc sous l'événement, ou l'objet n'est pas placé dans la salle |
| Le héros glisse sans fin | Il faut **Clavier: Aucune touche** avec **arrêter le mouvement** |
| Sprite invisible | L'objet n'a pas de sprite choisi |
| « Nom déjà utilisé » | Un sprite portant ce nom existe. Choisis un autre nom |
| Un nom est refusé | Utilise des lettres, des chiffres et des tirets bas, sans espace ni caractère spécial |
| Supprimé par erreur | Outils > Restaurer les ressources supprimées |
| Fenêtre de jeu grise | Souvent un ordinateur lent ou à court de mémoire. Attends, puis réessaie |
| Le score n'augmente pas (partie 7) | L'événement collision doit être sur **obj_heros** (pas sur obj_fruit), avec obj_fruit choisi dans le menu déroulant |
| Le jeu exporté a besoin d'internet | Les jeux qui utilisent du code Python chargent un environnement en ligne. Quand on te le demande, choisis de l'inclure pour un usage hors ligne |
| Un exemple utilise un bloc introuvable | Les exemples peuvent utiliser des blocs hors de l'ensemble Junior. Ils fonctionnent quand même ; les élèves ne peuvent simplement pas rajouter ce bloc |

## Limites à connaître

- Les élèves ne peuvent pas ajouter les blocs que Débutant a et que Junior n'a
  pas, par exemple Définir la gravité, Si collision et Pause, même quand un
  exemple les utilise.
- Un sprite démarre à 32 sur 32 pixels. Les élèves peuvent le redimensionner
  dans l'éditeur de sprites.
- HTML5 est le seul moyen de partager. Un enseignant qui a besoin d'un autre
  format peut passer l'édition en Débutant et utiliser **Compiler > Exporter le jeu**.

## Évaluer le travail

Demande à chaque élève de montrer : un sprite qu'il a dessiné, un objet qui
bouge, une salle, et le fichier `.html` exporté qui fonctionne dans le
navigateur.
