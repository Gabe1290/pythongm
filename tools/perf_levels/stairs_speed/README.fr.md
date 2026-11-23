# Niveau de test : vitesse de l'escalier

Un niveau à essayer à la main pour le test de vitesse de l'escalier
(`tests/test_raycast_stairs_render.py::test_a_staircase_costs_at_most_a_bit_more_than_a_flat_room`).
Il contient deux fois la salle que ce test mesure :

| Salle | Touche | Contenu |
|---|---|---|
| `salle_escalier` | **S** | 15 × 15 cases, un escalier de 5 cases de large (8, 16, 24, 32 px) jusqu'à une plateforme de 32 px |
| `salle_plate` | **F** | la même salle, sans les marches |

Ouvrez ce dossier avec **Fichier → Ouvrir un projet** puis lancez **Tester le jeu**. Les
flèches font avancer et tourner. Vous partez de l'endroit où le test place sa caméra,
face à l'escalier.

La ligne jaune en haut à gauche indique :

- **ms/image** : le temps de *travail* moyen par image sur les 30 dernières images (mise à
  jour et dessin, sans l'attente qui limite le jeu à 60 images par seconde). C'est ce
  chiffre qu'il faut comparer entre les deux salles : le test exige que l'escalier coûte
  au plus 1,6 × la salle plate, plus 5 ms.
- **i/s** : images par seconde (60 au maximum).

Mesuré sur la machine de développement (Linux, sans écran) : environ 17 ms avec l'escalier,
environ 11 ms sans, soit ≈ 1,6 ×. Sur les machines de la CI GitHub, le test mesure environ 2 ×.

Le niveau est généré à partir de `samples/raycast_5` par `tools/gen_stairs_perf_level.py` ;
relancez ce script après une modification de l'exemple plutôt que de modifier ces fichiers
à la main.
