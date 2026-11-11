# Labyrinthe au trésor : gemmes, clés, portes et bombes

## Comment utiliser cette fiche

Tu as environ 90 minutes. Fais chaque partie sur ton écran, puis coche la case.
Si tu es bloqué, demande d'abord à ton voisin, puis à ton enseignant. À la fin,
tu auras un vrai jeu de trésor, et tu le transformeras en **un seul fichier** qui
marche dans un navigateur web, et même sur un téléphone !

## Partie 1 : ouvre ton jeu (5 min)

- [ ] Clique sur **Fichier > Ouvrir un projet** et ouvre le dossier **Treasure Maze**.
- [ ] Regarde la liste à gauche. Tu as déjà sept images (sprites) :
      **spr_wall**, **spr_door**, **spr_gem**, **spr_key**, **spr_heart**,
      **spr_bomb** et **spr_goal**. Il y a aussi un **obj_wall** et une salle
      appelée **room0** avec des murs sur le bord.
- [ ] Appuie sur le triangle vert (ou sur **F5**) pour tester. Tu vois une salle
      vide. Ferme la fenêtre du jeu.

> TIP : appuie souvent sur **Enregistrer**. Le bouton avec la disquette
> sauvegarde ton jeu.

## Partie 2 : dessine ton héros (10 min)

Toutes les autres images sont prêtes. Le héros, c'est à toi de le dessiner !

- [ ] Clique sur **Ressources > Créer un sprite**. Appelle-le `spr_hero`, puis OK.
- [ ] Dessine ton héros. Remplis le carré. Clique sur **Enregistrer**.

> TIP : les noms utilisent seulement des lettres, des chiffres et `_`. Pas
> d'espace !

## Partie 3 : crée les objets (12 min)

Une image toute seule ne fait rien. Un **objet** est quelque chose dans ton jeu
qui peut faire des choses. Crée un objet pour chaque image.

- [ ] Ouvre **obj_wall** (double-clique dessus). Coche **Solide**.
- [ ] Clique sur **Ressources > Créer un objet** pour chaque ligne de ce tableau.
      Choisis le sprite. Coche **Solide** seulement quand le tableau dit Oui.

| Nom de l'objet | Sprite | Solide ? |
|---|---|---|
| obj_wall (déjà là) | spr_wall | **Oui** |
| obj_door | spr_door | **Oui** |
| obj_gem | spr_gem | Non |
| obj_key | spr_key | Non |
| obj_heart | spr_heart | Non |
| obj_bomb | spr_bomb | Non |
| obj_goal | spr_goal | Non |
| obj_hero | spr_hero | Non |

> INFO : un objet **Solide** est un bloc comme un mur. Les murs et les portes
> sont solides. Les choses que tu ramasses ne le sont pas.

> DONE : tu dois voir huit objets dans la liste.

## Partie 4 : construis ton labyrinthe (15 min)

- [ ] Ouvre **room0** (double-clique dessus dans la liste).
- [ ] Clique sur **obj_wall**, garde le bouton de la souris enfoncé et **glisse**
      pour peindre des murs à l'intérieur du bord.
- [ ] Place les autres objets, un clic chacun :

| Place | Combien |
|---|---|
| **obj_hero** | 1, au départ |
| **obj_goal** | 1, loin du héros |
| **obj_gem** | au moins 3 |
| **obj_key** | 1, **avant** la porte |
| **obj_door** | en travers d'un chemin, aussi large que le chemin |
| **obj_heart** | 1, un peu caché |
| **obj_bomb** | 2 ou 3, au bord d'un chemin |

> INFO : fais **tous les chemins larges de deux carrés** ou plus. Ton héros ne
> s'arrête pas toujours au milieu d'un chemin. Dans un chemin d'un seul carré, il
> peut rester coincé.

> TIP : mets une bombe sur le côté d'un chemin large, jamais en travers de tout
> le chemin. Le héros doit pouvoir la contourner.

> TIP : la clé doit être à un endroit où le héros peut aller **sans** passer par
> une porte !

- [ ] Appuie sur **F5**. Tu vois ton labyrinthe. Rien ne bouge encore. C'est la
      suite !

## Partie 5 : fais-le fonctionner (33 min)

Ouvre chaque objet et construis ses blocs dans la zone **Blockly**. Glisse les
blocs depuis la gauche. Clique sur **Enregistrer** après chaque objet.

### 5a. Le héros bouge (8 min)

Ouvre **obj_hero**.

| Quand ça arrive | Fais ceci |
|---|---|
| **Clavier:** Flèche gauche (maintenue) | **définir vitesse horizontale à** -4 |
| **Clavier:** Flèche droite (maintenue) | **définir vitesse horizontale à** 4 |
| **Clavier:** Flèche haut (maintenue) | **définir vitesse verticale à** -4 |
| **Clavier:** Flèche bas (maintenue) | **définir vitesse verticale à** 4 |
| **Clavier: Aucune touche** | **arrêter le mouvement** |
| **Quand collision avec** obj_wall | **arrêter le mouvement** |
| **Quand collision avec** obj_door | **arrêter le mouvement** |

> TIP : fais un clic droit sur un bloc pour le **dupliquer**. C'est plus rapide
> que de glisser un nouveau bloc à chaque fois.

> DONE : appuie sur **F5**. Le héros marche et s'arrête devant les murs et les
> portes.

### 5b. Les gemmes (4 min)

Ouvre **obj_gem**. Mets les deux blocs sous le même événement.

| Quand ça arrive | Fais ceci |
|---|---|
| **Quand collision avec** obj_hero | **Ajouter au score** 10 |
| (le même événement) | **Détruire cette instance** |

### 5c. La clé ouvre les portes (4 min)

Ouvre **obj_key**.

| Quand ça arrive | Fais ceci |
|---|---|
| **Quand collision avec** obj_hero | **Détruire toutes les instances de** obj_door |
| (le même événement) | **Détruire cette instance** |

### 5d. Le cœur (3 min)

Ouvre **obj_heart**.

| Quand ça arrive | Fais ceci |
|---|---|
| **Quand collision avec** obj_hero | **Ajouter aux vies** 1 |
| (le même événement) | **Détruire cette instance** |

### 5e. Les bombes (6 min)

C'est le héros qui décide ce qui se passe. Ouvre **obj_hero** de nouveau et
ajoute cet événement :

| Quand ça arrive | Fais ceci |
|---|---|
| **Quand collision avec** obj_bomb | **Ajouter aux vies** -1 |
| (le même événement) | **Détruire autre instance** |
| (le même événement) | **arrêter le mouvement** |
| (le même événement) | **Sauter à la position de départ** |

> INFO : « autre instance » veut dire l'autre chose qui a été touchée : la
> bombe. La bombe explose et disparaît. Le héros retourne au départ.

### 5f. Le but (6 min)

Ouvre **obj_goal**. Celui-ci pose une question : reste-t-il des gemmes ?
Utilise le bloc **If**. Il a deux emplacements : **then** (quand la réponse est
oui) et **else** (quand la réponse est non).

| Où | Blocs |
|---|---|
| L'événement | **Quand collision avec** obj_hero |
| Sous l'événement | **If** count of object : écris `obj_gem` dans la case, garde `==`, et mets le nombre **0** |
| Dans **then** | **Afficher message** « Tu as gagné ! », puis **Redémarrer le Jeu** en dessous |
| Dans **else** | **Afficher message** « Ramasse toutes les gemmes d'abord ! » |

> INFO : le bloc **If** commence avec le nom `obj_coin` dans sa case — clique
> dedans et écris `obj_gem` à la place. S'il ne reste aucune gemme (0), les
> blocs dans **then** se passent, sinon ceux dans **else** se passent. (Les mots
> du bloc restent en anglais, même en français.)

### 5g. Fin de partie (2 min)

Ouvre **obj_hero** de nouveau.

| Quand ça arrive | Fais ceci |
|---|---|
| **Autre événement :** Plus de vies | **Afficher message** « Partie terminée ! » |
| (le même événement) | **Redémarrer le Jeu** |

> DONE : appuie sur **F5** et joue ! Ramasse toutes les gemmes, prends la clé,
> ouvre la porte, évite les bombes et atteins le but.

## Partie 6 : partage ton jeu (7 min)

- [ ] Clique sur **Fichier > Exporter en HTML5**.
- [ ] Choisis un dossier. Clique sur **Oui** pour ouvrir le jeu dans ton navigateur.
- [ ] Regarde dans le dossier : tu as **un seul fichier** qui finit par `.html`.
      C'est ton jeu !
- [ ] Joue-y. Puis montre-le à un ami.

> TIP : sur un téléphone ou une tablette, des boutons flèches apparaissent sur
> l'écran. Garde un bouton appuyé pour avancer.

## Tu es bloqué ?

| Ce qui se passe | Essaie ceci |
|---|---|
| Le héros ne bouge pas | Le héros est-il dans la salle ? Y a-t-il un bloc sous **Clavier** ? |
| Le héros traverse les murs ou les portes | Ajoute **Quand collision avec** obj_wall (ou obj_door) avec **arrêter le mouvement** |
| Le héros est coincé dans un chemin | Fais le chemin large de deux carrés |
| La clé ne fait rien | As-tu construit **Détruire toutes les instances de** obj_door dans obj_key ? |
| Je n'arrive pas à ouvrir la porte | La clé est-elle placée où le héros peut aller sans passer par une porte ? |
| Le but dit « Ramasse toutes les gemmes d'abord ! » | Il reste une gemme quelque part. Trouve-la ! |
| J'ai perdu toutes mes vies | Le jeu recommence. Fais attention aux bombes ! |
| J'ai supprimé quelque chose par erreur | **Outils > Restaurer les ressources supprimées** |

## Mots à connaître

- **Sprite** : une image
- **Objet** : quelque chose dans ton jeu qui peut faire des choses
- **Solide** : un objet qui est un bloc comme un mur
- **Événement** : « quand quelque chose arrive »
- **Collision** : quand deux choses se touchent
- **Vies** : le nombre d'essais qu'il te reste

## Défis

- **Essaie (5 min) :** change les points que donne une gemme, ou les messages.
- **Va plus loin :** ajoute une deuxième clé et d'autres portes, ou cache une
  gemme derrière une porte.
- **Invente :** change d'ordinateur avec un ami et essaie de gagner son labyrinthe.

## Réfléchis

1. Que fait la clé quand le héros la touche ?
2. Pourquoi le but peut-il dire « Ramasse toutes les gemmes d'abord ! » ?
3. Que se passe-t-il quand tu perds toutes tes vies ?

## Mes notes

[[notes:5]]
