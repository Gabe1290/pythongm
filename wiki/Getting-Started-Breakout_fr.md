# Initiation à la Création de Jeux Vidéo avec PyGameMaker

*[Home_fr](Home_fr) | [Préréglage Débutant](Beginner-Preset_fr) | [English](Getting-Started-Breakout)*

**Par l'équipe PyGameMaker**

---

Nous allons voir dans ce tutoriel les bases de la création de jeux avec PyGameMaker. Étant un logiciel relativement complet et pourvu d'un très grand nombre de fonctions, nous allons nous attarder uniquement sur celles qui nous serviront lors de ce tutoriel.

Nous allons pour cela créer un jeu simple, de type Casse-brique, qui ressemblera à ceci :

![Concept du Casse-Briques](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Ce tutoriel est pour vous, même si vous n'avez pas la moindre connaissance en programmation, étant donné que PyGameMaker permet de créer des jeux aux plus débutants facilement, quelque soit leur niveau.

Bien, maintenant, commençons la conception de notre jeu !

---

## Étape 1 : Premiers Pas

Commencez tout d'abord par ouvrir PyGameMaker. Vous devriez voir apparaître l'interface principale avec le panneau **Assets** sur la gauche, listant les différentes catégories de ressources : Sprites, Sounds, Backgrounds, Fonts, Objects et Rooms.

Avant tout, dans un jeu vidéo, la première chose que le joueur remarque, c'est ce qu'il voit à l'écran. C'est d'ailleurs la base d'un jeu : un jeu sans graphismes n'existe pas, ou alors c'est un cas très particulier. Nous allons donc commencer par insérer des images dans notre jeu, qui seront la représentation graphique des objets que le joueur verra à l'écran. Dans le jargon, on appelle ces images des **Sprites**.

---

## Étape 2 : Création des Sprites

### 2.1 Créer le Sprite de la Batte

1. Faites un clic droit sur le répertoire **Sprites**, se trouvant tout en haut de la colonne de gauche
2. Cliquez sur **Create Sprite**
3. Une fenêtre, appelée **Sprite Properties**, va s'ouvrir. C'est ici que vous définirez toutes les caractéristiques de votre sprite
4. Utilisez l'éditeur intégré pour dessiner un rectangle horizontal (environ 64x16 pixels) dans une couleur de votre choix
5. **Important :** Cliquez sur **Center** pour régler l'origine au centre de votre sprite
   > L'origine d'une sprite est son centre, son point X:0 et Y:0. Ce sont ses coordonnées de base.
6. Changez le nom de votre sprite, à partir de la petite case en haut, et inscrivez-y `spr_batte`
   > Ça n'a aucune incidence technique, c'est juste pour mieux se repérer dans vos fichiers, une fois que vous en aurez un nombre plus important. D'ailleurs vous avez le droit de choisir n'importe quel nom pour ces sprites, ce que je donne est juste un petit exemple.
7. Cliquez sur **OK**

Vous venez de créer votre première sprite ! C'est votre batte, l'objet que le joueur contrôlera et qui servira à rattraper la balle.

### 2.2 Créer le Sprite de la Balle

Continuons dans cette voie. Répétez la même opération :

1. Clic droit sur **Sprites** → **Create Sprite**
2. Dessinez un petit cercle (environ 16x16 pixels)
3. Cliquez sur **Center** pour définir l'origine
4. Nommez-la `spr_balle`
5. Cliquez sur **OK**

### 2.3 Créer les Sprites des Blocs

Nous avons besoin de trois types de blocs. Créez-les un par un :

**Premier Bloc (Destructible) :**
1. Créez une nouvelle sprite
2. Dessinez un rectangle (environ 48x24 pixels) - utilisez une couleur vive comme le rouge
3. Cliquez sur **Center**, nommez-la `spr_bloc_1`
4. Cliquez sur **OK**

**Deuxième Bloc (Destructible) :**
1. Créez une nouvelle sprite
2. Dessinez un rectangle (même taille) - utilisez une couleur différente comme le bleu
3. Cliquez sur **Center**, nommez-la `spr_bloc_2`
4. Cliquez sur **OK**

**Troisième Bloc (Mur Indestructible) :**
1. Créez une nouvelle sprite
2. Dessinez un rectangle (même taille) - utilisez une couleur plus sombre comme le gris
3. Cliquez sur **Center**, nommez-la `spr_bloc_3`
4. Cliquez sur **OK**

Nous avons donc toutes les sprites de notre jeu réunies ici :
- `spr_batte` - La batte du joueur
- `spr_balle` - La balle rebondissante
- `spr_bloc_1` - Premier bloc destructible
- `spr_bloc_2` - Deuxième bloc destructible
- `spr_bloc_3` - Bloc mur indestructible

> **Note :** Il y a, en général, deux seules et uniques sources de rendus graphiques dans un jeu : les **Sprites** et les **Backgrounds**. C'est tout ce qui constitue ce que l'on voit à l'écran. Un Background est, comme son nom l'indique, un arrière-plan.

---

## Étape 3 : Comprendre les Objets et les Événements

Que disions-nous au début ? La première chose que le joueur remarque, c'est ce qu'il voit à l'écran. Ça, nous nous en sommes occupé avec nos sprites. Mais un jeu constitué uniquement d'images, ce n'est pas un jeu, c'est une fresque ! On va donc passer au stade suivant : les **Objects**.

Un Object est une entité dans votre jeu qui peut avoir des comportements, répondre à des événements et interagir avec d'autres objets. La sprite n'est que la représentation visuelle ; l'objet est ce qui lui donne vie.

### Comment Fonctionne la Logique de Jeu

Tout, dans la programmation d'actions dans un jeu, fonctionne avec ce schéma : **S'il se passe ça, alors j'exécute ceci.**

- Si le joueur appuie sur une touche, alors je fais ça
- Si cette variable est égale à ce taux, alors je fais ceci
- Si deux objets entrent en collision, alors quelque chose se passe

C'est ce qu'on appelle dans PyGameMaker des **Événements** et des **Actions** :
- **Événements** = Ce qui peut se produire (appui clavier, collision, timer, etc.)
- **Actions** = Ce que vous voulez faire quand les événements se produisent (bouger, détruire, changer le score, etc.)

Si tel événement se produit, alors telle action s'exécute. Ça marche comme ça.

---

## Étape 4 : Création de l'Objet Batte

Nous allons maintenant créer l'objet que contrôlera le joueur : la batte.

### 4.1 Créer l'Objet

1. Clic droit sur **Objects** → **Create Object**
2. Nommez-le `obj_batte`
3. Dans le menu déroulant **Sprite**, sélectionnez `spr_batte` - maintenant notre objet a une apparence visuelle !
4. Cochez la case **Solid** (nous en aurons besoin pour les collisions)

### 4.2 Programmer le Mouvement

Ce que l'on veut dans un casse-brique, c'est éviter que la gentille baballe ne nous fausse compagnie trop rapidement en filant à l'anglaise dans le bas du niveau. On doit donc pouvoir bouger pour la rattraper. Nous allons contrôler la batte avec le clavier.

**Se Déplacer à Droite :**
1. Cliquez sur **Add Event** → **Keyboard** → **Flèche Droite**
2. Depuis le panneau d'actions à droite, ajoutez l'action **Set Horizontal Speed**
3. Mettez la **valeur** à `5`
4. Cliquez sur **OK**

Cela signifie : "Quand la touche Flèche Droite est enfoncée, définir la vitesse horizontale à 5 (vers la droite)."

**Se Déplacer à Gauche :**
1. Cliquez sur **Add Event** → **Keyboard** → **Flèche Gauche**
2. Ajoutez l'action **Set Horizontal Speed**
3. Mettez la **valeur** à `-5`
4. Cliquez sur **OK**

**S'Arrêter Quand les Touches sont Relâchées :**

Si nous testons maintenant, la batte continuerait de bouger même après avoir relâché la touche ! Corrigeons cela :

1. Cliquez sur **Add Event** → **Keyboard Release** → **Flèche Droite**
2. Ajoutez l'action **Set Horizontal Speed** avec la valeur `0`
3. Cliquez sur **OK**

4. Cliquez sur **Add Event** → **Keyboard Release** → **Flèche Gauche**
5. Ajoutez l'action **Set Horizontal Speed** avec la valeur `0`
6. Cliquez sur **OK**

Maintenant la batte bouge quand les touches sont enfoncées et s'arrête quand elles sont relâchées. Nous n'avons plus rien à faire pour cet objet pour le moment !

---

## Étape 5 : Création de l'Objet Bloc Mur

Créons un bloc mur indestructible - celui-ci formera les limites de notre zone de jeu.

1. Créez un nouvel objet nommé `obj_bloc_3`
2. Assignez-lui la sprite `spr_bloc_3`
3. Cochez la case **Solid**

La balle devra rebondir sur ce bloc. Comme c'est juste un mur, nous n'avons besoin d'aucun événement - il doit juste être solid. Cliquez sur **OK** pour sauvegarder.

---

## Étape 6 : Création de l'Objet Balle

Nous allons maintenant créer la balle, élément important de notre petit jeu.

### 6.1 Créer l'Objet

1. Créez un nouvel objet nommé `obj_balle`
2. Assignez-lui la sprite `spr_balle`
3. Cochez la case **Solid**

### 6.2 Mouvement Initial

Nous voulons que la balle bouge par elle-même dès le début. Donnons-lui une vitesse et une direction de départ.

1. Cliquez sur **Add Event** → **Create**
   > L'événement Create s'exécute lorsque l'objet est créé dans le jeu, donc au moment où il entre en scène.
2. Ajoutez l'action **Set Horizontal Speed** avec la valeur `4`
3. Ajoutez l'action **Set Vertical Speed** avec la valeur `-4`
4. Cliquez sur **OK**

Cela donne à la balle un mouvement diagonal (droite et haut) au début du jeu.

### 6.3 Rebondir sur la Batte

Il faut maintenant faire rebondir notre balle lorsqu'elle entre en collision avec notre batte.

1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_batte`
   > Cet événement se déclenche quand la balle entre en collision avec la batte.
2. Ajoutez l'action **Reverse Vertical**
   > Cela inverse la direction verticale, faisant rebondir la balle.
3. Cliquez sur **OK**

### 6.4 Rebondir sur les Murs

Même opération pour les blocs murs :

1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_bloc_3`
2. Ajoutez l'action **Reverse Vertical**
3. Ajoutez l'action **Reverse Horizontal**
   > On ajoute les deux car la balle peut toucher le mur sous différents angles.
4. Cliquez sur **OK**

---

## Étape 7 : Tester Notre Progression - Création d'une Room

Après les Sprites et les Objects, voici maintenant les **Rooms**. Une room est l'endroit où se déroule le jeu : c'est une map, un niveau. C'est ici que vous placez tous les éléments de votre jeu, c'est ici que vous organisez ce qui apparaîtra à l'écran.

### 7.1 Créer la Room

1. Clic droit sur **Rooms** → **Create Room**
2. Nommez-la `room_jeu`

### 7.2 Placer Vos Objets

Il vous suffit maintenant de placer vos objets, à l'aide de la souris :
- **Clic gauche** pour placer un objet
- **Clic droit** pour effacer un objet

Sélectionnez l'objet à placer depuis le menu déroulant dans l'éditeur de room.

**Construisez votre niveau :**
1. Placez des instances de `obj_bloc_3` autour des bords (haut, gauche, droite) - laissez le bas ouvert !
2. Placez `obj_batte` en bas au centre
3. Placez `obj_balle` quelque part au milieu

### 7.3 Testez le Jeu !

Une fois votre niveau terminé, il vous suffit de lancer le jeu avec le bouton **Play** (flèche verte) dans la barre des tâches. Ceci permet de tester votre jeu à n'importe quel moment.

Vous pouvez déjà vous amuser en faisant rebondir la balle sur les murs et la batte !

C'est assez minime, mais déjà un bon début ! Vous avez votre base de jeu.

---

## Étape 8 : Ajouter des Blocs à Casser

Nous allons maintenant rajouter quelques blocs à casser, pour rendre notre jeu un peu plus fun.

### 8.1 Premier Bloc Destructible

1. Créez un nouvel objet nommé `obj_bloc_1`
2. Assignez-lui la sprite `spr_bloc_1`
3. Cochez **Solid**

Nous allons simplement rajouter le fait qu'il se détruise au contact de la balle :

1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_balle`
2. Ajoutez l'action **Destroy Instance** avec la cible **self**
   > Cette action sert à effacer un objet pendant le jeu, en l'occurrence ici le bloc lui-même.
3. Cliquez sur **OK**

Et aussi rapidement que ça, vous avez votre nouveau bloc destructible !

### 8.2 Deuxième Bloc Destructible (Utilisation du Parent)

Nous allons maintenant créer un deuxième bloc destructible, mais sans avoir à le reprogrammer. Il suffira d'en faire une sorte de « clone » en utilisant la fonction **Parent**.

1. Créez un nouvel objet nommé `obj_bloc_2`
2. Assignez-lui la sprite `spr_bloc_2`
3. Cochez **Solid**
4. Dans le menu **Parent**, sélectionnez `obj_bloc_1`

Qu'est-ce que cela signifie ? Simplement que ce que l'on a programmé dans `obj_bloc_1` va se retrouver dans `obj_bloc_2`, sans qu'on ait à le reproduire soi-même. La relation parent-enfant permet aux objets de partager des comportements !

Cliquez sur **OK** pour sauvegarder.

### 8.3 Faire Rebondir la Balle sur les Nouveaux Blocs

Rouvrez `obj_balle` en double-cliquant dessus, et ajoutez des événements de collision pour nos nouveaux blocs :

1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_bloc_1`
2. Ajoutez l'action **Reverse Vertical**
3. Cliquez sur **OK**

4. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_bloc_2`
5. Ajoutez l'action **Reverse Vertical**
6. Cliquez sur **OK**

---

## Étape 9 : Game Over - Redémarrer la Room

Nous allons aussi faire en sorte que le niveau redémarre si la balle sort de l'écran, donc si le joueur n'arrive pas à la rattraper.

Dans `obj_balle` :

1. Cliquez sur **Add Event** → **Other** → **Outside Room**
2. Ajoutez l'action **Restart Room**
   > Cette action sert à redémarrer la room en cours de jeu.
3. Cliquez sur **OK**

---

## Étape 10 : Design Final du Niveau

Il suffit maintenant de tout placer dans la room pour créer votre niveau de casse-brique final :

1. Ouvrez `room_jeu`
2. Disposez des murs `obj_bloc_3` autour du haut et des côtés
3. Placez des rangées de `obj_bloc_1` et `obj_bloc_2` en motifs en haut
4. Gardez `obj_batte` en bas au centre
5. Placez `obj_balle` au-dessus de la batte

**Exemple de disposition :**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]        (balle)         [3]
[3]                        [3]
[3]        [batte]         [3]
```

---

## Félicitations !

Votre casse-brique est terminé ! Vous pouvez maintenant profiter de votre travail en vous amusant un peu avec le jeu que vous venez de créer !

Vous pouvez aussi le fignoler, comme par exemple rajouter :
- **Des bruitages** pour les rebonds et la destruction des briques
- **Un système de score** en utilisant l'action Add Score
- **Des types de blocs supplémentaires** avec différents comportements
- **Plusieurs niveaux** avec différentes dispositions

---

## Résumé de Ce Que Vous Avez Appris

| Concept | Description |
|---------|-------------|
| **Sprites** | Images visuelles qui représentent les objets dans votre jeu |
| **Objects** | Entités de jeu avec des comportements, combinant sprites avec événements et actions |
| **Événements** | Déclencheurs qui exécutent des actions (Create, Keyboard, Collision, etc.) |
| **Actions** | Opérations à effectuer (Move, Destroy, Bounce, etc.) |
| **Solid** | Propriété qui active la détection de collision |
| **Parent** | Permet aux objets d'hériter des comportements d'autres objets |
| **Rooms** | Niveaux de jeu où vous placez les instances d'objets |

---

## Résumé des Objets

| Objet | Sprite | Solid | Événements |
|-------|--------|-------|------------|
| `obj_batte` | `spr_batte` | Oui | Keyboard (Gauche/Droite), Keyboard Release |
| `obj_balle` | `spr_balle` | Oui | Create, Collision (batte, blocs), Outside Room |
| `obj_bloc_1` | `spr_bloc_1` | Oui | Collision (balle) - Détruire self |
| `obj_bloc_2` | `spr_bloc_2` | Oui | Hérite de `obj_bloc_1` |
| `obj_bloc_3` | `spr_bloc_3` | Oui | Aucun (juste un mur) |

---

## Voir Aussi

- [Préréglage Débutant](Beginner-Preset_fr) - Événements et actions disponibles pour les débutants
- [Référence des Événements](Event-Reference_fr) - Liste complète de tous les événements
- [Référence des Actions](Full-Action-Reference_fr) - Liste complète de toutes les actions
- [Tutoriel : Casse-Briques](Tutorial-Breakout_fr) - Version plus courte de ce tutoriel

---

Vous êtes maintenant initié aux bases de la création de jeux vidéo avec PyGameMaker. À vous de jouer pour créer vos propres jeux à présent !
