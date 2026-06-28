# Editeur d'objets

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

> [Retour a l'accueil](Home_fr)

Les objets sont les elements de base de votre jeu. Ils representent tout, des joueurs aux ennemis, des collectibles aux elements d'interface.

---

## Ouvrir l'editeur d'objets

1. Double-cliquez sur un objet existant dans l'arbre des ressources, ou
2. Clic droit sur **Objets** > **Creer un objet**

---

## Proprietes de l'objet

| Propriete | Description |
|-----------|-------------|
| **Nom** | Identifiant unique de l'objet (ex: `obj_joueur`) |
| **Sprite** | La representation visuelle de l'objet |
| **Visible** | Si l'objet est dessine (par defaut: oui) |
| **Solide** | Utilise pour la detection de collision |
| **Profondeur** | Ordre de dessin (plus bas = dessine au-dessus) |
| **Persistant** | L'objet survit aux changements de salle |

---

## Evenements

Les evenements sont des declencheurs qui provoquent l'execution d'actions.

### Evenements courants

| Evenement | Quand il se declenche |
|-----------|----------------------|
| **Create** | Une fois quand une instance est creee |
| **Destroy** | Quand l'instance est detruite |
| **Step** | A chaque frame du jeu (60 fois par seconde) |
| **Draw** | Pendant la phase de dessin |
| **Alarm [0-11]** | Quand un minuteur atteint zero |

### Evenements clavier

| Evenement | Quand il se declenche |
|-----------|----------------------|
| **Touche pressee** | Une fois quand une touche est enfoncee |
| **Touche relachee** | Une fois quand une touche est relachee |
| **Clavier** | A chaque frame tant qu'une touche est maintenue |

### Evenements souris

| Evenement | Quand il se declenche |
|-----------|----------------------|
| **Bouton de souris** | Lors d'un clic sur l'instance |
| **Souris globale** | Lors d'un clic n'importe ou |
| **Entree souris** | Quand le curseur entre dans l'instance |
| **Sortie souris** | Quand le curseur quitte l'instance |

### Evenements de collision

| Evenement | Quand il se declenche |
|-----------|----------------------|
| **Collision avec [objet]** | Quand on touche un autre type d'objet |

---

## Actions

Les actions sont des operations effectuees lorsque les evenements se declenchent.

### Actions de mouvement
- **Definir la vitesse** - Definir la vitesse de deplacement
- **Definir la direction** - Definir la direction (0-360 degres)
- **Sauter a une position** - Se teleporter aux coordonnees
- **Sauter au depart** - Retourner a la position de depart

### Actions d'instance
- **Creer une instance** - Creer un nouvel objet
- **Detruire l'instance** - Supprimer l'instance actuelle

### Actions de score/vies/sante
- **Modifier le score** - Changer la valeur du score
- **Modifier les vies** - Changer le nombre de vies
- **Modifier la sante** - Changer la valeur de sante

### Actions de salle
- **Salle suivante** - Aller a la salle suivante
- **Salle precedente** - Aller a la salle precedente
- **Redemarrer la salle** - Reinitialiser la salle actuelle

---

## Programmation visuelle avec Blockly

Au lieu d'utiliser la liste d'actions, vous pouvez passer a l'onglet **Blockly** pour la programmation visuelle:

1. Ouvrez un objet
2. Cliquez sur l'onglet **Blockly**
3. Glissez des blocs depuis la boite a outils pour creer la logique

Voir [[Programmation-Visuelle_fr]] pour plus de details.

---

## Prochaines etapes

- [[Editeur-Salles_fr]] - Placer des objets dans vos niveaux
- [[Evenements-Actions_fr]] - Reference complete des evenements et actions
- [[Programmation-Visuelle_fr]] - Apprendre la programmation par blocs
