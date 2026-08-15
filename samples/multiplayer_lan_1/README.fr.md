# Multijoueur LAN — Démo

Une démonstration minimale de l'extension **LAN Multiplayer**
(`extensions/multiplayer_lan/`) — un carré bleu que vous déplacez avec les
flèches du clavier, et un second lancement séparé du même projet qui
observe ses déplacements en temps réel sur votre réseau local.

## Contrôles

| | |
|---|---|
| Flèches du clavier | Déplacer le carré dans la salle |

## Ce que ça démontre

Le `obj_player` de ce projet ne contient **aucune configuration
multijoueur** — pas d'action `set_network_mode`, rien du tout. C'est tout
l'intérêt : lancez-le normalement
(`python3 runtime/run_game.py samples/multiplayer_lan_1/project.json`, ou
Tester le jeu depuis l'IDE) et c'est un simple jeu solo qui déplace un
carré, sans aucun réseau. Le mode LAN s'active uniquement en ligne de
commande, avec deux lancements distincts du même projet :

```bash
# Terminal 1 — l'hôte (celui-ci contrôle le carré avec les flèches)
python3 runtime/run_game.py samples/multiplayer_lan_1/project.json en --net-host

# Terminal 2 — un client sur la même machine ou le même réseau local (127.0.0.1 pour la même machine)
python3 runtime/run_game.py samples/multiplayer_lan_1/project.json en --net-client 127.0.0.1
```

La fenêtre du client reflète en temps réel le carré de l'hôte. **Dans
cette première version, le client est un pur spectateur** — ses propres
appuis sur les flèches ne déplacent rien de façon durable, puisque chaque
instantané réseau envoyé par l'hôte écrase à nouveau la position de
l'instance synchronisée dès la trame suivante. Cela correspond exactement
au périmètre documenté de l'extension (voir la section « Explicitement
hors périmètre » de `docs/MULTIPLAYER_LAN_PLAN.md`) : il s'agit de « voir
où se trouve l'autre joueur », pas d'une simulation bidirectionnelle et
autoritaire — faire du client un second joueur contrôlable est une
évolution future légitime, pas un raccourci pris ici.

Si vous préférez construire un menu « Héberger » / « Rejoindre »
directement dans le jeu plutôt qu'en ligne de commande, la même
fonctionnalité est disponible via l'action `set_network_mode` (`mode` :
host/client, `host`, `port`) — appelez-la depuis la logique d'un objet
menu plutôt que de dépendre des options de ligne de commande.

## État du moteur

**Ordinateur uniquement.** Le multijoueur LAN n'a pas encore de prise en
charge pour l'export HTML5 ou Kivy (Android) — voir les notes de
périmètre de `docs/MULTIPLAYER_LAN_PLAN.md`. Cet exemple n'est donc pas
inclus dans la matrice de tests d'export HTML5/Kivy.
