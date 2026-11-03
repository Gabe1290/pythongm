# Corrigé de l'enseignant·e : fiches Thymio (simulateur)

Tous les programmes ci-dessous existent sous forme de listes d'actions dans `tools/thymio_fiches_solutions.py` et sont **exécutés dans le moteur** par `tests/test_thymio_fiches.py` (touches simulées, valeurs mesurées). Les nombres cités viennent de ces mesures.

Les conditions s'appliquent à l'action ou au bloc `start_block … end_block` qui les suit.

## Valeurs de référence du simulateur

| Grandeur | Valeur mesurée |
|---|---|
| Vitesse 30, en ligne droite | 1,2 pixel par image, soit 72 pixels par seconde |
| Rotation sur place (-30 / 30) | environ 1,45° par image : un quart de tour en 62 images (≈ 1,04 s) |
| Capteur de proximité sans obstacle | 0 |
| Capteur de proximité au contact d'un mur | environ 2300 |
| Capteur de sol, sol blanc / sol gris moyen / ruban noir | environ 1000 / 400 / 0 |
| Largeur du robot | 110 pixels |
| Rafraîchissement des capteurs | 10 fois par seconde (toutes les 6 images) |

## Fiche 1

| Événement | Actions |
|---|---|
| Button Forward | Set Top LED Color (0, 32, 0) |
| Button Backward | Set Top LED Color (32, 0, 0) |
| Button Left | Set Bottom Left LED (0, 0, 32) |
| Button Right | Set Bottom Right LED (0, 0, 32) |
| Button Center | Turn Off All LEDs |

Réponses : le bouton du centre éteint tout. Les deux LED du bas sont allumées ensemble si l'on a appuyé sur ← puis sur → (elles ne s'éteignent pas toutes seules).

## Fiche 2

Couleurs du tableau : (32, 32, 0) jaune ; (32, 16, 0) orange ; (32, 0, 32) magenta ; (0, 32, 32) cyan. Cercle : **Set All Circle LEDs** avec 32, 0, 32, 0, 32, 0, 32, 0 allume une LED sur deux.
Pour aller plus loin : 33 × 33 × 33 = 35 937 couleurs possibles. Rose : (32, 8, 16) environ ; vert clair : (8, 32, 8) environ.

## Fiche 3

| Événement | Actions (dans cet ordre) |
|---|---|
| Button Forward | If Button Pressed (forward) → Move Forward 30 ; If Button Released (forward) → Stop Motors |
| Button Backward | idem avec Move Backward 30 |
| Button Left | If Button Pressed (left) → Set Motor Speeds (-30, 30) ; If Button Released (left) → Stop Motors |
| Button Right | idem avec Set Motor Speeds (30, -30) |

Mesures : 60 images d'appui avancent le robot de 72 pixels (±3) ; il s'arrête au relâchement ; 62 images sur ← donnent -90° (±3), le quart de tour indiqué sur la fiche. À la vitesse 50, le quart de tour est atteint plus vite (≈ 37 images) : la vitesse change la durée du quart de tour, pas l'angle.

## Fiche 4

Arrêt : **Button Center** → If Button Pressed (center) → Move Forward 40 ; **Proximity Sensors Update** → If Proximity Detected (Front Center > 1000) → Stop Motors + LED rouge. Le robot s'arrête vers x = 371, soit une quinzaine de pixels devant la boîte (qui commence à x = 440).
Évitement : Move Forward 40 + LED verte, puis trois conditions (Front Right > 250, Front Left > 250, Front Center > 250) qui font tourner le robot (LED orange). Sur 3000 images, le centre du robot reste à plus de 40 pixels de tout obstacle (sa demi-largeur est 55 : il frôle sans traverser).
Remarque didactique : le capteur du centre ne voit pas un mur qui arrive en biais ; c'est pourquoi la solution utilise les trois capteurs de l'avant.

## Fiche 5

Button Center → If Button Pressed (center) → Move Forward 40 ; **Ground Sensors Update** → If Ground is Dark (0 - Left, seuil 300) → Stop Motors + LED rouge. Le robot s'arrête vers x = 419. Le capteur est 40 pixels devant le centre du robot et le ruban commence à x = 450 : le robot s'arrête donc quelques pixels après que le capteur a touché le bord, car les capteurs ne sont lus que 10 fois par seconde.

## Fiche 6

Button Forward : If Button Pressed → Increase Variable (compteur, 1) ; If Variable (compteur >= 3) → LED verte ; If Variable (compteur < 3) → LED rouge. Button Backward : même chose avec Decrease Variable. Button Center : If Button Pressed → Set Variable (compteur = 0) → LED rouge.
Réponse : la LED passe au vert au **troisième** appui. Le compteur n'augmente qu'une fois car la condition If Button Pressed est fausse au relâchement. Descendre sous 0 est possible (la variable devient négative, la LED reste rouge).

## Fiche 7

Clignotant : Button Center → If Button Pressed (center) → bloc [Set Variable (etat = 0), Set Timer Period (0, 500)] ; Timer 0 → Increase Variable (etat, 1) ; If Variable (etat == 1) → LED bleue ; If Variable (etat == 2) → bloc [Turn Off All LEDs, Set Variable (etat = 0)]. Le premier allumage a lieu après 500 ms (30 images) ; 250 ms fait clignoter deux fois plus vite.
Carré : Button Center → même démarrage avec la période 1040 ; Timer 0 → Increase Variable, If etat == 1 → Move Forward 30 ; If etat == 2 → bloc [Set Motor Speeds (-30, 30), etat = 0]. Mesuré : carré de 75 px de côté, tournant vers la gauche (le premier mouvement a lieu 1 s après l'appui).
Pour aller plus loin : carré vers la droite → (30, -30). Triangle : rotation de 120° ≈ 83 images ≈ 1,39 s de rotation (la période unique de 1040 ms ne convient plus : il faut deux durées, donc deux minuteurs ou plus d'états).

## Fiche 8

Les sons sortent du haut-parleur de l'ordinateur (touche **M** : muet). Une durée est en 1/60 s : 30 = 0,5 s, -1 = jusqu'à **Stop Sound**.

| Partie | Programme | Mesuré |
|---|---|---|
| 1. Notes | Button Forward / Left / Right / Backward → If Button Pressed → Play Tone 262 / 330 / 392 / 523, durée 30 | une note par appui ; sans le If Button Pressed, la note est jouée deux fois (appui et relâchement) |
| 2. Note tenue | Button Forward → If Pressed → Play Tone (440, -1) ; If Released → Stop Sound | le son dure autant que l'appui |
| 3. Mélodie | Button Center → bloc [Set Variable (note = 0), Play Tone (262, 20)] ; Sound Finished → Increase Variable (note), puis If note == 1 → 330 (20), == 2 → 392 (20), == 3 → 523 (40) | do, mi, sol, do aigu ; après la 4ᵉ note, note vaut 4 et plus rien ne se déclenche |
| 4. Sons du robot | Play System Sound (0 à 7) sur les boutons | chaque son est une courte mélodie (≤ 40 images) ; la durée de la mélodie est celle de Sound Finished |
| 5. Sirène | Button Center → bloc [etat = 0, période 500] ; Timer 0 → Increase Variable, etat == 1 → Play Tone (440, 30) + LED rouge ; etat == 2 → Play Tone (880, 30) + LED bleue + etat = 0 | alternance 440 / 880 Hz avec la lumière ; arrêt : période 0 + Stop Sound |
| 6. Radar | programme de la fiche 3 + Proximity Sensors Update : Front Center > 250 → Play Tone (800, 4) ; > 1000 → Play Tone (1500, 4) | silence de loin, 800 Hz puis 1500 Hz en approchant d'une boîte |

Réponses : quatre Play Tone à la suite → seul le dernier s'entend (chaque note remplace la précédente). « Au clair de la lune » demande onze notes donc dix If Variable ; une variable qui sert d'indice n'existe pas dans l'éditeur Thymio, donc il n'y a pas de raccourci.
Remarque : les sons du robot sont synthétisés (ils ressemblent aux originaux, ils ne les reproduisent pas). Le volume dépend de l'ordinateur ; en classe, prévoir des casques ou la touche M.

## Fiche 9

| Défi | Solution (résumé) |
|---|---|
| 1. Feu | Button Center démarre (etat = 0, période 1000 ms) ; Timer 0, etat de 1 à 3 : vert, orange, rouge (etat remis à 0 au 3). Le premier vert vient 1 s après l'appui. Pour arrêter (Button Backward) : **Set Timer Period** (période = 0) **et** Turn Off All LEDs ; éteindre seulement les LED ne suffit pas, le minuteur continue. |
| 2. Alarme | Programme de la fiche 3 + Proximity Sensors Update : LED verte ; si Front Center > 250, orange ; si > 1000, rouge. **Le rouge doit venir en dernier** car la dernière consigne l'emporte. Mesuré : vert, orange, rouge dans cet ordre en approchant de la boîte. |
| 3. Sablier | Button Center démarre ; Timer 0 à 1000 ms, etat de 1 à 5 : Set Circle LED 0, 2, 4, 6 ; à 5, Turn Off All LEDs et etat = 0. Mesuré : 0, 1, 2, 3, 4 LED allumées puis 0. Version huit LED : huit conditions (une par LED, etat de 1 à 8), puis Turn Off All LEDs et etat remis à 0 à la neuvième seconde. |
| 4. Arrêt avant la ligne | Programme de la fiche 3 + Ground Sensors Update (If Ground is Dark → Stop Motors + LED rouge). **Problème (mesuré) :** le robot s'arrête sur le ruban ; quand on appuie sur la flèche du bas, il recule de quelques pixels puis s'arrête à nouveau, car son capteur voit encore le noir à la mise à jour suivante et le programme ordonne **Stop Motors**. Il faut relâcher et rappuyer. Solution : ne tester le sol que lorsque la flèche du haut est enfoncée (une variable `avance` mise à 1 à l'appui sur la flèche du haut et à 0 au relâchement). |
| 5. Projet libre | Évaluer : idée claire, événements listés avant de construire, programme qui fonctionne, au moins une variable ou un minuteur. |

*Les défis 1 à 3 sont vérifiés dans le moteur par des tests ; le comportement décrit pour le défi 4 a été mesuré à part (mais n'est pas dans la suite de tests) ; le défi 5 est un projet libre.*
