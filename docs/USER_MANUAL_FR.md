# Manuel d'utilisation de PyGameMaker IDE

**Version 1.0.0-rc.4**
**Un IDE de developpement de jeux visuels inspire de GameMaker pour creer des jeux 2D avec Python**

---

## Table des matieres

1. [Introduction](#1-introduction)
2. [Installation et configuration](#2-installation-et-configuration)
3. [Presentation de l'IDE](#3-presentation-de-lide)
4. [Travailler avec les projets](#4-travailler-avec-les-projets)
5. [Sprites](#5-sprites)
6. [Sons](#6-sons)
7. [Arriere-plans](#7-arriere-plans)
8. [Objets](#8-objets)
9. [Salles](#9-salles)
10. [Reference des evenements](#10-reference-des-evenements)
11. [Reference des actions](#11-reference-des-actions)
12. [Tests et execution des jeux](#12-tests-et-execution-des-jeux)
13. [Exportation des jeux](#13-exportation-des-jeux)
14. [Programmation visuelle Blockly](#14-programmation-visuelle-blockly)
15. [Support du robot Thymio](#15-support-du-robot-thymio)
16. [Parametres et preferences](#16-parametres-et-preferences)
17. [Raccourcis clavier](#17-raccourcis-clavier)
18. [Tutoriels](#18-tutoriels)
19. [Depannage](#19-depannage)

---

## 1. Introduction

PyGameMaker est un IDE de developpement de jeux educatif inspire de GameMaker. Il vous permet de creer des jeux 2D visuellement a l'aide d'un systeme d'evenements/actions par glisser-deposer, sans avoir besoin d'ecrire du code. Il a ete concu avec deux objectifs :

- **Enseigner le developpement de jeux** visuellement grace a une interface intuitive
- **Enseigner la programmation Python** a travers le code source ouvert de l'IDE

PyGameMaker utilise PySide6 (Qt) pour l'interface de l'IDE et Pygame pour le moteur de jeu. Les jeux peuvent etre exportes sous forme d'executables autonomes, d'applications mobiles ou de jeux web HTML5.

### Fonctionnalites principales

- Programmation visuelle par evenements/actions (plus de 80 actions integrees)
- Editeur de sprites avec support des animations
- Editeur de salles avec placement d'instances, couches de tuiles et defilement d'arriere-plan
- Apercu du jeu en temps reel avec F5
- Exportation vers Windows EXE, mobile (Android/iOS via Kivy), HTML5 et robots Thymio
- Integration de Google Blockly pour les blocs de code visuels
- Simulateur de robot educatif Thymio
- Interface multilingue (plus de 8 langues)
- Themes sombre et clair

---

## 2. Installation et configuration

### Configuration requise

- Python 3.10 ou superieur
- PySide6
- Pygame
- Pillow (PIL)

### Installation des dependances

```bash
pip install PySide6 pygame Pillow
```

### Dependances optionnelles

Pour les fonctionnalites d'exportation :

```bash
pip install pyinstaller    # Pour l'exportation EXE
pip install kivy           # Pour l'exportation mobile
pip install buildozer      # Pour les compilations Android
pip install jinja2         # Pour les modeles de generation de code
```

### Lancement de l'IDE

```bash
python main.py
```

La fenetre de l'IDE s'ouvre avec des dimensions par defaut de 1400x900 pixels. La position et la taille de la fenetre sont sauvegardees entre les sessions.

---

## 3. Presentation de l'IDE

### Disposition de la fenetre

L'IDE utilise une disposition a trois panneaux :

```
+-------------------+---------------------------+------------------+
| Arbre des         |    Zone d'edition          |  Proprietes      |
| ressources        |    (Panneau central)       |  (Panneau droit) |
| (Panneau gauche)  |                           |                  |
|                   |   Editeurs a onglets      |  Proprietes      |
|   - Sprites       |   pour sprites, objets    |  contextuelles   |
|   - Sons          |   et salles               |                  |
|   - Arriere-plans |                           |                  |
|   - Objets        |                           |                  |
|   - Salles        |                           |                  |
|   - Scripts       |                           |                  |
|   - Polices       |                           |                  |
+-------------------+---------------------------+------------------+
|                      Barre d'etat                                |
+------------------------------------------------------------------+
```

- **Panneau gauche (Arbre des ressources) :** Affiche toutes les ressources du projet organisees par type. Double-cliquez sur une ressource pour l'ouvrir dans l'editeur.
- **Panneau central (Zone d'edition) :** Espace de travail a onglets pour editer les sprites, objets et salles. Un onglet d'accueil est affiche par defaut.
- **Panneau droit (Proprietes) :** Affiche les proprietes contextuelles de l'editeur actif. Peut etre reduit.
- **Barre d'etat :** Affiche l'etat de l'operation en cours et le nom du projet.

### Barre de menus

#### Menu Fichier

| Commande | Raccourci | Description |
|----------|-----------|-------------|
| Nouveau projet... | Ctrl+N | Creer un nouveau projet |
| Ouvrir un projet... | Ctrl+O | Ouvrir un projet existant |
| Enregistrer le projet | Ctrl+S | Enregistrer le projet actuel |
| Enregistrer sous... | Ctrl+Maj+S | Enregistrer dans un nouvel emplacement |
| Projets recents | | Sous-menu de 10 projets recents maximum |
| Exporter en HTML5... | | Exporter le jeu en fichier HTML unique |
| Exporter en Zip... | | Empaqueter le projet en archive ZIP |
| Exporter vers Kivy... | | Exporter pour deploiement mobile |
| Exporter le projet... | Ctrl+E | Ouvrir la boite de dialogue d'exportation |
| Ouvrir un projet Zip... | | Ouvrir un projet empaquete en ZIP |
| Sauvegarde auto en Zip | | Activer/desactiver la sauvegarde auto en ZIP |
| Activer la sauvegarde auto | | Activer/desactiver la sauvegarde automatique |
| Parametres de sauvegarde auto... | | Configurer l'intervalle de sauvegarde auto |
| Parametres du projet... | | Ouvrir la configuration du projet |
| Quitter | Ctrl+Q | Fermer l'IDE |

#### Menu Edition

| Commande | Raccourci | Description |
|----------|-----------|-------------|
| Annuler | Ctrl+Z | Annuler la derniere action |
| Retablir | Ctrl+Y | Retablir la derniere action annulee |
| Couper | Ctrl+X | Couper la selection |
| Copier | Ctrl+C | Copier la selection |
| Coller | Ctrl+V | Coller depuis le presse-papiers |
| Dupliquer | Ctrl+D | Dupliquer les elements selectionnes |
| Rechercher... | Ctrl+F | Ouvrir la boite de dialogue de recherche |
| Rechercher et remplacer... | Ctrl+H | Ouvrir la recherche et remplacement |

#### Menu Ressources

| Commande | Description |
|----------|-------------|
| Importer un sprite... | Importer des images de sprite (PNG, JPG, BMP, GIF) |
| Importer un son... | Importer des fichiers audio |
| Importer un arriere-plan... | Importer des images d'arriere-plan |
| Creer un objet... | Creer un nouvel objet de jeu |
| Creer une salle... (Ctrl+R) | Creer une nouvelle salle de jeu |
| Creer un script... | Creer un nouveau fichier de script |
| Creer une police... | Creer une nouvelle ressource de police |
| Importer un paquet d'objet... | Importer un paquet .gmobj |
| Importer un paquet de salle... | Importer un paquet .gmroom |

#### Menu Compilation

| Commande | Raccourci | Description |
|----------|-----------|-------------|
| Tester le jeu | F5 | Executer le jeu en mode test |
| Deboguer le jeu | F6 | Executer le jeu avec sortie de debogage |
| Compiler le jeu... | F7 | Ouvrir la configuration de compilation |
| Compiler et executer | F8 | Compiler et executer immediatement |
| Exporter le jeu... | | Exporter le jeu compile |

#### Menu Outils

| Commande | Description |
|----------|-------------|
| Preferences... | Ouvrir les preferences de l'IDE |
| Gestionnaire de ressources... | Ouvrir la fenetre de gestion des ressources |
| Configurer les blocs d'action... | Configurer les blocs Blockly |
| Configurer les blocs Thymio... | Configurer les blocs du robot Thymio |
| Valider le projet | Verifier le projet pour les erreurs |
| Nettoyer le projet | Supprimer les fichiers temporaires |
| Migrer vers la structure modulaire | Mettre a jour le format du projet |
| Langue | Changer la langue de l'interface |
| Programmation Thymio | Sous-menu de programmation robot |

#### Menu Aide

| Commande | Raccourci | Description |
|----------|-----------|-------------|
| Documentation | F1 | Ouvrir la documentation d'aide |
| Tutoriels | | Ouvrir les ressources de tutoriels |
| A propos de PyGameMaker | | Informations de version et de licence |

### Barre d'outils

La barre d'outils fournit un acces rapide aux actions courantes (de gauche a droite) :

| Bouton | Action |
|--------|--------|
| Nouveau | Creer un nouveau projet |
| Ouvrir | Ouvrir un projet existant |
| Enregistrer | Enregistrer le projet actuel |
| Tester | Executer le jeu (F5) |
| Deboguer | Deboguer le jeu (F6) |
| Exporter | Exporter le jeu |
| Importer sprite | Importer une image de sprite |
| Importer son | Importer un fichier audio |
| Thymio | Ajouter un evenement robot Thymio |

### Arbre des ressources

L'arbre des ressources dans le panneau gauche organise les ressources du projet en categories :

**Ressources multimedia :**
- **Sprites** - Images et bandes d'animation pour les objets de jeu
- **Sons** - Effets sonores et fichiers musicaux
- **Arriere-plans** - Images d'arriere-plan et jeux de tuiles

**Logique de jeu :**
- **Objets** - Definitions d'objets de jeu avec evenements et actions
- **Salles** - Niveaux/scenes de jeu avec instances placees

**Ressources de code :**
- **Scripts** - Fichiers de code
- **Polices** - Ressources de polices personnalisees

**Operations du menu contextuel :**
- Cliquez droit sur un en-tete de categorie pour creer ou importer des ressources
- Cliquez droit sur une ressource pour la renommer, supprimer, exporter ou voir ses proprietes
- Double-cliquez sur une ressource pour l'ouvrir dans l'editeur
- Les salles peuvent etre reordonnees (Monter/Descendre/Premier/Dernier)

---

## 4. Travailler avec les projets

### Creer un nouveau projet

1. Choisissez **Fichier > Nouveau projet** (Ctrl+N)
2. Entrez un **Nom de projet**
3. Choisissez un **Emplacement** pour le dossier du projet
4. Selectionnez un **Modele** (optionnel) :
   - **Projet vide** - Un projet vierge
   - **Modele de jeu de plateforme** - Pre-configure pour les jeux de plateforme
   - **Modele de jeu vue de dessus** - Pre-configure pour les jeux en vue de dessus
5. Cliquez sur **Creer le projet**

### Structure du projet

```
MonProjet/
|-- project.json          # Fichier principal du projet
|-- sprites/              # Images et metadonnees des sprites
|   |-- player.png
|   |-- player.json
|-- objects/              # Definitions des objets
|   |-- obj_player.json
|-- rooms/                # Donnees de disposition des salles
|   |-- room_start.json
|-- sounds/               # Fichiers audio et metadonnees
|-- backgrounds/          # Images d'arriere-plan
|-- thumbnails/           # Apercu generes automatiquement
```

### Enregistrer les projets

- **Ctrl+S** enregistre le projet a son emplacement actuel
- **Ctrl+Maj+S** enregistre dans un nouvel emplacement
- La **sauvegarde automatique** peut etre activee dans Fichier > Activer la sauvegarde auto
- Configurez l'intervalle de sauvegarde auto dans Fichier > Parametres de sauvegarde auto

### Ouvrir les projets

- **Ctrl+O** ouvre un dossier de projet
- Les projets recents sont listes dans **Fichier > Projets recents**
- Les projets ZIP peuvent etre ouverts avec **Fichier > Ouvrir un projet Zip**

---

## 5. Sprites

Les sprites sont les images visuelles utilisees par les objets de jeu. Ils peuvent etre des images statiques ou des bandes d'animation avec plusieurs images.

### Creer un sprite

1. Cliquez droit sur **Sprites** dans l'arbre des ressources et choisissez **Importer un sprite...**
2. Selectionnez un fichier image (PNG, JPG, BMP ou GIF)
3. Le sprite apparait dans l'arbre des ressources et s'ouvre dans l'editeur de sprites

### Editeur de sprites

L'editeur de sprites comporte quatre zones principales :

- **Panneau d'outils (Gauche) :** Outils de dessin
- **Canevas (Centre) :** La zone d'edition avec zoom et grille
- **Palette de couleurs (Droite) :** Couleurs de premier plan/arriere-plan et echantillons
- **Chronologie des images (Bas) :** Gestion des images d'animation

#### Outils de dessin

| Outil | Raccourci | Description |
|-------|-----------|-------------|
| Crayon | P | Dessin pixel standard |
| Gomme | E | Supprimer les pixels (rendre transparent) |
| Pipette | I | Prelever une couleur du canevas |
| Remplissage | G | Remplir les regions connectees |
| Ligne | L | Tracer des lignes droites |
| Rectangle | R | Tracer des rectangles (contour ou rempli) |
| Ellipse | O | Tracer des ellipses (contour ou rempli) |
| Selection | S | Selectionner, couper, copier, coller des regions |

#### Taille du pinceau

La taille du pinceau va de 1 a 16 pixels et affecte les outils Crayon, Gomme et Ligne.

#### Mode rempli

Basculez entre le mode contour et le mode rempli pour les outils Rectangle et Ellipse a l'aide du bouton **Rempli**.

#### Palette de couleurs

- **Clic gauche** sur l'echantillon de premier plan pour choisir une couleur de dessin
- **Clic droit** sur l'echantillon d'arriere-plan pour choisir une couleur secondaire
- **Bouton X** echange les couleurs de premier plan et d'arriere-plan
- Cliquez sur n'importe quelle couleur de la palette rapide pour la selectionner
- Double-cliquez sur un echantillon de palette pour le personnaliser
- Selecteur de couleurs RGBA complet avec support de la transparence (alpha)

### Images d'animation

Les sprites peuvent avoir plusieurs images d'animation disposees en bande horizontale.

**Controles de la chronologie des images :**
- **+ (Ajouter) :** Ajouter une nouvelle image vierge
- **D (Dupliquer) :** Copier l'image actuelle
- **- (Supprimer) :** Supprimer l'image actuelle (minimum 1 image)
- **Lecture/Arret :** Previsualiser l'animation
- Le compteur d'images affiche l'image actuelle/le total

**Proprietes de l'animation :**
- **Nombre d'images :** Nombre d'images d'animation
- **Vitesse d'animation :** Images par seconde (par defaut : 10 IPS)
- **Type d'animation :** single, strip_h (horizontale), strip_v (verticale) ou grid (grille)

**Support des GIF animes :** Importez directement des fichiers GIF animes. Toutes les images sont extraites automatiquement avec gestion de la transparence.

### Origine du sprite

Le point d'origine est la position d'ancrage utilisee pour le placement et la rotation dans le jeu.

**Positions predefinies :**
- Haut-Gauche (0, 0)
- Haut-Centre
- Centre (par defaut pour la plupart des sprites)
- Centre-Bas
- Bas-Gauche
- Bas-Droite
- Personnalise (saisie manuelle X/Y)

L'origine est affichee comme un reticule sur le canevas.

### Controles du canevas

- **Ctrl+Molette de la souris :** Zoomer/dezoomer (1x a 64x)
- **Basculer la grille :** Afficher/masquer la grille de pixels (visible a partir du zoom 4x)
- **Miroir H/V :** Retourner l'image actuelle horizontalement ou verticalement
- **Redimensionner/Mettre a l'echelle :** Modifier les dimensions du sprite avec des options de mise a l'echelle ou de redimensionnement du canevas

### Proprietes du sprite (sauvegardees)

| Propriete | Description |
|-----------|-------------|
| name | Nom de la ressource |
| file_path | Chemin vers le fichier PNG de la bande |
| width | Largeur totale de la bande |
| height | Hauteur de l'image |
| frame_width | Largeur d'une seule image |
| frame_height | Hauteur d'une seule image |
| frames | Nombre d'images |
| animation_type | single, strip_h, strip_v, grid |
| speed | IPS de l'animation |
| origin_x | Coordonnee X de l'origine |
| origin_y | Coordonnee Y de l'origine |

---

## 6. Sons

Les sons sont des fichiers audio utilises pour les effets sonores et la musique de fond.

### Importer des sons

1. Cliquez droit sur **Sons** dans l'arbre des ressources et choisissez **Importer un son...**
2. Selectionnez un fichier audio (WAV, OGG, MP3)
3. Le son est ajoute au projet

### Proprietes des sons

| Propriete | Description |
|-----------|-------------|
| name | Nom de la ressource sonore |
| file_path | Chemin vers le fichier audio |
| kind | "sound" (effet) ou "music" (streaming) |
| volume | Volume par defaut (0.0 a 1.0) |

**Les effets sonores** sont charges en memoire pour une lecture instantanee. **Les fichiers musicaux** sont diffuses depuis le disque et un seul peut etre lu a la fois.

---

## 7. Arriere-plans

Les arriere-plans sont des images utilisees derriere les objets de jeu. Ils peuvent egalement servir de jeux de tuiles pour les niveaux bases sur des tuiles.

### Importer des arriere-plans

1. Cliquez droit sur **Arriere-plans** dans l'arbre des ressources et choisissez **Importer un arriere-plan...**
2. Selectionnez un fichier image

### Configuration des jeux de tuiles

Les arriere-plans peuvent etre configures comme jeux de tuiles avec ces proprietes :

| Propriete | Description |
|-----------|-------------|
| tile_width | Largeur de chaque tuile (par defaut : 16) |
| tile_height | Hauteur de chaque tuile (par defaut : 16) |
| h_offset | Decalage horizontal vers la premiere tuile |
| v_offset | Decalage vertical vers la premiere tuile |
| h_sep | Espacement horizontal entre les tuiles |
| v_sep | Espacement vertical entre les tuiles |
| use_as_tileset | Activer le mode jeu de tuiles |

---

## 8. Objets

Les objets definissent les entites de jeu avec des proprietes, des evenements et des actions. Chaque objet peut avoir un sprite pour la representation visuelle et contient des gestionnaires d'evenements qui definissent son comportement.

### Creer un objet

1. Cliquez droit sur **Objets** dans l'arbre des ressources et choisissez **Creer un objet...**
2. Entrez un nom pour l'objet
3. L'objet s'ouvre dans l'editeur d'objets

### Proprietes de l'objet

| Propriete | Par defaut | Description |
|-----------|-----------|-------------|
| Sprite | Aucun | Le sprite visuel a afficher |
| Visible | Oui | Si les instances sont dessinees |
| Solide | Non | Si l'objet bloque le mouvement |
| Persistant | Non | Si les instances survivent aux changements de salle |
| Profondeur | 0 | Ordre de dessin (plus haut = derriere, plus bas = devant) |
| Parent | Aucun | Objet parent pour l'heritage |

### Objets parents

Les objets peuvent heriter d'un objet parent. Les objets enfants recoivent tous les evenements de collision du parent. C'est utile pour creer des hierarchies comme :

```
obj_ennemi (parent - a une collision avec obj_joueur)
  |-- obj_ennemi_melee (herite de la gestion des collisions)
  |-- obj_ennemi_distance (herite de la gestion des collisions)
```

### Ajouter des evenements

1. Ouvrez l'editeur d'objets
2. Cliquez sur **Ajouter un evenement** dans le panneau des evenements
3. Selectionnez un type d'evenement dans la liste (voir [Reference des evenements](#10-reference-des-evenements))
4. L'evenement apparait dans l'arbre des evenements

### Ajouter des actions aux evenements

1. Selectionnez un evenement dans l'arbre des evenements
2. Cliquez sur **Ajouter une action** ou cliquez droit et choisissez **Ajouter une action**
3. Choisissez un type d'action dans la liste categorisee
4. Configurez les parametres de l'action dans la boite de dialogue
5. Cliquez sur OK pour ajouter l'action

Les actions s'executent dans l'ordre de haut en bas lorsque l'evenement se declenche.

### Logique conditionnelle

Les actions supportent le flux conditionnel si/sinon :

1. Ajoutez une action conditionnelle (ex. **Si collision a**, **Tester une variable**)
2. Ajoutez une action **Debut de bloc** (accolade ouvrante)
3. Ajoutez les actions qui s'executent quand la condition est vraie
4. Ajoutez une action **Sinon** (optionnel)
5. Ajoutez un **Debut de bloc** pour la branche sinon
6. Ajoutez les actions pour le cas faux
7. Ajoutez des actions **Fin de bloc** pour fermer chaque bloc

Exemple de sequence d'actions :
```
Si collision a (self.x, self.y + 1, "solid")
  Debut de bloc
    Definir la vitesse verticale (0)
  Fin de bloc
Sinon
  Debut de bloc
    Definir la vitesse verticale (vspeed + 0.5)
  Fin de bloc
```

### Voir le code

Cochez l'option **Voir le code** dans l'editeur d'objets pour voir le code Python genere pour tous les evenements et actions. C'est utile pour comprendre comment les actions visuelles se traduisent en code.

---

## 9. Salles

Les salles sont les scenes ou niveaux de votre jeu. Chaque salle a un arriere-plan, des instances d'objets placees et des couches de tuiles optionnelles.

### Creer une salle

1. Cliquez droit sur **Salles** dans l'arbre des ressources et choisissez **Creer une salle...**
2. Entrez un nom pour la salle
3. La salle s'ouvre dans l'editeur de salles

### Proprietes de la salle

| Propriete | Par defaut | Description |
|-----------|-----------|-------------|
| Largeur | 1024 | Largeur de la salle en pixels |
| Hauteur | 768 | Hauteur de la salle en pixels |
| Couleur d'arriere-plan | #87CEEB (bleu ciel) | Couleur de remplissage derriere tout |
| Image d'arriere-plan | Aucune | Image d'arriere-plan optionnelle |
| Persistante | Non | Conserver l'etat en quittant |

### Placer des instances

1. Cliquez sur un objet dans la **Palette d'objets** (cote gauche de l'editeur de salles)
2. Cliquez dans le canevas de la salle pour placer une instance
3. Continuez a cliquer pour placer d'autres copies
4. Selectionnez les instances placees pour les deplacer ou les configurer

### Proprietes des instances

Lorsque vous selectionnez une instance placee :

| Propriete | Plage | Description |
|-----------|-------|-------------|
| Position X | 0-9999 | Position horizontale |
| Position Y | 0-9999 | Position verticale |
| Visible | Oui/Non | Visibilite de l'instance |
| Rotation | 0-360 | Rotation en degres |
| Echelle X | 10%-1000% | Echelle horizontale |
| Echelle Y | 10%-1000% | Echelle verticale |

### Grille et alignement

- **Basculer la grille :** Cliquez sur le bouton grille pour afficher/masquer la grille de placement
- **Basculer l'alignement :** Cliquez sur le bouton d'alignement pour activer/desactiver l'alignement a la grille
- **Taille de la grille :** 32x32 pixels par defaut (configurable dans les Preferences)

### Operations sur les instances

| Action | Raccourci | Description |
|--------|-----------|-------------|
| Deplacer | Glisser | Deplacer l'instance vers une nouvelle position |
| Selection multiple | Maj+Clic | Ajouter/retirer de la selection |
| Selection par rectangle | Glisser zone vide | Selectionner toutes les instances dans le rectangle |
| Supprimer | Touche Suppr | Supprimer les instances selectionnees |
| Couper | Ctrl+X | Couper dans le presse-papiers |
| Copier | Ctrl+C | Copier dans le presse-papiers |
| Coller | Ctrl+V | Coller depuis le presse-papiers |
| Dupliquer | Ctrl+D | Dupliquer les instances selectionnees |
| Tout effacer | Bouton barre d'outils | Supprimer toutes les instances (avec confirmation) |

### Couches d'arriere-plan

Les salles supportent jusqu'a 8 couches d'arriere-plan (indexees 0-7), chacune avec des parametres independants :

| Propriete | Description |
|-----------|-------------|
| Image d'arriere-plan | Quelle ressource d'arriere-plan utiliser |
| Visible | Afficher/masquer la couche |
| Premier plan | Si vrai, dessine devant les instances |
| Repeter horizontalement | Repeter sur la largeur de la salle |
| Repeter verticalement | Repeter sur la hauteur de la salle |
| Vitesse de defilement H | Pixels de defilement horizontal par image |
| Vitesse de defilement V | Pixels de defilement vertical par image |
| Etirer | Mettre a l'echelle pour remplir toute la salle |
| Decalage X / Y | Decalage de position de la couche |

### Couches de tuiles

Pour les niveaux bases sur les tuiles :

1. Cliquez sur **Palette de tuiles...** pour ouvrir le selecteur de tuiles
2. Choisissez un jeu de tuiles (arriere-plan marque comme jeu de tuiles)
3. Definissez la largeur et la hauteur des tuiles
4. Cliquez sur une tuile dans la palette pour la selectionner
5. Cliquez dans la salle pour placer des tuiles
6. Selectionnez une **Couche** (0-7) pour les tuiles

### Ordre des salles

Les salles s'executent dans l'ordre ou elles apparaissent dans l'arbre des ressources. La premiere salle est la salle de depart.

- Cliquez droit sur une salle et utilisez **Monter/Descendre/Premier/Dernier** pour reordonner
- Utilisez les actions **Salle suivante** et **Salle precedente** pour naviguer entre les salles a l'execution

### Systeme de vues

Les salles supportent jusqu'a 8 vues de camera (comme GameMaker) :

| Propriete | Description |
|-----------|-------------|
| Visible | Activer/desactiver cette vue |
| Vue X/Y | Position de la camera dans la salle |
| Vue L/H | Taille du viewport de la camera |
| Port X/Y | Position a l'ecran pour cette vue |
| Port L/H | Taille a l'ecran pour cette vue |
| Suivre l'objet | Objet a suivre avec la camera |
| Bordure H/V | Marge de defilement autour de l'objet suivi |
| Vitesse H/V | Vitesse maximale de defilement de la camera (-1 = instantane) |

---

## 10. Reference des evenements

Les evenements definissent quand les actions sont executees. Chaque evenement se declenche dans des conditions specifiques.

### Evenements d'objet

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Creation | Objet | L'instance est creee pour la premiere fois |
| Destruction | Objet | L'instance est detruite |
| Pas | Pas | Chaque image du jeu (~60 IPS) |
| Debut de pas | Pas | Debut de chaque image, avant la physique |
| Fin de pas | Pas | Fin de chaque image, apres les collisions |

### Evenements de collision

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Collision avec... | Collision | Deux instances se chevauchent (selectionnez l'objet cible) |

### Evenements clavier

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Clavier | Entree | Touche maintenue en continu (pour mouvement fluide) |
| Appui clavier | Entree | Touche appuyee pour la premiere fois (une fois par appui) |
| Relachement clavier | Entree | Touche relachee |

**Touches disponibles :** A-Z, 0-9, Touches flechees, Espace, Entree, Echap, Tab, Retour arriere, Suppr, F1-F12, Touches du pave numerique, Maj, Ctrl, Alt, et plus (plus de 76 touches au total).

**Evenements clavier speciaux :**
- **Aucune touche** - Se declenche quand aucune touche n'est appuyee
- **N'importe quelle touche** - Se declenche quand n'importe quelle touche est appuyee

### Evenements souris

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Appui souris gauche/droite/milieu | Entree | Bouton clique sur l'instance |
| Relachement souris gauche/droite/milieu | Entree | Bouton relache sur l'instance |
| Maintien souris gauche/droite/milieu | Entree | Bouton maintenu sur l'instance |
| Entree souris | Entree | Le curseur entre dans la zone de l'instance |
| Sortie souris | Entree | Le curseur quitte la zone de l'instance |
| Molette souris haut/bas | Entree | Molette de defilement sur l'instance |
| Appui souris global | Entree | Bouton clique n'importe ou dans la salle |
| Relachement souris global | Entree | Bouton relache n'importe ou dans la salle |

### Evenements de temporisation

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Alarme 0-11 | Temporisation | Le compte a rebours de l'alarme atteint zero (12 alarmes independantes) |

### Evenements de dessin

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Dessin | Dessin | L'instance est dessinee (remplace le dessin par defaut du sprite) |
| Dessin GUI | Dessin | Dessine par-dessus tout (pour HUD, affichage du score) |

### Evenements de salle

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Debut de salle | Salle | La salle commence (apres les evenements de creation) |
| Fin de salle | Salle | La salle est sur le point de se terminer |

### Evenements de jeu

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Debut du jeu | Jeu | Le jeu s'initialise (premiere salle uniquement) |
| Fin du jeu | Jeu | Le jeu se ferme |

### Autres evenements

| Evenement | Categorie | Se declenche quand |
|-----------|-----------|-------------------|
| Hors de la salle | Autre | L'instance est completement en dehors de la salle |
| Intersection de limite | Autre | L'instance touche le bord de la salle |
| Plus de vies | Autre | La valeur des vies atteint 0 ou moins |
| Plus de sante | Autre | La valeur de sante atteint 0 ou moins |
| Fin d'animation | Autre | L'animation du sprite atteint la derniere image |
| Evenement utilisateur 0-15 | Autre | 16 evenements personnalises declenches par le code |

---

## 11. Reference des actions

Les actions sont les elements de base du comportement du jeu. Elles sont placees dans les evenements et s'executent dans l'ordre.

### Actions de mouvement

| Action | Parametres | Description |
|--------|-----------|-------------|
| Mouvement grille | direction (gauche/droite/haut/bas), taille_grille (defaut : 32) | Deplacer d'une unite de grille dans une direction |
| Definir la vitesse horizontale | vitesse (pixels/image) | Definir hspeed pour un mouvement horizontal fluide |
| Definir la vitesse verticale | vitesse (pixels/image) | Definir vspeed pour un mouvement vertical fluide |
| Arreter le mouvement | (aucun) | Mettre les deux vitesses a zero |
| Mouvement fixe | directions (8 directions), vitesse | Commencer a se deplacer dans une direction fixe |
| Mouvement libre | direction (0-360 degres), vitesse | Se deplacer a un angle precis |
| Se deplacer vers | x, y, vitesse | Se deplacer vers une position cible |
| Definir la gravite | direction (270=bas), gravite | Appliquer une acceleration constante |
| Definir la friction | friction | Appliquer une deceleration a chaque image |
| Inverser l'horizontale | (aucun) | Inverser la direction de hspeed |
| Inverser la verticale | (aucun) | Inverser la direction de vspeed |
| Definir la vitesse | vitesse | Definir la magnitude du mouvement |
| Definir la direction | direction (degres) | Definir l'angle du mouvement |
| Sauter a la position | x, y | Se teleporter a une position |
| Sauter au depart | (aucun) | Se teleporter a la position de depart |
| Rebondir | (aucun) | Inverser la velocite lors d'une collision |

### Actions de grille

| Action | Parametres | Description |
|--------|-----------|-------------|
| Aligner sur la grille | taille_grille | Aligner la position au point de grille le plus proche |
| Si sur la grille | taille_grille | Verifier si aligne a la grille (conditionnel) |
| Arreter si pas de touches | taille_grille | S'arreter sur la grille quand les touches de mouvement sont relachees |

### Actions d'instance

| Action | Parametres | Description |
|--------|-----------|-------------|
| Creer une instance | objet, x, y, relatif | Creer une nouvelle instance d'objet |
| Detruire l'instance | cible (soi/autre) | Supprimer une instance du jeu |
| Changer le sprite | sprite | Changer le sprite affiche |
| Definir la visibilite | visible (vrai/faux) | Afficher ou masquer l'instance |
| Definir l'echelle | echelle_x, echelle_y | Changer la taille de l'instance |

### Actions de score, vies et sante

| Action | Parametres | Description |
|--------|-----------|-------------|
| Definir le score | valeur | Definir le score a une valeur specifique |
| Ajouter au score | valeur | Ajouter des points (peut etre negatif) |
| Definir les vies | valeur | Definir le nombre de vies |
| Ajouter des vies | valeur | Ajouter/retirer des vies |
| Definir la sante | valeur | Definir la sante (0-100) |
| Ajouter de la sante | valeur | Ajouter/retirer de la sante |
| Afficher le tableau des meilleurs scores | (aucun) | Afficher le tableau des meilleurs scores |

### Actions de salle et de jeu

| Action | Parametres | Description |
|--------|-----------|-------------|
| Redemarrer la salle | (aucun) | Recharger la salle actuelle |
| Salle suivante | (aucun) | Aller a la salle suivante dans l'ordre |
| Salle precedente | (aucun) | Aller a la salle precedente |
| Aller a la salle | salle | Sauter a une salle specifique |
| Si salle suivante existe | (aucun) | Conditionnel : y a-t-il une salle suivante ? |
| Si salle precedente existe | (aucun) | Conditionnel : y a-t-il une salle precedente ? |
| Redemarrer le jeu | (aucun) | Redemarrer depuis la premiere salle |
| Terminer le jeu | (aucun) | Fermer le jeu |

### Actions de temporisation

| Action | Parametres | Description |
|--------|-----------|-------------|
| Definir l'alarme | numero_alarme (0-11), pas | Demarrer un compte a rebours (30 pas = 0,5 sec a 60 IPS) |
| Retarder l'action | action, images_de_delai | Executer une action apres un delai |

### Actions de message et d'affichage

| Action | Parametres | Description |
|--------|-----------|-------------|
| Afficher un message | message | Afficher un message contextuel |
| Dessiner du texte | texte, x, y, couleur, taille | Dessiner du texte a l'ecran (utiliser dans l'evenement Dessin) |
| Dessiner un rectangle | x1, y1, x2, y2, couleur, rempli | Dessiner un rectangle |
| Dessiner un cercle | x, y, rayon, couleur, rempli | Dessiner un cercle |
| Dessiner une ellipse | x1, y1, x2, y2, couleur, rempli | Dessiner une ellipse |
| Dessiner une ligne | x1, y1, x2, y2, couleur | Dessiner une ligne |
| Dessiner un sprite | nom_sprite, x, y, sous_image | Dessiner un sprite a une position |
| Dessiner un arriere-plan | nom_arriere_plan, x, y, repete | Dessiner une image d'arriere-plan |
| Dessiner le score | x, y, legende | Dessiner la valeur du score a l'ecran |
| Dessiner les vies | x, y, sprite | Dessiner les vies sous forme d'icones de sprite |
| Dessiner la barre de sante | x, y, largeur, hauteur | Dessiner la barre de sante a l'ecran |

### Actions sonores

| Action | Parametres | Description |
|--------|-----------|-------------|
| Jouer un son | son, boucle | Jouer un effet sonore |
| Arreter un son | son | Arreter un son en cours de lecture |
| Jouer de la musique | musique | Jouer la musique de fond (streaming) |
| Arreter la musique | (aucun) | Arreter la musique de fond |
| Definir le volume | son, volume (0.0-1.0) | Ajuster le volume du son |

### Actions de flux de controle

| Action | Parametres | Description |
|--------|-----------|-------------|
| Si collision a | x, y, type_objet | Verifier une collision a une position |
| Si peut pousser | direction, type_objet | Verification de poussee style Sokoban |
| Definir une variable | nom, valeur, portee, relatif | Definir la valeur d'une variable |
| Tester une variable | nom, valeur, portee, operation | Comparer une variable |
| Tester une expression | expression | Evaluer une expression booleenne |
| Verifier si vide | x, y, solides_uniquement | Verifier si la position est libre |
| Verifier collision | x, y, solides_uniquement | Verifier une collision a une position |
| Debut de bloc | (aucun) | Commencer un bloc d'actions (accolade ouvrante) |
| Fin de bloc | (aucun) | Terminer un bloc d'actions (accolade fermante) |
| Sinon | (aucun) | Marque la branche sinon d'un conditionnel |
| Repeter | fois | Repeter l'action/bloc suivant N fois |
| Quitter l'evenement | (aucun) | Arreter l'execution des actions restantes |

### Portee des variables

Les variables peuvent etre accedees a l'aide de references de portee :

| Portee | Syntaxe | Description |
|--------|---------|-------------|
| Soi | `self.variable` ou simplement `variable` | Variable de l'instance actuelle |
| Autre | `other.variable` | L'autre instance dans une collision |
| Global | `global.variable` | Variable a l'echelle du jeu |

Variables d'instance integrees : `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Tests et execution des jeux

### Test rapide (F5)

Appuyez sur **F5** ou cliquez sur le bouton **Tester** pour executer votre jeu instantanement. Une fenetre Pygame separee s'ouvre affichant votre jeu.

- Appuyez sur **Echap** pour arreter le jeu et revenir a l'IDE
- La barre d'etat de l'IDE affiche "Jeu en cours..." pendant que le jeu est actif

### Mode debogage (F6)

Appuyez sur **F6** pour le mode debogage, qui affiche des informations supplementaires dans la console incluant :
- Journalisation de l'execution des evenements
- Details de la detection des collisions
- Valeurs des parametres des actions
- Creation et destruction des instances

### Ordre d'execution du jeu

Chaque image suit l'ordre des evenements de GameMaker 7.0 :

1. Evenements **Debut de pas**
2. Compte a rebours et declenchement des **Alarmes**
3. Evenements **Pas**
4. Evenements d'entree **Clavier/Souris**
5. **Mouvement** (physique : gravite, friction, hspeed/vspeed)
6. Detection et evenements de **Collision**
7. Evenements **Fin de pas**
8. Evenements **Destruction** pour les instances marquees
9. Evenements **Dessin** et rendu

### Titre de la fenetre

Le titre de la fenetre du jeu peut afficher les valeurs de score, vies et sante. Activez ceci avec les parametres d'affichage du titre dans les parametres du projet ou en utilisant les actions de score/vies/sante.

---

## 13. Exportation des jeux

### Exportation HTML5

**Fichier > Exporter en HTML5**

Cree un fichier HTML unique et autonome qui fonctionne dans n'importe quel navigateur web.

- Tous les sprites sont integres en donnees base64
- Les donnees du jeu sont compressees avec gzip
- Le moteur JavaScript gere le rendu via HTML5 Canvas
- Aucun serveur requis - ouvrez simplement le fichier dans un navigateur

### Exportation EXE (Windows)

**Fichier > Exporter le projet** ou **Compilation > Exporter le jeu**

Cree un executable Windows autonome utilisant PyInstaller.

**Prerequis :** PyInstaller et Kivy doivent etre installes.

**Processus :**
1. Genere un jeu base sur Kivy a partir de votre projet
2. Regroupe l'environnement Python et toutes les dependances
3. Cree un seul fichier EXE (peut prendre 5 a 10 minutes)

**Options :**
- Console de debogage (affiche la fenetre du terminal pour le debogage)
- Icone personnalisee
- Compression UPX (reduit la taille du fichier)

### Exportation mobile (Kivy)

**Fichier > Exporter vers Kivy**

Genere un projet Kivy pour le deploiement mobile.

**Contenu de la sortie :**
- Code de jeu Python adapte pour Kivy
- Ensemble de ressources optimise pour mobile
- Configuration `buildozer.spec` pour les compilations Android/iOS

**Pour compiler pour Android :**
```bash
cd projet_exporte
buildozer android debug
```

### Exportation ZIP

**Fichier > Exporter en Zip**

Empaquete l'ensemble du projet sous forme d'archive ZIP pour le partage ou la sauvegarde. Le ZIP peut etre rouvert avec **Fichier > Ouvrir un projet Zip**.

### Exportation Aseba (Robot Thymio)

Pour les projets de robot Thymio, exporte des fichiers de code AESL compatibles avec Aseba Studio.

---

## 14. Programmation visuelle Blockly

PyGameMaker integre Google Blockly pour la programmation par blocs de code visuels.

### Configurer les blocs

Ouvrez **Outils > Configurer les blocs d'action** pour personnaliser les blocs disponibles.

### Preselections de blocs

| Preselection | Description |
|-------------|-------------|
| Complet (Tous les blocs) | Les 173 blocs actives |
| Debutant | Blocs essentiels uniquement (evenements, mouvement de base, score, salles) |
| Intermediaire | Ajoute le dessin, plus de mouvements, vies, sante, son |
| Jeu de plateforme | Axe sur la physique : gravite, friction, collision |
| RPG en grille | Mouvement en grille, sante, transitions de salles |
| Sokoban (Puzzle de boites) | Mouvement en grille, mecaniques de poussee |
| Test | Uniquement les blocs valides |
| Implementes uniquement | Exclut les blocs non implementes |
| Editeur de code | Pour la programmation textuelle |
| Editeur Blockly | Pour le developpement visuel |
| Personnalise | Votre propre selection |

### Categories de blocs

Les blocs sont organises en categories codees par couleur :

| Categorie | Couleur | Blocs |
|-----------|---------|-------|
| Evenements | Jaune | 13 blocs d'evenements |
| Mouvement | Bleu | 14 blocs de mouvement |
| Temporisation | Rouge | Blocs de minuterie et d'alarme |
| Dessin | Violet | Dessin de formes et de texte |
| Score/Vies/Sante | Vert | Blocs de suivi du score |
| Instance | Rose | Creation/destruction d'instances |
| Salle | Marron | Navigation entre salles |
| Valeurs | Bleu fonce | Variables et expressions |
| Son | | Lecture audio |
| Sortie | | Messages et affichage |

### Dependances des blocs

Certains blocs necessitent d'autres blocs pour fonctionner. La boite de dialogue de configuration affiche des avertissements lorsque des dependances manquent. Par exemple, le bloc **Dessiner le score** necessite que **Definir le score** et **Ajouter au score** soient actives.

---

## 15. Support du robot Thymio

PyGameMaker inclut le support du robot educatif Thymio, vous permettant de simuler et programmer des robots Thymio dans l'IDE.

### Qu'est-ce que Thymio ?

Thymio est un petit robot educatif equipe de capteurs, de LED, de moteurs et de boutons. PyGameMaker peut simuler le comportement de Thymio et exporter du code a executer sur de vrais robots.

### Activer Thymio

Allez dans **Outils > Programmation Thymio > Afficher l'onglet Thymio dans l'editeur d'objets** pour activer les fonctionnalites Thymio dans l'editeur d'objets.

### Simulateur Thymio

Le simulateur modelise le robot Thymio physique :

**Specifications :**
- Taille du robot : 110x110 pixels (11cm x 11cm)
- Empattement des roues : 95 pixels
- Plage de vitesse des moteurs : -500 a +500

### Capteurs Thymio

| Capteur | Nombre | Plage | Description |
|---------|--------|-------|-------------|
| Proximite | 7 | 0-4000 | Capteurs de distance horizontaux (portee 10cm) |
| Sol | 2 | 0-1023 | Detecte les surfaces claires/sombres |
| Boutons | 5 | 0/1 | Avant, arriere, gauche, droite, centre |

### Evenements Thymio

| Evenement | Se declenche quand |
|-----------|-------------------|
| Bouton avant/arriere/gauche/droite/centre | Bouton capacitif appuye |
| N'importe quel bouton | Changement d'etat d'un bouton |
| Mise a jour de proximite | Mise a jour des capteurs de proximite (10 Hz) |
| Mise a jour du sol | Mise a jour des capteurs de sol (10 Hz) |
| Tapotement | L'accelerometre detecte un choc |
| Son detecte | Le microphone detecte un son |
| Minuterie 0/1 | La periode de la minuterie expire |
| Son termine | La lecture du son est terminee |
| Message recu | Communication IR recue |

### Actions Thymio

**Controle des moteurs :**
- Definir la vitesse des moteurs (gauche, droite independamment)
- Avancer / Reculer
- Tourner a gauche / Tourner a droite
- Arreter les moteurs

**Controle des LED :**
- Definir la LED superieure (couleur RVB)
- Definir la LED inferieure gauche/droite
- Definir les LED du cercle (8 LED autour du perimetre)
- Eteindre toutes les LED

**Son :**
- Jouer une tonalite (frequence, duree)
- Jouer un son systeme
- Arreter le son

**Conditions des capteurs :**
- Si proximite (capteur, seuil, comparaison)
- Si sol sombre / clair
- Si bouton appuye / relache

**Minuterie :**
- Definir la periode de la minuterie (minuterie 0 ou 1, periode en ms)

### Exporter vers un vrai Thymio

1. Exportez votre projet Thymio via l'exportateur Aseba
2. Ouvrez le fichier `.aesl` genere dans Aseba Studio
3. Connectez votre Thymio via USB
4. Cliquez sur **Charger** puis **Executer**

---

## 16. Parametres et preferences

Ouvrez **Outils > Preferences** pour configurer l'IDE.

### Onglet Apparence

| Parametre | Options | Par defaut |
|-----------|---------|-----------|
| Taille de police | 8-24 pt | 10 |
| Famille de police | Systeme par defaut, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | Systeme par defaut |
| Theme | Par defaut, Sombre, Clair | Par defaut |
| Echelle de l'interface | 0.5x - 2.0x | 1.0x |
| Afficher les infobulles | Oui/Non | Oui |

### Onglet Editeur

| Parametre | Options | Par defaut |
|-----------|---------|-----------|
| Activer la sauvegarde auto | Oui/Non | Oui |
| Intervalle de sauvegarde auto | 1-30 minutes | 5 min |
| Afficher la grille | Oui/Non | Oui |
| Taille de la grille | 8-128 px | 32 |
| Aligner sur la grille | Oui/Non | Oui |
| Afficher les boites de collision | Oui/Non | Non |

### Onglet Projet

| Parametre | Options | Par defaut |
|-----------|---------|-----------|
| Dossier des projets par defaut | Chemin | ~/PyGameMaker Projects |
| Limite de projets recents | 5-50 | 10 |
| Creer une sauvegarde a l'enregistrement | Oui/Non | Oui |

### Onglet Avance

| Parametre | Options | Par defaut |
|-----------|---------|-----------|
| Mode debogage | Oui/Non | Non |
| Afficher la sortie console | Oui/Non | Oui |
| Nombre maximal d'annulations | 10-200 | 50 |

### Fichier de configuration

Les parametres sont stockes dans `~/.pygamemaker/config.json` et persistent entre les sessions.

### Changer la langue

Allez dans **Outils > Langue** et selectionnez votre langue preferee.

**Langues supportees :**
- English (Anglais)
- Francais
- Espanol (Espagnol)
- Deutsch (Allemand)
- Italiano (Italien)
- Russky (Russe)
- Slovenscina (Slovene)
- Ukrainska (Ukrainien)

L'interface se met a jour immediatement. Certaines modifications peuvent necessiter un redemarrage de l'IDE.

---

## 17. Raccourcis clavier

### Raccourcis globaux

| Raccourci | Action |
|-----------|--------|
| Ctrl+N | Nouveau projet |
| Ctrl+O | Ouvrir un projet |
| Ctrl+S | Enregistrer le projet |
| Ctrl+Maj+S | Enregistrer sous |
| Ctrl+E | Exporter le projet |
| Ctrl+Q | Quitter l'IDE |
| Ctrl+R | Creer une salle |
| F1 | Documentation |
| F5 | Tester le jeu |
| F6 | Deboguer le jeu |
| F7 | Compiler le jeu |
| F8 | Compiler et executer |

### Raccourcis de l'editeur

| Raccourci | Action |
|-----------|--------|
| Ctrl+Z | Annuler |
| Ctrl+Y | Retablir |
| Ctrl+X | Couper |
| Ctrl+C | Copier |
| Ctrl+V | Coller |
| Ctrl+D | Dupliquer |
| Ctrl+F | Rechercher |
| Ctrl+H | Rechercher et remplacer |
| Suppr | Supprimer la selection |

### Raccourcis de l'editeur de sprites

| Raccourci | Action |
|-----------|--------|
| P | Outil crayon |
| E | Outil gomme |
| I | Pipette (compte-gouttes) |
| G | Outil remplissage (seau) |
| L | Outil ligne |
| R | Outil rectangle |
| O | Outil ellipse |
| S | Outil selection |
| Ctrl+Molette | Zoomer/dezoomer |

---

## 18. Tutoriels

PyGameMaker inclut des tutoriels integres pour vous aider a demarrer. Accedez-y depuis **Aide > Tutoriels** ou depuis le dossier Tutoriels dans le repertoire d'installation.

### Tutoriels disponibles

| # | Tutoriel | Description |
|---|----------|-------------|
| 01 | Premiers pas | Introduction a l'IDE et premier projet |
| 02 | Premier jeu | Creer votre premier jeu jouable |
| 03 | Pong | Jeu de Pong classique avec raquette et balle |
| 04 | Breakout | Casse-briques style Breakout |
| 05 | Sokoban | Jeu de puzzle de poussee de boites |
| 06 | Labyrinthe | Jeu de navigation dans un labyrinthe |
| 07 | Plateforme | Jeu de plateforme a defilement lateral |
| 08 | Alunissage | Jeu d'atterrissage base sur la gravite |

Les tutoriels sont disponibles en plusieurs langues (anglais, allemand, espagnol, francais, italien, russe, slovene, ukrainien).

---

## 19. Depannage

### Le jeu ne demarre pas (F5)

- Verifiez que votre projet a au moins une salle avec des instances
- Verifiez que les objets ont des sprites assignes
- Regardez la sortie console (mode debogage F6) pour les messages d'erreur

### Les sprites ne s'affichent pas

- Confirmez que le fichier sprite existe dans le dossier `sprites/`
- Verifiez que l'objet a un sprite assigne dans ses proprietes
- Verifiez que l'instance est definie sur `visible = true`

### Les collisions ne fonctionnent pas

- Assurez-vous que l'objet cible est marque comme **Solide** si vous utilisez la collision basee sur les solides
- Verifiez que vous avez un evenement **Collision avec** configure pour le bon objet
- Verifiez que les instances se chevauchent reellement (utilisez le mode debogage)

### Le son ne se joue pas

- Verifiez que le fichier son existe et est dans un format supporte (WAV, OGG, MP3)
- Verifiez que pygame.mixer s'est initialise correctement (voir la sortie console)
- Les fichiers musicaux sont diffuses depuis le disque - assurez-vous que le chemin du fichier est correct

### L'exportation echoue

- **Exportation EXE :** Assurez-vous que PyInstaller est installe (`pip install pyinstaller`)
- **Exportation Kivy :** Assurez-vous que Kivy est installe (`pip install kivy`)
- **Exportation HTML5 :** Verifiez la console pour les erreurs d'encodage
- Toutes les exportations necessitent un projet valide avec au moins une salle

### Problemes de performance

- Reduisez le nombre d'instances dans les salles
- Utilisez le systeme de collision par grille spatiale (active par defaut)
- Evitez les operations couteuses dans les evenements Pas (s'executent 60 fois par seconde)
- Utilisez des alarmes pour les taches periodiques au lieu de compter les images dans Pas

---

**PyGameMaker IDE** - Version 1.0.0-rc.4
Copyright 2024-2025 Gabriel Thullen
Licence GNU General Public License v3 (GPLv3)
GitHub : https://github.com/Gabe1290/pythongm
