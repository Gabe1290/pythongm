# Niveau de test : base aux nombreuses hauteurs

Un niveau de test 2,5D original pour le moteur d'escaliers, plus grand et plus haut que
`stairs_speed` : une grille de 32 × 24 cases avec **17 hauteurs de sol**, du sol (0 px)
à 128 px par paliers de 8 px. Ce n'est la copie d'aucune carte d'un jeu existant.

Ouvrez ce dossier avec **Fichier → Ouvrir un projet** puis lancez **Tester le jeu**. Les
flèches font avancer et tourner. On peut monter 12 px d'un coup : chaque marche de 8 px
se franchit, et on peut sauter de n'importe quelle hauteur.

## Ce qu'il contient

- **Hall d'entrée** (point de départ, au sol), avec des socles à 24, 48, 72 et 96 px.
  Ils sont décoratifs : trop hauts pour être escaladés.
- **Grand escalier** : 10 marches de 8 px jusqu'à un **balcon** à 80 px. Retournez-vous
  en haut pour regarder le hall en contrebas.
- **Tour** : un chemin en marches le long du bord nord du balcon jusqu'à un
  **belvédère à 128 px**, le niveau le plus haut.
- **Couloir en zigzag** : il descend du balcon (72 → 32 px) vers une cour avec des
  piliers et une plateforme surélevée (56 px).
- **Salle de la fosse** : une passerelle à 32 px autour d'un bassin de liquide vert
  (8 px). Des marches permettent d'en sortir.
- Des monstres et des drapeaux se tiennent à différentes hauteurs. Ils ne bougent pas
  et ne font pas de dégâts.

## La ligne jaune

- **ms/image** : temps de *travail* moyen par image sur les 30 dernières images (mise à
  jour et dessin, sans l'attente qui limite le jeu à 60 images par seconde).
- **i/s** : images par seconde (60 au maximum).
- **hauteur** : la hauteur du sol sous vos pieds.

La petite carte en haut à droite montre les murs et les monstres (en rouge).

Mesuré sur la machine de développement (Linux, sans écran) : 21 à 30 ms par image (34 à
48 images par seconde), surtout dans la salle de la fosse et dans l'escalier ; le niveau
`stairs_speed` coûte environ 17 ms.

## Carte

`#` mur, `.` sol, `1`–`9` = 8–72 px, `a`–`g` = 80–128 px, `n` = liquide (8 px).
Le nord est en haut.

```
################################
#....................abcdefgggg#
#....................aaaaaaaggg#
#..33..66............aaaaaaaaaa#
#..33..66..123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..........123456789aaaaaaaaaaa#
#..99..cc............aaaaaaaaaa#
#..99..cc............aaaaaaaaaa#
#....................aaaaaaaaaa#
#....................aaaaaaaaaa#
####11####################99####
####22####################88####
####33####################77####
#4444444444###55555555555566####
#4444444444###55555555555566####
#44nn3nnn44###55################
#44nn2nnn44###55555555555555555#
#44nnnnnn44###5555#55#555555555#
#44nnnnnn4444455555555555777775#
#44nnnnnn444445555#555556777775#
#4444444444#####555555555777775#
################################
```

Le niveau est généré à partir de `samples/raycast_5` par `tools/gen_heights_perf_level.py` ;
relancez ce script après une modification de l'exemple plutôt que de modifier ces
fichiers à la main. Ouvrir le niveau dans l'EDI puis l'enregistrer modifie ces fichiers :
rétablissez-les avec `git checkout -- tools/perf_levels/`.
