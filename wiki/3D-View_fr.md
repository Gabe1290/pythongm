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
| **Activer la vue Raycast** (`enable_raycast_view`) | Bascule la salle courante vers la vue à la première personne (ou revient en arrière) et configure la caméra : `camera_object`, `fov`, `render_distance`, `cell_size`, couleurs et textures des murs/sol/plafond, un `sky_texture` optionnel, `viewport_height` (une barre façon DOOM), `wall_height` (hauteur des murs et du plafond en cases, 1.5 par défaut) et `max_step` (la plus haute marche franchissable, en pixels, 12 par défaut). |
| **Définir l'angle de vue** (`set_facing_angle`) | Fait tourner la caméra. Angle en degrés GameMaker (0 = droite, 90 = haut) ; `relative` ajoute à l'angle courant. |
| **Dessiner la mini-carte** (`draw_minimap`) | Dessine une mini-carte orientée nord des murs de la salle avec un repère « vous êtes ici ». C'est une action d'ATH (HUD) — à placer dans un événement Dessin. |
| **Définir la hauteur du sol** (`set_floor_height`) | Fait de cette instance une **marche** : les cases de la grille couvertes par son sprite deviennent un sol surélevé de cette hauteur (en pixels). À placer dans l'événement Création d'un objet non solide. Textures du dessus et du côté facultatives. Voir *Escaliers et plates-formes* ci-dessous. |
| **Définir la rotation du sprite** (`set_billboard_rotation`) | Donne à un billboard plusieurs images selon l'angle de vue, pour qu'il montre ses côtés quand on tourne autour. |
| **Dessiner l'ATH DOOM** (`draw_doom_hud`) | Dessine une barre d'état inférieure façon DOOM : barre de santé + valeur, un visage réactif à la santé, le score, les vies et un compteur d'objectif. S'associe au `viewport_height` de `enable_raycast_view`. |

Voir la [Référence Complète des Actions](Full-Action-Reference-3D-View-Actions_fr) pour
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

## Escaliers et plates-formes

Une **marche** est un objet ordinaire *non solide*, avec **Définir la hauteur
du sol** dans son événement Création (`height` en pixels). Chaque case de la
grille couverte par son sprite devient un sol surélevé ; placez les marches sur
la grille comme des murs — le plus simple est un objet par hauteur
(`obj_step_8`, `obj_step_16`, …).

- **Monter :** tout ce qui bouge (le joueur, les monstres) peut monter une
  marche d'au plus **Marche maximale** pixels (dans Activer la vue Raycast, 12 par
  défaut) ; une marche plus haute l'arrête comme un mur, et il glisse le long.
  **Descendre** est toujours permis. La vue monte et descend en douceur.
- **De la place au-dessus :** augmentez **Hauteur des murs** (par exemple `3`) — à
  la valeur par défaut, 1.5, il n'y a de la place que pour 20 px de sol sous le
  plafond (les sols plus hauts sont ramenés à 20 px).
- **Deux variables sur chaque instance qui bouge :** `raycast_step_blocked`
  (1 pendant une image où une marche était trop haute — une marche refusée ne
  déclenche aucun événement, donc un monstre peut la tester avec *Tester une
  variable* dans Fin d'étape pour faire demi-tour) et `raycast_floor_z` (la
  hauteur du sol sous elle).
- Les objets à ramasser et les monstres se tiennent sur le sol de leur case,
  et les marches cachent ce qui est derrière elles. La mini-carte nuance les
  cases surélevées selon leur hauteur.

L'exemple **raycast_5** (*2.5 D — Niveau 5*) est un petit niveau construit
autour d'un escalier. Les escaliers fonctionnent sur ordinateur et dans les
exports HTML5 et Kivy (Android/iOS).

---

## Remarques et limites

- Les actions d'ATH (`draw_minimap`, `draw_doom_hud`, ainsi que les
  `draw_score` / `draw_lives` / `draw_text` habituelles) se superposent **par
  dessus** l'image à la première personne, en coordonnées d'écran.
- Les murs et les marches sont reconstruits à chaque image : un mur ou une
  marche créé ou détruit pendant le jeu (une porte, un pont) apparaît aussitôt.
- Il n'y a qu'une hauteur de plafond par salle (Wall Height), on ne peut ni
  regarder vers le haut ou le bas, ni sauter, et il n'y a pas de pentes —
  construisez les rampes avec de petites marches.
- Si l'extension 2.5D Raycast est **désactivée**, une salle qui active la vue
  s'affiche simplement en vue du dessus et l'IDE vous en avertit au chargement —
  voir [Extensions](Extensions_fr).

---

## Voir aussi

- [Extensions](Extensions_fr) — comment la Vue 3D est fournie et comment la désactiver
- [Référence Complète des Actions](Full-Action-Reference-3D-View-Actions_fr) — toutes les actions Vue 3D en détail
- [Éditeur de Salles](Editeur_Salles_fr) — placer les objets-murs à partir desquels la vue est construite

## Tutoriels

Le panneau Tutoriels de l'IDE contient une série 2.5D de quatre leçons : Premiers pas, Textures/ciel/sol, Objectifs/gemmes/monstres, et ATH/minicarte (Leçons 11 à 14). Elles sont masquées dans l'édition débutant.
