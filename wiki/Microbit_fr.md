# micro:bit (simulateur de BBC micro:bit)

*[Accueil](Home_fr) | [Référence Complète des Actions](Full-Action-Reference-Microbit-Actions_fr) | [Extensions](Extensions_fr)*

---

PyGameMaker peut placer une **BBC micro:bit simulée** dans la fenêtre de votre
jeu : un écran de 5×5 LED, les boutons **A** et **B**, un logo tactile, les
broches 0/1/2, un accéléromètre, des capteurs de lumière, de température, de
boussole et de son, un haut-parleur et une radio — le tout dessiné à l'écran et
programmé avec les mêmes événements et actions que le reste de l'IDE. Aucun
matériel n'est nécessaire. Cette fonctionnalité est fournie par l'**extension
micro:bit** intégrée, activée par défaut (voir [Extensions](Extensions_fr)).

L'exemple **`microbit_1`** (« Dé et humeurs ») est un jeu complet : A et B
affichent un visage content et un visage triste, une secousse lance un dé, et
toucher le logo fait défiler le nombre de lancers effectués.

---

## Pour commencer

1. Créez un objet dont le **nom commence par `microbit`** (par exemple
   `microbit_1`) et placez une instance de cet objet dans une salle. Cet objet
   *est* la micro:bit : le moteur dessine la carte par-dessus et fait tourner
   son simulateur.
2. Dans **Paramètres du projet → Extensions**, cochez **micro:bit**. (Un projet
   qui utilise déjà une action micro:bit l'a automatiquement ; un projet qui
   n'en utilise pas ne voit jamais les blocs ni les actions micro:bit.)
3. Mettez les événements sur **ce même objet** : chaque action micro:bit agit
   sur la micro:bit qui l'exécute. Par exemple *Button A Pressed* → *Afficher
   une image* `HAPPY`.
4. **Tester le jeu.** Cliquez sur les boutons de la carte.

On peut aussi faire d'un objet une micro:bit en cochant `is_microbit` sur son
instance dans la salle. Plusieurs micro:bit dans une même salle sont possibles
— c'est ce qui rend la radio utile.

---

## La carte et comment la piloter

| À l'écran | Souris | Clavier (à activer) |
|---|---|---|
| Bouton **A** / **B** | Clic (maintenu tant que la souris est enfoncée) | `A` / `B` |
| **A+B** ensemble | Clic droit sur l'un des boutons | maintenir `A` et `B` |
| **Logo** tactile (doré, au-dessus de l'écran) | Clic | — |
| Broches **0, 1, 2** (pastilles en bas) | Clic | — |
| **Zone d'inclinaison** | Glisser ; le bord vaut un g, et elle revient à plat au relâchement | flèches |
| Bouton **SHAKE** | Clic | `S` |
| Curseurs **Light / Temp / Compass / Sound** | Glisser ; la valeur reste | — |

Les raccourcis clavier sont **désactivés par défaut** pour ne jamais voler les
touches de votre propre jeu. Activez-les pour une carte avec la propriété
d'objet `microbit_keyboard` (la variable d'instance du même nom fonctionne
aussi).

Autres propriétés d'objet : `microbit_scale` (multiplicateur de taille, `1.0`
par défaut, environ 220 px de large) et `microbit_show_sensors` (mettez
`false` pour masquer la bande des capteurs). Si l'objet a un **sprite**, c'est
lui qui sert de corps à la carte, et seuls les LED et les commandes sont
dessinées par-dessus.

Un clic sur la carte n'atteint jamais en plus vos propres événements souris.

---

## Les actions (catégorie **micro:bit**)

| Action | Ce qu'elle fait |
|--------|-----------------|
| **Afficher une image** (`microbit_show_image`) | Un nom d'image intégrée (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… 64 au total) ou cinq lignes de cinq chiffres de luminosité comme `09090:99999:99999:09990:00900`. |
| **Faire défiler un texte** (`microbit_scroll_text`) | Faire défiler un texte sur l'écran (150 ms par colonne par défaut). |
| **Afficher un nombre** (`microbit_show_number`) | Un chiffre reste fixe ; un nombre plus long défile. |
| **Allumer une LED** (`microbit_set_pixel`) | Allumer une LED tout de suite : `x`, `y` de 0 à 4, luminosité de 0 à 9. |
| **Effacer l'écran** (`microbit_clear_display`) | Éteindre toutes les LED et abandonner ce qui était en attente. |
| **Luminosité de l'écran** (`microbit_set_brightness`) | Luminosité générale, de 0 à 255. |
| **Jouer une note** (`microbit_play_tone`) | Un bip à une fréquence pendant un nombre de millisecondes. |
| **Jouer une mélodie** (`microbit_play_melody`) | L'une des 21 mélodies intégrées (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) ou vos propres notes : `"C4:4 E G C5:8 R:4"` (note, octave, `:durée` ; `R` est un silence). |
| **Arrêter le son** (`microbit_stop_sound`) | Couper le haut-parleur et abandonner les sons en attente. |
| **Régler le groupe radio** (`microbit_radio_set_group`) | Choisir le groupe radio, de 0 à 255. |
| **Envoyer un message radio** (`microbit_radio_send`) | Envoyer un nombre ou un texte aux autres micro:bit du groupe. |
| **Lire un capteur** (`microbit_read_sensor`) | Mettre une mesure (accéléromètre x/y/z, intensité, boussole, lumière, température, niveau sonore, broches 0 à 2 en analogique) dans une variable — ou une variable globale si le nom commence par `global.`. |
| **Si bouton pressé** (`microbit_if_button`) | Condition : A, B, A+B ou le logo est maintenu. |
| **Si geste** (`microbit_if_gesture`) | Condition : la carte est dans un geste ou une position (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **Si inclinaison** (`microbit_if_tilt`) | Condition : comparer un axe de l'accéléromètre (milli-g) à une valeur. |
| **Si luminosité de la LED** (`microbit_if_pixel`) | Condition : comparer la luminosité d'une LED à une valeur. |

Les conditions gardent l'action ou le bloc qui les suit, à la manière de
GameMaker. Voir la [Référence Complète des
Actions](Full-Action-Reference-Microbit-Actions_fr) pour chaque paramètre.

> **Le texte se met entre guillemets doubles.** *Faire défiler un texte* et
> *Envoyer un message radio* lisent leur valeur comme n'importe quelle
> expression : `Score - 3` est donc un calcul. Écrivez un texte littéral
> `"Bonjour"`. L'écran ne connaît que l'ASCII imprimable ; les lettres
> accentuées apparaissent en `?`, comme sur la vraie carte.

---

## Les événements

Déclenchés sur l'objet de la micro:bit elle-même :

| Événement | Se déclenche quand |
|-----------|--------------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | Le ou les boutons sont enfoncés. |
| **Logo Touched** | Le logo est touché. |
| **Pin 0 / 1 / 2 Touched** | Cette broche est touchée. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | La carte détecte ce geste (le même algorithme que la vraie micro:bit). |
| **Loud Sound** / **Quiet Sound** | Le niveau du micro franchit le seuil fort / faible. |
| **Display Finished** | La file d'affichage a tout joué. |
| **Sound Finished** | Toutes les notes et mélodies en attente sont terminées. |
| **Radio Message Received** | Une autre micro:bit du même groupe a envoyé un message. |

Les noms des événements s'affichent en anglais dans l'éditeur. « Pour
toujours » est l'événement **Step** habituel.

### Radio

Chaque carte démarre dans le groupe 0. *Envoyer un message radio* livre le
message à toutes les *autres* micro:bit du même groupe (une carte ne s'entend
jamais elle-même, et un autre groupe n'entend rien). Le destinataire reçoit
l'événement et deux variables : `radio_number` (0 si le texte n'est pas un
nombre) et `radio_string` (toujours le texte). Le texte est coupé à 32
caractères, comme sur la vraie radio.

---

## Le temps : files d'affichage et de son

Sur une vraie micro:bit, faire défiler un texte *bloque* le programme. Un jeu
ne peut pas se bloquer : les actions d'affichage se mettent donc **en file
d'attente** et se jouent l'une après l'autre (16 au maximum ; demander ce qui
est déjà affiché ne fait rien). *Effacer l'écran* vide la file et **Display
Finished** indique quand elle est épuisée, pour enchaîner des animations. Les
sons font de même, avec *Arrêter le son* et **Sound Finished**.

Le son est une onde carrée, comme le buzzer de la carte. Si l'ordinateur n'a
pas de carte son, il est simplement ignoré (le simulateur le suit quand même).

---

## Exports

L'export **bureau** (Windows, Linux, macOS) embarque le vrai moteur : la
micro:bit y fonctionne exactement comme dans Tester le jeu. L'export
**HTML5** embarque aussi le simulateur : la carte et la bande de capteurs sont
dessinées dans le navigateur, on peut cliquer ou toucher les boutons, le logo
et les broches, faire glisser la zone d'inclinaison et les curseurs, et le
haut-parleur émet des bips (les navigateurs n'autorisent le son qu'après le
premier clic ou la première touche). L'export **Android/Kivy** l'a aussi : la carte
et la bande de capteurs sont dessinées (avec un aspect simplifié, aux coins
carrés), on peut toucher les boutons, le logo, les broches, la zone
d'inclinaison, le bouton de secousse et les curseurs, les événements se
déclenchent et le haut-parleur joue ses notes. Les raccourcis clavier ne
fonctionnent que pour une carte dont la variable `microbit_keyboard` est
activée. Une carte est reconnue par le nom de son objet (il doit commencer par
`microbit`) ou par `is_microbit` sur son instance dans la salle.

---

## Export MicroPython (vers une vraie micro:bit)

C'est un export d'un autre genre. Au lieu d'un jeu pour un autre ordinateur, il
transforme le programme de vos objets micro:bit en vrai code **MicroPython** qui
tourne sur une carte physique.

1. Ouvrez **Fichier → Exporter le code micro:bit (MicroPython)...** (un projet
   doit être ouvert).
2. Indiquez quelle carte vous avez : **V2 (2020 ou plus récent)**, **V1
   (d'origine, 2016-2020)** ou **Les deux (un seul fichier .hex pour les cartes
   V1 et V2)**.
3. Choisissez un dossier. Chaque objet micro:bit a son propre programme,
   `<dossier>/<nom de l'objet>/main.py`.
4. Quand un seul objet a été exporté, l'IDE propose deux façons de le mettre sur
   la carte. **Copier sur la micro:bit ?** copie `main.py` sur une carte
   branchée en USB et qui fait déjà tourner MicroPython (le programme démarre
   alors tout seul). **Créer un fichier .hex prêt à flasher ?** produit un
   fichier `.hex` que vous glissez sur le lecteur USB **MICROBIT** de la carte —
   cela marche aussi sur une carte neuve qui n'a jamais fait tourner
   MicroPython.

Toutes les actions et conditions micro:bit sont traduites, ainsi que *Définir
une variable*, *Tester une variable*, les blocs et les commentaires. Chaque
événement devient un test dans une seule boucle. Les actions de jeu qui n'ont
aucun sens sur une carte (salles, sprites, scores…) ne sont pas exportées. Dans
les expressions, `irandom`, `random` et `choose` fonctionnent ; les autres
fonctions de GameMaker ne sont pas traduites.

La boîte de dialogue d'export liste ce qui n'a pas pu être exporté :

- **Display Finished** et **Sound Finished** (les appels d'affichage et de son
  de la carte attendent déjà la fin de l'opération).
- Sur une carte V1, ce qui exige une V2 : la lecture du niveau sonore, le logo
  tactile (*Si bouton pressé* avec le logo, **Logo Touched**) et les événements
  **Loud Sound** / **Quiet Sound**.
- Tout le reste qui n'a pas d'équivalent en MicroPython.

**Taille :** le programme doit tenir en 8 187 octets sur une carte V1 et en
20 150 octets sur une V2. **Les deux** produit un seul Universal Hex : il est
donc limité par la taille V1 et s'exporte avec les règles de la V1.

> Les fichiers `.hex` ont été vérifiés par rapport au vrai micrologiciel de la
> micro:bit, mais pas encore sur une carte physique.

---

## Et ensuite

- Ouvrez l'exemple **`microbit_1`** depuis l'onglet d'accueil et lisez son
  guide.
- Essayez deux cartes dans une même salle, chacune avec un *Régler le groupe
  radio*, et envoyez un message depuis un bouton.
- Prévue : une liaison en direct avec une vraie micro:bit par USB. Elle n'est
  pas encore disponible.

Voir aussi : [Extensions](Extensions_fr), [Référence Complète des Actions](Full-Action-Reference-Microbit-Actions_fr), [Référence des Événements](Event-Reference_fr).
