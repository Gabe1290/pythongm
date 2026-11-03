# Fiche 4 : Les capteurs de proximité

**Exemple à ouvrir :** Thymio — Activités : les murs  ·  **Durée :** 30 minutes

## Ce que tu vas apprendre

- lire les capteurs de proximité du robot ;
- arrêter le robot devant un obstacle ;
- éviter les obstacles sans les toucher.

## 1. Les capteurs

Le robot a **7 capteurs** infrarouges : 5 à l'avant et 2 à l'arrière.

| N° | Capteur | N° | Capteur |
|---|---|---|---|
| 0 | Front Left Far | 4 | Front Right Far |
| 1 | Front Left | 5 | Back Left |
| 2 | **Front Center** | 6 | Back Right |
| 3 | Front Right | | |

Un capteur donne **0** quand il ne voit rien, et un nombre de plus en plus grand quand un obstacle s'approche (jusqu'à plus de 2000 au contact). Ils sont mis à jour **dix fois par seconde** : l'événement **Proximity Sensors Update** se déclenche à chaque mise à jour.

> INFO: dans cette pièce, l'arène est fermée par quatre murs et contient deux boîtes. Le robot part à gauche, tourné vers la droite.

## 2. S'arrêter devant l'obstacle

- [ ] Ajoute **Button Center** : **If Button Pressed** (center), puis **Move Forward** (speed 40).
- [ ] Ajoute l'événement **Proximity Sensors Update** avec cette condition :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **If Proximity Detected** (sensor_index = 2 - Front Center, comparison = **>**, threshold = **1000**) |
| 2 | `start_block` |
| 3 | **Stop Motors** |
| 4 | **Set Top LED Color** : rouge (32, 0, 0) |
| 5 | `end_block` |

- [ ] Teste : appuie sur la barre d'espace. Le robot s'arrête devant la première boîte et sa LED devient rouge.
- [ ] Remplace 1000 par 300, puis par 2000. Où s'arrête le robot dans chaque cas ? Avec lequel est-il le plus près de la boîte ?

> TIP: plus le seuil est grand, plus le robot s'arrête tard, donc près de l'obstacle. Avec un seuil trop grand, il est déjà entré dans l'obstacle quand il s'arrête : le robot virtuel n'est pas bloqué par les murs.

## 3. Éviter les obstacles

Le robot doit rouler sans jamais toucher un mur ni une boîte. Dans **Proximity Sensors Update**, mets, dans cet ordre :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Move Forward** (speed 40) et **Set Top LED Color** vert (0, 32, 0) : par défaut, on avance |
| 2 | Si **Front Right** > 250 : **Set Motor Speeds** (-30, 30) et LED orange (32, 16, 0) |
| 3 | Si **Front Left** > 250 : **Set Motor Speeds** (30, -30) et LED orange |
| 4 | Si **Front Center** > 250 : **Set Motor Speeds** (30, -30) et LED orange |

- [ ] Teste. Le robot explore l'arène : vert quand la voie est libre, orange quand il tourne.

> INFO: l'ordre compte. Les actions s'exécutent de haut en bas, donc **la dernière** consigne donnée gagne : on avance par défaut, et les capteurs prennent la main quand ils voient quelque chose.

> DONE: ton robot évite les obstacles tout seul.

## Pour aller plus loin

- Pourquoi utilise-t-on trois capteurs et pas seulement celui du centre ? Teste avec un seul pour voir.
- Utilise les capteurs **arrière** (5 et 6) : fais que le robot s'arrête s'il recule contre un mur.
- Fais varier la couleur de la LED selon la distance (rouge, orange, vert) avec trois seuils différents.
