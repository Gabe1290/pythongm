# Multijoueur par échange de fichiers

*[Accueil](Home_fr) | [Réseau](Network_fr) | [Extensions](Extensions_fr)*

---

> **Pas encore livré.** Cette page documente la conception prévue
> (`docs/MULTIPLAYER_FILE_EXCHANGE_PLAN.md`) pour qu'elle soit prête dès que
> l'extension sera là. **Ne publiez pas cette page (ni les liens croisés
> vers elle sur Accueil/Extensions/Réseau) sur le wiki en ligne avant que
> `extensions/multiplayer_files/` existe réellement et que cette remarque
> soit retirée.**

---

PyGameMaker peut aussi transformer un projet en **jeu multijoueur au tour
par tour qui échange son état via des fichiers sur un lecteur partagé**,
plutôt que par une connexion réseau en direct. C'est une bonne solution
pour une école où la connexion directe de machine à machine du [Réseau
(multijoueur LAN)](Network_fr) est bloquée par un pare-feu (fréquent sur un
profil réseau « Public » géré), mais où le lecteur partagé de la classe est
déjà ouvert à toutes les machines. Cette fonctionnalité est fournie par
l'**extension Multijoueur par échange de fichiers**
[(voir Extensions)](Extensions_fr).

L'exemple fourni **Morpion par échange de fichiers** est un jeu complet et
jouable : deux joueurs jouent chacun leur tour, chaque coup étant écrit
dans un fichier sur le lecteur partagé et lu par l'autre machine.

Pris en charge aujourd'hui : l'export **ordinateur** (pygame) uniquement,
en hôte comme en client. Voir « Pourquoi pas tous les exports » ci-dessous
pour savoir pourquoi HTML5 et Kivy/Android n'ont pas cette extension.

---

## En quoi c'est différent du Réseau (multijoueur LAN)

Le [Réseau (multijoueur LAN)](Network_fr) interroge une connexion réseau en
direct environ 60 fois par seconde — parfait pour un avatar partagé qui se
déplace en douceur dans une salle, mais cela nécessite une connexion
directe entre les machines que certains réseaux scolaires bloquent
purement et simplement.

Le Multijoueur par échange de fichiers lit et écrit à la place de petits
fichiers sur un lecteur réseau partagé — le même lecteur que les deux
machines utilisent déjà pour leurs propres fichiers, et qui est presque
toujours laissé ouvert même quand les connexions directes entre machines
ne le sont pas. Il vérifie s'il y a un nouveau tour environ une fois par
seconde, pas à chaque image, car une véritable lecture/écriture sur un
lecteur réseau peut prendre de quelques millisecondes à beaucoup plus
longtemps selon le serveur de l'école — un déplacement fluide et continu
n'est donc pas possible de cette façon, seul le jeu **au tour par tour**
l'est : un quiz, un morpion, une bataille navale, un jeu de négociation —
tout ce où un joueur agit, puis attend les autres.

**Utilisez le Réseau (multijoueur LAN)** quand vous voulez des avatars qui
se déplacent en direct. **Utilisez le Multijoueur par échange de fichiers**
quand jouer chacun son tour convient et qu'il faut contourner un pare-feu
scolaire.

---

## D'où vient cette idée

Échanger l'état d'un jeu via des fichiers, plutôt que par une connexion en
direct, n'est pas une idée nouvelle — c'est ainsi que tout un genre de jeux
multijoueurs fonctionnait avant que les connexions internet permanentes ne
soient courantes :

- Les **jeux par correspondance** (par courrier postal, puis par
  courriel), qui remontent à des décennies, sont la véritable origine : un
  « arbitre » humain ou informatique rassemblait le coup envoyé par chaque
  joueur, les traitait ensemble, puis renvoyait les résultats par courrier.
  Personne n'avait besoin d'être en ligne — ni même éveillé — au même
  moment.
- **VGA Planets** (1992) et **Stars!** (1995), deux jeux de stratégie
  classiques sur DOS/Windows, ont automatisé exactement ce processus :
  chaque tour d'un joueur produisait un petit fichier, un programme
  « hôte » combinait les fichiers de tout le monde pour produire le résultat
  du tour suivant, et les joueurs échangeaient ces fichiers par disquette,
  modem, puis plus tard par courriel — le fichier *était* tout le
  protocole.
- Les jeux « porte » de BBS (petits serveurs accessibles par modem) comme
  *Trade Wars 2002* et *Legend of the Red Dragon* utilisaient une idée
  voisine — le tour de chaque joueur était enregistré puis relu plus tard
  par qui en avait besoin, quel que soit le moment, plutôt que d'exiger que
  tout le monde soit connecté en même temps.

Le Multijoueur par échange de fichiers modernise cette même idée sur un
lecteur partagé de classe, avec les jeux des deux joueurs déjà en train de
tourner en même temps : **chaque coup d'un joueur est son propre fichier,
et deux joueurs n'écrivent jamais le même fichier** — il n'y a donc jamais
de risque de conflit d'écriture, la même protection dont bénéficiaient déjà
gratuitement les jeux par correspondance d'origine, puisqu'une seule lettre
était lue à la fois.

---

## Comment ça fonctionne

- Un joueur exécute **Héberger une partie (fichiers)**, en indiquant un
  dossier partagé que les deux machines peuvent atteindre. Cette machine
  devient l'**hôte** et l'arbitre de la partie.
- Les autres joueurs exécutent **Rejoindre une partie (fichiers)** avec le
  même dossier. Si l'hôte est injoignable, **la partie continue en solo**,
  la même garantie que donne déjà le [Réseau (multijoueur LAN)](Network_fr).
- À chaque tour, chaque joueur écrit son coup dans son propre fichier puis
  exécute **Terminer le tour**. Une fois que l'hôte a reçu le coup de
  chaque joueur (ou qu'un délai d'attente est dépassé), il publie le
  nouvel état de la partie pour que tout le monde le lise.
- L'identité du joueur et l'état du tour sont toujours lisibles via des
  variables globales : `global.is_host`, `global.player_id`,
  `global.player_count`, `global.round_number`, `global.turn_ready`,
  `global.waiting_for_players`.
- Une variable partagée définie avec **Définir une variable partagée**
  devient lisible *partout* via `global.<nom>` — mais seulement une fois
  que l'hôte a publié le tour suivant, pas instantanément comme avec la
  version du [Réseau (multijoueur LAN)](Network_fr). Votre propre
  changement n'apparaît pas non plus en avance sur votre propre écran.

---

## Les actions

| Action | Ce qu'elle fait |
|--------|-----------------|
| **Héberger une partie (fichiers)** | Devenir l'hôte ; créer/réserver le dossier partagé de la partie. |
| **Rejoindre une partie (fichiers)** | Se connecter au dossier partagé d'un hôte. |
| **Quitter la partie (fichiers)** | Arrêter de jouer ; laisse les fichiers des autres joueurs intacts. |
| **Définir une variable partagée** | Préparer une variable à publier avec votre prochain tour. |
| **Lire une variable partagée** | Copier une variable partagée dans une variable globale (pour un calcul). |
| **Terminer le tour** | Soumettre tout ce qui a été préparé ce tour comme votre coup. |
| **Envoyer un message réseau** | Joindre un petit événement personnalisé à votre prochain tour. |

Voir la [Référence Complète des Actions](Full-Action-Reference_fr) pour
tous les paramètres.

## Les événements

| Événement | Se déclenche quand |
|-----------|---------------------|
| **Session de fichiers démarrée** *(File Session Started)* | Un client termine sa connexion au dossier partagé de l'hôte. |
| **Joueur connecté (fichiers)** *(Player Joined Files)* | La demande de connexion d'un nouveau joueur est acceptée. |
| **Tour résolu** *(Round Resolved)* | L'hôte a publié l'état d'un nouveau tour et cette machine l'a récupéré. |
| **Tour manqué** *(Player Skipped Round)* | Le tour d'un joueur n'a pas été soumis avant la fin du délai d'attente. |
| **Session de fichiers perdue** *(File Session Lost)* | Le dossier partagé est devenu illisible (lecteur déconnecté, droits modifiés). |

---

## Un tour minimal de morpion (tours arbitrés par l'hôte)

Dans un objet contrôleur de salle :

- **Création :** `Héberger une partie (fichiers)` pointant vers le dossier
  partagé, si c'est la machine de l'enseignant, sinon `Rejoindre une
  partie (fichiers)` avec le même dossier.
- Au clic sur une case, gardé par `global.turn_ready` et le fait que ce
  soit le tour de ce joueur : `Définir une variable partagée` enregistrant
  la case choisie, puis `Terminer le tour`.
- **Tour résolu :** redessiner la grille à partir des variables partagées
  publiées, et vérifier une victoire.

---

## Pourquoi pas tous les exports

**HTML5** — une page de navigateur ne peut pas du tout écrire sur un
chemin de lecteur partagé arbitraire sans permissions supplémentaires
qu'une salle informatique scolaire n'a probablement pas accordées ; cette
extension ne tente donc pas de le faire là.

**Kivy/Android** — écrire sur un partage réseau depuis une application
téléphone ou tablette se heurte aux mêmes restrictions de stockage
modernes, et un appareil mobile n'est souvent même pas sur le même réseau
local que le lecteur partagé.

Ces deux restrictions ont exactement la même forme que celles déjà en
place pour le [Réseau (multijoueur LAN)](Network_fr) — voir la remarque
« Pris en charge aujourd'hui » de la page [Réseau](Network_fr).

---

## Remarques et limites

- **Un lecteur réseau partagé que les deux machines peuvent déjà
  écrire** — pas d'internet, pas de serveur, aucun port à ouvrir, mais il
  faut bien que ce lecteur partagé soit réellement accessible en écriture
  depuis les deux machines.
- **Tour par tour uniquement.** Il n'y a aucun moyen de déplacer quelque
  chose en douceur avec cette extension — c'est le rôle du [Réseau
  (multijoueur LAN)](Network_fr).
- **L'hôte fait autorité.** Si les coups de deux joueurs entrent
  véritablement en conflit (choisir la même case, par exemple), c'est la
  logique de jeu de l'hôte qui tranche — la même règle « le premier coup
  valide l'emporte » qu'un jeu ordinaire en chaise tournante utiliserait.
- Si l'extension Multijoueur par échange de fichiers est **désactivée**,
  ces actions et événements ne font simplement rien — voir
  [Extensions](Extensions_fr).

---

## Voir aussi

- [Réseau](Network_fr) — la variante à connexion en direct, pour les jeux
  qui ont besoin d'un mouvement fluide en temps réel
- [Extensions](Extensions_fr) — comment le Multijoueur par échange de
  fichiers est fourni et comment le désactiver
- [Référence Complète des Actions](Full-Action-Reference_fr) — chaque
  action et paramètre
- [Référence des Événements](Event-Reference_fr) — les événements
  d'échange de fichiers en contexte
