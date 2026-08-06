# Programmation visuelle

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

> [Retour à l'accueil](Home_fr)

PyGameMaker inclut Google Blockly pour la programmation visuelle par glisser-déposer. Construisez la logique du jeu en connectant des blocs au lieu d'écrire du code.

---

## Accéder à Blockly

1. Ouvrez un objet dans l'éditeur d'objets
2. Cliquez sur l'onglet **Blockly** (à côté de l'onglet Événements)
3. L'espace de travail Blockly apparaît avec une boîte à outils à gauche

**Les blocs visibles dépendent de votre préréglage.** `Outils > Configurer
les blocs d'action...` (ou `Préférences > Édition de l'IDE`, qui définit le
préréglage par défaut des nouveaux projets) contrôle l'ensemble de blocs —
voir le [Guide des Préréglages](Preset-Guide_fr) pour les détails. Les
tableaux ci-dessous listent tous les blocs existant dans un préréglage ou
un autre ; un projet donné peut en afficher moins.

---

## L'espace de travail Blockly

### Boîte à outils
Le panneau gauche contient les catégories de blocs :
- **Événements** - Blocs déclencheurs d'événements
- **Contrôle** - Conditions, variables et regroupement (les blocs
  conditionnels de ce projet sont des blocs empilables, pas des conteneurs
  si/sinon classiques — voir « Types de blocs » ci-dessous)
- **Mouvement** - Blocs de mouvement, de vitesse et de physique
- **Timing** - Alarmes
- **Dessin** - Blocs de texte et de formes
- **Score/Vies/Santé** - Blocs d'état du jeu
- **Instance** - Création/destruction d'objets
- **Salle** - Navigation entre salles
- **Valeurs** - Blocs valeur (position, vitesse, score, vies, santé, souris)
- **Son** - Lecture audio
- **Sortie** - Messages et code Python personnalisé
- **Jeu** - Terminer/redémarrer le jeu, table des meilleurs scores

Il n'existe pas de catégorie Math, Texte ou Logique séparée — les champs
numériques/texte se saisissent directement sur chaque bloc, et il n'y a pas
de bloc valeur booléen/de comparaison générique. Voir « Types de blocs »
ci-dessous pour savoir comment fonctionnent les conditions à la place.

### Espace de travail
La zone centrale où vous construisez votre programme en :
- Glissant des blocs depuis la boîte à outils
- Connectant les blocs ensemble
- Configurant les paramètres des blocs

### Corbeille
Faites glisser les blocs non désirés ici pour les supprimer, ou appuyez sur la touche Supprimer.

---

## Types de blocs

### Blocs chapeau (Événements)
Les blocs chapeau ont un sommet arrondi et démarrent une séquence. Ils représentent des événements :

```
┌─────────────────┐
│ Quand Create    │
└─────────────────┘
```

### Blocs empilables (Actions)
Les blocs empilables ont des encoches qui se connectent à d'autres blocs.
Presque tous les blocs hors de la catégorie Valeurs sont des blocs
empilables — y compris les blocs conditionnels :

```
├─────────────────┤
│ Définir Vitesse Horizontale [5] │
├─────────────────┤
```

### Blocs valeur (Valeurs)
Les blocs valeur sont arrondis et se branchent dans un champ numérique
d'un autre bloc (par ex. le champ vitesse de Déplacer Direction, ou le
champ valeur de Définir Variable). Ce projet en compte 9 — Position X,
Position Y, Vitesse Horizontale, Vitesse Verticale, Score, Vies, Santé,
Souris X, Souris Y :

```
( Position X )    ( Score )    ( 100 )
```

Il n'existe pas de bloc valeur `( vitesse )` ou `( direction )` générique —
ces notions ne sont pas suivies comme une valeur unique dans ce moteur (la
vitesse/direction de déplacement se déduisent de Vitesse Horizontale +
Vitesse Verticale ensemble), et il n'y a pas non plus de bloc valeur pour
les variables personnalisées (lisez-les via la comparaison de Tester une
Variable à la place).

### Conditions — blocs empilables, pas des conteneurs en C
Contrairement aux langages visuels façon Scratch, les blocs Si Condition /
Tester une Variable de ce projet sont des **blocs empilables avec un seul
créneau « alors »**, pas des conteneurs si/sinon à deux côtés, et il n'y a
pas de bloc booléen hexagonal à y brancher — la comparaison se construit
directement avec des champs sur le bloc :

```
┌───────────────────────────────────┐
│ Si le nombre de [obj_piece] [==] [0] │
├───────────────────────────────────┤
│  alors [actions ici]              │
└───────────────────────────────────┘
```

Pour ajouter une branche « sinon » ou exécuter plusieurs actions d'un côté
ou de l'autre, combinez-le avec trois autres blocs de Contrôle :
- **Sinon** - exécute son propre bloc suivant uniquement quand le test
  précédent était faux
- **Début de Bloc** / **Fin de Bloc** - regroupent plusieurs actions pour
  que le test précédent (ou Sinon) s'applique à tout le groupe, pas
  seulement au bloc suivant

C'est le même flux conditionnel plat façon GM80 qu'utilise le panneau
structuré Événements/Actions (voir [Événements et Actions](Evenements_Actions_fr))
— Blockly est une peau glisser-déposer par-dessus la même liste d'actions
sous-jacente, pas un modèle d'exécution séparé.

---

## Blocs d'événements

### Événement Create
```
┌─────────────────────┐
│ Quand Create        │
├─────────────────────┤
│ [actions ici]        │
└─────────────────────┘
```

### Événement Step
```
┌─────────────────────┐
│ Quand Step           │
├─────────────────────┤
│ [chaque frame]       │
└─────────────────────┘
```

### Événements clavier
Il existe quatre blocs chapeau clavier séparés — Touche Maintenue, Touche
Pressée, Touche Relâchée et Aucune Touche — chacun avec un menu déroulant
de nom de touche (Aucune Touche n'en a pas, puisqu'il se déclenche quand
rien n'est maintenu) :
```
┌─────────────────────────┐
│ Quand touche [maintenue : gauche] ▼│
├─────────────────────────┤
│ [actions ici]            │
└─────────────────────────┘
```

### Événements collision
```
┌────────────────────────────┐
│ Quand collision avec [obj] ▼│
├────────────────────────────┤
│ [actions ici]               │
└────────────────────────────┘
```

---

## Blocs de mouvement

| Bloc | Description |
|------|-------------|
| `Définir Vitesse Horizontale [4]` | Définir la vélocité X |
| `Définir Vitesse Verticale [-5]` | Définir la vélocité Y |
| `Arrêter le Mouvement` | Mettre les deux vitesses à zéro |
| `Déplacer [direction ▼] vitesse [3]` | Se déplacer dans une des 4 directions (ou diagonales, ou « stop ») |
| `Déplacement Libre [direction] [vitesse]` | Se déplacer selon un angle et une vitesse arbitraires |
| `Définir Vitesse [5]` | Définir la magnitude de vitesse, en préservant la direction actuelle |
| `Définir Direction [90]` | Définir l'angle de direction, en préservant la vitesse actuelle |
| `Se Déplacer Vers x:[100] y:[200] vitesse:[3]` | Se déplacer vers un point |
| `Aligner sur la Grille` | Aligner la position sur la grille |
| `Sauter à la Position x:[100] y:[200]` | Téléportation instantanée |
| `Déplacement Grille [direction]` | Se déplacer exactement d'une case de grille |
| `Arrêter si Aucune Touche` / `Vérifier Touches et Déplacer` / `Si Aligné sur la Grille` | Aides au déplacement sur grille |
| `Définir la Gravité` | Appliquer une force constante (vers le bas ou toute direction) à chaque image |
| `Définir le Frottement` | Appliquer une décroissance de vitesse à chaque image |
| `Inverser Horizontal` / `Inverser Vertical` | Inverser la direction X ou Y |
| `Rebondir` | Rebondir sur les objets solides |
| `Envelopper Autour de la Salle` | Réapparaître du côté opposé |
| `Se Déplacer Jusqu'au Contact` | Se déplacer jusqu'à toucher quelque chose |

Il n'existe pas de bloc « Sauter à la Position de Départ » ou « Sauter à
une Position Aléatoire » — ces deux actions n'existent que dans le panneau
structuré, pas dans Blockly.

---

## Blocs de dessin

| Bloc | Description |
|------|-------------|
| `Dessiner Texte [Bonjour] à x:[10] y:[10]` | Afficher du texte |
| `Dessiner Rectangle de x1,y1 à x2,y2` | Dessiner un rectangle rempli |
| `Dessiner Cercle à x,y rayon [r]` | Dessiner un cercle rempli |
| `Définir Sprite [spr]` | Changer le sprite de l'instance |
| `Définir Transparence [0-1]` | Définir l'alpha |

Il n'existe pas de bloc « Dessiner Sprite à une position » ou « Définir la
Couleur de Dessin » dans Blockly (les deux n'existent que dans le panneau
structuré). Dessiner Score/Dessiner Vies/Dessiner Barre de Santé sont listés
sous Score/Vies/Santé ci-dessous, pas ici.

---

## Blocs Score/Vies/Santé

| Bloc | Description |
|------|-------------|
| `Définir Score [100]` | Définir le score exact |
| `Ajouter au Score [10]` | Ajouter/soustraire au score |
| `Définir Vies [3]` | Définir les vies exactes |
| `Ajouter aux Vies [-1]` | Ajouter/soustraire aux vies |
| `Définir Santé [100]` | Définir la santé exacte |
| `Ajouter à la Santé [-25]` | Ajouter/soustraire à la santé |
| `Dessiner Score` | Afficher le texte du score |
| `Dessiner Vies` | Afficher les vies sous forme d'icônes répétées |
| `Dessiner Barre de Santé` | Afficher la santé sous forme de barre à deux couleurs |

---

## Blocs d'instance

| Bloc | Description |
|------|-------------|
| `Créer Instance [obj] à x:[100] y:[200]` | Faire apparaître une nouvelle instance |
| `Détruire Instance` | Se supprimer |
| `Détruire Autre` | Supprimer l'instance en collision (dans un événement de collision) |
| `Changer d'Instance [obj]` | Se transformer en un autre type d'objet |
| `Si Poussée Possible [obj] [direction]` | Vérification de poussée façon Sokoban |

Il n'existe pas de bloc « détruire tous d'un type » ou « créer à cette
position ».

---

## Blocs de salle

| Bloc | Description |
|------|-------------|
| `Salle Suivante` | Avancer à la salle suivante |
| `Salle Précédente` | Retourner d'une salle |
| `Redémarrer la Salle` | Réinitialiser la salle actuelle |
| `Aller à la Salle [nom_salle]` | Aller à une salle spécifique |
| `Si Salle Suivante Existe` / `Si Salle Précédente Existe` | Protéger la navigation multi-salles |

---

## Blocs de son

| Bloc | Description |
|------|-------------|
| `Jouer Son [snd]` | Jouer un effet sonore |
| `Jouer Musique [musique]` | Jouer une musique de fond (en boucle) |
| `Arrêter la Musique` | Arrêter la musique |

Il n'existe pas de bloc « Arrêter un Son » (par son) ou « Arrêter Tous les
Sons » dans Blockly (seulement Arrêter la Musique, qui arrête
spécifiquement la musique).

---

## Blocs de contrôle

| Bloc | Description |
|------|-------------|
| `Si le nombre de [obj] [==] [0] alors...` | Comparer le nombre d'instances d'un objet ; exécuter le(s) bloc(s) suivant(s) si vrai |
| `Si variable [var] [==] [valeur] alors...` | Comparer une variable personnalisée ; exécuter le(s) bloc(s) suivant(s) si vrai |
| `Définir Variable [nom] à [valeur]` | Assigner une variable d'instance ou globale |
| `Vérifier Vide à x,y` | Vrai quand une position n'a aucune collision (déplacement sur grille) |
| `Quitter l'Événement` | Arrêter le reste des actions de cet événement |
| `Sinon` | Exécute son propre bloc suivant quand le test précédent était faux |
| `Début de Bloc` / `Fin de Bloc` | Regrouper plusieurs actions sous un test/Sinon |

---

## Blocs de sortie et de jeu

| Bloc | Description |
|------|-------------|
| `Afficher un Message [texte]` | Afficher un message popup |
| `Exécuter du Code` | Exécuter du vrai Python (voir [Événements et Actions](Evenements_Actions_fr)) |
| `Terminer le Jeu` | Fermer le jeu |
| `Redémarrer le Jeu` | Redémarrer depuis la première salle |
| `Afficher les Meilleurs Scores` / `Effacer les Meilleurs Scores` | Afficher ou réinitialiser la table des meilleurs scores |

---

## Blocs de valeur

Blocs valeur — branchez-les dans un champ numérique d'un autre bloc :

| Bloc | Description |
|------|-------------|
| `Position X` | La coordonnée X de cette instance |
| `Position Y` | La coordonnée Y de cette instance |
| `Vitesse Horizontale` | La vélocité X de cette instance |
| `Vitesse Verticale` | La vélocité Y de cette instance |
| `Score` | Le score actuel |
| `Vies` | Les vies actuelles |
| `Santé` | La santé actuelle |
| `Souris X` / `Souris Y` | La position actuelle de la souris |

---

## Exemple : Mouvement du joueur

```
┌──────────────────────────┐
│ Quand touche [maintenue : gauche]│
├──────────────────────────┤
│ Définir Vitesse Horizontale [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ Quand touche [maintenue : droite]│
├──────────────────────────┤
│ Définir Vitesse Horizontale [4]│
└──────────────────────────┘

┌──────────────────────────┐
│ Quand touche [aucune touche]│
├──────────────────────────┤
│ Définir Vitesse Horizontale [0]│
└──────────────────────────┘
```

---

## Exemple : Collecter des pièces

```
┌─────────────────────────────┐
│ Quand collision avec obj_piece│
├─────────────────────────────┤
│ Ajouter au Score [10]        │
├─────────────────────────────┤
│ Jouer Son [snd_piece]        │
├─────────────────────────────┤
│ Détruire Autre                │
└─────────────────────────────┘
```

---

## Conseils

1. **Commencez par les événements** - Toujours commencer avec un bloc événement (bloc chapeau)
2. **Connectez verticalement** - Les blocs empilables se connectent de haut en bas
3. **Utilisez les couleurs** - Les couleurs des blocs indiquent leur catégorie
4. **Clic droit** - Accédez aux options de duplication, suppression et aide
5. **Zoom** - Utilisez la molette ou les contrôles de zoom pour les grands programmes
6. **Passer au panneau structuré** - Tout ce que Blockly peut faire
   correspond à une action de l'onglet Événements du panneau structuré, et
   l'inverse n'est pas toujours vrai (par ex. Sauter à la Position de
   Départ/Aléatoire et Arrêter un Son par son n'ont pas de bloc Blockly) —
   si vous en avez besoin, utilisez le panneau structuré pour cet événement
   plutôt que Blockly.

---

## Prochaines étapes

- [[Evenements_Actions_fr]] - Voir l'équivalent en liste d'actions
- [[Premier_Jeu_fr]] - Construire un jeu complet
- [[Editeur_Objets_fr]] - Où Blockly s'intègre
- [[Preset-Guide_fr]] - Quels blocs sont disponibles dans votre projet
