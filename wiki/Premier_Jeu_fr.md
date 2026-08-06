# Créer votre premier jeu

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

> [Retour à l'accueil](Home_fr)

Dans ce tutoriel, nous allons créer un jeu simple « Attrape les étoiles » où un joueur se déplace pour collecter des étoiles qui tombent.

---

## Ce que vous apprendrez

- Créer des sprites
- Créer des objets avec des événements et des actions
- Utiliser l'éditeur de salles
- Tester votre jeu

---

## Étape 1 : Créer un nouveau projet

1. Lancez PyGameMaker
2. Allez dans **Fichier > Nouveau projet**
3. Nommez votre projet « AttrapeLesEtoiles »
4. Cliquez sur **Créer**

---

## Étape 2 : Créer le sprite du joueur

1. Clic droit sur **Sprites** dans l'arbre des ressources
2. Sélectionnez **Créer un sprite**
3. Nommez-le `spr_joueur`
4. Cliquez sur **Éditer le sprite** pour l'ouvrir
5. Dessinez un personnage simple
6. Cliquez sur **Sauvegarder**

---

## Étape 3 : Créer le sprite de l'étoile

1. Clic droit sur **Sprites** > **Créer un sprite**
2. Nommez-le `spr_etoile`
3. Dessinez une forme d'étoile
4. Cliquez sur **Sauvegarder**

---

## Étape 4 : Créer l'objet joueur

1. Clic droit sur **Objets** dans l'arbre des ressources
2. Sélectionnez **Créer un objet**
3. Nommez-le `obj_joueur`
4. Définissez le **Sprite** sur `spr_joueur`

### Ajouter des événements clavier

**Flèche gauche :**
1. Cliquez sur **Ajouter un événement** > **Clavier** > **Gauche**
2. Ajoutez l'action : **Définir la vitesse horizontale** avec la valeur `-4`

**Flèche droite :**
1. Cliquez sur **Ajouter un événement** > **Clavier** > **Droite**
2. Ajoutez l'action : **Définir la vitesse horizontale** avec la valeur `4`

**Aucune touche :**
1. Cliquez sur **Ajouter un événement** > **Clavier** > **Aucune touche**
2. Ajoutez l'action : **Définir la vitesse horizontale** avec la valeur `0`

---

## Étape 5 : Créer l'objet étoile

1. Clic droit sur **Objets** > **Créer un objet**
2. Nommez-le `obj_etoile`
3. Définissez le **Sprite** sur `spr_etoile`

### Ajouter l'événement Create
1. Cliquez sur **Ajouter un événement** > **Create**
2. Ajoutez l'action : **Définir la vitesse verticale** avec la valeur `3`

### Ajouter la collision avec le joueur
1. Cliquez sur **Ajouter un événement** > **Collision** > sélectionnez `obj_joueur`
2. Ajoutez l'action : **Modifier le score** avec la valeur `10` et **Relatif** coché
3. Ajoutez l'action : **Sauter à une position aléatoire**

---

## Étape 6 : Créer la salle

1. Clic droit sur **Salles** dans l'arbre des ressources
2. Sélectionnez **Créer une salle**
3. Nommez-la `room_jeu`
4. Définissez la taille sur **640 x 480**

### Placer les objets
1. Sélectionnez l'onglet **Objets** dans l'éditeur de salles
2. Cliquez sur `obj_joueur` et placez-le en bas au centre
3. Cliquez sur `obj_etoile` et placez 5-10 étoiles en haut

---

## Étape 7 : Testez votre jeu !

1. Appuyez sur **F5** ou allez dans **Compiler > Tester le jeu**
2. Utilisez les flèches gauche et droite pour vous déplacer
3. Attrapez les étoiles pour augmenter votre score !

---

## Prochaines étapes

- [[Editeur_Objets_fr]] - En savoir plus sur les propriétés des objets
- [[Evenements_Actions_fr]] - Explorer tous les événements et actions
- [[Programmation_Visuelle_fr]] - Essayez les blocs Blockly
- [[Exportation_fr]] - Partagez votre jeu
