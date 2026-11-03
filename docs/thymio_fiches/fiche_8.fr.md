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

L'action **Play Tone** (catégorie **Sound**) joue une note. Elle a deux paramètres :

| Paramètre | Signification |
|---|---|
| **frequency** | la fréquence en Hz (par exemple 440) |
| **duration** | la durée en **soixantièmes de seconde** : 30 = une demi-seconde, 60 = une seconde |

- [ ] Ajoute **Button Forward** avec **If Button Pressed** (forward), puis **Play Tone** (frequency = 262, duration = 30).
- [ ] Fais de même avec **Button Left** (330), **Button Right** (392) et **Button Backward** (523).
- [ ] Lance **Test Game** et joue les quatre notes avec les flèches.
- [ ] Retire un **If Button Pressed**. Combien de fois la note est-elle jouée à chaque appui ? Pourquoi ?

> TIP: un événement de bouton se déclenche à l'appui **et** au relâchement (fiche 3). Sans la condition, la note est jouée deux fois.

## 2. Tenir la note

Avec la durée **-1**, la note ne s'arrête jamais toute seule. L'action **Stop Sound** l'arrête.

- [ ] Dans **Button Forward**, mets : **If Button Pressed** (forward) → **Play Tone** (440, **-1**) ; puis **If Button Released** (forward) → **Stop Sound**.
- [ ] Teste : la note dure **tant que tu tiens** la flèche du haut, comme une touche d'orgue.

## 3. Une mélodie

Si tu mets quatre **Play Tone** à la suite, tu n'entends que le dernier : chaque note remplace la précédente. Pour enchaîner, il faut attendre que la note soit finie. L'événement **Sound Finished** se déclenche à la fin de chaque note.

- [ ] Dans **Button Center** : **If Button Pressed** (center), puis un bloc `start_block` : **Set Variable** (note = 0), **Play Tone** (262, 20), `end_block`.
- [ ] Dans **Sound Finished** :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Increase Variable** (note, 1) |
| 2 | **If Variable** (note **==** 1), puis **Play Tone** (330, 20) |
| 3 | **If Variable** (note **==** 2), puis **Play Tone** (392, 20) |
| 4 | **If Variable** (note **==** 3), puis **Play Tone** (523, 40) |

- [ ] Appuie sur la barre d'espace : tu entends **do, mi, sol, do aigu**.
- [ ] Après la dernière note, que se passe-t-il ? Pourquoi la mélodie s'arrête-t-elle ? (Regarde la valeur de **note**.)

> INFO: la variable **note** compte les notes déjà jouées, comme la variable **etat** de la fiche 7.

## 4. Les sons du robot

Le robot connaît huit sons. L'action **Play System Sound** en joue un :

| N° | Nom | N° | Nom |
|---|---|---|---|
| 0 | Startup | 4 | Free Fall |
| 1 | Shutdown | 5 | Collision |
| 2 | Arrow | 6 | Target Friendly |
| 3 | Central | 7 | Target Detected |

- [ ] Associe un son à chaque bouton (avec **If Button Pressed**) : par exemple **Startup** à gauche, **Arrow** en avant, **Collision** en arrière, **Target Friendly** à droite, **Target Detected** au centre.
- [ ] Écoute-les. Lequel te fait penser à une joie ? à une alarme ? à une chute ?

> INFO: dans le simulateur, ces sons sont de **courtes mélodies synthétisées** qui ressemblent aux sons du robot. Ce ne sont pas les enregistrements du vrai Thymio : sur le robot réel, ils sonneront un peu différemment. **Sound Finished** se déclenche à la fin de la mélodie.

## 5. Une sirène

Une sirène alterne deux notes, avec une lumière qui clignote.

- [ ] Dans **Button Center** : **If Button Pressed** (center), puis un bloc : **Set Variable** (etat = 0), **Set Timer Period** (timer 0, période **500**).
- [ ] Dans **Timer 0** :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Increase Variable** (etat, 1) |
| 2 | **If Variable** (etat **==** 1), puis un bloc : **Play Tone** (440, 30), **Set Top LED Color** rouge (32, 0, 0) |
| 3 | **If Variable** (etat **==** 2), puis un bloc : **Play Tone** (880, 30), **Set Top LED Color** bleu (0, 0, 32), **Set Variable** (etat = 0) |

- [ ] Appuie sur la barre d'espace : le robot fait « pin-pon » avec une lumière rouge puis bleue.
- [ ] Pour l'arrêter, mets la période du minuteur à **0** (**Set Timer Period**) puis **Stop Sound**.

## 6. Un radar de recul

*Exemple : les murs.* Comme le radar d'une voiture qui recule : plus l'obstacle est proche, plus le bip est **aigu**.

- [ ] Reprends le programme de la fiche 3 (pilotage avec les quatre flèches).
- [ ] Ajoute **Proximity Sensors Update** avec :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **If Proximity Detected** (sensor_index = 2 - Front Center, comparison = **>**, threshold = **250**), puis **Play Tone** (800, 4) |
| 2 | **If Proximity Detected** (sensor_index = 2 - Front Center, comparison = **>**, threshold = **1000**), puis **Play Tone** (1500, 4) |

- [ ] Avance vers une boîte : rien ne sonne de loin, puis des bips graves, puis des bips aigus tout près. (Les capteurs sont lus dix fois par seconde : le bip dure 4 soixantièmes de seconde pour laisser un silence entre deux bips.)

> DONE: tu sais faire parler ton robot : notes, mélodies, alarmes et signaux.

## Pour aller plus loin

- Joue « Au clair de la lune » : do do do ré mi ré do mi ré ré do. Combien de **If Variable** te faut-il ? Y a-t-il un moyen plus court ?
- Change la sirène : trois notes, ou des lumières qui changent de couleur à chaque note.
- Fais jouer le son **Collision** quand le robot s'arrête devant un mur (fiche 4).
- Fais un radar encore plus précis avec un troisième seuil.
