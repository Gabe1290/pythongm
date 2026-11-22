# Fiche 7 : Le minuteur

**Exemple à ouvrir :** Thymio — Activités : arène libre  ·  **Durée :** 30 minutes

## Ce que tu vas apprendre

- faire agir le robot **à intervalles réguliers** ;
- faire clignoter une LED ;
- enchaîner des mouvements pour tracer un carré.

## 1. Le minuteur

Le robot possède deux minuteurs (0 et 1). On règle leur **période** en millisecondes (1000 ms = 1 s) avec **Régler la période de la minuterie**. À chaque fois que la période est écoulée, l'événement **Minuterie 0** (ou **Minuterie 1**) se déclenche.

- [ ] Ajoute l'événement **Bouton central** avec **Si bouton appuyé** (centre), puis **Régler la période de la minuterie** (Minuterie = 0, Période (ms) = **500**).
- [ ] Ajoute l'événement **Minuterie 0** avec **Régler la LED du dessus** bleu (0, 0, 32).
- [ ] Teste : appuie sur la barre d'espace. Au bout d'une demi-seconde, la LED devient bleue. Et ensuite ? Rien ne change : l'événement se répète, mais fait toujours la même chose.

## 2. Une LED qui clignote

Il faut que la LED soit allumée à un tick, éteinte au suivant. On le fait avec une variable **etat** qui compte les ticks.

- [ ] Dans **Bouton central**, ajoute aussi **Définir une variable** (etat = 0), juste après le **Si bouton appuyé** : un bloc `start_block` … `end_block` entoure les deux actions.
- [ ] Dans **Minuterie 0**, mets :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Augmenter une variable** (etat, 1) |
| 2 | **Si variable** (etat **==** 1), puis **Régler la LED du dessus** bleu |
| 3 | **Si variable** (etat **==** 2), puis un bloc `start_block` : **Éteindre les LED**, **Définir une variable** (etat = 0), `end_block` |

- [ ] Teste : après l'appui, la LED est allumée une demi-seconde, éteinte une demi-seconde, et ainsi de suite. Rappuie sur la barre d'espace : le clignotement repart de zéro.
- [ ] Change la période : 250, puis 1000. Que se passe-t-il ?

> INFO: **etat** vaut 1 (allumer), puis 2 (éteindre et revenir à 0). On « compte les temps » du motif.

## 3. Le carré

Pour tracer un carré, le robot **avance**, puis **tourne** d'un quart de tour, puis recommence. Avec la vitesse 30, il faut environ **1,04 seconde** pour avancer de 75 pixels, et la même durée pour tourner d'un quart de tour sur place.

- [ ] Dans **Bouton central** (dans un bloc après **Si bouton appuyé**) : **Définir une variable** (etat = 0), **Régler la période de la minuterie** (minuterie 0, période **1040**).
- [ ] Dans **Minuterie 0** :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Augmenter une variable** (etat, 1) |
| 2 | **Si variable** (etat **==** 1), puis **Avancer** (vitesse 30) |
| 3 | **Si variable** (etat **==** 2), puis un bloc : **Régler la vitesse des moteurs** (-30, 30), **Définir une variable** (etat = 0) |

- [ ] Teste : appuie sur la barre d'espace. Au bout d'une seconde, le robot trace un carré de 75 pixels de côté en tournant vers la gauche.

> DONE: un seul événement répété, une variable et des conditions suffisent pour fabriquer un petit programme qui se déroule dans le temps.

## Pour aller plus loin

- Fais tourner le carré **vers la droite**.
- Fais un triangle : l'angle de rotation est de 120° au lieu de 90°. Quelle durée faut-il ?
- Pour arrêter le minuteur, mets sa période à **0** (**Régler la période de la minuterie**). Ajoute un bouton qui arrête le robot et le minuteur.
- Utilise le **Minuterie 1** pour faire clignoter la LED du bas en même temps que le robot trace son carré.
