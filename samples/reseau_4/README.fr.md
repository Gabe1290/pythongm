# Réseau — Salle partagée (Test Game) — reseau_4

La même idée que **reseau_1** (une salle partagée où chaque joueur pilote
son propre carré et où tout le monde voit tout le monde bouger), mais on
la lance **directement depuis le bouton Tester le jeu de l'IDE** — sans
ligne de commande ni variable d'environnement.

## Comment jouer

Deux machines sur le même réseau local **filaire** (ou deux fenêtres
Tester le jeu sur une seule machine pour un essai rapide).

1. **Sur les deux machines :** ouvrez cet exemple et appuyez sur
   **Tester le jeu** (F5).
2. Sur la machine qui héberge, appuyez sur **H**. Un petit écran « en
   attente de joueurs » apparaît — appuyez sur **Démarrer** quand tout
   le monde a rejoint.
3. Sur chaque autre machine, appuyez sur **J**. Choisissez l'hôte dans
   la liste (ou saisissez son adresse réseau), puis connectez-vous.
4. Déplacez votre carré avec les **flèches**. Le titre de la fenêtre
   indique l'état de la connexion.

Si rien n'apparaît dans la liste des serveurs à l'étape 3, saisissez
l'adresse de l'hôte à la main — elle est affichée dans le titre de sa
fenêtre (ou lancez `ip addr` / `ipconfig`). Essai sur une seule
machine : connectez-vous à `127.0.0.1`.

## Comment ça marche

| Objet | Rôle |
|---|---|
| `obj_ctrl` | Contrôleur invisible, placé dans la salle. Son événement **clavier `h`** appelle `host_game` avec **Salon d'attente** (`show_lobby: true`) ; **clavier `j`** appelle `join_game` avec **Adresse de l'hôte = `auto`** (écran de connexion intégré). Sur **Partie réseau démarrée** (`network_game_started`), il fait un `network_spawn` de l'avatar de l'hôte (propriétaire `0`, protégé par `global.is_host == 1`) ; sur **Joueur connecté** (`player_joined`), il en crée un pour le nouveau joueur, propriétaire = `global.network_sender`. Il dessine aussi le menu H/J tant que la connexion n'est pas établie. |
| `obj_person` | L'avatar. Son événement **Étape** est protégé par **Si je pilote cette instance** (`is_instance_owner`) : seule la machine propriétaire lit les flèches. Sur toutes les autres machines, la même instance est un *fantôme* interpolé, piloté par les instantanés de l'hôte. |

La création se fait sur `network_game_started`, **pas** sur `game_start` —
dans ce déroulé piloté par un menu, la session réseau n'existe pas encore
au démarrage de la salle, seulement après que le joueur a appuyé sur H
ou J.

## Notes pour les enseignants

- Ports : **45782/TCP** (jeu) et **45783/UDP** (découverte). Demandez au
  service informatique avant d'utiliser sur un réseau géré.
- **Les salles filaires fonctionnent le mieux.** Beaucoup de points
  d'accès Wi-Fi scolaires bloquent le trafic entre appareils, ce qui
  empêche tout multijoueur en réseau local.
- Au premier hébergement, le pare-feu du système demandera sans doute
  d'« autoriser les connexions entrantes » — un enseignant/administrateur
  devra peut-être l'approuver une fois.
- Bureau uniquement (pas d'export HTML5 / Android pour le multijoueur en
  réseau local).
