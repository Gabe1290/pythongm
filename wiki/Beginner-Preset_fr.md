# Preset Debutant

*[Accueil](Home_fr) | [Guide des Presets](Preset-Guide_fr) | [Preset Intermediaire](Intermediate-Preset_fr)*

Le preset **Debutant** est concu pour les utilisateurs qui decouvrent le developpement de jeux. Il fournit un ensemble selectionne d'evenements et d'actions essentiels qui couvrent les bases de la creation de jeux 2D simples sans submerger les debutants avec trop d'options.

## Apercu

Le preset Debutant comprend :
- **4 Types d'Evenements** - Pour reagir aux situations du jeu
- **17 Types d'Actions** - Pour controler le comportement du jeu
- **6 Categories** - Evenements, Mouvement, Score/Vies/Sante, Instance, Salle, Sortie

---

## Evenements

Les evenements sont des declencheurs qui reagissent a des situations specifiques dans votre jeu. Lorsqu'un evenement se produit, les actions que vous avez definies pour cet evenement s'executent.

### Evenement Create

| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_create` |
| **Categorie** | Evenements |
| **Description** | Declenche une fois lorsqu'une instance est creee pour la premiere fois |

**Quand il se declenche :** Immediatement lorsqu'une instance d'objet est placee dans une salle ou creee avec l'action "Creer une Instance".

**Utilisations courantes :**
- Initialiser des variables
- Definir la position de depart
- Definir la vitesse ou la direction initiale
- Reinitialiser le score au debut du jeu

---

### Evenement Step

| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_step` |
| **Categorie** | Evenements |
| **Description** | Declenche a chaque image (generalement 60 fois par seconde) |

**Quand il se declenche :** En continu, a chaque image du jeu.

**Utilisations courantes :**
- Mouvement continu
- Verification des conditions
- Mise a jour de l'etat du jeu
- Controle de l'animation

---

### Evenement Touche Pressee

| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_keyboard_press` |
| **Categorie** | Evenements |
| **Description** | Declenche une fois lorsqu'une touche specifique est enfoncee |

**Quand il se declenche :** Une fois au moment ou une touche est pressee (pas pendant qu'elle est maintenue).

**Touches supportees :** Touches flechees (haut, bas, gauche, droite), Espace, Entree, lettres (A-Z), chiffres (0-9)

**Utilisations courantes :**
- Controles de mouvement du joueur
- Saut
- Tir
- Navigation dans les menus

---

### Evenement Collision

| Propriete | Valeur |
|-----------|--------|
| **Nom du Bloc** | `event_collision` |
| **Categorie** | Evenements |
| **Description** | Declenche lorsque cette instance entre en collision avec un autre objet |

**Quand il se declenche :** A chaque image ou deux instances se chevauchent.

**Variable speciale :** Dans un evenement de collision, `other` fait reference a l'instance avec laquelle il y a collision.

**Utilisations courantes :**
- Collecter des objets (pieces, bonus)
- Subir des degats des ennemis
- Heurter des murs ou des obstacles
- Atteindre des objectifs ou des points de controle

---

## Actions

Les actions sont des commandes qui s'executent lorsqu'un evenement est declenche. Plusieurs actions peuvent etre ajoutees a un seul evenement et s'executeront dans l'ordre.

---

## Actions de Mouvement

### Definir la Vitesse Horizontale

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_hspeed` |
| **Nom du Bloc** | `move_set_hspeed` |
| **Categorie** | Mouvement |
| **Icone** | ↔️ |

**Description :** Definit la vitesse de mouvement horizontal de l'instance.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Vitesse en pixels par image. Positif = droite, Negatif = gauche |

**Exemple :** Definissez `value` a `4` pour se deplacer vers la droite a 4 pixels par image, ou `-4` pour aller vers la gauche.

---

### Definir la Vitesse Verticale

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_vspeed` |
| **Nom du Bloc** | `move_set_vspeed` |
| **Categorie** | Mouvement |
| **Icone** | ↕️ |

**Description :** Definit la vitesse de mouvement vertical de l'instance.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Vitesse en pixels par image. Positif = bas, Negatif = haut |

**Exemple :** Definissez `value` a `-4` pour monter a 4 pixels par image, ou `4` pour descendre.

---

### Arreter le Mouvement

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `stop_movement` |
| **Nom du Bloc** | `move_stop` |
| **Categorie** | Mouvement |
| **Icone** | 🛑 |

**Description :** Arrete tout mouvement en mettant la vitesse horizontale et verticale a zero.

**Parametres :** Aucun

**Utilisations courantes :**
- Arreter le joueur lorsqu'il heurte un mur
- Arreter les ennemis lorsqu'ils atteignent une destination
- Mettre le mouvement en pause temporairement

---

### Sauter a une Position

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `jump_to_position` |
| **Nom du Bloc** | `move_jump_to` |
| **Categorie** | Mouvement |
| **Icone** | 📍 |

**Description :** Deplace instantanement l'instance a une position specifique (pas de mouvement fluide).

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Coordonnee X cible |
| `y` | Nombre | Coordonnee Y cible |

**Exemple :** Sauter a la position (100, 200) pour teleporter le joueur a cet emplacement.

---

## Actions d'Instance

### Detruire une Instance

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `destroy_instance` |
| **Nom du Bloc** | `instance_destroy` |
| **Categorie** | Instance |
| **Icone** | 💥 |

**Description :** Supprime une instance du jeu.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `target` | Choix | `self` = detruire cette instance, `other` = detruire l'instance en collision |

**Utilisations courantes :**
- Supprimer les pieces collectees (`target: other` dans l'evenement de collision)
- Detruire les balles lorsqu'elles touchent quelque chose
- Supprimer les ennemis lorsqu'ils sont vaincus

---

### Creer une Instance

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `create_instance` |
| **Nom du Bloc** | `instance_create` |
| **Categorie** | Instance |
| **Icone** | ✨ |

**Description :** Cree une nouvelle instance d'un objet a une position specifiee.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `object` | Objet | Le type d'objet a creer |
| `x` | Nombre | Coordonnee X pour la nouvelle instance |
| `y` | Nombre | Coordonnee Y pour la nouvelle instance |

**Exemple :** Creer une balle a la position du joueur lorsque Espace est presse.

---

## Actions de Score

### Definir le Score

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `set_score` |
| **Nom du Bloc** | `score_set` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | 🏆 |

**Description :** Definit le score a une valeur specifique, ou ajoute/soustrait du score actuel.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | La valeur du score |
| `relative` | Booleen | Si vrai, ajoute la valeur au score actuel. Si faux, definit le score a la valeur |

**Exemples :**
- Reinitialiser le score : `value: 0`, `relative: false`
- Ajouter 10 points : `value: 10`, `relative: true`
- Soustraire 5 points : `value: -5`, `relative: true`

---

### Ajouter au Score

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `add_score` |
| **Nom du Bloc** | `score_add` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | ➕🏆 |

**Description :** Ajoute une valeur au score actuel (raccourci pour set_score avec relative=true).

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `value` | Nombre | Points a ajouter (peut etre negatif pour soustraire) |

---

### Afficher le Score

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `draw_score` |
| **Nom du Bloc** | `draw_score` |
| **Categorie** | Score/Vies/Sante |
| **Icone** | 🖼️🏆 |

**Description :** Affiche le score actuel a l'ecran.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `x` | Nombre | Position X pour afficher le score |
| `y` | Nombre | Position Y pour afficher le score |
| `caption` | Chaine | Texte a afficher avant le score (ex: "Score: ") |

**Note :** Ceci devrait etre utilise dans un evenement Draw (disponible dans le preset Intermediaire).

---

## Actions de Salle

### Aller a la Salle Suivante

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `next_room` |
| **Nom du Bloc** | `room_goto_next` |
| **Categorie** | Salle |
| **Icone** | ➡️ |

**Description :** Passe a la salle suivante dans l'ordre des salles.

**Parametres :** Aucun

**Note :** Si vous etes deja dans la derniere salle, cette action n'a aucun effet (utilisez "Si la Salle Suivante Existe" pour verifier d'abord).

---

### Aller a la Salle Precedente

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `previous_room` |
| **Nom du Bloc** | `room_goto_previous` |
| **Categorie** | Salle |
| **Icone** | ⬅️ |

**Description :** Passe a la salle precedente dans l'ordre des salles.

**Parametres :** Aucun

**Note :** Si vous etes deja dans la premiere salle, cette action n'a aucun effet.

---

### Redemarrer la Salle

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `restart_room` |
| **Nom du Bloc** | `room_restart` |
| **Categorie** | Salle |
| **Icone** | 🔄 |

**Description :** Redemarrer la salle actuelle, reinitialisant toutes les instances a leur etat initial.

**Parametres :** Aucun

**Utilisations courantes :**
- Redemarrer le niveau apres la mort du joueur
- Reinitialiser le puzzle apres un echec
- Rejouer un mini-jeu

---

### Aller a une Salle

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `goto_room` |
| **Nom du Bloc** | `room_goto` |
| **Categorie** | Salle |
| **Icone** | 🚪 |

**Description :** Passe a une salle specifique par son nom.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `room` | Salle | La salle ou aller |

---

### Si la Salle Suivante Existe

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `if_next_room_exists` |
| **Nom du Bloc** | `room_if_next_exists` |
| **Categorie** | Salle |
| **Icone** | ❓➡️ |

**Description :** Bloc conditionnel qui n'execute les actions contenues que s'il existe une salle suivante.

**Parametres :** Aucun (les actions sont placees a l'interieur du bloc)

**Utilisations courantes :**
- Verifier avant d'aller a la salle suivante
- Afficher un message "Vous avez gagne !" s'il n'y a plus de salles

---

### Si la Salle Precedente Existe

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `if_previous_room_exists` |
| **Nom du Bloc** | `room_if_previous_exists` |
| **Categorie** | Salle |
| **Icone** | ❓⬅️ |

**Description :** Bloc conditionnel qui n'execute les actions contenues que s'il existe une salle precedente.

**Parametres :** Aucun (les actions sont placees a l'interieur du bloc)

---

## Actions de Sortie

### Afficher un Message

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `show_message` |
| **Nom du Bloc** | `output_message` |
| **Categorie** | Sortie |
| **Icone** | 💬 |

**Description :** Affiche une boite de dialogue popup au joueur.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `message` | Chaine | Le texte a afficher |

**Note :** Le jeu se met en pause pendant que le message est affiche. Le joueur doit cliquer sur OK pour continuer.

**Utilisations courantes :**
- Instructions du jeu
- Dialogues de l'histoire
- Messages de victoire/defaite
- Informations de debogage

---

### Executer du Code

| Propriete | Valeur |
|-----------|--------|
| **Nom de l'Action** | `execute_code` |
| **Nom du Bloc** | `execute_code` |
| **Categorie** | Sortie |
| **Icone** | 💻 |

**Description :** Execute du code Python personnalise.

**Parametres :**
| Parametre | Type | Description |
|-----------|------|-------------|
| `code` | Chaine | Code Python a executer |

**Note :** Ceci est une fonctionnalite avancee. Utilisez avec precaution car un code incorrect peut causer des erreurs.

---

## Resume des Categories

| Categorie | Evenements | Actions |
|-----------|------------|---------|
| **Evenements** | Create, Step, Touche Pressee, Collision | - |
| **Mouvement** | - | Definir Vitesse Horizontale, Definir Vitesse Verticale, Arreter Mouvement, Sauter a Position |
| **Instance** | - | Detruire Instance, Creer Instance |
| **Score/Vies/Sante** | - | Definir Score, Ajouter Score, Afficher Score |
| **Salle** | - | Salle Suivante, Salle Precedente, Redemarrer Salle, Aller a Salle, Si Salle Suivante Existe, Si Salle Precedente Existe |
| **Sortie** | - | Afficher Message, Executer Code |

---

## Exemple : Jeu Simple de Collecte de Pieces

Voici comment configurer un jeu basique de collecte de pieces en utilisant uniquement les fonctionnalites du preset Debutant :

### Objet Joueur (obj_player)

**Touche Pressee (Fleche Gauche) :**
- Definir Vitesse Horizontale : -4

**Touche Pressee (Fleche Droite) :**
- Definir Vitesse Horizontale : 4

**Touche Pressee (Fleche Haut) :**
- Definir Vitesse Verticale : -4

**Touche Pressee (Fleche Bas) :**
- Definir Vitesse Verticale : 4

**Collision avec obj_coin :**
- Definir Score : 10 (relative: true)
- Detruire Instance : other

**Collision avec obj_wall :**
- Arreter Mouvement

**Collision avec obj_goal :**
- Definir Score : 100 (relative: true)
- Salle Suivante

### Objet Piece (obj_coin)
Aucun evenement necessaire - juste un objet a collecter.

### Objet Mur (obj_wall)
Aucun evenement necessaire - juste un obstacle solide.

### Objet Objectif (obj_goal)
Aucun evenement necessaire - declenche la fin du niveau lorsque le joueur entre en collision.

---

## Passer au Niveau Intermediaire

Lorsque vous etes a l'aise avec le preset Debutant, envisagez de passer au **Intermediaire** pour acceder a :
- Evenement Draw (pour le rendu personnalise)
- Evenement Destroy (nettoyage lorsqu'une instance est detruite)
- Evenements Souris (detection des clics)
- Evenements Alarme (actions minutees)
- Systemes de Vies et de Sante
- Actions de Son et de Musique
- Plus d'options de mouvement (direction, se deplacer vers)

---

## Voir Aussi

- [Tutoriels](Tutorials_fr) - Tous les tutoriels en un seul endroit
- [Preset Intermediaire](Intermediate-Preset_fr) - Fonctionnalites du niveau suivant
- [Reference Complete des Actions](Full-Action-Reference_fr) - Liste complete des actions
- [Reference des Evenements](Event-Reference_fr) - Liste complete des evenements
- [Evenements et Actions](Events-and-Actions_fr) - Concepts fondamentaux
- [Creer Votre Premier Jeu](Creating-Your-First-Game_fr) - Tutoriel etape par etape
- [Tutoriel Pong](Tutorial-Pong_fr) - Creez un jeu Pong classique pour deux joueurs
- [Tutoriel Casse-Briques](Tutorial-Breakout_fr) - Creez un jeu de casse-briques classique
- [Initiation a la Creation de Jeux](Getting-Started-Breakout_fr) - Tutoriel complet pour debutants
