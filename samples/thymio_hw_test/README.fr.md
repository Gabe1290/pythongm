# Thymio — Test avec le robot

Six petits programmes, un par robot dans la salle, pour savoir si ce que PyGameMaker exporte
fonctionne sur un **vrai Thymio**. Dans PyGameMaker, vous pouvez d'abord les essayer dans le
simulateur, puis les exporter et les charger sur le robot, un à la fois.

Le premier essai sur un vrai robot est la partie intéressante : notez ce qui se passe (un tableau
de résultats se trouve à la fin).

## Avant de commencer

1. **Activez les fonctions Thymio** (elles sont désactivées par défaut) :
   *Outils → Préférences → Extensions* → cochez **Thymio Robot**, puis la case située dessous
   (*Afficher l'onglet, les menus et le bouton de la barre d'outils de cette extension*).
   Validez avec OK et **redémarrez** l'IDE.
2. **Installez le logiciel Thymio** (Thymio Suite). Il vous faut *Aseba Studio*, fourni avec
   (sous Windows : `C:\Program Files\Thymio\bin\asebastudio.exe`).
3. Prenez un **Thymio II** et un câble USB (ou la clé sans fil). Chargez-le.

## Étape 1 — essayer dans le simulateur

Ouvrez cet exemple et lancez **Tester le jeu**. **Cliquez sur les flèches dessinées** d'un robot
avec la souris : ses LED et ses roues réagissent. (Les flèches du clavier et la barre d'espace
appuient sur ce bouton sur les **six** robots à la fois, ce qui est amusant, mais gênant pour le
test des moteurs.) Cela montre si la *logique du programme* est celle que vous vouliez, avant que
le robot n'entre en jeu.

Comme le vrai robot, le simulateur exécute le programme d'un bouton **à l'appui et au relâchement** ;
le programme 2 avance donc tant que vous maintenez un bouton et s'arrête quand vous le relâchez.

Une chose reste différente : les capteurs de proximité et du sol indiquent « libre / clair » tant
que vous ne placez pas d'obstacles dans un terrain de jeu (playground).

## Étape 2 — exporter le code Aseba

*Fichier → Exporter le code Aseba (Thymio)…* puis choisissez un dossier. Vous obtenez **un fichier
par robot** :

| Fichier | Ce qu'il teste |
|---|---|
| `thymio_hw_1_leds.aesl` | LED : dessus, dessous gauche, dessous droite, tout éteint |
| `thymio_hw_2_motors.aesl` | Moteurs : avance seulement tant qu'un bouton est maintenu |
| `thymio_hw_3_counter.aesl` | Variables et condition : compter les appuis |
| `thymio_hw_4_proximity.aesl` | Capteurs de proximité : s'arrêter devant un obstacle |
| `thymio_hw_5_ground.aesl` | Capteurs du sol : s'arrêter sur une ligne sombre |
| `thymio_hw_6_timer.aesl` | Minuterie et son : un bip chaque seconde |

(Sans l'IDE, depuis le dossier de PyGameMaker :
`py -3.12 -m extensions.thymio.export.aseba_exporter samples/thymio_hw_test/project.json C:	empesl`
écrit les six mêmes fichiers.)

## Étape 3 — lancer un programme sur le robot

**Le moyen rapide, sans Aseba Studio :** installez une fois l'aide (`pip install --user tdmclient`), branchez le robot et
utilisez *Fichier → Envoyer au robot Thymio…*. L'IDE demande lequel des six objets envoyer, le compile sur le robot et le
démarre ; si le robot refuse le programme, son message d'erreur s'affiche dans l'IDE. Passez à « Ce que vous devez voir ».
Les étapes ci-dessous font la même chose à la main avec Aseba Studio.

1. Branchez le Thymio et allumez-le.
2. Ouvrez **Aseba Studio** ; il trouve le robot.
3. *Fichier → Ouvrir* le fichier `.aesl`, appuyez sur **Charger**, puis sur **Exécuter**.
4. Faites ce que dit le tableau. Appuyez sur **Stop** (ou éteignez le robot) quand vous avez fini.
5. Fichier suivant : ouvrez-le, **Charger**, **Exécuter**.

Commencez par `1_leds` — il ne fait rien bouger. Quand un programme est chargé et exécuté, la
**LED du dessus est bleu faible** (sauf pour la minuterie) ; si vous ne la voyez pas, le code n'a
pas été chargé.

## Ce que vous devez voir

| N° | Faites ceci | Vous devez voir |
|---|---|---|
| 1 | Appuyer sur avant / arrière | LED du dessus rouge / verte |
|   | Appuyer sur gauche / droite | LED dessous gauche / dessous droite bleue |
|   | Appuyer sur le centre | Toutes les LED éteintes |
| 2 | Maintenir avant, arrière, gauche, droite | Il avance (lentement), s'arrête au relâchement |
|   | Appuyer sur le centre | Il s'arrête |
| 3 | Appuyer trois fois sur le centre | La LED du dessus devient verte au troisième appui |
|   | Appuyer sur arrière | Retour au bleu faible (compteur remis à zéro) |
| 4 | Appuyer sur le centre | Il avance lentement |
|   | Placer une main ou un livre devant | Il s'arrête, LED rouge ; dégagé : verte |
| 5 | Appuyer sur le centre sur une table claire | Il avance lentement, LED verte |
|   | Ruban noir sous le capteur de sol **gauche** | Il s'arrête, LED rouge |
| 6 | (rien) | Un bip et une LED bleue une fois par seconde |
|   | Appuyer sur centre / avant | La minuterie s'arrête (silence) / repart |

**Sécurité :** les programmes 2, 4 et 5 font bouger le robot, mais seulement après un appui sur un
bouton, à faible vitesse. Gardez-le au sol ou au milieu d'une table et surveillez-le.

## Ce dont nous ne sommes pas sûrs (à regarder en premier)

C'est le premier essai sur du vrai matériel ; certaines choses du code exporté sont donc des
hypothèses :

- **Arrêter un son** (programme 6, bouton central) utilise `call sound.freq(0, -1)`. Si le bip ne
  s'arrête pas, dites-le-nous.
- **Le comptage** (programme 3) utilise la forme `count++`. Si Aseba Studio signale une erreur de
  syntaxe à cet endroit, c'est un résultat utile.
- **Seuils** : 2000 pour le capteur de proximité avant et 300 pour le capteur du sol sont les
  valeurs par défaut. Votre table, l'éclairage et le ruban décident s'ils conviennent.
- **Vitesses** 80 et 100 sont exprimées dans les unités du Thymio (le maximum est d'environ 500).
- Un événement de bouton se déclenche **à l'appui et au relâchement** ; c'est pourquoi les
  programmes vérifient `button.xxx == 1` avant d'agir.
- Le simulateur et le robot ne se comporteront pas de façon identique ; la question intéressante
  est de savoir *en quoi* ils diffèrent.

## Résultats

Copiez ce tableau et remplissez-le :

| N° | Chargé sans erreur ? | A fait ce que dit le tableau ? | Ce qui était différent |
|---|---|---|---|
| 1 LED | | | |
| 2 Moteurs | | | |
| 3 Compteur | | | |
| 4 Proximité | | | |
| 5 Sol | | | |
| 6 Minuterie + son | | | |

Renvoyez-le (un message d'erreur d'Aseba Studio, copié en texte, est ce qu'il y a de plus utile),
et ce qui diffère sera corrigé.

*Remarque :* les six robots et leurs étiquettes sont réunis dans une seule salle uniquement pour
voir les six programmes à la fois dans le simulateur. Sur le robot, on charge toujours **un seul**
fichier `.aesl` à la fois.
