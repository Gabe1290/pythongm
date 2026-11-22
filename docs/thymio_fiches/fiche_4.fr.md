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
| 0 | Avant gauche loin | 4 | Avant droit loin |
| 1 | Avant gauche | 5 | Arrière gauche |
| 2 | **Avant centre** | 6 | Arrière droit |
| 3 | Avant droit | | |

Un capteur donne **0** quand il ne voit rien, et un nombre de plus en plus grand quand un obstacle s'approche (jusqu'à plus de 2000 au contact). Ils sont mis à jour **dix fois par seconde** : l'événement **Mise à jour de proximité** se déclenche à chaque mise à jour.

> INFO: dans cette pièce, l'arène est fermée par quatre murs et contient deux boîtes. Le robot part à gauche, tourné vers la droite.

## 2. S'arrêter devant l'obstacle

- [ ] Ajoute **Bouton central** : **Si bouton appuyé** (centre), puis **Avancer** (vitesse 40).
- [ ] Ajoute l'événement **Mise à jour de proximité** avec cette condition :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Si proximité** (Capteur = 2 - Avant centre, Comparaison = **>**, Seuil = **1000**) |
| 2 | `start_block` |
| 3 | **Arrêter les moteurs** |
| 4 | **Régler la LED du dessus** : rouge (32, 0, 0) |
| 5 | `end_block` |

- [ ] Teste : appuie sur la barre d'espace. Le robot s'arrête devant la première boîte et sa LED devient rouge.
- [ ] Remplace 1000 par 300, puis par 2000. Où s'arrête le robot dans chaque cas ? Avec lequel est-il le plus près de la boîte ?

> TIP: plus le seuil est grand, plus le robot s'arrête tard, donc près de l'obstacle. Avec un seuil trop grand, il est déjà entré dans l'obstacle quand il s'arrête : le robot virtuel n'est pas bloqué par les murs.

## 3. Éviter les obstacles

Le robot doit rouler sans jamais toucher un mur ni une boîte. Dans **Mise à jour de proximité**, mets, dans cet ordre :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Avancer** (vitesse 40) et **Régler la LED du dessus** vert (0, 32, 0) : par défaut, on avance |
| 2 | Si **Avant droit** > 250 : **Régler la vitesse des moteurs** (-30, 30) et LED orange (32, 16, 0) |
| 3 | Si **Avant gauche** > 250 : **Régler la vitesse des moteurs** (30, -30) et LED orange |
| 4 | Si **Avant centre** > 250 : **Régler la vitesse des moteurs** (30, -30) et LED orange |

- [ ] Teste. Le robot explore l'arène : vert quand la voie est libre, orange quand il tourne.

> INFO: l'ordre compte. Les actions s'exécutent de haut en bas, donc **la dernière** consigne donnée gagne : on avance par défaut, et les capteurs prennent la main quand ils voient quelque chose.

> DONE: ton robot évite les obstacles tout seul.

## Pour aller plus loin

- Pourquoi utilise-t-on trois capteurs et pas seulement celui du centre ? Teste avec un seul pour voir.
- Utilise les capteurs **arrière** (5 et 6) : fais que le robot s'arrête s'il recule contre un mur.
- Fais varier la couleur de la LED selon la distance (rouge, orange, vert) avec trois seuils différents.
