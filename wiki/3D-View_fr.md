# Vue 3D (rendu à la première personne par lancer de rayons)

*[Accueil](Home_fr) | [Référence Complète des Actions](Full-Action-Reference_fr) | [Extensions](Extensions_fr)*

---

PyGameMaker peut afficher une salle comme une **vue 3D à la première personne, dans
le style de Doom/Wolfenstein**, au lieu de l'habituelle vue du dessus — les murs
comme des bandes verticales, un sol et un plafond colorés ou texturés, un ciel
panoramique optionnel, et des sprites en « panneau d'affichage » (billboards)
pour les objets à ramasser et les monstres. La *logique* du jeu (déplacements,
collisions, événements) ne change pas ; seule la manière de **dessiner** la salle
change.

Cette fonctionnalité est fournie par l'**extension 2.5D Raycast** intégrée, activée
par défaut (voir [Extensions](Extensions_fr)). Elle s'exporte vers les trois
cibles — ordinateur, HTML5 et Kivy/Android — de sorte qu'un jeu à la première
personne fonctionne partout de la même façon.

Les exemples fournis **`raycast_1` à `raycast_4`** sont des jeux complets et
jouables (un labyrinthe simple, un jeu à deux niveaux avec objets à ramasser et un
monstre, une variante avec santé et trousses de soins, et une démonstration de
barre d'état façon DOOM).

---

## Comment ça fonctionne

- Une salle passe à la première personne lorsqu'un objet exécute l'action
  **Activer la vue Raycast** (généralement dans son événement Création). Cet objet
  est la **caméra** par défaut — sa position est le point de vue et son
  `facing_angle` (angle de vue) est la direction du regard.
- **Les murs sont vos instances solides.** Le moteur déduit de fines *arêtes* de
  mur à partir de chaque objet solide de la salle, sur une grille dont la taille
  est le paramètre `cell_size` de l'action (32 par défaut — la taille utilisée par
  tous les exemples `maze_*`/`raycast_*`). Un objet solide muni d'un sprite de mur
  texture le mur ; sinon une couleur `wall_color` unie est utilisée.
- **La caméra tourne** en modifiant `facing_angle` (voir **Définir l'angle de
  vue**), et se déplace avec les actions de mouvement habituelles (par exemple
  `set_direction_speed` avec `direction = "facing_angle"` pour avancer tout droit).
- **Les instances non solides munies d'un sprite** (objectifs, objets à ramasser,
  monstres) s'affichent en **billboards** faisant face à la caméra, correctement
  masqués par les murs.

---

## Les actions (catégorie **Vue 3D**)

| Action | Ce qu'elle fait |
|--------|-----------------|
| **Activer la vue Raycast** (`enable_raycast_view`) | Bascule la salle courante vers la vue à la première personne (ou revient en arrière) et configure la caméra : `camera_object`, `fov`, `render_distance`, `cell_size`, couleurs et textures des murs/sol/plafond, un `sky_texture` optionnel, et `viewport_height` (une barre façon DOOM). |
| **Définir l'angle de vue** (`set_facing_angle`) | Fait tourner la caméra. Angle en degrés GameMaker (0 = droite, 90 = haut) ; `relative` ajoute à l'angle courant. |
| **Dessiner la mini-carte** (`draw_minimap`) | Dessine une mini-carte orientée nord des murs de la salle avec un repère « vous êtes ici ». C'est une action d'ATH (HUD) — à placer dans un événement Dessin. |
| **Dessiner l'ATH DOOM** (`draw_doom_hud`) | Dessine une barre d'état inférieure façon DOOM : barre de santé + valeur, un visage réactif à la santé, le score, les vies et un compteur d'objectif. S'associe au `viewport_height` de `enable_raycast_view`. |

Voir la [Référence Complète des Actions](Full-Action-Reference_fr#3d-view) pour
tous les paramètres.

---

## Un contrôleur minimal à la première personne

Dans l'objet du joueur :

- **Création :** `Activer la vue Raycast` (laissez `camera_object` vide pour que le
  joueur *soit* la caméra).
- **Clavier Gauche / Droite :** `Définir l'angle de vue` avec `relative` activé
  (par exemple ±3°).
- **Clavier Haut :** `Définir direction et vitesse` avec `direction = facing_angle`
  et une petite vitesse pour avancer.

Construisez la salle avec des objets-murs solides sur une grille de 32 pixels,
exactement comme les exemples `maze_*` — le moteur transforme ces murs en couloirs
3D.

---

## Remarques et limites

- Les actions d'ATH (`draw_minimap`, `draw_doom_hud`, ainsi que les
  `draw_score` / `draw_lives` / `draw_text` habituelles) se superposent **par
  dessus** l'image à la première personne, en coordonnées d'écran.
- Les murs sont statiques pour la passe à la première personne — les murs créés ou
  détruits après le chargement de la salle ne remodèlent pas la géométrie 3D.
- Si l'extension 2.5D Raycast est **désactivée**, une salle qui active la vue
  s'affiche simplement en vue du dessus et l'IDE vous en avertit au chargement —
  voir [Extensions](Extensions_fr).

---

## Voir aussi

- [Extensions](Extensions_fr) — comment la Vue 3D est fournie et comment la désactiver
- [Référence Complète des Actions](Full-Action-Reference_fr#3d-view) — les quatre actions en détail
- [Éditeur de Salles](Editeur_Salles_fr) — placer les objets-murs à partir desquels la vue est construite
