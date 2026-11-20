# 2.5 D — Niveau 5

Le cinquième niveau à la première personne, et le premier avec de la
**hauteur** : un escalier qu'on peut monter, une galerie où marcher, un rebord
d'où sauter, et un pilier trop haut pour être franchi. Jusqu'ici, toutes les
salles en 2.5 D étaient plates — celle-ci montre comment construire un
escalier avec des objets ordinaires.

## Comment jouer

| Touche | Action |
|---|---|
| **↑** / **↓** | Avancer / reculer |
| **←** / **→** | Tourner à gauche / à droite |

Tu commences en bas, face à l'escalier. Avance tout droit : la vue monte
marche après marche. En haut, tourne à droite et suis la galerie jusqu'au
**drapeau**. Attention au **monstre** qui patrouille dans la salle du bas —
s'il t'attrape, tu recommences.

## Comment on fabrique un escalier

Une marche est un objet ordinaire, **non solide**, avec une seule action dans
son événement **Create** :

**Set Floor Height** (3D View) — `height` en pixels de la salle, plus une
**Top Texture** et une **Side Texture** facultatives (vide = les textures du
sol et des murs).

Chaque case de la grille couverte par le sprite de la marche devient un sol
surélevé de cette hauteur. Cet exemple utilise un objet par hauteur —
`obj_step_8`, `obj_step_16`, `obj_step_24`, `obj_step_32` (la galerie) et
`obj_step_48` (le pilier) — placés sur la grille comme des murs. Dans
l'éditeur de salle, ce sont de simples carrés gris (plus clair = plus haut) ;
seule la vue à la première personne les dessine comme des marches.

Les objets se tiennent sur le sol de leur case : le drapeau posé sur la
galerie est dessiné là-haut ; passe derrière une marche et elle cache le bas
de ce qui se trouve derrière.

## Comment fonctionne la montée

Deux réglages de **Enable Raycast View** (dans l'événement Create de
`obj_person`) :

- **Wall Height** = `3` cases. La valeur habituelle, 1.5, laisse très peu de
  place au-dessus des yeux ; un sol surélevé demande des murs plus hauts et un
  plafond plus haut.
- **Max Step** = `12` pixels : la plus haute marche qu'on peut monter. Les
  marches de 8 px passent ; le pilier de 48 px t'arrête comme un mur (tu
  glisses le long). **Descendre** est toujours permis — tu peux sauter de la
  galerie n'importe où.

La vue monte en douceur quand tu grimpes et redescend quand tu sautes d'un
rebord.

La même règle s'applique à **tout ce qui bouge**, pas seulement au joueur : le
monstre ne peut pas non plus monter sur le pilier. Une marche refusée ne
déclenche aucun événement ; chaque instance qui bouge reçoit donc une variable
à la place :

| Variable | Signification |
|---|---|
| `raycast_step_blocked` | `1` pendant une image où une marche était trop haute, sinon `0` |
| `raycast_floor_z` | la hauteur du sol sous elle, en pixels |

L'événement **End Step** du monstre utilise la première :
*Test Variable* `raycast_step_blocked` = `1` → *Reverse Horizontal*. C'est
ainsi qu'il fait demi-tour devant le pilier. Tu pourrais utiliser
`raycast_floor_z` pour tester « suis-je sur la galerie ? »
(`raycast_floor_z` = `32`).

## La minicarte

La minicarte (en haut à gauche, `draw_minimap` dans l'événement Draw de
`obj_person`) assombrit ou éclaircit les cases surélevées selon leur hauteur :
l'escalier et la galerie apparaissent comme des marches de gris, et le
drapeau est marqué en cyan.

## Structure du projet

| Objet | Rôle |
|---|---|
| `obj_person` | Le joueur et la caméra : commandes, réglages de la vue, minicarte, collisions avec le monstre et le drapeau |
| `obj_wall` | Les murs solides autour de la salle |
| `obj_step_8` … `obj_step_48` | Les marches, la galerie et le pilier (Set Floor Height) |
| `obj_monster` | Patrouille dans la salle du bas, fait demi-tour devant les murs et le pilier |
| `obj_goal` | Le drapeau sur la galerie |

La salle est générée par `tools/gen_raycast_5_stairs.py` : on peut la
reconstruire ou la modifier à un seul endroit (les tests vérifient que les
fichiers lui correspondent).

## À expérimenter

- Mets **Max Step** à `24` dans Enable Raycast View : tu peux maintenant
  monter sur l'escalier par le côté, directement de la salle à la marche de
  16 px.
- Change la **Set Floor Height** de `obj_step_16` à `30` : depuis la marche de
  8 px, cela fait une montée de 22 px, plus que Max Step — l'escalier est
  bloqué.
- Remets **Wall Height** à `1.5` : il n'y a plus la place d'une galerie de
  32 px sous le plafond, donc tout sol plus haut que 20 px est ramené à 20 px
  (un avertissement est écrit dans le journal).
- Donne une **Top Texture** à `obj_step_32` pour que le sol de la galerie ne
  ressemble pas à celui de la salle.

## État de l'export

Les escaliers fonctionnent sur ordinateur, dans l'export HTML5 et dans
l'export Kivy (Android/iOS). Personne n'a encore joué à cet exemple sur un
téléphone : si tu le fais, dis-nous comment on y grimpe.
