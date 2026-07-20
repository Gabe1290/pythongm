# Plateforme — Niveau 2

Un jeu de plateformes à défilement latéral importé de GameMaker 8.x
(`samples/plateforme_2.gmk`). Comparé à un premier niveau minimal, celui-ci
enrichit la liste des objets : au lieu d'un simple joueur et d'un unique bloc, on
passe à quatre objets (une plateforme de base, plus des variantes horizontale et
verticale qui en héritent) disposés dans une salle de 126 instances construite à
partir d'un jeu de tuiles automatiques sur le thème de la neige, plutôt que de
quelques blocs placés à la main.

**Où ce niveau se situe :** il fait partie de la famille `plateforme_*`, et —
contrairement au minimal `plateforme_1` — c'est ici qu'apparaît l'**arrière-plan
en tuiles** : 127 morceaux de tuiles placés individuellement (le tableau `tiles`
de la salle), plus une image d'arrière-plan en dégradé (`fond_degrade`),
superposés sous les *objets* briques solides qui gèrent toujours les collisions.
C'est l'étape que `plateforme_*` ajoute par rapport à `maze_*` ; voir
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
pour la progression complète.

**Sons et musique :** aucun — aucun fichier sonore n'est fourni avec cet exemple.

## Comment jouer

- **Flèches gauche / droite** — déplacent le pingouin (`obj_personnage`) vers la
  gauche ou la droite.
- **Flèche haut** — saut, mais uniquement quand le joueur repose sur une
  plateforme solide (vérifié par un test de collision un pixel plus bas).
- **Objectif** — il n'y a ni objectif ni drapeau d'arrivée dans cet exemple :
  c'est un décor de plateformes à explorer et à parcourir en circulant sur les
  `obj_brique*`.
- **Condition de défaite** — aucune n'est définie (ni danger, ni objet mortel, ni
  détection de chute) ; la rangée de briques du bas fait office de sol.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `project.json` | Manifeste du projet — réglages de fenêtre et de salle, copies intégrées des ressources. |
| `rooms/niveau_01.json` | L'unique salle : 800×640, 126 instances et 127 tuiles d'arrière-plan. C'est la référence pour le contenu de la salle (la liste `instances` intégrée dans `project.json` est vide). |
| `objects/*.json` | Fichiers annexes des 4 objets ; identiques aux copies intégrées dans `project.json` à ce jour. |
| `sprites/` | 5 sprites (bandes d'animation de marche du joueur et blocs de plateforme solides). |
| `backgrounds/` | Jeu de tuiles enneigées (`tuiles_neige.png`, utilisé comme source de tuiles automatiques) et un petit dégradé vertical (`fond_degrade.png`) étiré en arrière-plan de la salle. |
| `CREDITS.txt` | Mentions de licence des graphismes (voir « Ressources » ci-dessous). |

## Objets

| Objet | Rôle | Événements principaux |
|---|---|---|
| `obj_personnage` | Joueur (pingouin) — déplacement, saut, gravité, détection du sol | `create`, `step`, `collision_with_obj_brique`, `keyboard` (gauche, droite, haut), `keyboard_release` (GAUCHE, DROITE) |
| `obj_brique` | Bloc de plateforme solide de base (32×32) | (aucun — pas d'événement, seulement l'indicateur « solide ») |
| `obj_brique_h` | Variante large de plateforme solide (32×16), enfant d'`obj_brique` | (aucun) |
| `obj_brique_v` | Variante étroite de plateforme solide (8×16), enfant d'`obj_brique` ; définie mais non placée dans `niveau_01` | (aucun) |

## Ressources

5 sprites (`spr_pingus_dr` / `spr_pingus_ga`, bandes de marche de 8 images, plus
trois blocs de couleur unie servant de substituts, en 32×32 / 32×16 / 8×16) et
2 arrière-plans ; aucun son. Les graphismes des sprites et des arrière-plans sont
adaptés du projet Pingus (GPL-3.0-or-later) — voir `CREDITS.txt` pour la mention
complète et les termes de la licence ; ce guide ne reformule ni n'étend ces
mentions.

## À expérimenter

- La vitesse horizontale du joueur est un simple `hspeed = 4` dans les événements
  clavier.
- L'impulsion de saut vaut `vspeed = -10` ; la gravité de chute est de `0,45`
  (appliquée uniquement en l'air), avec une vitesse limite plafonnée à
  `vspeed = 24`.
- La salle fait 800×640 avec `room_speed = 30`.

## État de l'export

Cet exemple figure dans la liste `SAMPLES` de `tools/smoke_run_samples.py` : il
est donc couvert par les tests automatiques (la vraie boucle de jeu est exécutée
pendant environ 180 images avec des appuis de touches simulés) à chaque passage
de ce banc d'essai. Aucune vérification n'a été faite spécifiquement pour cet
exemple sur les cibles d'export (Kivy/Web). Il est présent dans l'onglet
d'accueil de l'IDE sous le nom **« Plateforme — Niveau 2 »**
(`widgets/welcome_tab.py`).
