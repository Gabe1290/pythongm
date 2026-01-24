# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Un environnement de développement de jeux vidéo inspiré de GameMaker 7.0**

PyGameMaker est un IDE open-source qui rend la création de jeux 2D accessible grâce à la programmation visuelle par blocs (Google Blockly) et un système d'événements-actions. Créez des jeux sans connaissances approfondies en programmation, puis exportez-les vers Windows, Linux, HTML5 ou plateformes mobiles.

---

## Choisissez Votre Niveau

PyGameMaker utilise des **préréglages** pour contrôler quels événements et actions sont disponibles. Cela aide les débutants à se concentrer sur les fonctionnalités essentielles tout en permettant aux utilisateurs expérimentés d'accéder à l'ensemble des outils.

| Préréglage | Idéal Pour | Fonctionnalités |
|------------|------------|-----------------|
| [**Débutant**](Beginner-Preset_fr) | Nouveaux en développement de jeux | 4 événements, 17 actions - Mouvement, collisions, score, salles |
| [**Intermédiaire**](Intermediate-Preset_fr) | Quelques connaissances | +4 événements, +12 actions - Vies, santé, son, alarmes, dessin |
| **Avancé** | Utilisateurs expérimentés | Tous les 40+ événements et actions disponibles |

**Nouveaux utilisateurs:** Commencez avec le [Préréglage Débutant](Beginner-Preset_fr) pour apprendre les bases sans être submergé.

Consultez le [Guide des Préréglages](Preset-Guide_fr) pour un aperçu complet du système de préréglages.

---

## Fonctionnalités en Bref

| Fonctionnalité | Description |
|----------------|-------------|
| **Programmation Visuelle** | Codage par glisser-déposer avec Google Blockly 12.x |
| **Système Événements-Actions** | Logique événementielle compatible GameMaker 7.0 |
| **Préréglages par Niveau** | Ensembles de fonctionnalités Débutant, Intermédiaire et Avancé |
| **Export Multi-Plateforme** | Windows EXE, HTML5, Linux, Kivy (mobile/bureau) |
| **Gestion des Ressources** | Sprites, sons, arrière-plans, polices et salles |
| **Interface Multilingue** | Anglais, Français, Allemand, Italien, Espagnol, Portugais, Slovène, Ukrainien, Russe |
| **Extensible** | Système de plugins pour événements et actions personnalisés |

---

## Pour Commencer

### Configuration Requise

- **Python** 3.10 ou supérieur
- **Système d'exploitation:** Windows, Linux ou macOS

### Installation

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Créez un environnement virtuel (recommandé):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

4. Lancez PyGameMaker:
   ```bash
   python main.py
   ```

---

## Concepts Fondamentaux

### Objets
Entités de jeu avec sprites, propriétés et comportements. Chaque objet peut avoir plusieurs événements avec des actions associées.

### Événements
Déclencheurs qui exécutent des actions lorsque des conditions spécifiques se produisent:
- **Create** - Quand une instance est créée
- **Step** - Chaque frame (généralement 60 FPS)
- **Draw** - Phase de rendu personnalisé
- **Destroy** - Quand une instance est détruite
- **Keyboard** - Touche pressée, relâchée ou maintenue
- **Mouse** - Clics, mouvement, entrée/sortie
- **Collision** - Quand des instances se touchent
- **Alarm** - Minuteries (12 disponibles)

Consultez la [Référence des Événements](Event-Reference_fr) pour la documentation complète.

### Actions
Opérations effectuées quand les événements se déclenchent. 40+ actions intégrées pour:
- Mouvement et physique
- Dessin et sprites
- Score, vies et santé
- Son et musique
- Gestion des instances et salles

Consultez la [Référence Complète des Actions](Full-Action-Reference_fr) pour la documentation complète.

### Salles
Niveaux de jeu où vous placez les instances d'objets, définissez les arrière-plans et la zone de jeu.

---

## Programmation Visuelle avec Blockly

PyGameMaker intègre Google Blockly pour la programmation visuelle. Les blocs sont organisés en catégories:

- **Événements** - Create, Step, Draw, Keyboard, Mouse
- **Mouvement** - Vitesse, direction, position, gravité
- **Timing** - Alarmes et délais
- **Dessin** - Formes, texte, sprites
- **Score/Vies/Santé** - Suivi de l'état du jeu
- **Instance** - Créer et détruire des objets
- **Salle** - Navigation et gestion
- **Valeurs** - Variables et expressions
- **Son** - Lecture audio
- **Sortie** - Debug et affichage

---

## Options d'Export

### Windows EXE
Exécutables Windows autonomes utilisant PyInstaller. Aucun Python requis sur la machine cible.

### HTML5
Jeux web mono-fichier qui fonctionnent dans tout navigateur moderne. Compressés avec gzip pour un chargement rapide.

### Linux
Exécutables Linux natifs pour environnements Python 3.10+.

### Kivy
Applications multiplateformes pour mobile (iOS/Android) et bureau via Buildozer.

---

## Structure du Projet

```
nom_du_projet/
├── project.json      # Configuration du projet
├── backgrounds/      # Images d'arrière-plan et métadonnées
├── data/             # Fichiers de données personnalisés
├── fonts/            # Définitions de polices
├── objects/          # Définitions d'objets (JSON)
├── rooms/            # Dispositions des salles (JSON)
├── scripts/          # Scripts personnalisés
├── sounds/           # Fichiers audio et métadonnées
├── sprites/          # Images de sprites et métadonnées
└── thumbnails/       # Miniatures générées des ressources
```

---

## Contenu du Wiki

### Préréglages et Référence
- [Guide des Préréglages](Preset-Guide_fr) - Aperçu du système de préréglages
- [Préréglage Débutant](Beginner-Preset_fr) - Fonctionnalités essentielles pour les nouveaux utilisateurs
- [Préréglage Intermédiaire](Intermediate-Preset_fr) - Fonctionnalités supplémentaires
- [Référence des Événements](Event-Reference_fr) - Documentation complète des événements
- [Référence des Actions](Full-Action-Reference_fr) - Documentation complète des actions

### Tutoriels et Guides
- [Premiers Pas](Demarrage_fr) - Premiers pas avec PyGameMaker
- [Créer Votre Premier Jeu](Premier_Jeu_fr) - Tutoriel pas à pas
- [Éditeur d'Objets](Editeur_Objets_fr) - Travailler avec les objets de jeu
- [Éditeur de Salles](Editeur_Salles_fr) - Concevoir des niveaux
- [Événements et Actions](Evenements_Actions_fr) - Référence de la logique de jeu
- [Programmation Visuelle](Programmation_Visuelle_fr) - Utiliser les blocs Blockly
- [Exporter des Jeux](Exportation_fr) - Compiler pour différentes plateformes
- [FAQ](FAQ_fr) - Questions fréquemment posées

---

## Contribuer

Les contributions sont les bienvenues! Consultez nos directives de contribution pour:
- Rapports de bugs et demandes de fonctionnalités
- Contributions au code
- Traductions
- Améliorations de la documentation

---

## Licence

PyGameMaker est sous licence **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Liens

- [Dépôt GitHub](https://github.com/Gabe1290/pythongm)
- [Suivi des Issues](https://github.com/Gabe1290/pythongm/issues)
- [Versions](https://github.com/Gabe1290/pythongm/releases)
