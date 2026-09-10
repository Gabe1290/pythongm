# Échange de fichiers — Morpion (fichier_1)

Un morpion (Tic-Tac-Toe) à deux joueurs, joué via l'extension
**Multijoueur par échange de fichiers**
(`extensions/multiplayer_files/`) plutôt qu'une connexion réseau en
direct — les coups s'échangent par de simples fichiers sur un dossier
partagé. Voir [la page du wiki](../../wiki/FileExchange_fr.md) pour la
conception complète et l'histoire des années 1990 (VGA Planets, Stars!,
Diplomacy par courrier) dont ce principe est issu.

Contrairement à **reseau_1**–**reseau_4** (`extensions/multiplayer_lan/`,
une connexion réseau en direct), cet échantillon n'ouvre jamais aucun
port réseau — il fonctionne à travers un pare-feu d'établissement qui
bloque les connexions directes de machine à machine, du moment que les
deux machines peuvent déjà atteindre le même lecteur partagé.

## Lancer la partie

Deux machines pouvant toutes deux accéder au même dossier partagé (un
lecteur réseau mappé, un dossier Dropbox/OneDrive synchronisé, ...) — ou
une seule machine avec deux fenêtres Tester le Jeu pour une vérification
rapide en local.

1. **Sur la machine hôte :** ouvrez cet échantillon, appuyez sur
   **Tester le Jeu** (F5), puis sur **H** — vous jouez **X**. Par
   défaut, cela héberge dans un dossier nommé `tictactoe_files`, créé à
   côté de l'endroit où le jeu est lancé (suffisant pour un test sur une
   seule machine ; pour une vraie partie à deux machines, ouvrez
   l'événement clavier `h` de `obj_game` et changez le paramètre
   **Dossier partagé** de `Héberger une partie (échange de fichiers)`
   pour un chemin réel accessible depuis les deux machines — une lettre
   de lecteur mappé, ou un chemin UNC du type
   `\\serveur\partage\morpion`).
2. **Sur la machine qui rejoint :** appuyez sur **Tester le Jeu**, puis
   sur **J** — un petit écran apparaît demandant le chemin du dossier
   partagé. Tapez le *même* chemin que celui utilisé par l'hôte
   (`tictactoe_files` pour un test sur une seule machine) et appuyez sur
   Entrée ou sur **Se connecter**. Vous jouez **O**.
3. Cliquez sur une case à votre tour. Le bas de la fenêtre indique à qui
   c'est le tour.

## Comment ça marche

| Objet | Rôle |
|---|---|
| `obj_game` | Tout — la seule instance de la salle. Son événement clavier `h` appelle directement `Héberger une partie (échange de fichiers)` et fixe immédiatement la marque de cette machine à X (héberger réussit ou échoue de façon synchrone — aucune incertitude à attendre). Son événement clavier `j` appelle `Rejoindre une partie (échange de fichiers)` avec **Dossier partagé = `"auto"`**, ce qui ouvre l'écran de connexion intégré pour taper le chemin ; la marque n'est fixée à O que dans l'événement **Session de fichiers démarrée**, une fois que l'hôte a réellement accueilli cette machine — jamais de façon synchrone juste après l'appui sur la touche, car une connexion en `"auto"` peut être annulée à cet écran, et le jeu ne doit pas croire qu'il joue une partie qui n'a jamais commencé. Son événement **Step** détermine à qui c'est le tour d'après la parité de `global.round_number` et, sur la machine dont ce n'est *pas* le tour, appelle `Terminer le tour (échange de fichiers)` sans rien avoir préparé — un « passe » — pour que la manche se résolve rapidement plutôt que d'attendre tout le `round_deadline`. |

Le plateau est composé de neuf variables partagées (`cell_0_0` …
`cell_2_2`, colonne puis ligne), chacune définie avec `Définir une
variable partagée (échange de fichiers)` et publiée vers l'autre machine
seulement une fois `Terminer le tour (échange de fichiers)` appelé et la
manche assemblée par l'hôte — c'est toute la raison d'être de cette
extension : les écritures ne prennent effet qu'à la prochaine manche
publiée, jamais instantanément, puisqu'il n'y a pas de connexion en
direct à écraser.

Les deux machines évaluent la condition de victoire indépendamment sur
le même plateau publié (vérifiée pour *les deux* marques, pas seulement
« ma propre marque a-t-elle gagné » — un joueur perdant doit lui aussi
être informé que la partie est terminée), et un plateau plein sans ligne
alignée est un match nul.

## Pistes à explorer

- Ajouter une revanche : quand `won == 1`, appeler `Quitter la partie
  (échange de fichiers)` et réinitialiser `won`/`my_mark`/les variables
  de case, pour qu'un nouvel appui sur H/J relance une partie sans
  redémarrer tout l'échantillon.
- Envoyer un `Message réseau personnalisé (échange de fichiers)` quand
  un joueur gagne (`target = all`) et faire réagir la machine perdante
  différemment de sa propre détection de défaite basée sur le plateau —
  un avant-goût de `send_network_message_files` au-delà du simple
  plateau partagé.
- Élargir le plateau à 4×4 (il faut alors gagner avec une ligne de 3
  n'importe où) comme exercice de condition de victoire plus poussé.

## Notes pour les enseignants

- **Aucun port, aucune exception de pare-feu nécessaire** — c'est toute
  la raison d'être de cette extension. Si le multijoueur LAN de
  `reseau_*` est bloqué par le service informatique de l'établissement,
  voici la solution de repli : il ne faut qu'un accès en lecture/écriture
  à un lecteur partagé que la classe utilise déjà.
- **Le dossier partagé doit être réel et accessible depuis les deux
  machines** — contrairement à la découverte de serveurs du multijoueur
  LAN, il n'y a ici aucun balayage réseau, juste un chemin tapé au
  clavier (Phase 4 du plan ; un véritable navigateur de dossiers reste
  explicitement hors du périmètre). Pointez les deux machines vers
  exactement le même chemin ; l'écran de connexion refuse un chemin
  inexistant ou non accessible en écriture avant même de tenter de se
  connecter.
- Une manche peut prendre quelques secondes à se résoudre sur un lecteur
  réseau lent ou très chargé — l'extension vérifie une fois par seconde,
  pas à chaque image, c'est voulu (voir la section « pourquoi c'est
  différent du multijoueur LAN » de la page du wiki).
- Ordinateur uniquement (pas d'export HTML5 / Android pour cette
  extension).
