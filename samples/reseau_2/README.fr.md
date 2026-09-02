# Réseau — Quiz de classe (reseau_2)

Un jeu multijoueur en réseau local à variables partagées (niveau A) :
**l'hôte est le maître du jeu, jusqu'à 3 joueurs connectés répondent à
des questions à choix multiples, et tout le monde voit un tableau des
scores en direct.** Aucun avatar, aucun déplacement — c'est la façon la
plus douce d'enseigner `host_game`/`join_game`, les variables partagées
et les messages personnalisés.

## Lancer le jeu

Il faut **deux machines ou plus sur le même réseau local filaire** (ou
deux fenêtres sur une seule machine pour un test rapide). Lancez le jeu
normalement (double-clic sur l'export, ou **Tester le jeu** dans l'IDE),
puis :

- **Hôte** (le maître du jeu) : appuyez sur **H**. Un salon d'attente
  apparaît — attendez que les joueurs se connectent, puis cliquez sur le
  bouton « Démarrer » à l'écran.
- **Chaque autre joueur** : appuyez sur **J**, ce qui ouvre la liste des
  serveurs détectés (ou tapez directement l'adresse locale de l'hôte).
  Une fois connecté, attendez que l'hôte démarre la partie.

Une fois la partie démarrée, appuyez sur **A**, **B**, **C** ou **D**
pour répondre. Chaque question dure 8 secondes ; les scores se mettent à
jour en direct pour tout le monde.

## Fonctionnement

| Objet | Rôle |
|---|---|
| `obj_quiz` | Le seul objet. Tout le monde exécute le même code, en branchant selon `global.is_host` / `global.is_client`. |

- **L'hôte possède le quiz.** À **Partie réseau démarrée**
  (`network_game_started`, protégé par `global.is_host == 1`), il publie
  le texte complet de la première question dans des variables partagées
  (`question`, `option_a`..`option_d`) et démarre une alarme de 8
  secondes. Quand l'alarme se déclenche, il passe à la question
  suivante — ou, une fois les trois questions épuisées, publie
  `etat = "fin"`.
- **Un client répond en envoyant un message**, pas en écrivant
  directement une variable partagée : appuyer sur A/B/C/D appelle
  `send_network_message(event="reponse", data="A", target="host")`.
  Seul le gestionnaire **Message réseau** (`network_message`) de l'hôte
  attribue le point, en comparant `global.network_data` à la variable
  d'instance `self.correct` (un secret propre à chaque machine — jamais
  publié comme variable partagée, donc illisible depuis une autre
  machine).
- **Chaque score est sa propre variable partagée** (`score_0`..`score_3`,
  une par emplacement de joueur). Les *noms* des paramètres d'action
  (comme le champ `name` de `set_shared_var`) sont lus littéralement,
  jamais évalués comme une expression — attribuer un point se fait donc
  par des branches explicites sur `global.network_sender` (0/1/2/3)
  plutôt qu'en essayant de construire un nom de variable dynamiquement.
- **Le tableau des scores est toujours visible** (bas de l'écran), même
  pendant l'affichage de la question en cours — pas de phase « résultats »
  séparée.

## À essayer

- Changez les questions (les actions de configuration de manche dans
  **Partie réseau démarrée** et **alarm_0**) pour votre propre quiz — le
  motif est entièrement fait de branches explicites, facile à étendre à
  plus de manches ou plus de joueurs.
- Ajoutez un gestionnaire `network_message` pour un **nouveau** nom
  d'événement (par ex. `"buzz"`) pour qu'un joueur puisse se manifester
  avant de répondre, comme dans un vrai jeu télévisé.
- Raccourcissez ou allongez le minuteur de chaque question en changeant
  le `steps` de `set_alarm` (240 = 8 secondes à `room_speed` = 30 fps
  dans cette salle).

## Notes pour l'enseignant

- Ports utilisés : **45782/TCP** (jeu) et **45783/UDP** (découverte).
  Demandez au service informatique avant d'utiliser sur un réseau géré.
- **Les salles filaires fonctionnent le mieux.** Beaucoup de points
  d'accès Wi-Fi scolaires bloquent le trafic entre appareils, ce qui
  empêche totalement le multijoueur local — aucun logiciel ne peut
  contourner cela.
- Contrairement à `reseau_1`, personne n'a besoin de bouger ou de réagir
  vite — une image perdue ou un instant de latence ne coûte la manche à
  personne, ce qui en fait une bonne première séance de multijoueur
  local à mener avec une classe.
