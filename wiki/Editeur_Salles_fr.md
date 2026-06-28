# Editeur de salles

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

> [Retour a l'accueil](Home_fr)

Les salles sont les niveaux, ecrans ou scenes de votre jeu. L'editeur de salles vous permet de concevoir ces espaces en placant des objets et en configurant les arriere-plans.

---

## Ouvrir l'editeur de salles

1. Double-cliquez sur une salle existante dans l'arbre des ressources, ou
2. Clic droit sur **Salles** > **Creer une salle**

---

## Proprietes de la salle

| Propriete | Description |
|-----------|-------------|
| **Nom** | Identifiant unique (ex: `room_niveau1`) |
| **Largeur** | Largeur de la salle en pixels |
| **Hauteur** | Hauteur de la salle en pixels |
| **Vitesse** | Vitesse du jeu en images par seconde (defaut: 60) |
| **Persistante** | Conserver l'etat de la salle en la quittant/revenant |

---

## Placer des objets

### Ajouter des instances

1. Selectionnez un objet dans le panneau **Objets**
2. Cliquez dans la vue de la salle pour placer une instance
3. Cliquez et faites glisser pour placer plusieurs instances

### Selectionner des instances

- Cliquez sur une instance pour la selectionner
- Maintenez **Ctrl** et cliquez pour selectionner plusieurs
- Dessinez un rectangle pour selectionner toutes les instances a l'interieur

### Deplacer des instances

- Faites glisser les instances selectionnees avec la souris
- Utilisez les touches flechees pour un deplacement precis

### Supprimer des instances

- Selectionnez les instances et appuyez sur **Supprimer**, ou
- Clic droit et choisissez **Supprimer**

---

## Parametres de grille

Activez la grille pour un placement precis:

1. Allez dans **Vue > Afficher la grille**
2. Definissez la taille de la grille (ex: 32x32)
3. Activez **Aligner sur la grille**

Tailles de grille courantes:
- **16x16** - Petites tuiles
- **32x32** - Tuiles standard
- **64x64** - Grandes tuiles

---

## Arriere-plans

### Definir un arriere-plan

1. Cliquez sur l'onglet **Arriere-plans**
2. Selectionnez une ressource d'arriere-plan
3. Configurez les options d'affichage

### Options d'arriere-plan

| Option | Description |
|--------|-------------|
| **Visible** | Afficher/masquer l'arriere-plan |
| **Premier plan** | Dessiner devant les objets |
| **Repeter horizontalement** | Repeter horizontalement |
| **Repeter verticalement** | Repeter verticalement |
| **Etirer** | Etirer pour remplir la salle |
| **Vitesse horizontale** | Vitesse de defilement (parallaxe) |
| **Vitesse verticale** | Vitesse de defilement (parallaxe) |

---

## Ordre des salles

L'ordre des salles dans l'arbre des ressources determine:
1. Quelle salle se charge en premier (salle du haut = salle de depart)
2. L'ordre pour les actions "Salle suivante" et "Salle precedente"

### Changer l'ordre des salles

- Faites glisser les salles dans l'arbre des ressources pour les reordonner
- Ou clic droit et utilisez **Monter** / **Descendre**

---

## Conseils et bonnes pratiques

### Organisation
- Nommez clairement les salles selon leur fonction
- Gardez le menu principal comme premiere salle
- Utilisez des tailles de salle coherentes dans un jeu

### Performance
- Ne placez pas trop d'instances dans une salle
- Utilisez des tuiles pour la geometrie statique des niveaux
- Detruisez les instances hors ecran si possible

---

## Prochaines etapes

- [[Editeur-Objets_fr]] - Creer des objets a placer dans les salles
- [[Evenements-Actions_fr]] - Ajouter de l'interactivite a vos niveaux
- [[Exportation_fr]] - Partager votre jeu termine
