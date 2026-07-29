# Éditeur de salles

> [English](Room-Editor) | [Français](Editeur_Salles_fr) | [Deutsch](Raum_Editor_de) | [Italiano](Editor_Stanze_it) | [Español](Editor_Salas_es) | [Português](Editor_Salas_pt) | [Slovenščina](Urejevalnik_Sob_sl) | [Українська](Redaktor_Kimnat_uk) | [Русский](Redaktor_Komnat_ru)

---

> [Retour à l'accueil](Home_fr)

Les salles sont les niveaux, écrans ou scènes de votre jeu. L'éditeur de salles vous permet de concevoir ces espaces en plaçant des objets et en configurant les arrière-plans.

---

## Ouvrir l'éditeur de salles

1. Double-cliquez sur une salle existante dans l'arbre des ressources, ou
2. Clic droit sur **Salles** > **Créer une salle**

---

## Propriétés de la salle

| Propriété | Description |
|-----------|-------------|
| **Nom** | Identifiant unique (ex : `room_niveau1`) |
| **Largeur** | Largeur de la salle en pixels |
| **Hauteur** | Hauteur de la salle en pixels |
| **Vitesse** | Vitesse du jeu en images par seconde (défaut : 60) |
| **Persistante** | Conserver l'état de la salle en la quittant/y revenant |

---

## Placer des objets

### Ajouter des instances

1. Sélectionnez un objet dans le panneau **Objets**
2. Cliquez dans la vue de la salle pour placer une instance
3. Cliquez et faites glisser pour placer plusieurs instances

### Sélectionner des instances

- Cliquez sur une instance pour la sélectionner
- Maintenez **Ctrl** et cliquez pour en sélectionner plusieurs
- Dessinez un rectangle pour sélectionner toutes les instances à l'intérieur

### Déplacer des instances

- Faites glisser les instances sélectionnées avec la souris
- Utilisez les touches fléchées pour un déplacement précis

### Supprimer des instances

- Sélectionnez les instances et appuyez sur **Supprimer**, ou
- Clic droit et choisissez **Supprimer**

---

## Paramètres de grille

Activez la grille pour un placement précis :

1. Allez dans **Vue > Afficher la grille**
2. Définissez la taille de la grille (ex : 32x32)
3. Activez **Aligner sur la grille**

Tailles de grille courantes :
- **16x16** - Petites tuiles
- **32x32** - Tuiles standard
- **64x64** - Grandes tuiles

---

## Arrière-plans

### Définir un arrière-plan

1. Cliquez sur l'onglet **Arrière-plans**
2. Sélectionnez une ressource d'arrière-plan
3. Configurez les options d'affichage

### Options d'arrière-plan

| Option | Description |
|--------|-------------|
| **Visible** | Afficher/masquer l'arrière-plan |
| **Premier plan** | Dessiner devant les objets |
| **Répéter horizontalement** | Répéter horizontalement |
| **Répéter verticalement** | Répéter verticalement |
| **Étirer** | Étirer pour remplir la salle |
| **Vitesse horizontale** | Vitesse de défilement (parallaxe) |
| **Vitesse verticale** | Vitesse de défilement (parallaxe) |

---

## Ordre des salles

L'ordre des salles dans l'arbre des ressources détermine :
1. Quelle salle se charge en premier (salle du haut = salle de départ)
2. L'ordre pour les actions « Salle suivante » et « Salle précédente »

### Changer l'ordre des salles

- Faites glisser les salles dans l'arbre des ressources pour les réordonner
- Ou clic droit et utilisez **Monter** / **Descendre**

---

## Conseils et bonnes pratiques

### Organisation
- Nommez clairement les salles selon leur fonction
- Gardez le menu principal comme première salle
- Utilisez des tailles de salle cohérentes dans un jeu

### Performance
- Ne placez pas trop d'instances dans une salle
- Utilisez des tuiles pour la géométrie statique des niveaux
- Détruisez les instances hors écran si possible

---

## Prochaines étapes

- [[Editeur_Objets_fr]] - Créer des objets à placer dans les salles
- [[Evenements_Actions_fr]] - Ajouter de l'interactivité à vos niveaux
- [[Exportation_fr]] - Partager votre jeu terminé
