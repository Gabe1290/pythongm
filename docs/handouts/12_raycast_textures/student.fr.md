# PyGameMaker — Tutoriel 12 : 2.5D, textures, ciel et sol

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > 2.5D : Textures, ciel et sol** (4 pages, environ 20 à 25 minutes). Il te faut ton projet terminé du Tutoriel 11 (ou la copie de ton enseignant·e). Cette leçon n'est pas dans l'édition débutant. Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

La même salle à la première personne, mais habillée : des murs en briques, un ciel qui glisse quand tu tournes, et un sol dallé. Rien ne change dans la façon de jouer ; seule l'apparence change.

## Phase 1 : Des murs texturés

- [ ] **1.** Crée un sprite `spr_wall_texture`, **64×64** : un fond rouge brique avec des joints plus clairs (une ligne horizontale tous les 16 pixels, et de courtes lignes verticales décalées d'une demi-brique une rangée sur deux). Ou importe une image carrée.
- [ ] **2.** Dans **Quand créé** de `obj_player`, sur *Activer la vue Raycast*, règle **Wall Texture** sur `spr_wall_texture`.

> DONE: **Tu dois voir :** appuie sur **F5**. Chaque mur montre des briques. Les murs tournés à l'opposé de la lumière sont plus sombres. Les briques grossissent quand tu t'approches.

## Phase 2 : Ciel et sol

- [ ] **3.** Crée un sprite `spr_sky`, **256×64** (large et bas, comme une bande de panorama) : bleu ciel avec des nuages, un soleil ou des montagnes.
- [ ] **4.** Crée un sprite `spr_floor`, **32×32**, la taille d'une case de la grille : un damier, des dalles ou des planches.
- [ ] **5.** Sur *Activer la vue Raycast*, règle **Sky Texture** sur `spr_sky` et **Floor Texture** sur `spr_floor`.
- [ ] **6.** Facultatif : pas de ciel ? Laisse **Sky Texture** vide et règle **Ceiling Texture** à la place (elle n'est utilisée que s'il n'y a pas de ciel).

> DONE: **Tu dois voir :** appuie sur **F5**. Le ciel glisse latéralement quand tu tournes, mais ne grossit pas quand tu marches. Les dalles du sol rétrécissent vers l'horizon et rejoignent proprement les murs.

## Phase 3 : Régler l'apparence

- [ ] **7.** Vide **Sky Texture** et relance : tu retrouves la couleur unie du plafond.
- [ ] **8.** Mets **Textured Walls** sur non : des murs de couleur unie même si une Wall Texture est définie.
- [ ] **9.** Essaie **Columns** (320 par défaut) et **Floor Detail** (4 par défaut) avec d'autres valeurs. Monte Floor Detail à 6 ou 8 pour la vitesse ; baisse Columns si c'est encore lent.

> DONE: **Tu dois voir :** les couleurs de secours quand une texture est vide, et une image plus grossière mais plus rapide avec un Floor Detail plus haut ou moins de Columns.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Les murs sont toujours de couleur unie | Wall Texture est vide ou mal écrite, ou **Textured Walls** est désactivé | Tape le nom exact du sprite ; active Textured Walls |
| Le ciel n'apparaît pas | Sky Texture est vide ou le nom est faux | Règle-la exactement sur `spr_sky` |
| Le sol est flou | La dalle n'est pas de 32×32, ou Floor Detail est élevé | Utilise une dalle de 32×32 ; essaie Floor Detail 4 |
| Les briques paraissent étirées | L'image n'est pas carrée | Utilise une image carrée comme 64×64 |
| La texture de plafond ne fait rien | Une Sky Texture est définie (le ciel l'emporte) | Vide Sky Texture pour voir le plafond |
| Le jeu est lent | Floor Detail est bas ou Columns est élevé | Monte Floor Detail, baisse Columns |
| Le ciel saute quand je tourne | L'image est trop étroite | Utilise une image large comme 256×64 |
| Le nom de la texture a une faute | Les noms doivent correspondre exactement | Copie le nom du sprite |

## Défis

- **Essaie (5 minutes) :** fabrique un second aspect de mur (pierre moussue) et change de texture en modifiant un seul nom.
- **Va plus loin :** conçois une salle intérieure sans ciel avec une **Ceiling Texture** en planches de bois.
- **Invente :** une grotte sombre avec une couleur de plafond presque noire et une Render Distance courte (5).

## Vocabulaire

| Terme | Ce que cela veut dire |
| Texture | Un sprite ordinaire utilisé pour recouvrir un mur, le sol ou le plafond |
| Panorama | Une image large qui t'entoure (le ciel) |
| Dalle | Une petite image répétée sur une zone (le sol) |
| Couleur de secours | La couleur unie utilisée quand une texture est vide |
| Floor Detail | La finesse du sol ; plus haut est plus rapide mais plus pixellisé |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Que fait le ciel quand tu tournes, et que ne fait-il pas quand tu marches ?
2. Que deviennent les murs si tu laisses **Wall Texture** vide ?
3. Quels deux réglages échangent du détail contre de la vitesse ?

## Mes notes

[[notes:10]]
