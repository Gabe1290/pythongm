# Creer votre premier jeu

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

> [Retour a l'accueil](Home_fr)

Dans ce tutoriel, nous allons creer un jeu simple "Attrape les etoiles" ou un joueur se deplace pour collecter des etoiles qui tombent.

---

## Ce que vous apprendrez

- Creer des sprites
- Creer des objets avec des evenements et des actions
- Utiliser l'editeur de salles
- Tester votre jeu

---

## Etape 1: Creer un nouveau projet

1. Lancez PyGameMaker
2. Allez dans **Fichier > Nouveau projet**
3. Nommez votre projet "AttrapeLesEtoiles"
4. Cliquez sur **Creer**

---

## Etape 2: Creer le sprite du joueur

1. Clic droit sur **Sprites** dans l'arbre des ressources
2. Selectionnez **Creer un sprite**
3. Nommez-le `spr_joueur`
4. Cliquez sur **Editer le sprite** pour l'ouvrir
5. Dessinez un personnage simple
6. Cliquez sur **Sauvegarder**

---

## Etape 3: Creer le sprite de l'etoile

1. Clic droit sur **Sprites** > **Creer un sprite**
2. Nommez-le `spr_etoile`
3. Dessinez une forme d'etoile
4. Cliquez sur **Sauvegarder**

---

## Etape 4: Creer l'objet joueur

1. Clic droit sur **Objets** dans l'arbre des ressources
2. Selectionnez **Creer un objet**
3. Nommez-le `obj_joueur`
4. Definissez le **Sprite** sur `spr_joueur`

### Ajouter des evenements clavier

**Fleche gauche:**
1. Cliquez sur **Ajouter un evenement** > **Clavier** > **Gauche**
2. Ajoutez l'action: **Definir la vitesse horizontale** avec la valeur `-4`

**Fleche droite:**
1. Cliquez sur **Ajouter un evenement** > **Clavier** > **Droite**
2. Ajoutez l'action: **Definir la vitesse horizontale** avec la valeur `4`

**Aucune touche:**
1. Cliquez sur **Ajouter un evenement** > **Clavier** > **Aucune touche**
2. Ajoutez l'action: **Definir la vitesse horizontale** avec la valeur `0`

---

## Etape 5: Creer l'objet etoile

1. Clic droit sur **Objets** > **Creer un objet**
2. Nommez-le `obj_etoile`
3. Definissez le **Sprite** sur `spr_etoile`

### Ajouter l'evenement Create
1. Cliquez sur **Ajouter un evenement** > **Create**
2. Ajoutez l'action: **Definir la vitesse verticale** avec la valeur `3`

### Ajouter la collision avec le joueur
1. Cliquez sur **Ajouter un evenement** > **Collision** > selectionnez `obj_joueur`
2. Ajoutez l'action: **Modifier le score** avec la valeur `10` et **Relatif** coche
3. Ajoutez l'action: **Sauter a une position aleatoire**

---

## Etape 6: Creer la salle

1. Clic droit sur **Salles** dans l'arbre des ressources
2. Selectionnez **Creer une salle**
3. Nommez-la `room_jeu`
4. Definissez la taille sur **640 x 480**

### Placer les objets
1. Selectionnez l'onglet **Objets** dans l'editeur de salles
2. Cliquez sur `obj_joueur` et placez-le en bas au centre
3. Cliquez sur `obj_etoile` et placez 5-10 etoiles en haut

---

## Etape 7: Testez votre jeu!

1. Appuyez sur **F5** ou allez dans **Executer > Lancer le jeu**
2. Utilisez les fleches gauche et droite pour vous deplacer
3. Attrapez les etoiles pour augmenter votre score!

---

## Prochaines etapes

- [[Editeur-Objets_fr]] - En savoir plus sur les proprietes des objets
- [[Evenements-Actions_fr]] - Explorer tous les evenements et actions
- [[Programmation-Visuelle_fr]] - Essayez les blocs Blockly
- [[Exportation_fr]] - Partagez votre jeu
