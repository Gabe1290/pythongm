# Réseau — Salle partagée (reseau_1)

Un premier jeu multijoueur en réseau local : **chaque joueur déplace son
propre carré, et tout le monde voit tout le monde bouger en temps réel.**

## Lancer le jeu

Il faut **deux machines sur le même réseau local filaire** (ou deux
terminaux sur une seule machine pour un test rapide).

**Hôte** (joueur 0) :

```
PYGM_NET_AUTOHOST=1 python runtime/run_game.py samples/reseau_1/project.json
```

**Chaque autre joueur** — remplacez `<IP-HOTE>` par l'adresse locale de la
machine hôte (affichée dans le titre de sa fenêtre, ou via `ipconfig` /
`ip addr`) :

```
PYGM_NET_AUTOJOIN=<IP-HOTE> python runtime/run_game.py samples/reseau_1/project.json
```

Pour un test sur une seule machine, utilisez
`PYGM_NET_AUTOJOIN=127.0.0.1`.

Déplacez-vous avec les **flèches**. Le titre de la fenêtre indique l'état
de la connexion.

## Fonctionnement

| Objet | Rôle |
|---|---|
| `obj_ctrl` | Contrôleur invisible. À **Démarrage du jeu** il `network_spawn` l'avatar de l'hôte (propriétaire `0`) ; à **Joueur connecté** (`player_joined`) il en crée un pour le nouveau joueur, propriétaire = `global.network_sender`. Il affiche aussi la ligne d'instructions. |
| `obj_person` | L'avatar. Son événement **Étape** est protégé par **Si je pilote cette instance** (`is_instance_owner`) : seule la machine propriétaire lit les flèches et le déplace. Sur toutes les autres machines, la même instance est un *fantôme* interpolé piloté par les instantanés de l'hôte. |

L'idée centrale — **l'hôte possède le monde**. Seul l'hôte exécute
`network_spawn` ; il attribue chaque avatar à un joueur avec le paramètre
`owner`. Un client dont le numéro correspond au propriétaire d'un avatar
simule cet avatar localement (pour qu'il réagisse bien) et renvoie sa
position à l'hôte, qui la retransmet à tout le monde.

## À essayer

- Ajoutez un événement **collision_with_obj_person** sur `obj_person`,
  protégé par `global.is_host == 1`, qui écarte les joueurs — les
  collisions ne comptent que chez l'hôte.
- Dans **Joueur connecté**, `set_shared_var "scores_" + player_id` à 0,
  puis donnez un point à chaque joueur pour une action et affichez le
  tableau des scores partagé (`draw_text`) sur tous les écrans.
- Donnez une couleur à chaque joueur : dans **Création** de `obj_person`,
  protégé par `is_instance_owner`, teintez selon `global.player_id`.

## Notes pour l'enseignant

- Ports utilisés : **45782/TCP** (jeu) et **45783/UDP** (découverte).
  Demandez au service informatique avant d'utiliser sur un réseau géré.
- **Les salles filaires fonctionnent le mieux.** Beaucoup de points
  d'accès Wi-Fi scolaires bloquent le trafic entre appareils, ce qui
  empêche totalement le multijoueur local — aucun logiciel ne peut
  contourner cela.
- Si l'hébergement échoue, c'est presque toujours le pare-feu du système
  qui demande d'« autoriser les connexions entrantes » — un enseignant ou
  un administrateur doit parfois l'accepter une fois.
