# 2.5 D — Niveau 6 : la jonction

Le sixième niveau à la première personne, celui qui trompe l'œil. La vue 2.5 D
ne peut pas mettre un sol au-dessus d'un autre sol : les jeux de ce genre
(Doom et ses descendants) trichent. **Un plafond bas** cache ce qu'il y a au-
dessus, et **un saut sans coupure dans une autre salle** fait que deux salles
paraissent n'en former qu'une. Ce niveau utilise les deux.

## Comment jouer

| Touche | Action |
|---|---|
| **↑** / **↓** | Avancer / reculer |
| **←** / **→** | Tourner à gauche / à droite |

Tu commences dans un hall avec une **galerie** (une plateforme) au fond,
qu'on atteint par un petit escalier. Trouve le **couloir** du côté est — son
plafond est bien plus bas que celui du hall — et va jusqu'aux **drapeaux** à
son extrémité. En chemin, tu changes de salle sans t'en apercevoir. Fais
ensuite demi-tour et retourne vers l'ouest : le hall derrière toi n'est pas
celui que tu as quitté.

## Plafonds bas

Une action **Définir la hauteur du plafond** (3D View) dans l'événement
**Create** d'un objet non solide abaisse le plafond au-dessus de chaque case
de la grille couverte par son sprite :

- **Hauteur** — en pixels de salle au-dessus du sol, comme Définir la hauteur
  du sol (`40` ici : l'œil est à 24 px, le couloir paraît donc bas).
- **Texture du plafond** — facultative (vide = la texture de plafond de la
  caméra).

Cet exemple utilise un seul objet, `obj_low` (invisible), posé sur chaque case
du couloir — et, dans la deuxième salle, sur chaque case du hall : le hall y
est *sous la galerie*, donc son plafond est bas. Un plafond n'est jamais plus
bas que le sol plus l'œil plus 4 px, on peut donc toujours se tenir dans une
case ; là où un plafond plus bas commence, on voit un **linteau** (la texture
de mur qui descend).

La hauteur du plafond se lit aussi : `raycast_ceiling_z` sur toute instance
mobile (le plafond au-dessus d'elle), à côté de `raycast_floor_z`.

## Le saut sans coupure

**Aller dans une salle sans transition** (3D View) a deux réglages :

- **Salle** — où aller.
- **Objet** — un *repère* : une instance de cet objet placée dans **chaque**
  salle, au même endroit de la géométrie que les deux salles partagent.

La caméra arrive dans l'autre salle à la même distance du repère, regardant
dans la même direction, à la même vitesse, avec les mêmes touches enfoncées et
la même hauteur de vue — et aucune image n'est jamais dessinée au départ de la
nouvelle salle. Contrairement à **Aller à la salle**, il n'y a ni fondu ni pause.

Ici, le repère est `obj_junction` (invisible), au milieu du couloir dans les
deux salles. Le saut est déclenché par un **portillon** invisible en travers
du couloir (`obj_gate_a`, dans la première salle) ; la deuxième salle a une
ligne de `obj_gate_b` en travers de son hall qui ramène en arrière. Garde un
portillon loin de l'endroit où l'*autre* salle te fait arriver — sinon tu
repartirais aussitôt.

Pour que l'illusion fonctionne, les deux salles doivent se ressembler autour
du repère aussi loin que le joueur peut voir : ici le couloir est identique, et
seul ce qui est derrière toi diffère.

## Structure du projet

| Objet | Rôle |
|---|---|
| `obj_person` | Le joueur et la caméra : commandes, réglages de la vue, les deux portillons, le drapeau |
| `obj_wall` | Murs solides |
| `obj_low` | Abaisse le plafond au-dessus de ses cases (Définir la hauteur du plafond) |
| `obj_step_8` … `obj_step_32` | L'escalier et la galerie (Définir la hauteur du sol) |
| `obj_junction` | Le repère, dans les deux salles au même endroit |
| `obj_gate_a`, `obj_gate_b` | Déclencheurs invisibles qui lancent Aller dans une salle sans transition |
| `obj_goal` | Les drapeaux au bout du couloir, dans les deux salles |

Les salles sont générées par `tools/gen_raycast_6_junction.py` : on peut les
reconstruire ou les modifier en un seul endroit (la suite de tests vérifie que
les fichiers correspondent).

## À essayer

- Mets la **Hauteur** de `obj_low` à `60` : un couloir plus haut, et un
  linteau plus petit à son entrée.
- Donne à `obj_low` une **Texture du plafond** (n'importe quel sprite) pour
  texturer les plafonds bas.
- Déplace `obj_junction` dans **une seule** salle : le saut te décale
  maintenant sur le côté. Les deux repères doivent être au même endroit.

## État de l'export

Les deux fonctions marchent sur ordinateur, dans l'export HTML5 et dans
l'export Kivy (Android/iOS). Personne n'a encore joué à cet exemple sur un
téléphone : si tu le fais, dis-nous ce que donne le saut.
