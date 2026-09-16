# PyGameMaker — Tutoriel 1 : Premiers pas

## Comment utiliser cette fiche

Cette fiche suit les 4 pages du tutoriel intégré, disponible dans
**Aide > Tutoriels > Premiers pas**. Lisez chaque partie ici, puis
faites la partie correspondante sur votre écran — les titres des
sections ci-dessous correspondent aux titres des pages du tutoriel.
Cochez les cases au fur et à mesure, et utilisez la section **Mes
notes** à la fin pour écrire ce que vous voulez retenir.

## Partie 1 : Bienvenue dans PyGameMaker

PyGameMaker est un logiciel de création de jeux vidéo visuel, dans le
même esprit que des outils comme GameMaker Studio. Vous construisez
des jeux 2D en créant des **ressources** — des sprites (images), des
objets (des éléments qui se comportent d'une certaine façon) et des
salles (les niveaux) — puis en les reliant entre eux. Aucune
expérience de programmation n'est nécessaire pour commencer : le
système visuel de PyGameMaker est conçu pour les débutants.

À la fin de cette série de tutoriels, vous serez capable de :

- Naviguer dans l'interface de PyGameMaker en toute confiance
- Créer et gérer les ressources du jeu (sprites, objets, salles)
- Ajouter des comportements aux objets en utilisant des événements et des actions
- Tester et exporter vos propres jeux

> TIP: Vous pouvez fermer le panneau de tutoriel à tout moment avec le
> bouton « Fermer » en haut. Pour le rouvrir plus tard, utilisez
> **Aide > Tutoriels** dans le menu.

## Partie 2 : L'interface de PyGameMaker

Avant de construire quoi que ce soit, prenez un moment pour regarder
autour de vous. La fenêtre de PyGameMaker est divisée en trois zones
principales.

### 1. Arborescence des ressources (panneau gauche)

C'est ici que vivent toutes les ressources de votre projet, organisées
par type :

- **Sprites** — les images et animations utilisées par votre jeu
- **Sons** — effets sonores et musique
- **Objets** — les entités du jeu qui font réellement quelque chose
- **Salles** — les niveaux ou écrans de votre jeu

Faites un clic droit sur une catégorie pour créer une nouvelle
ressource de ce type.

### 2. Zone d'édition (centre)

C'est ici que vous éditez réellement les choses. Double-cliquez sur une
ressource dans l'arborescence, et son éditeur s'ouvre ici dans un
onglet :

- L'**éditeur de sprites** permet de visualiser et dessiner des sprites
- L'**éditeur d'objets** permet de définir ce que fait un objet, à l'aide d'événements
- L'**éditeur de salles** permet de concevoir un niveau en y plaçant des objets

### 3. Panneau des propriétés (panneau droit)

Affiche les réglages de l'élément actuellement sélectionné. Quand vous
éditez une salle ou un objet, c'est ici que vous modifiez ses détails.

### Menus principaux

- **Fichier** — créer, ouvrir et enregistrer des projets
- **Ressources** — créer et importer des ressources de jeu
- **Compilation** — tester et exporter votre jeu
- **Aide** — tutoriels et documentation

> TIP: Appuyez sur **F5** à tout moment pour tester rapidement votre jeu !

## Partie 3 : Créez votre premier projet

C'est maintenant le moment de construire quelque chose ! Suivez ces
six étapes dans l'ordre. Chacune explique ce que vous faites et
pourquoi, avant de vous dire sur quoi cliquer.

- [ ] **1. Créer un nouveau projet.** Chaque jeu commence par un projet, qui est un dossier contenant toutes ses ressources. Allez dans **Fichier > Nouveau projet** (ou appuyez sur **Ctrl+N**), donnez un nom à votre projet et choisissez où l'enregistrer.
- [ ] **2. Créer un sprite.** Un sprite est l'image qu'utilisera votre personnage (ou tout autre objet). Faites un clic droit sur **Sprites**, choisissez **Créer un sprite**, et nommez-le `spr_player`. Importez ensuite une image existante, ou dessinez un personnage simple dans l'éditeur de sprites.
- [ ] **3. Créer un objet.** Un sprite n'est qu'une image — un objet est ce qui apparaît et se comporte réellement dans votre jeu. Faites un clic droit sur **Objets**, choisissez **Créer un objet**, nommez-le `obj_player`, et assignez-lui le sprite que vous venez de créer dans ses propriétés.
- [ ] **4. Créer une salle.** Une salle est un niveau ou un écran de votre jeu. Faites un clic droit sur **Salles**, choisissez **Créer une salle**, et nommez-la `room_game`. Ce sera votre tout premier niveau.
- [ ] **5. Placer votre objet.** Un objet n'apparaît dans le jeu qu'une fois placé dans une salle. Double-cliquez sur votre salle pour ouvrir l'éditeur de salles, sélectionnez `obj_player` dans la liste, puis cliquez dans la salle pour le placer.
- [ ] **6. Tester votre jeu.** Appuyez sur **F5** (ou allez dans **Compilation > Tester le jeu**). Une fenêtre s'ouvrira montrant votre salle, avec l'objet que vous avez placé dedans !

> DONE: Félicitations ! Vous venez de créer votre premier projet
> PyGameMaker. Il ne fait pas encore grand-chose — votre objet ne
> bougera pas et ne réagira à rien — mais vous apprendrez à ajouter des
> comportements dans les prochains tutoriels.

## Partie 4 : Un aperçu de la suite

Maintenant que vous connaissez les bases, voici un aperçu de ce qui
arrive ensuite. Vous n'avez rien à faire aujourd'hui — lisez juste
cette partie pour savoir ce qui vous attend.

- **Ajouter du mouvement** — utiliser un événement Clavier et des actions comme « Déplacer dans une direction » pour que votre objet réagisse aux touches
- **Détection des collisions** — faire réagir les objets quand ils se touchent, par exemple s'arrêter devant un mur
- **Programmation visuelle avec Blockly** — construire des comportements en connectant des blocs au lieu d'écrire du code
- **Salles multiples** — créer plusieurs niveaux et passer de l'un à l'autre
- **Exporter votre jeu** — transformer votre projet terminé en un jeu que d'autres personnes peuvent jouer, par exemple sous forme de page web

> INFO: Besoin d'aide ? Demandez à votre enseignant·e, ou appuyez sur
> **F1** dans PyGameMaker pour ouvrir la documentation.

## Vocabulaire

| Terme | Ce que cela signifie |
| Ressource (Asset) | Tout élément de votre projet — un sprite, un son, un objet ou une salle |
| Sprite | Une image (ou animation) utilisée pour dessiner quelque chose à l'écran |
| Objet | Une entité de jeu — ce qui apparaît et se comporte réellement dans une salle |
| Salle | Un niveau ou un écran de votre jeu, où l'on place les objets |

## Mes notes

[[notes:14]]
