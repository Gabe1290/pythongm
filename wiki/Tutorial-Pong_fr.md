# Tutoriel : Créer un jeu Pong classique

> **Sélectionnez votre langue / Select your language / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Introduction

Dans ce tutoriel, vous allez créer un jeu **Pong** classique - l'un des premiers jeux vidéo jamais créés ! Pong est un jeu à deux joueurs où chaque joueur contrôle une raquette et essaie de faire passer le ballon au-delà de la raquette de son adversaire pour marquer des points.

**Ce que vous apprendrez :**
- Créer des sprites pour les raquettes, le ballon et les murs
- Gérer l'entrée au clavier pour deux joueurs
- Faire rebondir les objets les uns contre les autres
- Suivre et afficher les scores des deux joueurs
- Utiliser des variables globales

**Difficulté :** Débutant
**Préréglage :** Préréglage Débutant

---

## Étape 1 : Planifiez votre jeu

Avant de commencer, comprenons ce dont nous avons besoin :

| Élément | Objectif |
|---------|----------|
| **Ballon** | Rebondit entre les joueurs |
| **Raquette gauche** | Le joueur 1 contrôle avec les touches W/S |
| **Raquette droite** | Le joueur 2 contrôle avec les flèches Haut/Bas |
| **Murs** | Limites supérieure et inférieure |
| **Zones de but** | Zones invisibles derrière chaque raquette pour détecter les points |
| **Affichage du score** | Montre les scores des deux joueurs |

---

## Étape 2 : Créez les sprites

### 2.1 Sprite du ballon

1. Dans l'**Arborescence des ressources**, cliquez avec le bouton droit sur **Sprites** et sélectionnez **Créer un sprite**
2. Nommez-le `spr_ball`
3. Cliquez sur **Éditer un sprite** pour ouvrir l'éditeur de sprite
4. Dessinez un petit cercle blanc (environ 16x16 pixels)
5. Cliquez sur **OK** pour enregistrer

### 2.2 Sprites des raquettes

Nous allons créer deux raquettes - une pour chaque joueur :

**Raquette gauche (Joueur 1) :**
1. Créez un nouveau sprite nommé `spr_paddle_left`
2. Dessinez un rectangle haut et mince courbé comme une parenthèse « ) » - couleur bleue recommandée
3. Taille : environ 16x64 pixels

**Raquette droite (Joueur 2) :**
1. Créez un nouveau sprite nommé `spr_paddle_right`
2. Dessinez un rectangle haut et mince courbé comme une parenthèse « ( » - couleur rouge recommandée
3. Taille : environ 16x64 pixels

### 2.3 Sprite du mur

1. Créez un nouveau sprite nommé `spr_wall`
2. Dessinez un rectangle solide (gris ou blanc)
3. Taille : 32x32 pixels (nous l'étirerons dans la salle)

### 2.4 Sprite de la zone de but (Invisible)

1. Créez un nouveau sprite nommé `spr_goal`
2. Faites-le 32x32 pixels
3. Laissez-le transparent ou faites-le d'une couleur unie (il sera invisible dans le jeu)

---

## Étape 3 : Créez l'objet mur

L'objet mur crée des limites en haut et en bas de la zone de jeu.

1. Cliquez avec le bouton droit sur **Objets** et sélectionnez **Créer un objet**
2. Nommez-le `obj_wall`
3. Définissez le sprite sur `spr_wall`
4. **Cochez la case "Solide"** - c'est important pour le rebondissement !
5. Aucun événement nécessaire - le mur reste juste là

---

## Étape 4 : Créez les objets raquette

### 4.1 Raquette gauche (Joueur 1)

1. Créez un nouvel objet nommé `obj_paddle_left`
2. Définissez le sprite sur `spr_paddle_left`
3. **Cochez la case "Solide"**

**Ajoutez des événements clavier pour le mouvement :**

**Événement : Appui sur la touche W**
1. Ajouter un événement → Clavier → Appui sur W
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `-8` (se déplace vers le haut)

**Événement : Relâcher la touche W**
1. Ajouter un événement → Clavier → Relâcher W
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `0` (arrête de se déplacer)

**Événement : Appui sur la touche S**
1. Ajouter un événement → Clavier → Appui sur S
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `8` (se déplace vers le bas)

**Événement : Relâcher la touche S**
1. Ajouter un événement → Clavier → Relâcher S
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `0` (arrête de se déplacer)

**Événement : Collision avec obj_wall**
1. Ajouter un événement → Collision → obj_wall
2. Ajouter une action : **Mouvement** → **Rebondir contre les objets**
3. Sélectionnez « Contre les objets solides »

### 4.2 Raquette droite (Joueur 2)

1. Créez un nouvel objet nommé `obj_paddle_right`
2. Définissez le sprite sur `spr_paddle_right`
3. **Cochez la case "Solide"**

**Ajoutez des événements clavier pour le mouvement :**

**Événement : Appui sur la flèche haut**
1. Ajouter un événement → Clavier → Appui sur Haut
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `-8`

**Événement : Relâcher la flèche haut**
1. Ajouter un événement → Clavier → Relâcher Haut
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `0`

**Événement : Appui sur la flèche bas**
1. Ajouter un événement → Clavier → Appui sur Bas
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `8`

**Événement : Relâcher la flèche bas**
1. Ajouter un événement → Clavier → Relâcher Bas
2. Ajouter une action : **Mouvement** → **Définir la vitesse verticale**
3. Définissez la vitesse verticale sur `0`

**Événement : Collision avec obj_wall**
1. Ajouter un événement → Collision → obj_wall
2. Ajouter une action : **Mouvement** → **Rebondir contre les objets**
3. Sélectionnez « Contre les objets solides »

---

## Étape 5 : Créez l'objet ballon

1. Créez un nouvel objet nommé `obj_ball`
2. Définissez le sprite sur `spr_ball`

**Événement : Créer**
1. Ajouter un événement → Créer
2. Ajouter une action : **Mouvement** → **Commencer à se déplacer dans une direction**
3. Choisissez une direction diagonale (pas tout à fait vers le haut ou vers le bas)
4. Définissez la vitesse sur `6`

**Événement : Collision avec obj_paddle_left**
1. Ajouter un événement → Collision → obj_paddle_left
2. Ajouter une action : **Mouvement** → **Rebondir contre les objets**
3. Sélectionnez « Contre les objets solides »

**Événement : Collision avec obj_paddle_right**
1. Ajouter un événement → Collision → obj_paddle_right
2. Ajouter une action : **Mouvement** → **Rebondir contre les objets**
3. Sélectionnez « Contre les objets solides »

**Événement : Collision avec obj_wall**
1. Ajouter un événement → Collision → obj_wall
2. Ajouter une action : **Mouvement** → **Rebondir contre les objets**
3. Sélectionnez « Contre les objets solides »

---

## Étape 6 : Créez les objets de zone de but

Les zones de but sont des zones invisibles derrière chaque raquette. Quand le ballon entre dans une zone de but, le joueur adverse marque.

### 6.1 Zone de but gauche

1. Créez un nouvel objet nommé `obj_goal_left`
2. Définissez le sprite sur `spr_goal`
3. **Décochez "Visible"** - la zone de but doit être invisible
4. **Cochez "Solide"**

### 6.2 Zone de but droite

1. Créez un nouvel objet nommé `obj_goal_right`
2. Définissez le sprite sur `spr_goal`
3. **Décochez "Visible"**
4. **Cochez "Solide"**

### 6.3 Ajoutez des événements de collision de zone de but au ballon

Retournez à `obj_ball` et ajoutez ces événements :

**Événement : Collision avec obj_goal_left**
1. Ajouter un événement → Collision → obj_goal_left
2. Ajouter une action : **Mouvement** → **Sauter à la position de départ** (réinitialise le ballon)
3. Ajouter une action : **Score** → **Définir le score**
   - Variable : `global.p2score`
   - Valeur : `1`
   - Cochez « Relatif » (ajoute 1 au score actuel)

**Événement : Collision avec obj_goal_right**
1. Ajouter un événement → Collision → obj_goal_right
2. Ajouter une action : **Mouvement** → **Sauter à la position de départ**
3. Ajouter une action : **Score** → **Définir le score**
   - Variable : `global.p1score`
   - Valeur : `1`
   - Cochez « Relatif »

---

## Étape 7 : Créez l'objet d'affichage du score

1. Créez un nouvel objet nommé `obj_score`
2. Aucun sprite nécessaire

**Événement : Créer**
1. Ajouter un événement → Créer
2. Ajouter une action : **Score** → **Définir le score**
   - Variable : `global.p1score`
   - Valeur : `0`
3. Ajouter une action : **Score** → **Définir le score**
   - Variable : `global.p2score`
   - Valeur : `0`

**Événement : Dessiner**
1. Ajouter un événement → Dessiner
2. Ajouter une action : **Dessiner** → **Dessiner du texte**
   - Texte : `Joueur 1 :`
   - X : `10`
   - Y : `10`
3. Ajouter une action : **Dessiner** → **Dessiner une variable**
   - Variable : `global.p1score`
   - X : `100`
   - Y : `10`
4. Ajouter une action : **Dessiner** → **Dessiner du texte**
   - Texte : `Joueur 2 :`
   - X : `10`
   - Y : `30`
5. Ajouter une action : **Dessiner** → **Dessiner une variable**
   - Variable : `global.p2score`
   - X : `100`
   - Y : `30`

---

## Étape 8 : Concevez la salle

1. Cliquez avec le bouton droit sur **Salles** et sélectionnez **Créer une salle**
2. Nommez-la `room_pong`
3. Définissez la taille de la salle (par exemple, 640x480)

**Placez les objets :**

1. **Murs** : Placez les instances de `obj_wall` le long des bords supérieur et inférieur de la salle
2. **Raquette gauche** : Placez `obj_paddle_left` près du bord gauche, centré verticalement
3. **Raquette droite** : Placez `obj_paddle_right` près du bord droit, centré verticalement
4. **Ballon** : Placez `obj_ball` au centre de la salle
5. **Zones de but** :
   - Placez les instances de `obj_goal_left` le long du bord gauche (derrière où se trouve la raquette)
   - Placez les instances de `obj_goal_right` le long du bord droit
6. **Affichage du score** : Placez `obj_score` n'importe où (il n'a pas de sprite, il dessine juste du texte)

**Exemple de disposition de la salle :**
```
[MUR MUR MUR MUR MUR MUR MUR MUR MUR MUR]
[BUT]  [RAQUETTE_G]            [BALLON]            [RAQUETTE_D]  [BUT]
[BUT]  [RAQUETTE_G]                              [RAQUETTE_D]  [BUT]
[BUT]                                                      [BUT]
[MUR MUR MUR MUR MUR MUR MUR MUR MUR MUR]
```

---

## Étape 9 : Testez votre jeu !

1. Cliquez sur **Lancer** ou appuyez sur **F5** pour tester votre jeu
2. Le joueur 1 utilise **W** (haut) et **S** (bas)
3. Le joueur 2 utilise les flèches **Haut** et **Bas**
4. Essayez de faire passer le ballon au-delà de la raquette de votre adversaire !

---

## Améliorations (Optionnel)

### Augmentation de la vitesse
Augmentez la vitesse du ballon à chaque fois qu'il frappe une raquette en ajoutant aux événements de collision :
- Après l'action de rebondissement, ajoutez **Mouvement** → **Définir la vitesse**
- Définissez la vitesse sur `vitesse + 0,5` avec « Relatif » coché

### Effets sonores
Ajoutez des sons quand :
- Le ballon frappe une raquette
- Le ballon frappe un mur
- Un joueur marque

### Condition de victoire
Ajoutez une vérification dans l'événement Dessiner :
- Si `global.p1score >= 10`, affichez « Le joueur 1 gagne ! »
- Si `global.p2score >= 10`, affichez « Le joueur 2 gagne ! »

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Le ballon traverse la raquette | Assurez-vous que les raquettes ont « Solide » coché |
| La raquette ne s'arrête pas aux murs | Ajoutez un événement de collision avec obj_wall |
| Le score ne se met pas à jour | Vérifiez que les noms de variables correspondent exactement (global.p1score, global.p2score) |
| Le ballon ne se déplace pas | Vérifiez que l'événement Créer a l'action de mouvement |

---

## Ce que vous avez appris

Félicitations ! Vous avez créé un jeu Pong complet à deux joueurs ! Vous avez appris :

- Comment gérer l'entrée au clavier pour deux joueurs différents
- Comment utiliser les événements de relâchement de touche pour arrêter le mouvement
- Comment faire rebondir les objets les uns contre les autres
- Comment utiliser des variables globales pour suivre les scores
- Comment afficher du texte et des variables à l'écran

---

## Voir aussi

- [Préréglage Débutant](Beginner-Preset_fr) - Aperçu des fonctionnalités de débutant
- [Tutoriel : Breakout](Tutorial-Breakout_fr) - Créez un jeu de casse-briques
- [Référence des événements](Event-Reference_fr) - Documentation complète des événements
- [Référence complète des actions](Full-Action-Reference_fr) - Toutes les actions disponibles
