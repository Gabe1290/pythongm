# Tutoriel : Créer un Casse-Briques

*[Home_fr](Home_fr) | [Préréglage Débutant](Beginner-Preset_fr) | [English](Tutorial-Breakout)*

Ce tutoriel vous guidera dans la création d'un jeu de casse-briques classique. C'est un premier projet parfait pour apprendre PyGameMaker !

![Concept du Casse-Briques](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Ce que vous allez apprendre

- Créer et utiliser des sprites
- Configurer des objets de jeu avec des événements et des actions
- Contrôles clavier pour le mouvement du joueur
- Détection de collision et rebondissement
- Détruire des objets lors d'une collision
- Construire une salle de jeu

---

## Étape 1 : Créer les Sprites

D'abord, nous devons créer les éléments visuels de notre jeu.

### 1.1 Créer le Sprite de la Barre
1. Dans le panneau **Assets**, clic droit sur **Sprites** → **Créer Sprite**
2. Nommez-le `spr_barre`
3. Dessinez un rectangle horizontal (environ 64x16 pixels)
4. **Important :** Cliquez sur **Centre** pour définir l'origine au centre

### 1.2 Créer le Sprite de la Balle
1. Créez un autre sprite nommé `spr_balle`
2. Dessinez un petit cercle (environ 16x16 pixels)
3. Cliquez sur **Centre** pour définir l'origine

### 1.3 Créer le Sprite de la Brique
1. Créez un sprite nommé `spr_brique`
2. Dessinez un rectangle (environ 48x24 pixels)
3. Cliquez sur **Centre** pour définir l'origine

### 1.4 Créer le Sprite du Mur
1. Créez un sprite nommé `spr_mur`
2. Dessinez un carré (environ 32x32 pixels) - ce sera la limite du terrain
3. Cliquez sur **Centre** pour définir l'origine

### 1.5 Créer un Arrière-plan (Optionnel)
1. Clic droit sur **Backgrounds** → **Créer Background**
2. Nommez-le `bg_jeu`
3. Dessinez ou chargez une image d'arrière-plan

---

## Étape 2 : Créer l'Objet Barre

Maintenant, programmons la barre que le joueur contrôle.

### 2.1 Créer l'Objet
1. Clic droit sur **Objects** → **Créer Object**
2. Nommez-le `obj_barre`
3. Définissez le **Sprite** sur `spr_barre`
4. Cochez la case **Solid**

### 2.2 Ajouter le Mouvement Flèche Droite
1. Cliquez sur **Add Event** → **Keyboard** → sélectionnez **Flèche Droite**
2. Ajoutez l'action **Set Horizontal Speed**
3. Mettez **value** à `5` (ou la vitesse que vous préférez)

### 2.3 Ajouter le Mouvement Flèche Gauche
1. Cliquez sur **Add Event** → **Keyboard** → sélectionnez **Flèche Gauche**
2. Ajoutez l'action **Set Horizontal Speed**
3. Mettez **value** à `-5`

### 2.4 Arrêter Quand les Touches sont Relâchées
La barre continue de bouger même après avoir relâché la touche ! Corrigeons cela.

1. Cliquez sur **Add Event** → **Keyboard Release** → sélectionnez **Flèche Droite**
2. Ajoutez l'action **Set Horizontal Speed**
3. Mettez **value** à `0`

4. Cliquez sur **Add Event** → **Keyboard Release** → sélectionnez **Flèche Gauche**
5. Ajoutez l'action **Set Horizontal Speed**
6. Mettez **value** à `0`

Maintenant la barre s'arrête quand vous relâchez les touches.

---

## Étape 3 : Créer l'Objet Balle

### 3.1 Créer l'Objet
1. Créez un nouvel objet nommé `obj_balle`
2. Définissez le **Sprite** sur `spr_balle`
3. Cochez la case **Solid**

### 3.2 Définir le Mouvement Initial
1. Cliquez sur **Add Event** → **Create**
2. Ajoutez l'action **Move in Direction** (ou **Set Horizontal/Vertical Speed**)
3. Définissez une direction diagonale avec vitesse `5`
   - Par exemple : **hspeed** = `4`, **vspeed** = `-4`

Cela fait bouger la balle dès le début du jeu.

### 3.3 Rebondir sur la Barre
1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_barre`
2. Ajoutez l'action **Reverse Vertical** (pour rebondir)

### 3.4 Rebondir sur les Murs
1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_mur`
2. Ajoutez l'action **Reverse Horizontal** ou **Reverse Vertical** selon besoin
   - Ou utilisez les deux pour gérer les rebonds dans les coins

---

## Étape 4 : Créer l'Objet Brique

### 4.1 Créer l'Objet
1. Créez un nouvel objet nommé `obj_brique`
2. Définissez le **Sprite** sur `spr_brique`
3. Cochez la case **Solid**

### 4.2 Détruire lors de la Collision avec la Balle
1. Cliquez sur **Add Event** → **Collision** → sélectionnez `obj_balle`
2. Ajoutez l'action **Destroy Instance** avec cible **self**

Cela détruit la brique quand la balle la touche !

### 4.3 Faire Rebondir la Balle
Dans le même événement de collision, ajoutez aussi :
1. Ajoutez l'action **Reverse Vertical** (appliquée à **other** - la balle)

Ou retournez à `obj_balle` et ajoutez :
1. **Add Event** → **Collision** → sélectionnez `obj_brique`
2. Ajoutez l'action **Reverse Vertical**

---

## Étape 5 : Créer l'Objet Mur

### 5.1 Créer l'Objet
1. Créez un nouvel objet nommé `obj_mur`
2. Définissez le **Sprite** sur `spr_mur`
3. Cochez la case **Solid**

C'est tout - le mur doit juste être solide pour que la balle rebondisse.

---

## Étape 6 : Créer la Salle de Jeu

### 6.1 Créer la Salle
1. Clic droit sur **Rooms** → **Créer Room**
2. Nommez-la `room_jeu`

### 6.2 Définir l'Arrière-plan (Optionnel)
1. Dans les paramètres de la salle, trouvez **Background**
2. Sélectionnez votre arrière-plan `bg_jeu`
3. Cochez **Stretch** si vous voulez qu'il remplisse la salle

### 6.3 Placer les Objets

Maintenant placez vos objets dans la salle :

1. **Placez la Barre :** Mettez `obj_barre` en bas au centre de la salle

2. **Placez les Murs :** Mettez des instances de `obj_mur` autour des bords :
   - Le long du haut
   - Le long du côté gauche
   - Le long du côté droit
   - Laissez le bas ouvert (c'est par là que la balle peut s'échapper !)

3. **Placez la Balle :** Mettez `obj_balle` quelque part au milieu

4. **Placez les Briques :** Disposez des instances de `obj_brique` en rangées en haut de la salle

---

## Étape 7 : Testez Votre Jeu !

1. Cliquez sur le bouton **Play** (flèche verte)
2. Utilisez les touches **Gauche** et **Droite** pour déplacer la barre
3. Essayez de faire rebondir la balle pour détruire toutes les briques !
4. Appuyez sur **Échap** pour quitter

---

## Et Après ?

Votre jeu de casse-briques basique est terminé ! Voici quelques améliorations à essayer :

### Ajouter un Système de Vies
- Ajoutez un événement **No More Lives** pour afficher "Game Over"
- Perdez une vie quand la balle sort par le bas

### Ajouter un Score
- Utilisez l'action **Add Score** en détruisant les briques
- Affichez le score avec **Draw Score**

### Ajouter Plusieurs Niveaux
- Créez plus de salles avec différentes dispositions de briques
- Utilisez **Next Room** quand toutes les briques sont détruites

### Ajouter des Effets Sonores
- Ajoutez des sons pour les rebonds et la destruction des briques
- Utilisez l'action **Play Sound**

---

## Résumé des Objets

| Objet | Sprite | Solid | Événements |
|-------|--------|-------|------------|
| `obj_barre` | `spr_barre` | Oui | Keyboard (Gauche/Droite), Keyboard Release |
| `obj_balle` | `spr_balle` | Oui | Create, Collision (barre, mur, brique) |
| `obj_brique` | `spr_brique` | Oui | Collision (balle) - Détruire self |
| `obj_mur` | `spr_mur` | Oui | Aucun nécessaire |

---

## Voir Aussi

- [Préréglage Débutant](Beginner-Preset_fr) - Événements et actions utilisés dans ce tutoriel
- [Référence des Événements](Event-Reference_fr) - Tous les événements disponibles
- [Référence des Actions](Full-Action-Reference_fr) - Toutes les actions disponibles
