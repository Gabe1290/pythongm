# Fiche 5 : Les capteurs de sol

**Exemple à ouvrir :** Thymio — Activités : le sol et le ruban  ·  **Durée :** 25 minutes

## Ce que tu vas apprendre

- lire les deux capteurs de sol ;
- distinguer un sol clair d'un sol sombre ;
- arrêter le robot sur une ligne noire.

## 1. Les capteurs sous le robot

Sous l'avant du robot, deux capteurs regardent le **sol** : **0 – Left** et **1 – Right**. Chacun donne un nombre :

| Le sol est… | Valeur lue |
|---|---|
| blanc ou clair | grande (environ **900 à 1000**) |
| noir | petite (près de **0**) |

L'événement **Ground Sensors Update** se déclenche dix fois par seconde.

> INFO: dans la pièce, un **ruban noir** traverse le sol et le **bord de la table** (noir lui aussi) est à droite. Le robot part à gauche, tourné vers la droite.

## 2. Voir les valeurs

- [ ] Avec **Button Forward** (If Button Pressed, **Move Forward** vitesse 40, comme à la fiche 3), fais avancer le robot.
- [ ] Pour savoir quand le capteur voit du noir, ajoute **Ground Sensors Update** avec :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **If Ground is Dark** (sensor_index = 0 - Left, threshold = **300**) |
| 2 | **Set Top LED Color** : rouge (32, 0, 0) |

- [ ] Teste : la LED du dessus devient rouge quand le capteur gauche passe sur le ruban.

> TIP: **If Ground is Dark** est vrai quand la valeur lue est **plus petite** que le seuil. **If Ground is Light** est l'inverse.

## 3. Arrêt sur la ligne

- [ ] Remplace l'action de l'étape précédente par un bloc : `start_block`, **Stop Motors**, **Set Top LED Color** rouge, `end_block`.
- [ ] Teste : le robot s'arrête juste avant le ruban, au moment où son capteur le voit.
- [ ] Où est le robot par rapport au ruban quand il s'arrête ? Les capteurs sont **devant** le centre du robot, pas dessous.

> DONE: ton robot réagit à ce qu'il y a par terre. C'est ce qui permet de ne pas tomber d'une table.

## Pour aller plus loin

- Fais que le robot s'arrête aussi si c'est le capteur **droit** qui voit du noir.
- Ajoute **If Ground is Light** : la LED redevient verte quand le sol est clair.
- Fais reculer le robot (**Move Backward**) au lieu de s'arrêter : il fait alors des allers-retours devant le ruban ?
