# Tutoriel : Créer un Jeu de Plateforme

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduction

Dans ce tutoriel, vous allez créer un **Jeu de Plateforme** - un jeu d'action à défilement horizontal où le joueur court, saute et navigue sur des plateformes tout en évitant les dangers et en collectant des pièces. Ce genre classique est parfait pour apprendre la gravité, les mécaniques de saut et la collision avec les plateformes.

**Ce que vous apprendrez :**
- La gravité et la physique de chute
- Les mécaniques de saut avec détection du sol
- La collision avec les plateformes (atterrir dessus)
- Le mouvement gauche/droite
- Les objets à collecter et les dangers

**Difficulté :** Débutant
**Preset :** Preset Débutant

---

## Étape 1 : Comprendre le Jeu

### Mécaniques de Jeu
1. Le joueur est affecté par la gravité et tombe
2. Le joueur peut se déplacer à gauche et à droite
3. Le joueur peut sauter quand il est sur le sol
4. Les plateformes empêchent le joueur de tomber à travers
5. Collectez des pièces pour des points
6. Atteignez le drapeau pour terminer le niveau

### Ce Dont Nous Avons Besoin

| Élément | Rôle |
|---------|------|
| **Joueur** | Le personnage que vous contrôlez |
| **Sol/Plateforme** | Surfaces solides pour se tenir debout |
| **Pièce** | Objets à collecter pour le score |
| **Pic** | Danger qui blesse le joueur |
| **Drapeau** | Objectif qui termine le niveau |

---

## Étape 2 : Créer les Sprites

### 2.1 Sprite du Joueur

1. Dans l'**Arbre des Ressources**, faites un clic droit sur **Sprites** et sélectionnez **Créer Sprite**
2. Nommez-le `spr_player`
3. Cliquez sur **Éditer Sprite** pour ouvrir l'éditeur
4. Dessinez un personnage simple (rectangle avec visage, ou bonhomme)
5. Utilisez une couleur vive comme le bleu ou le rouge
6. Taille : 32x48 pixels (plus haut que large pour un personnage)
7. Cliquez sur **OK** pour sauvegarder

### 2.2 Sprite du Sol

1. Créez un nouveau sprite nommé `spr_ground`
2. Dessinez une tuile de plateforme herbe/terre
3. Utilisez des couleurs marron et vert
4. Taille : 32x32 pixels

### 2.3 Sprite de Plateforme

1. Créez un nouveau sprite nommé `spr_platform`
2. Dessinez une plateforme flottante (bois ou pierre)
3. Taille : 64x16 pixels (large et fine)

### 2.4 Sprite de Pièce

1. Créez un nouveau sprite nommé `spr_coin`
2. Dessinez un petit cercle jaune/doré
3. Taille : 16x16 pixels

### 2.5 Sprite de Pic

1. Créez un nouveau sprite nommé `spr_spike`
2. Dessinez des pics triangulaires pointant vers le haut
3. Utilisez des couleurs grises ou rouges
4. Taille : 32x32 pixels

### 2.6 Sprite du Drapeau

1. Créez un nouveau sprite nommé `spr_flag`
2. Dessinez un drapeau sur un poteau
3. Utilisez des couleurs vives (drapeau vert, poteau marron)
4. Taille : 32x64 pixels

---

## Étape 3 : Créer l'Objet Sol

Le sol est une plateforme solide qui empêche le joueur de tomber.

1. Faites un clic droit sur **Objets** et sélectionnez **Créer Objet**
2. Nommez-le `obj_ground`
3. Définissez le sprite sur `spr_ground`
4. **Cochez la case "Solide"**
5. Aucun événement nécessaire

---

## Étape 4 : Créer l'Objet Plateforme

Les plateformes fonctionnent comme le sol mais peuvent être placées dans l'air.

1. Créez un nouvel objet nommé `obj_platform`
2. Définissez le sprite sur `spr_platform`
3. **Cochez la case "Solide"**
4. Aucun événement nécessaire

---

## Étape 5 : Créer l'Objet Joueur

Le joueur est l'objet le plus complexe avec la gravité, le saut et le mouvement.

1. Créez un nouvel objet nommé `obj_player`
2. Définissez le sprite sur `spr_player`

### 5.1 Gravité

**Événement : Create** — Ajouter Action : **Move** → **Set Gravity**
(Direction : `270`, Gravity : `0.5`) — 270° correspond à vers le bas ; la
valeur est ajoutée à la vitesse verticale du joueur à chaque image, donc le
joueur accélère vers le bas tout seul à partir de maintenant.

### 5.2 Mouvement, Saut et Collision avec le Sol

Ajoutez ces événements, selon le même modèle que les tutoriels précédents
de ce wiki :

| Événement | Action |
|---|---|
| Keyboard (maintenue) → Left Arrow | Set Horizontal Speed à `-4` |
| Keyboard (maintenue) → Right Arrow | Set Horizontal Speed à `4` |
| Keyboard: No Key | Set Horizontal Speed à `0` |
| Key Press → Up Arrow | Set Vertical Speed à `-10` |
| Collision avec obj_ground | Stop Movement |

Deux détails qui rendent la sensation correcte :

- **No Key ne règle QUE la vitesse horizontale à 0** — n'utilisez jamais
  Stop Movement ici, car Stop Movement remet aussi la vitesse verticale à
  zéro, ce qui annulerait la gravité à chaque fois que le joueur relâche
  une touche de direction.
- **Key Press (pas maintenue)** est ce qui fait de Up une seule impulsion
  de saut au lieu de propulser le joueur vers le haut à chaque image où la
  touche est maintenue. **Stop Movement** à l'atterrissage annule ensuite
  cette impulsion, pour que le joueur ne continue pas à monter une fois
  posé — la collision solide intégrée du moteur (l'étape 3 a déjà rendu
  `obj_ground` Solid) empêche déjà le joueur de s'enfoncer dans le sol ;
  l'événement ici se contente d'effacer la vitesse de chute restante.

---

## Étape 6 : Créer l'Objet Pièce

Les pièces ajoutent au score quand elles sont collectées.

1. Créez un nouvel objet nommé `obj_coin`
2. Définissez le sprite sur `spr_coin`

**Événement : Collision avec obj_player**
1. Ajouter Événement → Collision → obj_player
2. Ajouter Action : **Score** → **Définir Score** (Nouveau Score : `10`, Cochez "Relatif")
3. Ajouter Action : **Main1** → **Détruire Instance** (S'applique à : Self)

---

## Étape 7 : Créer l'Objet Pic

Les pics blessent le joueur et redémarrent le niveau.

1. Créez un nouvel objet nommé `obj_spike`
2. Définissez le sprite sur `spr_spike`

**Événement : Collision avec obj_player**
1. Ajouter Événement → Collision → obj_player
2. Ajouter Action : **Main2** → **Afficher Message** (Message : `Aïe ! Vous avez touché un pic !`)
3. Ajouter Action : **Main1** → **Redémarrer Room**

---

## Étape 8 : Créer l'Objet Drapeau

Le drapeau termine le niveau quand le joueur l'atteint.

1. Créez un nouvel objet nommé `obj_flag`
2. Définissez le sprite sur `spr_flag`

**Événement : Collision avec obj_player**
1. Ajouter Événement → Collision → obj_player
2. Ajouter Action : **Output** → **Show Message** (Message : `Niveau terminé !`)
3. Ajouter Action : **Room** → **Next Room**

Le texte de Show Message est une chaîne fixe — il ne peut pas afficher une
valeur en direct comme le score.

---

## Étape 9 : Concevoir Votre Niveau

1. Faites un clic droit sur **Rooms** et sélectionnez **Créer Room**
2. Nommez-la `room_level1`
3. Définissez la taille de la room (ex : 800x480)
4. Activez "Aligner sur la Grille" et réglez la grille sur 32x32

### Placement des Objets

1. **Créez le sol** - Placez `obj_ground` en bas
2. **Ajoutez des plateformes** - Placez `obj_platform` dans l'air
3. **Ajoutez des trous** - Laissez des espaces dans le sol
4. **Placez des pièces** - Dispersez-les sur les plateformes
5. **Ajoutez des pics** - Près des trous ou sur les plateformes
6. **Placez le drapeau** - À la fin du niveau
7. **Placez le joueur** - Au début (côté gauche)

---

## Étape 10 : Testez Votre Jeu !

1. Cliquez sur **Exécuter** ou appuyez sur **F5** pour tester
2. Utilisez les flèches **Gauche/Droite** pour vous déplacer
3. Appuyez sur **Haut** ou **Espace** pour sauter
4. Collectez les pièces pour des points
5. Évitez les pics !
6. Atteignez le drapeau pour gagner !

---

## Ce que Vous Avez Appris

Félicitations ! Vous avez créé un jeu de plateforme ! Vous avez appris :

- **La physique de gravité** - Set Gravity applique une force vers le bas constante à chaque image
- **Les mécaniques de saut** - Un événement Key Press (pas maintenue) donne une seule impulsion de vitesse vers le haut
- **La collision solide intégrée** - Le sol bloque le joueur automatiquement une fois marqué Solid, sans code de vérification manuelle
- **Les dangers** - Créer des objets qui redémarrent le niveau

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Plus de tutoriels de jeux
- [Tutoriel : Labyrinthe](Tutorial-Maze_fr) - Créer un jeu de labyrinthe
- [Tutoriel : Breakout](Tutorial-Breakout_fr) - Créer un jeu de casse-briques
