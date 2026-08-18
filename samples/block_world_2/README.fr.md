# Block World — Terrain Infini

Un monde en voxels sans limites, construit sur la génération procédurale
de terrain de l'extension **Block World** (Tier 7e,
`docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md`). Il n'y a aucune frontière
sur la carte — marchez dans n'importe quelle direction et des collines
vallonnées d'herbe et de terre continuent de se générer autour de vous,
indéfiniment.

**Le but :** il n'y en a pas. C'est un bac à sable, pas un niveau —
marchez, creusez, construisez, et regardez votre score de **Distance**
(affiché en haut à gauche via l'affichage du score) augmenter à mesure
que vous vous éloignez de votre point de départ. Revenez près de votre
point de départ et le terrain y est exactement le même que lorsque vous
l'avez quitté — rien n'est régénéré une fois qu'il a été visité.

## Contrôles

| | |
|---|---|
| `W` `A` `S` `D` | Se déplacer (nord/sud/ouest/est — voir la remarque ci-dessous) |
| Flèche gauche / droite | Tourner pour regarder à gauche/droite |
| Flèche haut / bas | Regarder en haut/en bas |
| `Espace` | Casser le bloc visé |
| `Shift` | Placer un bloc depuis votre barre d'objets |
| `Q` / `E` | Faire défiler la sélection de votre barre d'objets |

**Le déplacement suit la direction de la carte, pas celle du regard** —
la même simplification délibérée que le guide de `block_world_1`
explique en détail.

## Ce que ça démontre

- **Un terrain procédural, pas un monde construit à la main ou chargé.**
  L'événement `create` de la salle appelle `enable_block_world_view` avec
  « Generate Terrain » activé et une « Seed » (graine) fixe — aucune
  action `load_block_world` nulle part dans ce projet. Chaque colline que
  vous voyez a été calculée à la volée à partir de ce seul nombre, au
  moment où vous vous en êtes suffisamment approché pour la voir.
- **Un monde sans coût mémoire pour ce que vous n'avez pas touché.**
  Éloignez-vous et le terrain derrière vous est discrètement oublié (il
  n'est pas perdu — voir ci-dessous) ; revenez et il se régénère à
  l'identique, car c'est une pure fonction de la graine et de votre
  position, pas quelque chose de stocké.
- **Creuser et construire fonctionnent exactement comme dans
  `block_world_1`.** Cassez un bloc dans le flanc d'une colline générée,
  ou placez-en un — cette modification précise EST mémorisée à partir de
  ce moment (même pour une colline loin derrière vous qui serait plus
  tard « oubliée » puis régénérée : votre modification réapparaît
  correctement, seules les parties non modifiées autour d'elle sont
  régénérées à neuf).

## État du moteur

**Le bureau (desktop), le HTML5 et Kivy (export Android/application de
bureau) génèrent tous un vrai terrain.** Une différence entre les
cibles, délibérée et documentée dans
`docs/BLOCK_WORLD_INFINITE_TERRAIN_PLAN.md` : seule la version bureau
oublie le terrain lointain non modifié pour limiter la mémoire lors
d'une longue session de jeu — les exports HTML5/Kivy conservent tout ce
qu'ils ont généré pendant toute la durée de cet onglet de navigateur ou
de cette session d'application, ce qui est volontairement considéré
comme acceptable pour la durée réelle d'une session de jeu typique. Rien
concernant le terrain lui-même, ni ce que vous pouvez creuser et
construire, ne diffère entre les cibles.
