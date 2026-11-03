# Fiche 3 : Les moteurs

**Exemple à ouvrir :** Thymio — Activités : arène libre  ·  **Durée :** 25 minutes

## Ce que tu vas apprendre

- faire avancer, reculer et tourner le robot ;
- le faire **s'arrêter** quand on relâche un bouton ;
- distinguer l'appui du relâchement.

## 1. Avancer

- [ ] Efface les programmes précédents (ou ouvre à nouveau l'exemple). Ajoute **Button Forward** avec l'action **Move Forward**, **speed = 30**.
- [ ] Teste : appuie sur **↑**. Le robot avance, puis ne s'arrête plus. Pourquoi ?

> INFO: dans le simulateur, la vitesse **30** donne environ **72 pixels par seconde**. Le robot fait 110 pixels de large : vitesse 30 = un peu plus d'une demi-largeur par seconde. Reste entre **20 et 50**.

## 2. Un événement, deux moments

Un événement de bouton se déclenche **deux fois** : quand tu **appuies**, et quand tu **relâches**. Pour agir seulement à l'appui, ou seulement au relâchement, on utilise une condition qui s'applique à l'action suivante.

- [ ] Dans **Button Forward**, mets, dans cet ordre :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **If Button Pressed** (button = forward) |
| 2 | **Move Forward** (speed = 30) |
| 3 | **If Button Released** (button = forward) |
| 4 | **Stop Motors** |

- [ ] Teste : le robot avance **tant que tu tiens** la touche ↑ et s'arrête dès que tu la relâches.

> TIP: une condition s'applique à l'action qui la suit. Pour plusieurs actions, entoure-les avec **start_block** et **end_block**.

## 3. Reculer et tourner

- [ ] Fais la même chose pour **Button Backward** avec **Move Backward** (speed 30).
- [ ] Pour tourner sur place, utilise **Set Motor Speeds** (la roue gauche et la roue droite tournent en sens contraires) :

| Bouton | left_speed | right_speed | Le robot… |
|---|---|---|---|
| **Button Left** | -30 | 30 | tourne vers la gauche |
| **Button Right** | 30 | -30 | tourne vers la droite |

- [ ] Maintiens **←** environ **une seconde** : le robot fait à peu près **un quart de tour**.

> DONE: tu pilotes le robot comme avec une télécommande. N'oublie pas qu'un mur ne l'arrêtera pas : c'est le sujet de la fiche 4.

## Pour aller plus loin

- Le robot sort de la pièce ? Remets-le au centre en relançant le jeu, puis essaie de dessiner un carré **à la main** avec les quatre boutons.
- Fais en sorte que **Button Center** arrête le robot, quoi qu'il fasse.
- Essaie la vitesse 50. Que remarques-tu pour le quart de tour ?
