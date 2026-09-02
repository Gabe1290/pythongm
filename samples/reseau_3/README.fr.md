# Réseau — Récolte en équipe (reseau_3)

Un jeu multijoueur en réseau local à instances synchronisées (niveau B) :
**chacun pilote son propre avatar, ramasse des gemmes partagées pour un
score d'équipe, et évite un monstre simulé par l'hôte.** S'appuie
directement sur le motif d'avatar de `reseau_1`, en ajoutant des objets
à collecter contrôlés par l'hôte et un ennemi simple.

## Lancer le jeu

Il faut **deux machines ou plus sur le même réseau local filaire** (ou
deux fenêtres sur une seule machine pour un test rapide). Lancez le jeu,
puis :

- **Hôte** : appuyez sur **H**. Un salon d'attente apparaît — attendez
  les joueurs, puis cliquez sur « Démarrer ». L'hébergement crée aussi
  l'avatar de l'hôte, le monstre et 5 gemmes.
- **Chaque autre joueur** : appuyez sur **J** pour ouvrir la liste des
  serveurs (ou tapez directement l'adresse de l'hôte).

Déplacez-vous avec les **flèches**. Marchez sur une gemme pour la
ramasser (+1 au score d'équipe partagé) ; toucher le monstre coûte un
point à l'équipe.

## Fonctionnement

| Objet | Rôle |
|---|---|
| `obj_ctrl` | Contrôleur invisible. Crée l'avatar de l'hôte, le monstre et 5 gemmes dès le début de l'hébergement ; crée un avatar pour chaque joueur qui se connecte (`player_joined`). Affiche le score d'équipe et les instructions. |
| `obj_person` | L'avatar — même motif de déplacement **Si je pilote cette instance** que `reseau_1`. Ses gestionnaires de collision avec la gemme/le monstre sont protégés par `global.is_host == 1` : seule la simulation de l'hôte détruit une gemme ou retire un point, car les collisions sur les copies fantômes locales d'un client ne comptent pas. |
| `obj_gem` | Passive — aucun événement propre. Détruite par le gestionnaire de collision de `obj_person` (`destroy_instance`, cible `other`). |
| `obj_monster` | Patrouille gauche-droite simulée par l'hôte (`step`, protégé par `global.is_host == 1`) — les clients n'exécutent jamais son IA localement ; ils voient seulement la position diffusée par l'hôte, interpolée comme toute autre instance synchronisée. |

- **L'hôte possède le monde**, même principe que `reseau_1` : seul
  l'hôte appelle `network_spawn`, et chaque action qui affecte le jeu
  (détruire une gemme, ajuster le score, déplacer le monstre) est
  protégée par `global.is_host == 1`. Le déplacement reste réactif pour
  tout le monde car l'avatar de chaque joueur est simulé localement sur
  sa propre machine (autorité du client sur son propre avatar
  uniquement).
- **Pourquoi le monstre ne téléporte pas le joueur touché au départ** :
  chez l'hôte, la position d'un avatar *possédé par un client* continue
  d'être signalée par ce client à chaque image — l'hôte la téléporter
  localement serait simplement écrasé par le prochain signalement du
  client. Retirer un point au score partagé évite complètement ce
  conflit tout en rendant le contact réellement coûteux.

## À essayer

- Ajoutez plus de gemmes, ou faites réapparaître une gemme ramassée
  après un délai plutôt que de la détruire définitivement.
- Donnez au monstre un second axe de patrouille (haut-bas en plus de
  gauche-droite), ou faites-le poursuivre l'avatar le plus proche au
  lieu de suivre un trajet fixe.
- Ajoutez une condition de victoire : une fois `global.team_score`
  atteint un objectif, envoyez un `send_network_message` avec
  l'événement `"victoire"` pour célébrer sur tous les écrans.

## Notes pour l'enseignant

- Ports utilisés : **45782/TCP** (jeu) et **45783/UDP** (découverte).
  Demandez au service informatique avant d'utiliser sur un réseau géré.
- **Les salles filaires fonctionnent le mieux.** Beaucoup de points
  d'accès Wi-Fi scolaires bloquent le trafic entre appareils, ce qui
  empêche totalement le multijoueur local.
- C'est le plus orienté « action » des exemples `reseau_*` — une bonne
  deuxième séance une fois que `reseau_1` (déplacement) et `reseau_2`
  (sans déplacement du tout, le plus tolérant au Wi-Fi) se sont bien
  passés.
