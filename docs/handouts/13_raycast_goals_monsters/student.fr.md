# PyGameMaker — Tutoriel 13 : 2.5D, objectifs, gemmes et monstres

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > 2.5D : Objectifs, gemmes et monstres** (4 pages, environ 30 minutes). Tu poursuis la salle du Tutoriel 11 (les textures du Tutoriel 12 sont facultatives). Cette leçon n'est pas dans l'édition débutant. Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Ton labyrinthe à la première personne devient un vrai jeu : ramasse des gemmes pour gagner des points, évite un monstre qui patrouille (le toucher coûte une vie), et atteins la sortie, qui ne s'ouvre que lorsque toutes les gemmes sont à toi.

## Phase 1 : Gemmes et score

- [ ] **1.** Crée un sprite `spr_gem` (16×16, un diamant jaune) et un objet `obj_gem` avec ce sprite. Laisse **Solide** décoché.
- [ ] **2.** Dans `obj_gem` : **Quand collision avec obj_player** avec *Détruire cette instance* ; et un événement **Destroy** (destruction) avec *Ajouter au score 10*.
- [ ] **3.** Dans `obj_player`, ajoute un événement **Game Start** (dans *Autres événements*) : *Définir le score à 0* et *Définir les vies à 3*. Ne les mets **pas** dans Création.
- [ ] **4.** Dans la salle, place quelques gemmes dans des couloirs dégagés, en dehors des murs, la première en ligne droite devant le joueur.

> DONE: **Tu dois voir :** appuie sur **F5**. Les gemmes flottent devant toi et grossissent quand tu approches. Marche dedans : elle disparaît et tu gagnes 10 points. Une gemme derrière un mur est cachée tant que le mur la masque. (Tu ne vois pas encore le score : c'est le Tutoriel 14.)

## Phase 2 : Le monstre et les vies

- [ ] **5.** Crée un sprite `spr_monster` (16×16, rouge) et un `obj_monster` non solide. **Quand créé** : *Commencer à bouger (direction)* gauche et droite, vitesse 2. **Quand collision avec obj_wall** : *Inverser horizontalement*.
- [ ] **6.** Place le monstre dans une longue rangée droite pour qu'il ait de la place pour patrouiller.
- [ ] **7.** Dans `obj_player` : **Quand collision avec obj_monster** : *Définir les vies à -1* (Relatif), puis *Redémarrer la salle*. **No More Lives** (plus de vies) : *Redémarrer le jeu*.

> DONE: **Tu dois voir :** appuie sur **F5**. Le monstre glisse le long de son couloir et fait demi-tour à chaque bout. Tu le vois arriver, et il se cache derrière les murs. Le toucher coûte une vie ; après la troisième, la partie recommence.

## Phase 3 : La sortie

- [ ] **8.** Crée un sprite `spr_goal` (16×16, bleu) et un `obj_goal` non solide.
- [ ] **9.** Dans `obj_goal`, **Quand collision avec obj_player** avec deux vérifications : *Tester le nombre d'instances de* `obj_gem` *égal à 0* : *Début de bloc*, *Afficher un message* « You win! », *Redémarrer le jeu*, *Fin de bloc*. Puis *Tester le nombre d'instances de* `obj_gem` *supérieur à 0* : *Début de bloc*, *Afficher un message* « Collect all the gems first! », *Fin de bloc*.
- [ ] **10.** Place `obj_goal` dans la salle.

> DONE: **Tu dois voir :** appuie sur **F5**. Entre dans le but alors qu'il reste des gemmes : tu obtiens l'avertissement. Ramasse toutes les gemmes, puis entre dans le but : « You win! ».

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
| Je ne vois pas les gemmes | La gemme est Solide (elle devient un mur) ou n'a pas de sprite | Décoche **Solide** ; donne-lui un sprite |
| La gemme ne disparaît pas | L'événement de collision manque, ou il est sur le mauvais objet | Ajoute **Quand collision avec obj_player** à `obj_gem` |
| Je ne gagne aucun point | L'événement **Destroy** avec *Ajouter au score 10* manque | Ajoute-le à `obj_gem` |
| Je récupère toutes mes vies après un contact | Les vies ont été réglées dans **Création**, qui se relance à chaque redémarrage | Règle le score et les vies dans **Game Start** |
| Le monstre ne bouge pas | L'événement **Quand créé** manque, ou le monstre n'est pas dans la salle | Ajoute *Commencer à bouger (direction)* ; place-le |
| Le monstre traverse les murs | Pas d'événement **Quand collision avec obj_wall** sur le monstre | Ajoute-le avec *Inverser horizontalement* |
| La sortie me laisse partir avec des gemmes restantes | La vérification du nombre manque ou utilise un mauvais nombre | Utilise *Tester le nombre d'instances de obj_gem égal à 0* pour la branche de victoire |
| La sortie ne me fait jamais gagner | Les vérifications utilisent un mauvais nom d'objet, ou une gemme est inaccessible | Vérifie le nom ; assure-toi que chaque gemme est accessible |

## Défis

- **Essaie (5 minutes) :** rends le monstre plus rapide (vitesse 4), ou change la valeur d'une gemme.
- **Va plus loin :** ajoute un second monstre dans un autre couloir, ou une gemme « trésor » qui vaut 50.
- **Invente :** construis une seconde salle avec **Salle suivante** à la sortie, avec son propre objet caméra et ses propres textures.

## Vocabulaire

| Terme | Ce que cela veut dire |
| Panneau (billboard) | Une image qui te fait toujours face, dessinée dans la vue 3D pour les objets non solides |
| Occlusion | Caché derrière quelque chose (une gemme derrière un mur) |
| Game Start | Un événement qui s'exécute une fois, au début de toute la partie |
| Nombre d'instances | Combien de copies d'un objet existent en ce moment |
| Patrouiller | Aller et venir le long d'un chemin fixe |

## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Quels objets apparaissent comme des panneaux dans la vue à la première personne, et lesquels deviennent des murs ?
2. Pourquoi règle-t-on les vies dans **Game Start** et non dans **Création** ?
3. Comment la sortie sait-elle que toutes les gemmes ont été ramassées ?

## Mes notes

[[notes:10]]
