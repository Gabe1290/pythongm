# Thymio dans le simulateur : fiches d'activités

Huit fiches progressives pour apprendre à programmer le robot **Thymio** avec le simulateur de PyGameMaker, sans robot réel. Elles suivent la même progression que les fiches Thymio classiques (boutons, couleurs, moteurs, capteurs, variables, minuteur, défis), mais ne contiennent **que ce que le simulateur sait faire**.

## Avant de commencer (une seule fois)

1. Menu **Outils → Préférences → Extensions**, section Thymio : coche **Afficher l'onglet Thymio** puis **redémarre** PyGameMaker.
2. Dans l'onglet **Bienvenue**, ouvre l'exemple indiqué en tête de chaque fiche :

| Exemple | Contenu | Fiches |
|---|---|---|
| **Thymio — Activités : arène libre** | une pièce vide, un robot | 1, 2, 3, 6, 7, 8 |
| **Thymio — Activités : les murs** | une arène fermée avec deux boîtes | 4, 8 |
| **Thymio — Activités : le sol et le ruban** | un sol blanc, un ruban noir, un bord de table | 5, 8 |

3. Ouvre l'objet **thymio_1** : son onglet **Thymio** est l'endroit où tu écris le programme. Le bouton **+ Événement** ajoute un événement ; un clic droit sur l'événement → **Add Action** ajoute une action, rangée par catégorie (**Leds**, **Motors**, **Sensors**, **Conditions**, **Variables**, **Timing**).
4. Lance avec **Test Game** (F5). Les boutons du robot se commandent au clavier : **↑ ↓ ← →** et **barre d'espace** (bouton du centre), ou en cliquant sur les boutons dessinés sur le robot.

> INFO: les noms des événements et des actions restent en anglais dans l'éditeur (par exemple **Button Forward**, **Set Top LED Color**). Les fiches les écrivent exactement comme tu les vois à l'écran.

## Ce que le simulateur fait… et ne fait pas

| Oui | Non (donc absent des fiches) |
|---|---|
| boutons, LED du dessus, du dessous et du cercle | sons (aucun son n'est joué) |
| moteurs, rotation | modes préprogrammés (comportements Thymio couleur, explorateur…) |
| 7 capteurs de proximité, 2 capteurs de sol | accéléromètre, tape, microphone, télécommande |
| variables, conditions, 2 minuteurs | communication entre robots |

À savoir :

- **Le simulateur est rapide.** La vitesse 200 du vrai robot fait courir le robot virtuel presque 12 fois plus vite que la réalité. Dans les fiches, on utilise des vitesses de **20 à 50**.
- **Un mur ne bloque pas le robot virtuel** : il passe à travers. C'est donc à ton programme de le faire s'arrêter, avec les capteurs.
- **Un événement de bouton se déclenche à l'appui et au relâchement**, comme sur le vrai robot. On les distingue avec les conditions **If Button Pressed** / **If Button Released**.
- Une condition (« si… ») s'applique à l'action ou au bloc `start_block … end_block` qui la suit.

## Les fiches

| N° | Titre | Notion |
|---|---|---|
| 1 | Découvrir le simulateur | boutons, événements, LED |
| 2 | Couleurs | mélange rouge / vert / bleu, cercle de LED |
| 3 | Les moteurs | avancer, reculer, tourner, s'arrêter |
| 4 | Les capteurs de proximité | s'arrêter devant un obstacle, l'éviter |
| 5 | Les capteurs de sol | détecter une ligne noire, un bord |
| 6 | Variables et conditions | compter, comparer |
| 7 | Le minuteur | clignoter, tracer un carré |
| 8 | Défis | combiner tout ce qui précède |

Le corrigé de l'enseignant·e (programmes de référence, valeurs mesurées) est dans [corrige.fr.md](corrige.fr.md). Tous ces programmes sont vérifiés automatiquement dans le moteur (`tests/test_thymio_fiches.py`).

*Progression inspirée des fiches Thymio du DIP Genève ; textes et exercices écrits pour le simulateur PyGameMaker.*
