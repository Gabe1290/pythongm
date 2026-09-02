# Contrôle

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Vérifier si vide

| Propriété | Valeur |
|----------|-------|
| **Nom** | `check_empty` |
| **Icône** | 🔍 |
| **Catégorie** | Contrôle |

Vrai lorsque (x, y) est sans collision. À utiliser avec start_block/end_block pour conditionner la ou les actions suivantes, façon GM

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `self.x` | Position X à vérifier (expression acceptée, par ex. self.x + 32) |
| `y` | Texte | `self.y` | Position Y à vérifier (expression acceptée, par ex. self.y + 32) |
| `relative` | Oui/Non | Non | Traiter X/Y comme des décalages par rapport à la position de cette instance au lieu de coordonnées absolues; optionnel |
| `objects` | Choix | `solid` | Quelles instances comptent comme occupant la position; Choix: `solid`, `all` |

### Commentaire

| Propriété | Valeur |
|----------|-------|
| **Nom** | `comment` |
| **Icône** | ⚠️ |
| **Catégorie** | Contrôle |

Un commentaire dans la liste d'actions (sans effet à l'exécution)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Texte de commentaire libre; optionnel |

### Sinon

| Propriété | Valeur |
|----------|-------|
| **Nom** | `else_action` |
| **Icône** | ⚡ |
| **Catégorie** | Contrôle |

Marque la branche « sinon » d'une condition

*Paramètres:* aucun

### Fin de bloc

| Propriété | Valeur |
|----------|-------|
| **Nom** | `end_block` |
| **Icône** | 📁 |
| **Catégorie** | Contrôle |

Terminer un bloc d'actions

*Paramètres:* aucun

### Exécuter du code

| Propriété | Valeur |
|----------|-------|
| **Nom** | `execute_code` |
| **Icône** | 📜 |
| **Catégorie** | Contrôle |

Exécuter un bloc de code Python intégré

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `code` | Code | — | Code source Python à évaluer sur l'instance |

### Exécuter un script

| Propriété | Valeur |
|----------|-------|
| **Nom** | `execute_script` |
| **Icône** | 📜 |
| **Catégorie** | Contrôle |

Exécuter l'un des scripts du projet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `script` | Script | — | Nom du script du projet à exécuter |
| `arg0` | Texte | — | Disponible dans le script sous argument0; optionnel |
| `arg1` | Texte | — | Disponible dans le script sous argument1; optionnel |
| `arg2` | Texte | — | Disponible dans le script sous argument2; optionnel |
| `arg3` | Texte | — | Disponible dans le script sous argument3; optionnel |
| `arg4` | Texte | — | Disponible dans le script sous argument4; optionnel |

### Quitter l'événement

| Propriété | Valeur |
|----------|-------|
| **Nom** | `exit_event` |
| **Icône** | 🚪 |
| **Catégorie** | Contrôle |

Arrêter l'exécution des actions restantes de cet événement

*Paramètres:* aucun

### Si poussée possible

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_can_push` |
| **Icône** | 📦 |
| **Catégorie** | Contrôle |

Vérifier si une caisse/un objet peut être poussé dans la direction actuelle (façon Sokoban)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `direction` | Choix | `facing` | Direction à vérifier pour la poussée; Choix: `facing` |
| `object_type` | Texte | `box` | Type d'objet poussé |
| `then_action` | Choix | `push_and_move` | Action si la poussée est possible; Choix: `push_and_move`, `none` |
| `else_action` | Choix | `stop_movement` | Action si la poussée est bloquée; Choix: `stop_movement`, `none` |

### Si collision

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_collision` |
| **Icône** | ❓💥 |
| **Catégorie** | Contrôle |

Condition : vrai si l'instance entrerait en collision au décalage (x, y)

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | Décalage horizontal à tester |
| `y` | Nombre | `0` | Décalage vertical à tester |
| `object` | Texte | `any` | « any », « solid », ou un nom d'objet; Choix: `any`, `solid`; optionnel |
| `not_flag` | Oui/Non | Non | Inverser le résultat; optionnel |

### Si collision à

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_collision_at` |
| **Icône** | 🎯 |
| **Catégorie** | Contrôle |

Vérifier une collision à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Texte | `self.x + 32` | Expression de la position X |
| `y` | Texte | `self.y` | Expression de la position Y |
| `object_type` | Choix | `any` | Type d'objet à vérifier; Choix: `any`, `solid` |
| `then_actions` | Liste d'actions | — | Actions si collision trouvée |
| `else_actions` | Liste d'actions | — | Actions si aucune collision |

### Si condition

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_condition` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Vérification conditionnelle avec des actions alors/sinon

*Paramètres:* aucun

### Si l'objet existe

| Propriété | Valeur |
|----------|-------|
| **Nom** | `if_object_exists` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Condition : vrai s'il existe au moins une instance de l'objet

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `object` | Objet | — | Type d'objet à vérifier |
| `not_flag` | Oui/Non | Non | Inverser le résultat (agir quand l'objet n'existe PAS); optionnel |

### Répéter

| Propriété | Valeur |
|----------|-------|
| **Nom** | `repeat` |
| **Icône** | 🔁 |
| **Catégorie** | Contrôle |

Répéter l'action/le bloc suivant N fois

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `times` | Nombre | `10` | Nombre de répétitions |
| `actions` | Liste d'actions | — | Actions à répéter |

### Définir une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_variable` |
| **Icône** | 📝 |
| **Catégorie** | Contrôle |

Définir une variable d'instance ou globale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `variable` | Texte | — | Nom de la variable |
| `value` | Texte | `0` | Valeur (nombre, chaîne ou expression) |
| `scope` | Choix | `self` | Portée de la variable; Choix: `self`, `other`, `global` |
| `relative` | Oui/Non | Non | Ajouter à la valeur actuelle au lieu de la remplacer |

### Début de bloc

| Propriété | Valeur |
|----------|-------|
| **Nom** | `start_block` |
| **Icône** | 📂 |
| **Catégorie** | Contrôle |

Débuter un bloc d'actions (pour le regroupement)

*Paramètres:* aucun

### Tester la chance

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_chance` |
| **Icône** | 🎲❓ |
| **Catégorie** | Contrôle |

Condition : vrai avec une probabilité de 1 sur « sides »

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `sides` | Nombre | `6` | Une chance sur N d'être vrai |

### Tester une expression

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_expression` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Tester si une expression est vraie

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `expression` | Texte | — | Expression à évaluer (vrai si >= 0.5) |
| `then_actions` | Liste d'actions | — | Actions si vrai |
| `else_actions` | Liste d'actions | — | Actions si faux |

### Poser une question

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_question` |
| **Icône** | ❓💬 |
| **Catégorie** | Contrôle |

Condition : afficher une boîte de dialogue oui/non ; vrai si l'utilisateur répond oui

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `question` | Texte | `Continue?` | Question affichée au joueur |

### Tester une variable

| Propriété | Valeur |
|----------|-------|
| **Nom** | `test_variable` |
| **Icône** | ❓ |
| **Catégorie** | Contrôle |

Tester la valeur d'une variable d'instance ou globale

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `variable` | Texte | — | Nom de la variable |
| `value` | Texte | `0` | Valeur à comparer |
| `scope` | Choix | `self` | Portée de la variable; Choix: `self`, `other`, `global` |
| `operation` | Choix | `equal` | Opérateur de comparaison; Choix: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (20)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (11)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Jeu](Full-Action-Reference-Game_fr) (25)
- [Grille](Full-Action-Reference-Grid_fr) (4)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (16)
- [Particles](Full-Action-Reference-Particles_fr) (8)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (15)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
