# Fiche 8 : Les sons

**Exemples à ouvrir :** Thymio — Activités : arène libre (et : les murs pour la fin)  ·  **Durée :** 40 minutes

## Ce que tu vas apprendre

- jouer une note, tenir une note, enchaîner des notes ;
- faire jouer les sons du robot ;
- utiliser un son pour renseigner : une sirène, un radar de recul.

> INFO: le simulateur joue les sons avec le **haut-parleur de l'ordinateur**. Règle le volume de l'ordinateur, ou appuie sur la touche **M** pendant le jeu pour **couper le son** (et rappuie dessus pour le remettre). Le programme continue de fonctionner, seul le son est coupé.

## 1. Une note

Un son est défini par sa **fréquence** en hertz (Hz) : plus le nombre est grand, plus le son est **aigu**. Voici les notes de la gamme de do :

| do | ré | mi | fa | sol | la | si | do aigu |
|---|---|---|---|---|---|---|---|
| 262 | 294 | 330 | 349 | 392 | 440 | 494 | 523 |

L'action **Jouer une note** (catégorie **Sound**) joue une note. Elle a deux paramètres :

| Paramètre | Signification |
|---|---|
| **Fréquence (Hz)** | la fréquence en Hz (par exemple 440) |
| **Durée** | la durée en **soixantièmes de seconde** : 30 = une demi-seconde, 60 = une seconde |

- [ ] Ajoute **Bouton avant** avec **Si bouton appuyé** (avant), puis **Jouer une note** (Fréquence (Hz) = 262, Durée = 30).
- [ ] Fais de même avec **Bouton gauche** (330), **Bouton droit** (392) et **Bouton arrière** (523).
- [ ] Lance **Test Game** et joue les quatre notes avec les flèches.
- [ ] Retire un **Si bouton appuyé**. Combien de fois la note est-elle jouée à chaque appui ? Pourquoi ?

> TIP: un événement de bouton se déclenche à l'appui **et** au relâchement (fiche 3). Sans la condition, la note est jouée deux fois.

## 2. Tenir la note

Avec la durée **-1**, la note ne s'arrête jamais toute seule. L'action **Arrêter le son** l'arrête.

- [ ] Dans **Bouton avant**, mets : **Si bouton appuyé** (avant) → **Jouer une note** (440, **-1**) ; puis **Si bouton relâché** (avant) → **Arrêter le son**.
- [ ] Teste : la note dure **tant que tu tiens** la flèche du haut, comme une touche d'orgue.

## 3. Une mélodie

Si tu mets quatre **Jouer une note** à la suite, tu n'entends que le dernier : chaque note remplace la précédente. Pour enchaîner, il faut attendre que la note soit finie. L'événement **Son terminé** se déclenche à la fin de chaque note.

- [ ] Dans **Bouton central** : **Si bouton appuyé** (centre), puis un bloc `start_block` : **Définir une variable** (note = 0), **Jouer une note** (262, 20), `end_block`.
- [ ] Dans **Son terminé** :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Augmenter une variable** (note, 1) |
| 2 | **Si variable** (note **==** 1), puis **Jouer une note** (330, 20) |
| 3 | **Si variable** (note **==** 2), puis **Jouer une note** (392, 20) |
| 4 | **Si variable** (note **==** 3), puis **Jouer une note** (523, 40) |

- [ ] Appuie sur la barre d'espace : tu entends **do, mi, sol, do aigu**.
- [ ] Après la dernière note, que se passe-t-il ? Pourquoi la mélodie s'arrête-t-elle ? (Regarde la valeur de **note**.)

> INFO: la variable **note** compte les notes déjà jouées, comme la variable **etat** de la fiche 7.

## 4. Les sons du robot

Le robot connaît huit sons. L'action **Jouer un son système** en joue un :

| N° | Nom | N° | Nom |
|---|---|---|---|
| 0 | Démarrage | 4 | Chute libre |
| 1 | Extinction | 5 | Collision |
| 2 | Flèche | 6 | Cible amie |
| 3 | Central | 7 | Cible détectée |

- [ ] Associe un son à chaque bouton (avec **Si bouton appuyé**) : par exemple **Démarrage** à gauche, **Flèche** en avant, **Collision** en arrière, **Cible amie** à droite, **Cible détectée** au centre.
- [ ] Écoute-les. Lequel te fait penser à une joie ? à une alarme ? à une chute ?

> INFO: dans le simulateur, ces sons sont de **courtes mélodies synthétisées** qui ressemblent aux sons du robot. Ce ne sont pas les enregistrements du vrai Thymio : sur le robot réel, ils sonneront un peu différemment. **Son terminé** se déclenche à la fin de la mélodie.

## 5. Une sirène

Une sirène alterne deux notes, avec une lumière qui clignote.

- [ ] Dans **Bouton central** : **Si bouton appuyé** (centre), puis un bloc : **Définir une variable** (etat = 0), **Régler la période de la minuterie** (minuterie 0, période **500**).
- [ ] Dans **Minuterie 0** :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Augmenter une variable** (etat, 1) |
| 2 | **Si variable** (etat **==** 1), puis un bloc : **Jouer une note** (440, 30), **Régler la LED du dessus** rouge (32, 0, 0) |
| 3 | **Si variable** (etat **==** 2), puis un bloc : **Jouer une note** (880, 30), **Régler la LED du dessus** bleu (0, 0, 32), **Définir une variable** (etat = 0) |

- [ ] Appuie sur la barre d'espace : le robot fait « pin-pon » avec une lumière rouge puis bleue.
- [ ] Pour l'arrêter, mets la période du minuteur à **0** (**Régler la période de la minuterie**) puis **Arrêter le son**.

## 6. Un radar de recul

*Exemple : les murs.* Comme le radar d'une voiture qui recule : plus l'obstacle est proche, plus le bip est **aigu**.

- [ ] Reprends le programme de la fiche 3 (pilotage avec les quatre flèches).
- [ ] Ajoute **Mise à jour de proximité** avec :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Si proximité** (Capteur = 2 - Avant centre, Comparaison = **>**, Seuil = **250**), puis **Jouer une note** (800, 4) |
| 2 | **Si proximité** (Capteur = 2 - Avant centre, Comparaison = **>**, Seuil = **1000**), puis **Jouer une note** (1500, 4) |

- [ ] Avance vers une boîte : rien ne sonne de loin, puis des bips graves, puis des bips aigus tout près. (Les capteurs sont lus dix fois par seconde : le bip dure 4 soixantièmes de seconde pour laisser un silence entre deux bips.)

> DONE: tu sais faire parler ton robot : notes, mélodies, alarmes et signaux.

## Pour aller plus loin

- Joue « Au clair de la lune » : do do do ré mi ré do mi ré ré do. Combien de **Si variable** te faut-il ? Y a-t-il un moyen plus court ?
- Change la sirène : trois notes, ou des lumières qui changent de couleur à chaque note.
- Fais jouer le son **Collision** quand le robot s'arrête devant un mur (fiche 4).
- Fais un radar encore plus précis avec un troisième seuil.
