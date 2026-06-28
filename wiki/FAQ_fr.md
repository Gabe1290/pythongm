# Questions frequemment posees

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Retour a l'accueil](Home_fr)

---

## Questions generales

### Qu'est-ce que PyGameMaker?

PyGameMaker est un IDE de developpement de jeux open-source inspire de GameMaker 7.0. Il vous permet de creer des jeux 2D en utilisant la programmation visuelle (Google Blockly) ou un systeme evenement-action, sans avoir besoin d'ecrire du code.

### PyGameMaker est-il gratuit?

Oui! PyGameMaker est completement gratuit et open-source — le code source est sous licence MIT, et la documentation sous licence CC BY 4.0.

### Vers quelles plateformes puis-je exporter?

- Windows (executable .exe autonome)
- HTML5 (navigateurs web)
- Linux (binaire natif)
- Mobile (iOS/Android via Kivy)

### Ai-je besoin d'experience en programmation?

Non! PyGameMaker est concu pour les debutants. Vous pouvez creer des jeux en utilisant:
- Les blocs Blockly par glisser-deposer
- Le systeme evenement/action par pointer-cliquer
- Aucun codage requis

### Est-il compatible avec les fichiers GameMaker?

PyGameMaker est inspire de GameMaker 7.0 mais utilise son propre format de projet. Vous ne pouvez pas importer directement des fichiers GameMaker, mais les concepts et le flux de travail sont similaires.

---

## Installation

### Quelles sont les exigences systeme?

- Python 3.10 ou superieur
- Windows, Linux ou macOS
- 4 Go de RAM minimum (8 Go recommande)
- ~500 Mo d'espace disque

### Comment installer PyGameMaker?

Voir [[Demarrage_fr]] pour des instructions d'installation detaillees. La version courte:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python main.py
```

### Python n'est pas reconnu / non trouve

Assurez-vous que Python est installe et ajoute au PATH de votre systeme. Vous pouvez verifier en executant:

```bash
python --version
```

Si cela echoue, reinstallez Python et cochez "Ajouter Python au PATH" lors de l'installation.

### J'obtiens des erreurs d'importation au demarrage

Essayez de reinstaller les dependances:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projets

### Ou sont sauvegardes mes projets?

Les projets sont sauvegardes dans des dossiers que vous choisissez. Chaque projet contient:
- `project.json` - Fichier de projet principal
- Dossiers pour les sprites, sons, objets, salles, etc.

### Puis-je avoir plusieurs projets ouverts?

Actuellement, PyGameMaker ouvre un projet a la fois. Utilisez **Fichier > Ouvrir un projet** pour basculer entre les projets.

### Comment sauvegarder mon projet?

Copiez simplement le dossier entier du projet. Toutes les ressources et parametres sont contenus a l'interieur. Considerez l'utilisation de git pour le controle de version:

```bash
cd mon_projet
git init
git add .
git commit -m "Sauvegarde initiale"
```

### Mon projet ne s'ouvre pas / est corrompu

Essayez ces etapes:
1. Verifiez si `project.json` existe et n'est pas vide
2. Ouvrez `project.json` dans un editeur de texte pour verifier les erreurs JSON
3. Restaurez depuis une sauvegarde si disponible
4. Verifiez la sortie console pour des messages d'erreur specifiques

---

## Objets et evenements

### Quelle est la difference entre un objet et une instance?

- **Objet**: Un modele/plan definissant un comportement
- **Instance**: Une copie specifique d'un objet placee dans une salle

Par exemple, `obj_ennemi` est un objet. Placer 5 ennemis dans une salle cree 5 instances de `obj_ennemi`.

### Pourquoi mon evenement ne se declenche-t-il pas?

Causes courantes:
1. **Mauvais type d'evenement**: Assurez-vous d'utiliser le bon evenement (ex: "Touche pressee" vs "Clavier")
2. **Pas d'instances**: L'objet doit avoir des instances dans la salle
3. **Objet non visible**: Verifiez la propriete visible
4. **Ordre d'execution**: Certains evenements s'executent avant d'autres

### Comment faire interagir les objets?

Utilisez les evenements de collision:
1. Ouvrez l'objet qui doit detecter la collision
2. Ajoutez l'evenement **Collision avec [autre_objet]**
3. Ajoutez des actions pour ce qui se passe lors de la collision

### Quelle est la difference entre les evenements "Clavier" et "Touche pressee"?

- **Clavier [touche]**: Se declenche a chaque frame tant que la touche est maintenue
- **Touche pressee [touche]**: Se declenche une fois quand la touche est d'abord enfoncee
- **Touche relachee [touche]**: Se declenche une fois quand la touche est relachee

---

## Salles

### Quelle salle se charge en premier?

La premiere salle dans l'arbre des ressources (en haut de la liste) se charge au demarrage du jeu. Faites glisser les salles pour les reordonner.

### Comment changer de salle?

Utilisez les actions de salle:
- **Salle suivante**: Aller a la salle suivante dans l'ordre
- **Salle precedente**: Aller a la salle precedente
- **Aller a la salle**: Aller a une salle specifique

### Les objets disparaissent quand je change de salle

Les objets sont detruits en quittant une salle sauf s'ils sont marques comme **Persistants** dans leurs proprietes.

### Ma salle est trop grande/petite a l'ecran

La taille de la fenetre de jeu correspond aux dimensions de la premiere salle. Vous pouvez:
- Changer la taille de la salle pour correspondre a la taille de fenetre desiree
- Utiliser les Vues pour n'afficher qu'une partie de la salle

---

## Graphiques et sprites

### Quels formats d'image sont supportes?

- PNG (recommande, supporte la transparence)
- JPEG/JPG
- BMP
- GIF (premiere image seulement)

### Mon sprite apparait a la mauvaise position

Verifiez le parametre **Origine** dans l'editeur de sprite. L'origine est le point d'ancrage pour le positionnement. Parametres courants:
- Haut-gauche (0, 0): Par defaut
- Centre: Bon pour les objets en rotation
- Bas-centre: Bon pour les personnages

### Comment animer un sprite?

1. Creez un sprite avec plusieurs frames (bande horizontale)
2. Definissez le **Nombre de frames** dans les proprietes du sprite
3. Ajustez la **Vitesse d'animation** (frames par seconde)

### Les sprites sont flous

Cela arrive lors de la mise a l'echelle des sprites. Pour le pixel art, desactivez l'interpolation/lissage dans les parametres du jeu si disponible.

---

## Son et musique

### Quels formats audio sont supportes?

- WAV (non compresse)
- OGG (recommande pour la musique)
- MP3

### Le son ne joue pas

Verifiez:
1. Le fichier audio existe dans le dossier des sons
2. Le format de fichier est supporte
3. Vous utilisez le bon nom de son dans les actions
4. Le navigateur peut necessiter une interaction utilisateur (pour HTML5)

### Comment mettre en boucle la musique de fond?

Utilisez l'action **Jouer musique** avec l'option boucle activee, ou utilisez **Jouer son** avec le parametre boucle defini sur vrai.

---

## Exportation

### Mon jeu exporte ne fonctionne pas

Problemes courants:
- **Windows**: DLLs manquantes - assurez-vous que tout le dossier de sortie est inclus
- **HTML5**: Navigateur bloquant les fichiers locaux - hebergez sur un serveur
- **Ressources manquantes**: Verifiez que tous les fichiers sont inclus

### Le fichier exporte est enorme

La taille du jeu inclut Python et toutes les bibliotheques. Pour reduire la taille:
- Supprimez les ressources inutilisees
- Compressez les images et l'audio
- Utilisez des formats appropries (OGG au lieu de WAV)
- Activez la compression UPX pour les builds Windows

### Puis-je vendre des jeux crees avec PyGameMaker?

Oui! Les jeux que vous creez vous appartiennent entierement et vous pouvez les vendre. Le code source de PyGameMaker est sous licence MIT permissive, vous pouvez donc l'utiliser librement dans des projets commerciaux — et contrairement aux licences copyleft, vous n'etes pas oblige de publier vos propres modifications en open-source (meme si les contributions sont toujours les bienvenues).

---

## Blockly / Programmation visuelle

### Ou trouver l'editeur Blockly?

1. Ouvrez un objet
2. Cliquez sur l'onglet **Blockly** dans l'editeur d'objets
3. L'espace de travail de programmation visuelle apparait

### Comment basculer entre Blockly et les evenements?

Les deux systemes fonctionnent sur le meme objet. L'onglet Blockly et l'onglet Evenements montrent des vues differentes de la meme logique. Les changements dans l'un sont refletes dans l'autre.

### Mes blocs Blockly ont disparu

Verifiez:
1. Vous visualisez le bon objet
2. Faites defiler l'espace de travail (les blocs pourraient etre hors ecran)
3. Verifiez le niveau de zoom

---

## Performance

### Mon jeu tourne lentement

Conseils pour de meilleures performances:
1. Reduisez le nombre d'instances
2. Evitez les calculs lourds dans les evenements Step
3. Utilisez des alarmes au lieu de compter les frames
4. Optimisez les tailles des sprites
5. Detruisez les instances qui quittent la salle

### L'evenement Step s'execute trop souvent

L'evenement Step s'execute a chaque frame (60 fois/seconde par defaut). Utilisez:
- Des alarmes pour les actions differees
- Des conditions pour verifier avant les operations lourdes
- Une vitesse de salle plus basse si approprie

---

## Obtenir de l'aide

### Ou puis-je signaler des bugs?

Signalez les bugs sur la page [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Incluez:
- Ce que vous attendiez
- Ce qui s'est reellement passe
- Les etapes pour reproduire
- Votre systeme d'exploitation et version de Python

### Comment puis-je contribuer?

Les contributions sont les bienvenues! Consultez le depot GitHub pour:
- Contributions au code
- Rapports de bugs
- Demandes de fonctionnalites
- Traductions
- Ameliorations de documentation

### Ou puis-je en apprendre plus?

- [[Demarrage_fr]] - Installation et bases
- [[Premier-Jeu_fr]] - Tutoriel etape par etape
- [[Evenements-Actions_fr]] - Reference complete
- [[Programmation-Visuelle_fr]] - Guide Blockly
