# Questions fréquemment posées

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Retour à l'accueil](Home_fr)

---

## Questions générales

### Qu'est-ce que PyGameMaker ?

PyGameMaker est un IDE de développement de jeux open-source inspiré de GameMaker 7.0. Il vous permet de créer des jeux 2D en utilisant la programmation visuelle (Google Blockly) ou un système événement-action, sans avoir besoin d'écrire du code.

### PyGameMaker est-il gratuit ?

Oui ! PyGameMaker est complètement gratuit et open-source — le code source est sous licence MIT, et la documentation sous licence CC BY 4.0.

### Vers quelles plateformes puis-je exporter ?

- Windows (exécutable .exe autonome)
- macOS (paquet .app)
- HTML5 (navigateurs web)
- Linux (binaire natif)
- Mobile (iOS/Android via Kivy)

### Ai-je besoin d'expérience en programmation ?

Non ! PyGameMaker est conçu pour les débutants. Vous pouvez créer des jeux en utilisant :
- Les blocs Blockly par glisser-déposer
- Le système événement/action par pointer-cliquer
- Aucun codage requis

### Est-il compatible avec les fichiers GameMaker ?

PyGameMaker est inspiré de GameMaker 7.0 mais utilise son propre format de projet. Vous ne pouvez pas importer directement des fichiers GameMaker, mais les concepts et le flux de travail sont similaires.

---

## Installation

### Quelles sont les exigences système ?

- Python 3.10 ou supérieur
- Windows, Linux ou macOS
- 4 Go de RAM minimum (8 Go recommandé)
- ~500 Mo d'espace disque

### Comment installer PyGameMaker ?

Voir [[Demarrage_fr]] pour des instructions d'installation détaillées. La version courte :

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python main.py
```

### Python n'est pas reconnu / non trouvé

Assurez-vous que Python est installé et ajouté au PATH de votre système. Vous pouvez vérifier en exécutant :

```bash
python --version
```

Si cela échoue, réinstallez Python et cochez « Ajouter Python au PATH » lors de l'installation.

### J'obtiens des erreurs d'importation au démarrage

Essayez de réinstaller les dépendances :

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projets

### Où sont sauvegardés mes projets ?

Les projets sont sauvegardés dans des dossiers que vous choisissez. Chaque projet contient :
- `project.json` - Fichier de projet principal
- Des dossiers pour les sprites, sons, objets, salles, etc.

### Puis-je avoir plusieurs projets ouverts ?

Actuellement, PyGameMaker ouvre un projet à la fois. Utilisez **Fichier > Ouvrir un projet** pour basculer entre les projets.

### Comment sauvegarder mon projet ?

Copiez simplement le dossier entier du projet. Toutes les ressources et tous les paramètres sont contenus à l'intérieur. Envisagez l'utilisation de git pour le contrôle de version :

```bash
cd mon_projet
git init
git add .
git commit -m "Sauvegarde initiale"
```

### Mon projet ne s'ouvre pas / est corrompu

Essayez ces étapes :
1. Vérifiez si `project.json` existe et n'est pas vide
2. Ouvrez `project.json` dans un éditeur de texte pour vérifier les erreurs JSON
3. Restaurez depuis une sauvegarde si disponible
4. Vérifiez la sortie console pour des messages d'erreur spécifiques

---

## Objets et événements

### Quelle est la différence entre un objet et une instance ?

- **Objet** : Un modèle/plan définissant un comportement
- **Instance** : Une copie spécifique d'un objet placée dans une salle

Par exemple, `obj_ennemi` est un objet. Placer 5 ennemis dans une salle crée 5 instances de `obj_ennemi`.

### Pourquoi mon événement ne se déclenche-t-il pas ?

Causes courantes :
1. **Mauvais type d'événement** : Assurez-vous d'utiliser le bon événement (ex : « Touche pressée » vs « Clavier »)
2. **Pas d'instances** : L'objet doit avoir des instances dans la salle
3. **Objet non visible** : Vérifiez la propriété visible
4. **Ordre d'exécution** : Certains événements s'exécutent avant d'autres

### Comment faire interagir les objets ?

Utilisez les événements de collision :
1. Ouvrez l'objet qui doit détecter la collision
2. Ajoutez l'événement **Collision avec [autre_objet]**
3. Ajoutez des actions pour ce qui se passe lors de la collision

### Quelle est la différence entre les événements « Clavier » et « Touche pressée » ?

- **Clavier [touche]** : Se déclenche à chaque frame tant que la touche est maintenue
- **Touche pressée [touche]** : Se déclenche une fois quand la touche est d'abord enfoncée
- **Touche relâchée [touche]** : Se déclenche une fois quand la touche est relâchée

---

## Salles

### Quelle salle se charge en premier ?

La première salle dans l'arbre des ressources (en haut de la liste) se charge au démarrage du jeu. Faites glisser les salles pour les réordonner.

### Comment changer de salle ?

Utilisez les actions de salle :
- **Salle suivante** : Aller à la salle suivante dans l'ordre
- **Salle précédente** : Aller à la salle précédente
- **Aller à la salle** : Aller à une salle spécifique

### Les objets disparaissent quand je change de salle

Les objets sont détruits en quittant une salle sauf s'ils sont marqués comme **Persistants** dans leurs propriétés.

### Ma salle est trop grande/petite à l'écran

La taille de la fenêtre de jeu correspond aux dimensions de la première salle. Vous pouvez :
- Changer la taille de la salle pour correspondre à la taille de fenêtre désirée
- Utiliser les Vues pour n'afficher qu'une partie de la salle

---

## Graphiques et sprites

### Quels formats d'image sont supportés ?

- PNG (recommandé, prend en charge la transparence)
- JPEG/JPG
- BMP
- GIF (première image seulement)

### Mon sprite apparaît à la mauvaise position

Vérifiez le paramètre **Origine** dans l'éditeur de sprite. L'origine est le point d'ancrage pour le positionnement. Paramètres courants :
- Haut-gauche (0, 0) : Par défaut
- Centre : Bon pour les objets en rotation
- Bas-centre : Bon pour les personnages

### Comment animer un sprite ?

1. Créez un sprite avec plusieurs frames (bande horizontale)
2. Définissez le **Nombre de frames** dans les propriétés du sprite
3. Ajustez la **Vitesse d'animation** (frames par seconde)

### Les sprites sont flous

Cela arrive lors de la mise à l'échelle des sprites. Pour le pixel art, désactivez l'interpolation/le lissage dans les paramètres du jeu si disponible.

---

## Son et musique

### Quels formats audio sont supportés ?

- WAV (non compressé)
- OGG (recommandé pour la musique)
- MP3

### Le son ne joue pas

Vérifiez :
1. Le fichier audio existe dans le dossier des sons
2. Le format de fichier est supporté
3. Vous utilisez le bon nom de son dans les actions
4. Le navigateur peut nécessiter une interaction utilisateur (pour HTML5)

### Comment mettre en boucle la musique de fond ?

Utilisez l'action **Jouer une musique** avec l'option boucle activée, ou utilisez **Jouer un son** avec le paramètre boucle défini sur vrai.

---

## Exportation

### Mon jeu exporté ne fonctionne pas

Problèmes courants :
- **Windows** : DLL manquantes - assurez-vous que tout le dossier de sortie est inclus
- **HTML5** : Navigateur bloquant les fichiers locaux - hébergez sur un serveur
- **Ressources manquantes** : Vérifiez que tous les fichiers sont inclus

### Le fichier exporté est énorme

La taille du jeu inclut Python et toutes les bibliothèques. Pour réduire la taille :
- Supprimez les ressources inutilisées
- Compressez les images et l'audio
- Utilisez des formats appropriés (OGG au lieu de WAV)
- Activez la compression UPX pour les builds Windows

### Puis-je vendre des jeux créés avec PyGameMaker ?

Oui ! Les jeux que vous créez vous appartiennent entièrement et vous pouvez les vendre. Le code source de PyGameMaker est sous licence MIT permissive, vous pouvez donc l'utiliser librement dans des projets commerciaux — et contrairement aux licences copyleft, vous n'êtes pas obligé de publier vos propres modifications en open-source.

---

## Blockly / Programmation visuelle

### Où trouver l'éditeur Blockly ?

1. Ouvrez un objet
2. Cliquez sur l'onglet **Blockly** dans l'éditeur d'objets
3. L'espace de travail de programmation visuelle apparaît

### Comment basculer entre Blockly et les événements ?

Les deux systèmes fonctionnent sur le même objet. L'onglet Blockly et l'onglet Événements montrent des vues différentes de la même logique. Les changements dans l'un sont reflétés dans l'autre.

### Mes blocs Blockly ont disparu

Vérifiez :
1. Vous visualisez le bon objet
2. Faites défiler l'espace de travail (les blocs pourraient être hors écran)
3. Vérifiez le niveau de zoom

---

## Performance

### Mon jeu tourne lentement

Conseils pour de meilleures performances :
1. Réduisez le nombre d'instances
2. Évitez les calculs lourds dans les événements Step
3. Utilisez des alarmes au lieu de compter les frames
4. Optimisez les tailles des sprites
5. Détruisez les instances qui quittent la salle

### L'événement Step s'exécute trop souvent

L'événement Step s'exécute à chaque frame (60 fois/seconde par défaut). Utilisez :
- Des alarmes pour les actions différées
- Des conditions pour vérifier avant les opérations lourdes
- Une vitesse de salle plus basse si approprié

---

## Obtenir de l'aide

### Où puis-je signaler des bugs ?

Signalez les bugs sur la page [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Incluez :
- Ce que vous attendiez
- Ce qui s'est réellement passé
- Les étapes pour reproduire
- Votre système d'exploitation et votre version de Python

### Où puis-je en apprendre plus ?

- [[Demarrage_fr]] - Installation et bases
- [[Premier_Jeu_fr]] - Tutoriel étape par étape
- [[Evenements_Actions_fr]] - Référence complète
- [[Programmation_Visuelle_fr]] - Guide Blockly
