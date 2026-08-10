# Éditeur de Sprites

> [English](Sprite-Editor) | [Français](Sprite-Editor_fr) | [Deutsch](Sprite-Editor_de) | [Italiano](Sprite-Editor_it) | [Español](Sprite-Editor_es) | [Português](Sprite-Editor_pt) | [Русский](Sprite-Editor_ru) | [Slovenščina](Sprite-Editor_sl)

---

> [Retour à l'accueil](Home_fr)

Les sprites sont les images et animations attachées aux objets. L'Éditeur de Sprites est un outil de pixel-art intégré — dessinez vos sprites directement dans PyGameMaker, sans éditeur d'image externe.

---

## Ouvrir l'Éditeur de Sprites

1. Double-cliquez sur un sprite existant dans l'arborescence des ressources, ou
2. Clic droit sur **Sprites** > **Créer un Sprite**

![L'Éditeur de Sprites : outils de dessin et taille du pinceau à gauche,
le sélecteur d'origine et l'option Collision Précise en dessous, une
palette de couleurs, la zone de dessin au centre montrant un personnage
en pixel-art à un zoom de 10x, et la bande d'images en bas (8 images,
bouton Lecture, ajout/duplication/suppression d'image)](images/sprite-editor.png)

---

## Outils de Dessin

| Outil | Raccourci | Ce qu'il fait |
|------|----------|---------------|
| **Crayon** | P | Dessiner pixel par pixel |
| **Gomme** | E | Effacer des pixels (transparence) |
| **Pipette** | I | Prélever une couleur sur la zone de dessin |
| **Remplissage** | G | Remplir une zone connectée (pot de peinture) |
| **Ligne** | L | Dessiner une ligne droite |
| **Rectangle** | R | Dessiner un rectangle (bascule **Rempli** pour plein/contour) |
| **Ellipse** | O | Dessiner une ellipse (respecte aussi **Rempli**) |
| **Sélection** | S | Sélection rectangulaire — déplacer, copier, couper, coller ou supprimer les pixels sélectionnés |

**La taille du pinceau** s'applique au Crayon, à la Gomme et aux contours
des lignes/formes. La palette de couleurs contient un jeu de couleurs de
travail plus la palette rapide standard à 12 couleurs ; cliquez sur une
pastille pour la choisir, ou utilisez la Pipette pour prélever une
couleur directement sur le sprite.

---

## Opérations sur la Zone de Dessin

- **Miroir H / Miroir V** — retourne l'image actuelle horizontalement ou verticalement
- **Redimensionner** — ouvre une boîte de dialogue avec deux modes distincts :
  - **Redimensionner l'Image** — étire le contenu existant vers une nouvelle taille
  - **Redimensionner le Canevas** — conserve le contenu à sa taille d'origine et ajoute/rogne de l'espace autour, ancré sur un coin, un bord ou le centre au choix
- **Grille** — active/désactive une superposition de grille au niveau des pixels (n'affecte pas l'image enregistrée)
- **Zoom Avant / Zoom Arrière** — la zone de dessin travaille souvent à 10x ou plus, les sprites étant généralement petits (16×16 à 64×64 est courant)
- **Exporter PNG…** — enregistre l'image actuelle comme fichier `.png` autonome
- Clic droit sur la zone de dessin pour **Copier / Couper / Coller / Supprimer / Désélectionner / Tout Sélectionner** (raccourcis standards : Ctrl+C / Ctrl+X / Ctrl+V / Suppr / Échap)

---

## Images et Animation

Un sprite peut contenir plusieurs images, jouées en animation lors de
l'exécution du jeu. La bande d'images en bas de l'éditeur :

| Contrôle | Effet |
|---------|--------|
| **+** | Ajouter une nouvelle image vierge |
| **D** | Dupliquer l'image actuelle |
| **-** | Supprimer l'image actuelle |
| **Lecture** | Prévisualiser l'animation dans l'éditeur à la fréquence d'images du sprite |

Cliquez sur une vignette d'image pour vous y rendre et dessiner spécifiquement sur cette image.

---

## Origine et Collision

- **Origine** — le point que les objets utilisant ce sprite considèrent
  comme leur position `(x, y)`. Préréglages : Haut-Gauche, Haut-Centre,
  Centre, Centre-Bas, Bas-Gauche, Bas-Droite, ou **Personnalisé** (X/Y
  exacts). La plupart des personnages de plateforme/vue du dessus
  utilisent **Centre-Bas** pour que les pieds du sprite soient à la
  position Y de l'objet.
- **Collision Précise** — une fois activée, les collisions contre ce
  sprite testent les pixels non transparents réels plutôt que la boîte
  englobante du sprite. Plus précis pour les sprites de forme irrégulière,
  plus coûteux à calculer — laissez désactivé pour les formes simples
  (murs, pièces) et réservez-le aux sprites où une collision par boîte
  englobante paraîtrait visiblement fausse.

---

## Étapes Suivantes

- [[Editeur_Objets_fr|Éditeur d'Objets]] - Attacher un sprite à un objet de jeu
- [[Editeur_Salles_fr|Éditeur de Salles]] - Placer des instances d'objet utilisant votre sprite
- [[Premier_Jeu_fr|Créer Votre Premier Jeu]] - Un tutoriel complet qui commence par dessiner des sprites
