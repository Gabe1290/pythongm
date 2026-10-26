# micro:bit — Dé et humeurs (microbit_1)

Une **micro:bit** (BBC) simulée dans la fenêtre de votre jeu — aucun matériel
nécessaire. Cliquez sur ses boutons, secouez-la, et regardez l'écran de
5×5 LED réagir aux événements que vous programmez.

## Lancer

Ouvrez le projet et appuyez sur **Tester le jeu** (ou lancez
`python runtime/run_game.py samples/microbit_1/project.json`).

| Faites ceci | Résultat |
|---|---|
| Cliquer sur **A** | un visage content |
| Cliquer sur **B** | un visage triste |
| Appuyer sur le bouton **SHAKE** (ou la touche **S**) | la carte « lance un dé » : une face de 1 à 6 points |
| Toucher le **logo** doré | il fait défiler le mot *Rolls*, puis le nombre de fois où vous l'avez secouée |

Tout le reste de la carte fonctionne aussi, même si ce jeu ne s'en sert pas :
un **clic droit** sur A ou B appuie sur **A+B** ensemble, vous pouvez toucher
les pastilles 0, 1 et 2, faire glisser la **zone d'inclinaison** pour pencher
la carte, et déplacer les curseurs pour changer la luminosité, la
température, le cap de la boussole et le niveau sonore. Les touches **A**,
**B**, **S** et les flèches font la même chose au clavier — cet objet l'active
avec `microbit_keyboard`.

## Comment ça marche

| Objet | Rôle |
|---|---|
| `microbit_1` | La carte. Tout objet dont le nom **commence par `microbit`** devient une micro:bit : le moteur dessine la carte par-dessus et fait tourner son simulateur. Ses événements sont les boutons, la secousse et le logo ; ses actions dessinent sur l'écran de LED. |
| `obj_help` | Dessine les trois lignes d'instructions sous la carte. |

Les événements de `microbit_1` :

- **Création** — `rolls = 0`, et afficher un `HEART`.
- **Bouton A pressé** — *Afficher une image* `HAPPY`.
- **Bouton B pressé** — *Afficher une image* `SAD`.
- **Geste : secousse** — tire `roll = irandom(5) + 1`, puis six paires
  *Tester une variable* / *Afficher une image* montrent la face qui
  correspond (chaque paire dit « si `roll` vaut *k*, afficher l'image du
  dé *k* »), et ajoute 1 à `rolls`.
- **Logo touché** — *Faire défiler un texte* `"Rolls"`, puis *Afficher un
  nombre* `rolls`. Les actions d'affichage se mettent **en file d'attente** :
  le nombre attend que le mot ait fini de défiler, exactement comme sur la
  vraie carte.

Une face de dé est une image personnalisée : cinq lignes de cinq chiffres de
luminosité, de `0` (éteint) à `9` (maximum), séparées par des deux-points —
par exemple le point central est `00000:00000:00900:00000:00000`.

## À essayer

- Remplacez les deux humeurs par `HEART`, `SKULL`, `YES` ou `NO` — il y a
  64 images intégrées (voir l'infobulle de *Afficher une image*), ou dessinez
  les vôtres.
- Ajoutez **Jouer une mélodie** `POWER_UP` à l'événement de secousse, ou
  **Jouer une note** avec votre propre fréquence. Ajoutez **Arrêter le son**
  sur le bouton B.
- Utilisez **Si inclinaison** (axe x, `>` 300) dans un événement **Step** pour
  afficher une flèche quand vous penchez la carte vers la droite.
- Copiez l'objet en `microbit_2`, donnez un **Régler le groupe radio** aux
  deux, et faites que le bouton A **Envoie un message radio** `1` : l'autre
  carte reçoit un événement *Message radio reçu*, avec la valeur dans
  `radio_number`.

## Bon à savoir

- Les événements doivent être sur **l'objet de la carte lui-même**
  (`microbit_1`) : chaque action micro:bit agit sur la micro:bit qui
  l'exécute.
- Le texte à afficher tel quel se met **entre guillemets doubles**
  (`"Rolls"`), comme partout dans PyGameMaker ; sans eux, un tiret ou un plus
  serait lu comme un calcul.
- Ce projet déclare l'extension dans **Paramètres du projet → Extensions**,
  ce qui fait apparaître les blocs et actions micro:bit dans ses éditeurs. Un
  projet qui ne l'active pas ne les voit jamais.
- L'écran n'affiche que l'ASCII imprimable ; les lettres accentuées
  apparaissent en `?`, comme sur la vraie carte.
- Le simulateur fonctionne dans **Tester le jeu et les exports bureau**. Les
  exports HTML5 et Android se lancent mais ne dessinent pas encore la carte.
