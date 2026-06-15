# Liste de vérification des tests — PyGameMaker IDE

Une liste de vérification complète pour tester toutes les fonctionnalités de PyGameMaker IDE.

> Chaque élément comporte trois cases à cocher : **L** = Linux, **M** = macOS, **W** = Windows. Cochez la case pour chaque plateforme sur laquelle vous l'avez testé.

## 0. Nouveautés de la 1.0.0-rc.12 (phase audit + visuel)

Valide spécifiquement le travail ajouté dans la version rc.12. Chaque élément
référence le commit dans lequel il a été livré, afin de faciliter le bisect en
cas de régression.

### Onglet d'accueil (commits e42d4b6 / 7e86274 / 37d7186)
- L [ ] M [ ] W [ ] L'onglet d'accueil est l'onglet par défaut au premier lancement sans projet
- L [ ] M [ ] W [ ] Le titre « Welcome to PyGameMaker IDE » + l'étiquette de version « v1.0.0-rc.12 » sont visibles
- L [ ] M [ ] W [ ] La colonne **Get started** affiche New Project, Open Project, et le menu déroulant **More options**
- L [ ] M [ ] W [ ] Le menu déroulant « More options » ouvre un menu avec les entrées Open ZIP / Import GMK / Import Roberta
- L [ ] M [ ] W [ ] La liste **Continue where you left off** affiche les projets récents avec des horodatages « N days ago »
- L [ ] M [ ] W [ ] Cliquer sur une ligne de projet récent ouvre ce projet
- L [ ] M [ ] W [ ] La liste des projets récents est entourée d'un rectangle visible (cadre thématisé)
- L [ ] M [ ] W [ ] Le lien « Clear recent projects » se masque lui-même lorsque la liste est vide
- L [ ] M [ ] W [ ] Les liens de pied de page (Documentation / Tutorials / About) ouvrent les bonnes cibles

### Essayer un exemple de jeu — exemples intégrés + copie à l'ouverture (commits a8f78d0 / f8a0eb7)
- L [ ] M [ ] W [ ] Le menu déroulant **Try a sample game** ouvre un menu listant Maze 1–3
- L [ ] M [ ] W [ ] Cliquer sur un exemple l'ouvre **immédiatement** — pas d'invite « choose output folder », pas d'attente d'import GMK
- L [ ] M [ ] W [ ] Après le clic, le titre de l'IDE affiche le nom de l'exemple (p. ex. `maze_1 — PyGameMaker IDE`)
- L [ ] M [ ] W [ ] Le projet nouvellement ouvert se trouve dans `<Documents>/PyGameMaker Projects/<sample>/` — et non sous `samples/`
- L [ ] M [ ] W [ ] Cliquer deux fois sur le même exemple ouvre une nouvelle copie dans `<sample>_2/`, en laissant la première intacte
- L [ ] M [ ] W [ ] Après modification et appui sur Ctrl+S, seule la copie de travail change ; `samples/<sample>/` sur le disque reste intact
- L [ ] M [ ] W [ ] Chaque exemple se charge dans un état modifiable (ressources visibles dans l'arborescence, salles ouvrables, etc.)

### Titre de la fenêtre (commit 00911b3)
- L [ ] M [ ] W [ ] Titre sans projet : « PyGameMaker IDE »
- L [ ] M [ ] W [ ] Projet chargé : « &lt;ProjectName&gt; — PyGameMaker IDE »
- L [ ] M [ ] W [ ] Après des modifications non enregistrées : un « * » final apparaît dans le titre en temps réel
- L [ ] M [ ] W [ ] Après enregistrement : le « * » disparaît

### Barre d'outils (commit 00911b3)
- L [ ] M [ ] W [ ] Survoler une icône de la barre d'outils → info-bulle avec un texte descriptif + indication du raccourci
  (p. ex. « Save Project (Ctrl+S) », « Test Game (F5) »)
- L [ ] M [ ] W [ ] Les icônes Save / Test / Debug / Export / Import Sprite / Import Sound sont grisées
      lorsqu'aucun projet n'est ouvert
- L [ ] M [ ] W [ ] Les mêmes icônes s'activent correctement une fois un projet chargé
- L [ ] M [ ] W [ ] Les icônes New / Open restent activées dans les deux états

### Grisage du menu Tools (commit 78e190d)
- L [ ] M [ ] W [ ] Aucun projet chargé : « Validate Project », « Migrate to Modular Structure »,
      et Thymio → Add Event / Add Action sont grisés
- L [ ] M [ ] W [ ] Aucun projet chargé : Preferences, Configure Action Blocks, Configure
      Thymio Blocks, Language, Open Playground, Import Open Roberta XML
      restent activés
- L [ ] M [ ] W [ ] Projet chargé : chaque élément du menu Tools devient activé

### Indication d'état vide de l'arborescence des ressources (commit 00911b3)
- L [ ] M [ ] W [ ] Aucun projet chargé : une indication en italique est visible sous la liste des catégories
      (« No project loaded. Use File → New / Open Project to begin. »)
- L [ ] M [ ] W [ ] L'indication disparaît une fois un projet chargé
- L [ ] M [ ] W [ ] L'indication s'atténue correctement avec les thèmes clair et sombre

### Espace réservé d'état vide du panneau de droite (commit 00911b3)
- L [ ] M [ ] W [ ] Aucun projet chargé : les boîtes de groupe Asset Information / Properties / Preview
      sont masquées ; un seul message en italique centré prend leur place
- L [ ] M [ ] W [ ] Le message apparaît avec les thèmes clair et sombre
- L [ ] M [ ] W [ ] Projet chargé : les trois boîtes de groupe réapparaissent ; l'espace réservé est masqué

### Export de code Aseba (commit 71e19f3)
- L [ ] M [ ] W [ ] Le menu File → Export contient « Export Aseba (Thymio) code… »
- L [ ] M [ ] W [ ] L'élément est grisé lorsqu'aucun projet n'est ouvert, activé lorsqu'il y en a un
- L [ ] M [ ] W [ ] Cliquer dessus demande un répertoire de sortie
- L [ ] M [ ] W [ ] Sur un projet avec des objets Thymio : écrit un `.aesl` par objet + un
      `README.md` dans le répertoire choisi
- L [ ] M [ ] W [ ] Sur un projet sans objet Thymio : affiche l'avertissement « No Thymio objects
      found » au lieu de la boîte de dialogue d'échec générique
- L [ ] M [ ] W [ ] La boîte de dialogue de succès propose d'ouvrir le dossier de sortie ; fonctionne sous
      Windows / macOS / Linux

### Invites « ouvrir le dossier » d'export multiplateforme (commit a44f750)
- L [ ] M [ ] W [ ] Après un export réussi de binaire Linux, l'invite « open folder? »
      utilise la commande d'ouverture native du bon OS (start / open / xdg-open)
- L [ ] M [ ] W [ ] Idem pour l'export iOS (lorsqu'il est accessible)
- L [ ] M [ ] W [ ] Idem pour les exports HTML5, exe, macos, android (vérification de non-régression)

### Valeurs par défaut localisées Desktop / Documents (commit 53ec9ae)
- L [ ] M [ ] W [ ] Sous Windows avec un Bureau redirigé vers OneDrive : la boîte de dialogue d'export
      utilise par défaut le chemin OneDrive-Desktop, et non un `~/Desktop` inexistant
- L [ ] M [ ] W [ ] Sous Linux avec une locale non anglaise : la boîte de dialogue d'export utilise par défaut
      le dossier de bureau localisé (Bureau / Schreibtisch / etc.)
- L [ ] M [ ] W [ ] La boîte de dialogue de nouveau projet utilise par défaut le dossier Documents localisé

### Suppression du clignotement de console Windows (commit 53ec9ae)
- L [ ] M [ ] W [ ] Sous Windows en mode dev, en appuyant sur F5 pour Test Game : aucune fenêtre de
      console `python.exe` ne clignote avant l'ouverture de pygame

### Ordre des barres de boutons des boîtes de dialogue (commit 00911b3)
- L [ ] M [ ] W [ ] Boîte de dialogue Sprite Strip Import : la rangée de boutons Cancel/OK suit la
      convention de la plateforme (OK-puis-Cancel sous Win/Linux, Cancel-puis-OK
      sous macOS)
- L [ ] M [ ] W [ ] Boîte de dialogue Blockly Block Config : Select All / Select None restent à
      gauche ; la paire Save/Cancel à droite suit la convention de la plateforme

### Couverture de traduction (commit ad47e68)
- L [ ] M [ ] W [ ] Changer de langue à l'exécution (Tools → Language) modifie effectivement
      les libellés visibles (vérification que les fichiers .qm se chargent)
- L [ ] M [ ] W [ ] Les 7 langues actives (de, es, fr, it, ru, sl, uk) apparaissent dans le
      menu Language lorsque leurs fichiers .qm sont présents

---

## 1. Démarrage de l'application et opérations de base

- L [x] M [ ] W [ ] L'application se lance sans erreur  *(vérifié après `afb9c75` : console propre, pas d'avertissement Qt UniqueConnection, pas de lignes de journal `pygm.X` en double)*
- L [ ] M [ ] W [ ] La fenêtre principale s'affiche correctement
- L [ ] M [ ] W [ ] La barre de menus est visible et réactive
- L [ ] M [ ] W [ ] Les boutons de la barre d'outils sont visibles et cliquables
- L [ ] M [ ] W [ ] La barre d'état affiche des informations
- L [ ] M [ ] W [ ] Le panneau d'arborescence des ressources est visible
- L [ ] M [ ] W [ ] Le panneau des propriétés est visible

## 2. Gestion de projet

- L [ ] M [ ] W [ ] Créer un nouveau projet (File > New Project)
- L [ ] M [ ] W [ ] Ouvrir un projet existant (File > Open Project)
- L [ ] M [ ] W [ ] Enregistrer le projet (File > Save / Ctrl+S)
- L [ ] M [ ] W [ ] Enregistrer le projet sous un nouveau nom (File > Save As)
- L [ ] M [ ] W [ ] Fermer le projet (File > Close Project)
- L [ ] M [ ] W [ ] La liste des projets récents fonctionne
- L [ ] M [ ] W [ ] La boîte de dialogue des paramètres du projet s'ouvre et enregistre

## 3. Opérations sur l'arborescence des ressources

### Sprites
- L [ ] M [ ] W [ ] Créer un nouveau sprite
- L [ ] M [ ] W [ ] Importer un sprite depuis un fichier image (PNG, JPG, GIF)
- L [ ] M [ ] W [ ] Modifier les propriétés du sprite (nom, origine, masque de collision)
- L [ ] M [ ] W [ ] Supprimer un sprite
- L [ ] M [ ] W [ ] Dupliquer un sprite
- L [ ] M [ ] W [ ] Renommer un sprite

### Sons
- L [ ] M [ ] W [ ] Créer/importer un nouveau son (WAV, MP3, OGG)
- L [ ] M [ ] W [ ] Prévisualiser la lecture du son
- L [ ] M [ ] W [ ] Modifier les propriétés du son
- L [ ] M [ ] W [ ] Supprimer un son

### Arrière-plans
- L [ ] M [ ] W [ ] Créer un nouvel arrière-plan
- L [ ] M [ ] W [ ] Importer une image d'arrière-plan
- L [ ] M [ ] W [ ] Modifier les propriétés de l'arrière-plan (juxtaposition, défilement)
- L [ ] M [ ] W [ ] Supprimer un arrière-plan

### Objets
- L [ ] M [ ] W [ ] Créer un nouvel objet
- L [ ] M [ ] W [ ] Assigner un sprite à un objet
- L [ ] M [ ] W [ ] Modifier les propriétés de l'objet (visible, solide, profondeur, persistant)
- L [ ] M [ ] W [ ] Ajouter des événements à un objet
- L [ ] M [ ] W [ ] Ajouter des actions aux événements
- L [ ] M [ ] W [ ] Supprimer un objet
- L [ ] M [ ] W [ ] Dupliquer un objet
- L [ ] M [ ] W [ ] Relations parent/enfant entre objets

### Salles
- L [ ] M [ ] W [ ] Créer une nouvelle salle
- L [ ] M [ ] W [ ] Modifier les propriétés de la salle (largeur, hauteur, vitesse)
- L [ ] M [ ] W [ ] Définir l'arrière-plan de la salle
- L [ ] M [ ] W [ ] Placer des instances d'objets dans la salle
- L [ ] M [ ] W [ ] Déplacer/redimensionner les instances
- L [ ] M [ ] W [ ] Supprimer des instances
- L [ ] M [ ] W [ ] Définir l'ordre des salles (première salle)
- L [ ] M [ ] W [ ] Supprimer une salle

## 4. Test des événements d'objet

### Événement Create
- L [ ] M [ ] W [ ] Ajouter un événement Create
- L [ ] M [ ] W [ ] Les actions s'exécutent à la création de l'instance
- L [ ] M [ ] W [ ] L'initialisation des variables fonctionne

### Événement Destroy
- L [ ] M [ ] W [ ] Ajouter un événement Destroy
- L [ ] M [ ] W [ ] Les actions s'exécutent à la destruction de l'instance

### Événements Step
- L [ ] M [ ] W [ ] L'événement Step se déclenche à chaque frame
- L [ ] M [ ] W [ ] L'événement Begin Step se déclenche avant Step
- L [ ] M [ ] W [ ] L'événement End Step se déclenche après Step

### Événements Alarm
- L [ ] M [ ] W [ ] Les alarmes 0 à 11 peuvent être définies
- L [ ] M [ ] W [ ] L'alarme se déclenche au bon moment
- L [ ] M [ ] W [ ] L'alarme peut être réinitialisée

### Événements clavier
- L [ ] M [ ] W [ ] Événement Key Press (se déclenche une fois à l'appui de la touche)
- L [ ] M [ ] W [ ] Événement Key Release (se déclenche une fois au relâchement de la touche)
- L [ ] M [ ] W [ ] Événement Key Down (se déclenche en continu tant que la touche est maintenue)
- L [ ] M [ ] W [ ] Détection de touche spécifique (flèches, WASD, Espace, Entrée, etc.)
- L [ ] M [ ] W [ ] Détection de n'importe quelle touche

### Événements souris
- L [ ] M [ ] W [ ] Bouton gauche appui/relâchement/maintien
- L [ ] M [ ] W [ ] Bouton droit appui/relâchement/maintien
- L [ ] M [ ] W [ ] Bouton du milieu appui/relâchement/maintien
- L [ ] M [ ] W [ ] Mouse enter (le curseur entre dans l'instance)
- L [ ] M [ ] W [ ] Mouse leave (le curseur quitte l'instance)
- L [ ] M [ ] W [ ] Événements souris globaux (n'importe où à l'écran)

### Événements de collision
- L [ ] M [ ] W [ ] Collision avec un objet spécifique
- L [ ] M [ ] W [ ] Précision de la détection de collision
- L [ ] M [ ] W [ ] Plusieurs événements de collision sur le même objet

### Autres événements
- L [ ] M [ ] W [ ] Événement Outside Room
- L [ ] M [ ] W [ ] Événement Intersect Boundary
- L [ ] M [ ] W [ ] Événement Game Start
- L [ ] M [ ] W [ ] Événement Game End
- L [ ] M [ ] W [ ] Événement Room Start
- L [ ] M [ ] W [ ] Événement Room End
- L [ ] M [ ] W [ ] Événement Animation End
- L [ ] M [ ] W [ ] Événements définis par l'utilisateur

### Événements Draw
- L [ ] M [ ] W [ ] L'événement Draw remplace le dessin par défaut du sprite
- L [ ] M [ ] W [ ] Événement Draw GUI pour les éléments du HUD
- L [ ] M [ ] W [ ] Événements Draw Begin/End

## 5. Test des actions

### Actions de mouvement
- L [ ] M [ ] W [ ] Move Fixed (8 directions + arrêt)
- L [ ] M [ ] W [ ] Move Free (direction + vitesse)
- L [ ] M [ ] W [ ] Move Towards (point cible)
- L [ ] M [ ] W [ ] Set Speed
- L [ ] M [ ] W [ ] Set Direction
- L [ ] M [ ] W [ ] Set Horizontal Speed (hspeed)
- L [ ] M [ ] W [ ] Set Vertical Speed (vspeed)
- L [ ] M [ ] W [ ] Reverse Horizontal
- L [ ] M [ ] W [ ] Reverse Vertical
- L [ ] M [ ] W [ ] Set Gravity
- L [ ] M [ ] W [ ] Set Friction
- L [ ] M [ ] W [ ] Jump to Position
- L [ ] M [ ] W [ ] Jump to Start Position
- L [ ] M [ ] W [ ] Jump to Random Position
- L [ ] M [ ] W [ ] Snap to Grid
- L [ ] M [ ] W [ ] Wrap Screen
- L [ ] M [ ] W [ ] Move to Contact
- L [ ] M [ ] W [ ] Bounce against objects

### Actions sur les instances
- L [ ] M [ ] W [ ] Create Instance
- L [ ] M [ ] W [ ] Create Instance with Motion
- L [ ] M [ ] W [ ] Create Random Instance
- L [ ] M [ ] W [ ] Change Instance (transformer en un objet différent)
- L [ ] M [ ] W [ ] Destroy Instance
- L [ ] M [ ] W [ ] Destroy at Position

### Actions de contrôle de flux
- L [ ] M [ ] W [ ] If Variable (comparaison)
- L [ ] M [ ] W [ ] If Instance Count
- L [ ] M [ ] W [ ] If Dice (chance aléatoire)
- L [ ] M [ ] W [ ] If Question (invite utilisateur)
- L [ ] M [ ] W [ ] If Expression
- L [ ] M [ ] W [ ] If Mouse Button
- L [ ] M [ ] W [ ] If Instance Aligned with Grid
- L [ ] M [ ] W [ ] Start Block / End Block
- L [ ] M [ ] W [ ] Else
- L [ ] M [ ] W [ ] Exit Event
- L [ ] M [ ] W [ ] Repeat
- L [ ] M [ ] W [ ] Call Parent Event

### Actions sur les salles
- L [ ] M [ ] W [ ] Go to Next Room
- L [ ] M [ ] W [ ] Go to Previous Room
- L [ ] M [ ] W [ ] Restart Room
- L [ ] M [ ] W [ ] Go to Room (spécifique)
- L [ ] M [ ] W [ ] If Previous Room Exists
- L [ ] M [ ] W [ ] If Next Room Exists

### Actions sur les variables
- L [ ] M [ ] W [ ] Set Variable
- L [ ] M [ ] W [ ] If Variable
- L [ ] M [ ] W [ ] Draw Variable

### Actions Score/Vies/Santé
- L [ ] M [ ] W [ ] Set Score
- L [ ] M [ ] W [ ] If Score
- L [ ] M [ ] W [ ] Draw Score
- L [ ] M [ ] W [ ] Set Lives
- L [ ] M [ ] W [ ] If Lives
- L [ ] M [ ] W [ ] Draw Lives
- L [ ] M [ ] W [ ] Set Health
- L [ ] M [ ] W [ ] If Health
- L [ ] M [ ] W [ ] Draw Health
- L [ ] M [ ] W [ ] Draw Health Bar

### Actions de dessin
- L [ ] M [ ] W [ ] Draw Sprite
- L [ ] M [ ] W [ ] Draw Background
- L [ ] M [ ] W [ ] Draw Text
- L [ ] M [ ] W [ ] Draw Text Transformed
- L [ ] M [ ] W [ ] Draw Rectangle
- L [ ] M [ ] W [ ] Draw Ellipse
- L [ ] M [ ] W [ ] Draw Line
- L [ ] M [ ] W [ ] Draw Arrow
- L [ ] M [ ] W [ ] Set Color
- L [ ] M [ ] W [ ] Set Font
- L [ ] M [ ] W [ ] Set Full Screen

### Actions sonores
- L [ ] M [ ] W [ ] Play Sound
- L [ ] M [ ] W [ ] Stop Sound
- L [ ] M [ ] W [ ] If Sound Playing
- L [ ] M [ ] W [ ] Set Volume
- L [ ] M [ ] W [ ] Set Pan

### Actions de minutage
- L [ ] M [ ] W [ ] Set Alarm
- L [ ] M [ ] W [ ] Sleep (mettre l'exécution en pause)
- L [ ] M [ ] W [ ] Set Timeline

### Actions Info/Jeu
- L [ ] M [ ] W [ ] Display Message
- L [ ] M [ ] W [ ] Show Info
- L [ ] M [ ] W [ ] Show Video
- L [ ] M [ ] W [ ] Restart Game
- L [ ] M [ ] W [ ] End Game
- L [ ] M [ ] W [ ] Save Game
- L [ ] M [ ] W [ ] Load Game

## 6. Éditeur de salle

- L [ ] M [ ] W [ ] Bascule de l'affichage de la grille
- L [ ] M [ ] W [ ] Bascule de l'aimantation à la grille
- L [ ] M [ ] W [ ] Zoom avant/arrière
- L [ ] M [ ] W [ ] Déplacement/défilement de la vue de la salle
- L [ ] M [ ] W [ ] Placement d'instance
- L [ ] M [ ] W [ ] Sélection d'instance (clic)
- L [ ] M [ ] W [ ] Multi-sélection d'instances (Ctrl+clic ou rectangle de sélection)
- L [ ] M [ ] W [ ] Déplacer les instances sélectionnées
- L [ ] M [ ] W [ ] Supprimer les instances sélectionnées (touche Suppr)
- L [ ] M [ ] W [ ] Copier/coller des instances
- L [ ] M [ ] W [ ] Panneau des propriétés d'instance
- L [ ] M [ ] W [ ] Gestion des calques (le cas échéant)
- L [ ] M [ ] W [ ] Édition du calque d'arrière-plan
- L [ ] M [ ] W [ ] Paramètres de vue (afficher/masquer les éléments)

## 7. Programmation visuelle Blockly

- L [ ] M [ ] W [ ] L'éditeur Blockly s'ouvre pour les actions
- L [ ] M [ ] W [ ] Les blocs peuvent être glissés depuis la boîte à outils
- L [ ] M [ ] W [ ] Les blocs s'emboîtent correctement
- L [ ] M [ ] W [ ] La suppression de bloc fonctionne
- L [ ] M [ ] W [ ] Annuler/rétablir dans Blockly
- L [ ] M [ ] W [ ] Génération de code à partir des blocs
- L [ ] M [ ] W [ ] Toutes les catégories d'actions disponibles dans la boîte à outils
- L [ ] M [ ] W [ ] Blocs personnalisés (le cas échéant)

## 8. Éditeur de code

- L [ ] M [ ] W [ ] L'éditeur de code Python s'ouvre
- L [ ] M [ ] W [ ] La coloration syntaxique fonctionne
- L [ ] M [ ] W [ ] La complétion de code (si disponible)
- L [ ] M [ ] W [ ] Le code peut être enregistré
- L [ ] M [ ] W [ ] Le code s'exécute correctement dans le jeu

## 9. Exécution du jeu

### Lancer le jeu (F5)
- L [ ] M [ ] W [ ] La fenêtre du jeu s'ouvre
- L [ ] M [ ] W [ ] La première salle se charge correctement
- L [ ] M [ ] W [ ] Les objets apparaissent aux bonnes positions
- L [ ] M [ ] W [ ] Les sprites s'affichent correctement
- L [ ] M [ ] W [ ] Les animations se jouent
- L [ ] M [ ] W [ ] Les événements se déclenchent correctement
- L [ ] M [ ] W [ ] Les collisions sont détectées
- L [ ] M [ ] W [ ] La saisie au clavier fonctionne
- L [ ] M [ ] W [ ] La saisie à la souris fonctionne
- L [ ] M [ ] W [ ] Le son se joue
- L [ ] M [ ] W [ ] Les transitions entre salles fonctionnent
- L [ ] M [ ] W [ ] Le jeu peut être fermé proprement

### Mode débogage
- L [ ] M [ ] W [ ] La sortie de débogage est visible
- L [ ] M [ ] W [ ] Affichage des FPS (si activé)
- L [ ] M [ ] W [ ] Inspection des variables (si disponible)
- L [ ] M [ ] W [ ] Exécution pas à pas (si disponible)

## 10. Export/Build

### Export HTML5
- L [ ] M [ ] W [ ] L'export en HTML5 fonctionne
- L [ ] M [ ] W [ ] Le jeu s'exécute dans le navigateur
- L [ ] M [ ] W [ ] Toutes les fonctionnalités marchent dans le navigateur

### Export autonome
- L [ ] M [ ] W [ ] L'export en exécutable fonctionne
- L [ ] M [ ] W [ ] Le jeu s'exécute sans l'IDE
- L [ ] M [ ] W [ ] Toutes les ressources sont correctement empaquetées

## 11. Préférences/Paramètres

- L [ ] M [ ] W [ ] La boîte de dialogue des préférences s'ouvre
- L [ ] M [ ] W [ ] La sélection de la langue fonctionne
- L [ ] M [ ] W [ ] La sélection du thème fonctionne (clair/sombre)
- L [ ] M [ ] W [ ] Les paramètres de police fonctionnent
- L [ ] M [ ] W [ ] Les paramètres de grille persistent
- L [ ] M [ ] W [ ] Les paramètres sont enregistrés entre les sessions

## 12. Système d'aide

- L [ ] M [ ] W [ ] Le menu Help est accessible
- L [ ] M [ ] W [ ] La documentation s'ouvre
- L [ ] M [ ] W [ ] La boîte de dialogue About affiche les informations de version
- L [ ] M [ ] W [ ] Les liens fonctionnent (site web, GitHub, etc.)

## 13. Test de l'exécutable autonome

- L [ ] M [ ] W [ ] L'application se lance depuis l'exécutable
- L [ ] M [ ] W [ ] Aucun répertoire vide n'est créé dans le dossier de lancement
- L [ ] M [ ] W [ ] Les projets peuvent être créés/ouverts
- L [ ] M [ ] W [ ] Les jeux peuvent être lancés (F5)
- L [ ] M [ ] W [ ] L'aperçu de la salle affiche un message approprié
- L [ ] M [ ] W [ ] Tous les éléments d'interface s'affichent correctement
- L [ ] M [ ] W [ ] Aucune erreur liée à Python dans la console

## 14. Gestion des erreurs

- L [ ] M [ ] W [ ] Un fichier de projet invalide affiche un message d'erreur
- L [ ] M [ ] W [ ] Les références de ressources manquantes sont gérées proprement
- L [ ] M [ ] W [ ] Les erreurs de syntaxe dans le code affichent des messages utiles
- L [ ] M [ ] W [ ] Récupération après plantage (enregistrement automatique, si disponible)
- L [ ] M [ ] W [ ] L'annulation fonctionne après des erreurs

---

## Notes sur l'environnement de test

**Date du test :** _______________

**Version :** _______________

**Système d'exploitation :** _______________

**Testeur :** _______________

**Notes :**
