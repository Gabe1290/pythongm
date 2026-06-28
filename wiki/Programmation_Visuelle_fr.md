# Programmation visuelle

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

> [Retour a l'accueil](Home_fr)

PyGameMaker inclut Google Blockly pour la programmation visuelle par glisser-deposer. Construisez la logique du jeu en connectant des blocs au lieu d'ecrire du code.

---

## Acceder a Blockly

1. Ouvrez un objet dans l'editeur d'objets
2. Cliquez sur l'onglet **Blockly** (a cote de l'onglet Evenements)
3. L'espace de travail Blockly apparait avec une boite a outils a gauche

---

## L'espace de travail Blockly

### Boite a outils
Le panneau gauche contient les categories de blocs:
- **Evenements** - Blocs declencheurs d'evenements
- **Mouvement** - Blocs de mouvement et de position
- **Timing** - Alarmes et delais
- **Dessin** - Blocs de rendu visuel
- **Score/Vies/Sante** - Blocs d'etat du jeu
- **Instance** - Creation/destruction d'objets
- **Salle** - Navigation entre salles
- **Valeurs** - Variables et expressions
- **Son** - Lecture audio
- **Logique** - Si/sinon et boucles
- **Math** - Operations mathematiques
- **Texte** - Manipulation de chaines

### Espace de travail
La zone centrale ou vous construisez votre programme en:
- Glissant des blocs depuis la boite a outils
- Connectant les blocs ensemble
- Configurant les parametres des blocs

### Corbeille
Faites glisser les blocs non desires ici pour les supprimer, ou appuyez sur la touche Supprimer.

---

## Types de blocs

### Blocs chapeau (Evenements)
Les blocs chapeau ont un sommet arrondi et demarrent une sequence. Ils representent des evenements:

```
+---------------------+
| Quand Create        |
+---------------------+
```

### Blocs empilables (Actions)
Les blocs empilables ont des encoches qui se connectent a d'autres blocs:

```
|---------------------|
| Definir vitesse a 5 |
|---------------------|
```

### Blocs valeur (Valeurs)
Les blocs valeur sont arrondis et retournent des valeurs:

```
( position x )    ( score )    ( 100 )
```

### Blocs booleens (Conditions)
Les blocs booleens sont hexagonaux et retournent vrai/faux:

```
< touche obj_mur >    < touche pressee: espace >
```

### Blocs C (Conteneurs)
Les blocs C enveloppent d'autres blocs:

```
+---------------------+
| si < condition >    |
|  |-----------------|+
|  | faire action    ||
|  |-----------------|+
+---------------------+
```

---

## Blocs d'evenements

### Evenement Create
```
+---------------------+
| Quand Create        |
|---------------------|
| [actions ici]       |
+---------------------+
```

### Evenement Step
```
+---------------------+
| Quand Step          |
|---------------------|
| [chaque frame]      |
+---------------------+
```

### Evenements clavier
```
+-------------------------+
| Quand touche [gauche] v |
|-------------------------|
| [actions ici]           |
+-------------------------+
```

### Evenements collision
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
| `definir vitesse a [5]` | Definir la vitesse de deplacement |
| `definir direction a [90]` | Definir la direction de deplacement |
| `definir hspeed a [4]` | Definir la velocite horizontale |
| `definir vspeed a [-5]` | Definir la velocite verticale |
| `aller a x: [100] y: [200]` | Sauter a une position |
| `aller vers x: [100] y: [200] a vitesse [3]` | Se deplacer vers un point |
| `sauter a la position de depart` | Retourner au point de creation |
| `sauter a une position aleatoire` | Se deplacer aleatoirement |
| `rebondir sur les objets solides` | Inverser lors d'une collision |

---

## Blocs de dessin

| Bloc | Description |
|------|-------------|
| `dessiner sprite [spr] a x: [0] y: [0]` | Dessiner un sprite |
| `dessiner texte [Bonjour] a x: [10] y: [10]` | Afficher du texte |
| `dessiner score a x: [10] y: [10]` | Montrer le score |
| `dessiner rectangle de [x1,y1] a [x2,y2]` | Dessiner un rectangle |
| `definir couleur de dessin a [couleur]` | Changer la couleur de dessin |

---

## Blocs Score/Vies/Sante

| Bloc | Description |
|------|-------------|
| `definir score a [100]` | Definir le score exact |
| `modifier score de [10]` | Ajouter/soustraire au score |
| `definir vies a [3]` | Definir les vies exactes |
| `modifier vies de [-1]` | Ajouter/soustraire aux vies |
| `definir sante a [100]` | Definir la sante exacte |
| `modifier sante de [-25]` | Ajouter/soustraire a la sante |

---

## Blocs d'instance

| Bloc | Description |
|------|-------------|
| `creer [obj] a x: [100] y: [200]` | Faire apparaitre une nouvelle instance |
| `creer [obj] a cette position` | Faire apparaitre a sa propre position |
| `detruire cette instance` | Se supprimer |
| `detruire tous les [obj]` | Supprimer tous d'un type |

---

## Blocs de salle

| Bloc | Description |
|------|-------------|
| `aller a la salle suivante` | Avancer a la salle suivante |
| `aller a la salle precedente` | Retourner d'une salle |
| `redemarrer la salle actuelle` | Reinitialiser la salle |
| `aller a la salle [nom_salle]` | Aller a une salle specifique |

---

## Blocs de son

| Bloc | Description |
|------|-------------|
| `jouer son [snd]` | Jouer le son une fois |
| `jouer son [snd] en boucle` | Repeter le son |
| `arreter son [snd]` | Arreter un son specifique |
| `arreter tous les sons` | Tout mettre en silence |

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

### Repeter
```
+-------------------------+
| repeter [10] fois       |
|  |---------------------|+
|  | [faire ceci]        ||
|  |---------------------|+
+-------------------------+
```

### Comparaison
- `< [x] = [10] >`
- `< [score] > [100] >`
- `< [vies] < [1] >`

### Logique booleenne
- `< [condition1] et [condition2] >`
- `< [condition1] ou [condition2] >`
- `< non [condition] >`

---

## Blocs de valeur

### Variables
- `( x )` - Position X
- `( y )` - Position Y
- `( speed )` - Vitesse de deplacement
- `( direction )` - Direction du mouvement
- `( score )` - Score actuel
- `( lives )` - Vies actuelles
- `( health )` - Sante actuelle

### Math
- `( [5] + [3] )` - Addition
- `( [10] - [2] )` - Soustraction
- `( [4] x [3] )` - Multiplication
- `( [20] / [4] )` - Division
- `( aleatoire 1 a [100] )` - Nombre aleatoire

---

## Exemple: Mouvement du joueur

```
+----------------------------+
| Quand touche [fleche_gauche]|
|----------------------------|
| definir hspeed a [-4]      |
+----------------------------+

+----------------------------+
| Quand touche [fleche_droite]|
|----------------------------|
| definir hspeed a [4]       |
+----------------------------+

+----------------------------+
| Quand touche [aucune touche]|
|----------------------------|
| definir hspeed a [0]       |
+----------------------------+
```

---

## Exemple: Collecter des pieces

```
+-------------------------------+
| Quand collision avec obj_piece|
|-------------------------------|
| modifier score de [10]        |
|-------------------------------|
| jouer son [snd_piece]         |
|-------------------------------|
| detruire autre instance       |
+-------------------------------+
```

---

## Conseils

1. **Commencez par les evenements** - Toujours commencer avec un bloc evenement (bloc chapeau)
2. **Connectez verticalement** - Les blocs empilables se connectent de haut en bas
3. **Utilisez les couleurs** - Les couleurs des blocs indiquent leur categorie
4. **Clic droit** - Accedez aux options de duplication, suppression et aide
5. **Zoom** - Utilisez la molette ou les controles de zoom pour les grands programmes

---

## Prochaines etapes

- [[Evenements-Actions_fr]] - Voir l'equivalent en liste d'actions
- [[Premier-Jeu_fr]] - Construire un jeu complet
- [[Editeur-Objets_fr]] - Ou Blockly s'integre
