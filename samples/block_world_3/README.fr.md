# Monde de Blocs — Artisanat

Un petit monde en voxels construit sur l'extension **Monde de Blocs**
(`extensions/block_world/`), qui met en avant ses actions d'artisanat du
Tier 8 (`docs/BLOCK_WORLD_CRAFTING_PLAN.md`) : « Définir une recette de
fabrication » et « Fabriquer un objet ».

**Le but :** extraire l'argile du filon dans le mur est, la transformer en
briques, puis en apporter au moins 4 à la balise dorée, plus près du
centre de la salle. Il suffit de s'y rendre avec assez de briques dans
l'inventaire pour gagner — aucun casse-tête de construction, aucune visée
précise. Atteindre la balise sans assez de briques ne fait rien ; il faut
continuer à extraire et à fabriquer. Le filon fait 4 blocs de large : il
faut donc se déplacer latéralement (`W`/`S`) le long du mur pour atteindre
chacun d'eux — un appui sur `Espace` ne casse que le bloc directement visé.

## Contrôles

|  | |
|---|---|
| `W` `A` `S` `D` | Se déplacer (nord/sud/ouest/est — direction de la carte, pas du regard) |
| Flèche gauche / droite | Tourner le regard à gauche/droite |
| Flèche haut / bas | Regarder vers le haut/bas |
| `Espace` | Casser le bloc visé (extraire l'argile du filon dans le mur) |
| `C` | Fabriquer : transforme 4 argiles de l'inventaire en 4 briques, si vous en avez assez |
| `H` | Afficher ou masquer les commandes (affichées au démarrage) |

**Le déplacement suit la carte, pas le regard** — même convention que
`block_world_1`/`block_world_2` : appuyer sur `D` déplace toujours vers
l'est, quelle que soit la direction du regard de la caméra.

## Ce que ça montre

- **« Définir une recette de fabrication »**, appelée une fois dans
  l'événement Création, juste après « Activer la vue Block World » :
  4 `clay` (argile) → 4 `brick` (brique), une recette à un seul
  ingrédient (l'exemple le plus simple donné par le plan lui-même).
- **« Fabriquer un objet »**, liée à une touche (`C`) : tente la recette
  enregistrée à partir de l'inventaire du joueur (le paramètre
  **Inventaire** de « Activer la vue Block World » est activé, le même
  mécanisme du Tier 7c que « Casser un bloc »/« Poser un bloc »
  utilisent déjà) — tout ou rien : appuyer sur `C` avec moins de 4
  argiles ne fait rien plutôt que de n'en consommer qu'une partie.
- **Le HUD d'inventaire intégré** (« Afficher le HUD Block World ») —
  aucune interface d'artisanat sur mesure n'est nécessaire ; le nombre de
  briques fabriquées apparaît dans la barre d'accès rapide comme n'importe
  quel autre type de bloc, puisque les résultats d'artisanat sont de
  simples types de blocs, pas une notion d'« objet » séparée.
- **Un monde chargé depuis des données** : `blocks/room0.json` (généré
  par le script `tools/gen_block_world_3_room.py`, versionné dans le
  dépôt) est chargé par une action « Charger un monde Block World » dans
  l'événement Démarrage du jeu du joueur, le même schéma que
  `block_world_1`.

## Pourquoi le but ne demande pas de construire quoi que ce soit

Le README de `block_world_1` explique pourquoi une conception antérieure,
demandant au joueur de *construire* un pont ou un escalier pour atteindre
un but, a été abandonnée — elle exigeait une combinaison délicate d'angle
de vue et de distance pour poser les blocs de façon fiable. Cet
échantillon évite entièrement ce risque : la condition de victoire se
résume à « avez-vous fabriqué assez de briques, et êtes-vous au bon
endroit » — les deux vérifiés en lisant l'inventaire et la position du
joueur, sans aucune précision de placement nulle part.

## Pourquoi l'argile est intégrée au mur plutôt qu'un tas au sol

Un vrai test de jeu sur un `GameRunner` réel (pas seulement une lecture du
code) a révélé deux erreurs des deux premières versions de ce monde,
utiles à connaître pour construire son propre niveau Monde de Blocs :

1. Un tas d'argile posé au sol, haut d'une seule couche, n'était jamais
   réellement miné en jeu normal — le moteur traite tout obstacle d'une
   seule couche comme une **marche escaladable**
   (`state.DEFAULT_MAX_STEP_UP`), donc marcher vers lui faisait
   automatiquement monter le joueur dessus au lieu de le bloquer comme un
   vrai obstacle. Une fois monté dessus, le rayon de visée au niveau
   passait par-dessus sans le toucher.
2. Empiler le tas sur deux couches corrigeait cela (bien inescaladable),
   mais alors seule la couche du BAS était minable en visée de niveau —
   la hauteur de repos d'un corps au-dessus d'un bloc de sol est UNE
   couche au-dessus du sol, donc un rayon en visée de niveau depuis le
   sol vise la couche AU-DESSUS de celle qu'on pourrait attendre, pas la
   toute première.

Intégrer le filon dans la couche du milieu du mur (les couches au-dessus
et en dessous restant du mur ordinaire) évite les deux problèmes d'un
coup : le mur reste totalement inescaladable (on n'est donc jamais dirigé
dessus ou par-dessus), et son argile se trouve exactement à la hauteur
qu'atteint une visée de niveau depuis le sol — la même interaction
« s'approcher d'un mur, viser au niveau, `Espace` » que le mur
d'enceinte de `block_world_1` utilise déjà, sans nouvelle interaction à
maîtriser.

## État du moteur

L'artisanat est entièrement porté sur les trois cibles de Monde de Blocs
— ordinateur (pygame), HTML5 et Kivy (export Android/application de
bureau) — avec un test de parité entre moteurs
(`tests/test_block_world_crafting_export_parity.py`) qui garantit un
comportement identique entre l'ordinateur et Kivy.
