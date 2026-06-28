# Demarrage

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

> [Retour a l'accueil](Home_fr)

Ce guide vous aidera a installer et lancer PyGameMaker sur votre systeme.

---

## Configuration requise

- **Python** 3.10 ou superieur
- **Systeme d'exploitation:** Windows, Linux ou macOS
- **Espace disque:** ~500 Mo pour l'installation
- **RAM:** 4 Go minimum, 8 Go recommande

---

## Installation

### Etape 1: Installer Python

Telechargez Python 3.10+ depuis [python.org](https://www.python.org/downloads/) et installez-le. Assurez-vous de cocher "Ajouter Python au PATH" lors de l'installation sur Windows.

### Etape 2: Cloner le depot

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Ou telechargez le fichier ZIP depuis la [page des releases](https://github.com/Gabe1290/pythongm/releases).

### Etape 3: Creer un environnement virtuel

```bash
python -m venv venv
```

Activez l'environnement virtuel:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Etape 4: Installer les dependances

```bash
pip install -r requirements.txt
```

### Etape 5: Lancer PyGameMaker

```bash
python main.py
```

---

## Premier lancement

Au premier lancement de PyGameMaker, vous verrez:

1. **Barre de menu** - Fichier, Edition, Ressources, Executer et Aide
2. **Arbre des ressources** - Panneau gauche montrant les ressources du projet
3. **Espace de travail** - Zone centrale pour editer les ressources
4. **Panneau des proprietes** - Panneau droit pour les proprietes

---

## Changer de langue

PyGameMaker supporte plusieurs langues:

1. Allez dans **Edition > Preferences**
2. Selectionnez votre langue preferee
3. Redemarrez PyGameMaker pour appliquer le changement

Langues disponibles: Anglais, francais, allemand, italien, espagnol, portugais, slovene, ukrainien, russe

---

## Prochaines etapes

- [[Premier-Jeu_fr]] - Creez votre premier jeu etape par etape
- [[Editeur-Objets_fr]] - Apprenez a creer des objets
- [[Editeur-Salles_fr]] - Concevez vos niveaux
- [[Evenements-Actions_fr]] - Comprenez la logique du jeu
- [[FAQ_fr]] - Questions frequemment posees
