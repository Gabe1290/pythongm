# Éditeur d'objets

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

> [Retour à l'accueil](Home_fr)

Les objets sont les éléments de base de votre jeu. Ils représentent tout, des joueurs aux ennemis, des objets à collecter aux éléments d'interface.

---

## Ouvrir l'éditeur d'objets

1. Double-cliquez sur un objet existant dans l'arbre des ressources, ou
2. Clic droit sur **Objets** > **Créer un objet**

![L'Éditeur d'Objets : une liste d'événements à gauche (Create, Step,
plusieurs événements de Collision, Keyboard, No More Lives, Game Start),
les propriétés de l'objet (sprite, parent, Visible/Persistent/Solid) à
droite, et les onglets Liste d'Événements / Blockly / Éditeur de Code qui
changent la façon d'écrire les actions de chaque
événement](images/object-editor.png)

---

## Propriétés de l'objet

| Propriété | Description |
|-----------|-------------|
| **Nom** | Identifiant unique de l'objet (ex : `obj_joueur`) |
| **Sprite** | La représentation visuelle de l'objet |
| **Visible** | Si l'objet est dessiné (par défaut : oui) |
| **Solide** | Utilisé pour la détection de collision |
| **Profondeur** | Ordre de dessin (plus bas = dessiné au-dessus) |
| **Persistant** | L'objet survit aux changements de salle |

---

## Événements

Les événements sont des déclencheurs qui provoquent l'exécution d'actions.

### Événements courants

| Événement | Quand il se déclenche |
|-----------|----------------------|
| **Create** | Une fois quand une instance est créée |
| **Destroy** | Quand l'instance est détruite |
| **Step** | À chaque frame du jeu (60 fois par seconde) |
| **Draw** | Pendant la phase de dessin |
| **Alarm [0-11]** | Quand un minuteur atteint zéro |

### Événements clavier

| Événement | Quand il se déclenche |
|-----------|----------------------|
| **Touche pressée** | Une fois quand une touche est enfoncée |
| **Touche relâchée** | Une fois quand une touche est relâchée |
| **Clavier** | À chaque frame tant qu'une touche est maintenue |

### Événements souris

| Événement | Quand il se déclenche |
|-----------|----------------------|
| **Bouton de souris** | Lors d'un clic sur l'instance |
| **Souris globale** | Lors d'un clic n'importe où |
| **Entrée souris** | Quand le curseur entre dans l'instance |
| **Sortie souris** | Quand le curseur quitte l'instance |

### Événements de collision

| Événement | Quand il se déclenche |
|-----------|----------------------|
| **Collision avec [objet]** | Quand on touche un autre type d'objet |

---

## Actions

Les actions sont des opérations effectuées lorsque les événements se déclenchent.

### Actions de mouvement
- **Définir la vitesse** - Définir la vitesse de déplacement
- **Définir la direction** - Définir la direction (0-360 degrés)
- **Sauter à une position** - Se téléporter aux coordonnées
- **Sauter au départ** - Retourner à la position de départ

### Actions d'instance
- **Créer une instance** - Créer un nouvel objet
- **Détruire l'instance** - Supprimer l'instance actuelle

### Actions de score/vies/santé
- **Modifier le score** - Changer la valeur du score
- **Modifier les vies** - Changer le nombre de vies
- **Modifier la santé** - Changer la valeur de santé

### Actions de salle
- **Salle suivante** - Aller à la salle suivante
- **Salle précédente** - Aller à la salle précédente
- **Redémarrer la salle** - Réinitialiser la salle actuelle

---

## Programmation visuelle avec Blockly

Au lieu d'utiliser la liste d'actions, vous pouvez passer à l'onglet **Blockly** pour la programmation visuelle :

1. Ouvrez un objet
2. Cliquez sur l'onglet **Blockly**
3. Glissez des blocs depuis la boîte à outils pour créer la logique

Voir [[Programmation_Visuelle_fr]] pour plus de détails.

---

## Prochaines étapes

- [[Editeur_Salles_fr]] - Placer des objets dans vos niveaux
- [[Evenements_Actions_fr]] - Référence complète des événements et actions
- [[Programmation_Visuelle_fr]] - Apprendre la programmation par blocs
