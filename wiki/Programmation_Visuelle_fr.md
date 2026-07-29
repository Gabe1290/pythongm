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

---

## L'espace de travail Blockly

### Boîte à outils
Le panneau gauche contient les catégories de blocs :
- **Événements** - Blocs déclencheurs d'événements
- **Mouvement** - Blocs de mouvement et de position
- **Timing** - Alarmes et délais
- **Dessin** - Blocs de rendu visuel
- **Score/Vies/Santé** - Blocs d'état du jeu
- **Instance** - Création/destruction d'objets
- **Salle** - Navigation entre salles
- **Valeurs** - Variables et expressions
- **Son** - Lecture audio
- **Logique** - Si/sinon et boucles
- **Math** - Opérations mathématiques
- **Texte** - Manipulation de chaînes

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
+---------------------+
| Quand Create        |
+---------------------+
```

### Blocs empilables (Actions)
Les blocs empilables ont des encoches qui se connectent à d'autres blocs :

```
|---------------------|
| Définir vitesse à 5 |
|---------------------|
```

### Blocs valeur (Valeurs)
Les blocs valeur sont arrondis et retournent des valeurs :

```
( position x )    ( score )    ( 100 )
```

### Blocs booléens (Conditions)
Les blocs booléens sont hexagonaux et retournent vrai/faux :

```
< touche obj_mur >    < touche pressée : espace >
```

### Blocs C (Conteneurs)
Les blocs C enveloppent d'autres blocs :

```
+---------------------+
| si < condition >    |
|  |-----------------|+
|  | faire action    ||
|  |-----------------|+
+---------------------+
```

---

## Blocs d'événements

### Événement Create
```
+---------------------+
| Quand Create        |
|---------------------|
| [actions ici]       |
+---------------------+
```

### Événement Step
```
+---------------------+
| Quand Step          |
|---------------------|
| [chaque frame]      |
+---------------------+
```

### Événements clavier
```
+-------------------------+
| Quand touche [gauche] v |
|-------------------------|
| [actions ici]           |
+-------------------------+
```

### Événements collision
```
+----------------------------+
| Quand collision avec [obj] v|
|----------------------------|
| [actions ici]              |
+----------------------------+
```

---

## Blocs de mouvement

| Bloc | Description |
|------|-------------|
| `définir vitesse à [5]` | Définir la vitesse de déplacement |
| `définir direction à [90]` | Définir la direction de déplacement |
| `définir hspeed à [4]` | Définir la vélocité horizontale |
| `définir vspeed à [-5]` | Définir la vélocité verticale |
| `aller à x : [100] y : [200]` | Sauter à une position |
| `aller vers x : [100] y : [200] à vitesse [3]` | Se déplacer vers un point |
| `sauter à la position de départ` | Retourner au point de création |
| `sauter à une position aléatoire` | Se déplacer aléatoirement |
| `rebondir sur les objets solides` | Inverser lors d'une collision |

---

## Blocs de dessin

| Bloc | Description |
|------|-------------|
| `dessiner sprite [spr] à x : [0] y : [0]` | Dessiner un sprite |
| `dessiner texte [Bonjour] à x : [10] y : [10]` | Afficher du texte |
| `dessiner score à x : [10] y : [10]` | Montrer le score |
| `dessiner rectangle de [x1,y1] à [x2,y2]` | Dessiner un rectangle |
| `définir couleur de dessin à [couleur]` | Changer la couleur de dessin |

---

## Blocs Score/Vies/Santé

| Bloc | Description |
|------|-------------|
| `définir score à [100]` | Définir le score exact |
| `modifier score de [10]` | Ajouter/soustraire au score |
| `définir vies à [3]` | Définir les vies exactes |
| `modifier vies de [-1]` | Ajouter/soustraire aux vies |
| `définir santé à [100]` | Définir la santé exacte |
| `modifier santé de [-25]` | Ajouter/soustraire à la santé |

---

## Blocs d'instance

| Bloc | Description |
|------|-------------|
| `créer [obj] à x : [100] y : [200]` | Faire apparaître une nouvelle instance |
| `créer [obj] à cette position` | Faire apparaître à sa propre position |
| `détruire cette instance` | Se supprimer |
| `détruire tous les [obj]` | Supprimer tous d'un type |

---

## Blocs de salle

| Bloc | Description |
|------|-------------|
| `aller à la salle suivante` | Avancer à la salle suivante |
| `aller à la salle précédente` | Retourner d'une salle |
| `redémarrer la salle actuelle` | Réinitialiser la salle |
| `aller à la salle [nom_salle]` | Aller à une salle spécifique |

---

## Blocs de son

| Bloc | Description |
|------|-------------|
| `jouer son [snd]` | Jouer le son une fois |
| `jouer son [snd] en boucle` | Répéter le son |
| `arrêter son [snd]` | Arrêter un son spécifique |
| `arrêter tous les sons` | Tout mettre en silence |

---

## Blocs de logique

### Si/Sinon
```
+-------------------------+
| si < condition >        |
|  |---------------------|+
|  | [alors faire ceci]  ||
|  |---------------------|+
| sinon                   |
|  |---------------------|+
|  | [sinon cela]        ||
|  |---------------------|+
+-------------------------+
```

### Répéter
```
+-------------------------+
| répéter [10] fois       |
|  |---------------------|+
|  | [faire ceci]        ||
|  |---------------------|+
+-------------------------+
```

### Comparaison
- `< [x] = [10] >`
- `< [score] > [100] >`
- `< [vies] < [1] >`

### Logique booléenne
- `< [condition1] et [condition2] >`
- `< [condition1] ou [condition2] >`
- `< non [condition] >`

---

## Blocs de valeur

### Variables
- `( x )` - Position X
- `( y )` - Position Y
- `( speed )` - Vitesse de déplacement
- `( direction )` - Direction du mouvement
- `( score )` - Score actuel
- `( lives )` - Vies actuelles
- `( health )` - Santé actuelle

### Math
- `( [5] + [3] )` - Addition
- `( [10] - [2] )` - Soustraction
- `( [4] x [3] )` - Multiplication
- `( [20] / [4] )` - Division
- `( aléatoire 1 à [100] )` - Nombre aléatoire

---

## Exemple : Mouvement du joueur

```
+----------------------------+
| Quand touche [fleche_gauche]|
|----------------------------|
| définir hspeed à [-4]      |
+----------------------------+

+----------------------------+
| Quand touche [fleche_droite]|
|----------------------------|
| définir hspeed à [4]       |
+----------------------------+

+----------------------------+
| Quand touche [aucune touche]|
|----------------------------|
| définir hspeed à [0]       |
+----------------------------+
```

---

## Exemple : Collecter des pièces

```
+-------------------------------+
| Quand collision avec obj_piece|
|-------------------------------|
| modifier score de [10]        |
|-------------------------------|
| jouer son [snd_piece]         |
|-------------------------------|
| détruire autre instance       |
+-------------------------------+
```

---

## Conseils

1. **Commencez par les événements** - Toujours commencer avec un bloc événement (bloc chapeau)
2. **Connectez verticalement** - Les blocs empilables se connectent de haut en bas
3. **Utilisez les couleurs** - Les couleurs des blocs indiquent leur catégorie
4. **Clic droit** - Accédez aux options de duplication, suppression et aide
5. **Zoom** - Utilisez la molette ou les contrôles de zoom pour les grands programmes

---

## Prochaines étapes

- [[Evenements_Actions_fr]] - Voir l'équivalent en liste d'actions
- [[Premier_Jeu_fr]] - Construire un jeu complet
- [[Editeur_Objets_fr]] - Où Blockly s'intègre
