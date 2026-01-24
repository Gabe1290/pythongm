# Reference Complète des Actions

*[Accueil](Home_fr) | [Guide des Presets](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

Cette page documente toutes les actions disponibles dans PyGameMaker. Les actions sont des commandes qui s'exécutent lorsque des événements sont déclenchés.

## Catégories d'Actions

- [Actions de Mouvement](#actions-de-mouvement)
- [Actions d'Instance](#actions-dinstance)
- [Actions Score, Vies et Santé](#actions-score-vies--santé)
- [Actions de Salle](#actions-de-salle)
- [Actions de Temporisation](#actions-de-temporisation)
- [Actions Sonores](#actions-sonores)
- [Actions de Dessin](#actions-de-dessin)
- [Actions de Contrôle de Flux](#actions-de-contrôle-de-flux)
- [Actions de Sortie](#actions-de-sortie)

---

## Actions de Mouvement

### Définir la Vitesse Horizontale
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_hspeed` |
| **Icône** | ↔️ |
| **Preset** | Débutant |

**Description :** Définit la vitesse de mouvement horizontal.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 0 | Vitesse en pixels/frame. Positif=droite, Négatif=gauche |

---

### Définir la Vitesse Verticale
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_vspeed` |
| **Icône** | ↕️ |
| **Preset** | Débutant |

**Description :** Définit la vitesse de mouvement vertical.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 0 | Vitesse en pixels/frame. Positif=bas, Négatif=haut |

---

### Arrêter le Mouvement
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `stop_movement` |
| **Icône** | 🛑 |
| **Preset** | Débutant |

**Description :** Arrête tout mouvement (définit hspeed et vspeed à 0).

**Paramètres :** Aucun

---

### Sauter à une Position
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `jump_to_position` |
| **Icône** | 📍 |
| **Preset** | Débutant |

**Description :** Se déplace instantanément vers une position spécifique.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Nombre | 0 | Coordonnée X cible |
| `y` | Nombre | 0 | Coordonnée Y cible |

---

### Mouvement Fixe
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `move_fixed` |
| **Icône** | ➡️ |
| **Preset** | Avancé |

**Description :** Se déplace dans l'une des 8 directions fixes.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `directions` | Choix | right | Direction(s) de déplacement |
| `speed` | Nombre | 4 | Vitesse de mouvement |

**Choix de direction :** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Mouvement Libre
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `move_free` |
| **Icône** | 🧭 |
| **Preset** | Avancé |

**Description :** Se déplace dans n'importe quelle direction (0-360 degrés).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `direction` | Nombre | 0 | Direction en degrés (0=droite, 90=haut) |
| `speed` | Nombre | 4 | Vitesse de mouvement |

---

### Se Déplacer Vers
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `move_towards` |
| **Icône** | 🎯 |
| **Preset** | Intermédiaire |

**Description :** Se déplace vers une position cible.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Expression | 0 | X cible (peut utiliser des expressions comme `other.x`) |
| `y` | Expression | 0 | Y cible |
| `speed` | Nombre | 4 | Vitesse de mouvement |

---

### Définir la Vitesse
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_speed` |
| **Icône** | ⚡ |
| **Preset** | Avancé |

**Description :** Définit la magnitude de la vitesse (maintient la direction).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `speed` | Nombre | 0 | Magnitude de la vitesse |

---

### Définir la Direction
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_direction` |
| **Icône** | 🧭 |
| **Preset** | Avancé |

**Description :** Définit la direction du mouvement (maintient la vitesse).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `direction` | Nombre | 0 | Direction en degrés |

---

### Inverser Horizontal
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `reverse_horizontal` |
| **Icône** | ↔️ |
| **Preset** | Avancé |

**Description :** Inverse la direction horizontale (multiplie hspeed par -1).

**Paramètres :** Aucun

---

### Inverser Vertical
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `reverse_vertical` |
| **Icône** | ↕️ |
| **Preset** | Avancé |

**Description :** Inverse la direction verticale (multiplie vspeed par -1).

**Paramètres :** Aucun

---

### Définir la Gravité
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_gravity` |
| **Icône** | ⬇️ |
| **Preset** | Platformer |

**Description :** Applique la gravité à l'instance.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `direction` | Nombre | 270 | Direction de la gravité (270=bas) |
| `gravity` | Nombre | 0.5 | Force de la gravité |

---

### Définir la Friction
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_friction` |
| **Icône** | 🛑 |
| **Preset** | Avancé |

**Description :** Applique une friction (ralentissement progressif).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `friction` | Nombre | 0.1 | Quantité de friction |

---

## Actions d'Instance

### Détruire l'Instance
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `destroy_instance` |
| **Icône** | 💥 |
| **Preset** | Débutant |

**Description :** Supprime une instance du jeu.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `target` | Choix | self | `self` ou `other` (dans les événements de collision) |

---

### Créer une Instance
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `create_instance` |
| **Icône** | ✨ |
| **Preset** | Débutant |

**Description :** Crée une nouvelle instance d'un objet.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `object` | Objet | - | Type d'objet à créer |
| `x` | Nombre | 0 | Position X |
| `y` | Nombre | 0 | Position Y |

---

### Définir le Sprite
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_sprite` |
| **Icône** | 🖼️ |
| **Preset** | Avancé |

**Description :** Change le sprite de l'instance.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `sprite` | Sprite | - | Nouveau sprite |

---

## Actions Score, Vies et Santé

### Définir le Score
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_score` |
| **Icône** | 🏆 |
| **Preset** | Débutant |

**Description :** Définit ou modifie le score.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 0 | Valeur du score |
| `relative` | Booléen | false | Si vrai, ajoute au score actuel |

---

### Ajouter au Score (Raccourci)
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `add_score` |
| **Icône** | ➕🏆 |
| **Preset** | Débutant |

**Description :** Ajoute des points au score.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 10 | Points à ajouter (négatif pour soustraire) |

---

### Définir les Vies
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_lives` |
| **Icône** | ❤️ |
| **Preset** | Intermédiaire |

**Description :** Définit ou modifie le nombre de vies.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 3 | Valeur des vies |
| `relative` | Booléen | false | Si vrai, ajoute aux vies actuelles |

**Note :** Déclenche l'événement `no_more_lives` lorsqu'il atteint 0.

---

### Ajouter des Vies (Raccourci)
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `add_lives` |
| **Icône** | ➕❤️ |
| **Preset** | Intermédiaire |

**Description :** Ajoute ou retire des vies.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 1 | Vies à ajouter (négatif pour soustraire) |

---

### Définir la Santé
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_health` |
| **Icône** | 💚 |
| **Preset** | Intermédiaire |

**Description :** Définit ou modifie la santé (0-100).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 100 | Valeur de santé |
| `relative` | Booléen | false | Si vrai, ajoute à la santé actuelle |

**Note :** Déclenche l'événement `no_more_health` lorsqu'il atteint 0.

---

### Ajouter de la Santé (Raccourci)
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `add_health` |
| **Icône** | ➕💚 |
| **Preset** | Intermédiaire |

**Description :** Ajoute ou retire de la santé.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `value` | Nombre | 10 | Santé à ajouter (négatif pour les dégâts) |

---

### Dessiner le Score
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_score` |
| **Icône** | 🖼️🏆 |
| **Preset** | Débutant |

**Description :** Affiche le score à l'écran.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Nombre | 10 | Position X |
| `y` | Nombre | 10 | Position Y |
| `caption` | Chaîne | "Score: " | Texte avant le score |

---

### Dessiner les Vies
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_lives` |
| **Icône** | 🖼️❤️ |
| **Preset** | Intermédiaire |

**Description :** Affiche les vies à l'écran.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Nombre | 10 | Position X |
| `y` | Nombre | 30 | Position Y |
| `sprite` | Sprite | - | Sprite d'icône de vie optionnel |

---

### Dessiner la Barre de Santé
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_health_bar` |
| **Icône** | 📊💚 |
| **Preset** | Intermédiaire |

**Description :** Dessine une barre de santé.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x1` | Nombre | 10 | X gauche |
| `y1` | Nombre | 50 | Y haut |
| `x2` | Nombre | 110 | X droite |
| `y2` | Nombre | 60 | Y bas |
| `back_color` | Couleur | gray | Couleur de fond |
| `bar_color` | Couleur | green | Couleur de la barre |

---

## Actions de Salle

### Salle Suivante
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `next_room` |
| **Icône** | ➡️ |
| **Preset** | Débutant |

**Description :** Aller à la salle suivante dans l'ordre des salles.

**Paramètres :** Aucun

---

### Salle Précédente
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `previous_room` |
| **Icône** | ⬅️ |
| **Preset** | Débutant |

**Description :** Aller à la salle précédente dans l'ordre des salles.

**Paramètres :** Aucun

---

### Redémarrer la Salle
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `restart_room` |
| **Icône** | 🔄 |
| **Preset** | Débutant |

**Description :** Redémarre la salle actuelle.

**Paramètres :** Aucun

---

### Aller à la Salle
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `goto_room` |
| **Icône** | 🚪 |
| **Preset** | Débutant |

**Description :** Aller à une salle spécifique.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `room` | Salle | - | Salle cible |

---

### Si Salle Suivante Existe
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `if_next_room_exists` |
| **Icône** | ❓➡️ |
| **Preset** | Débutant |

**Description :** Conditionnel - exécute les actions uniquement s'il y a une salle suivante.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `then_actions` | Liste d'Actions | Actions si la salle suivante existe |
| `else_actions` | Liste d'Actions | Actions s'il n'y a pas de salle suivante |

---

### Si Salle Précédente Existe
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `if_previous_room_exists` |
| **Icône** | ❓⬅️ |
| **Preset** | Débutant |

**Description :** Conditionnel - exécute les actions uniquement s'il y a une salle précédente.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `then_actions` | Liste d'Actions | Actions si la salle précédente existe |
| `else_actions` | Liste d'Actions | Actions s'il n'y a pas de salle précédente |

---

## Actions de Temporisation

### Définir une Alarme
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_alarm` |
| **Icône** | ⏰ |
| **Preset** | Intermédiaire |

**Description :** Définit une alarme qui se déclenche après un délai.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `alarm` | Nombre | 0 | Numéro d'alarme (0-11) |
| `steps` | Nombre | 60 | Pas jusqu'au déclenchement de l'alarme |

**Note :** À 60 FPS, 60 pas = 1 seconde.

---

## Actions Sonores

### Jouer un Son
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `play_sound` |
| **Icône** | 🔊 |
| **Preset** | Intermédiaire |

**Description :** Joue un effet sonore.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `sound` | Son | - | Ressource sonore |
| `loop` | Booléen | false | Répéter le son en boucle |

---

### Jouer de la Musique
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `play_music` |
| **Icône** | 🎵 |
| **Preset** | Intermédiaire |

**Description :** Joue de la musique de fond.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `sound` | Son | - | Ressource musicale |
| `loop` | Booléen | true | Répéter la musique en boucle |

---

### Arrêter la Musique
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `stop_music` |
| **Icône** | 🔇 |
| **Preset** | Intermédiaire |

**Description :** Arrête toute la musique en cours.

**Paramètres :** Aucun

---

### Définir le Volume
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_volume` |
| **Icône** | 🔉 |
| **Preset** | Avancé |

**Description :** Définit le volume audio.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `volume` | Nombre | 1.0 | Niveau de volume (0.0 à 1.0) |

---

## Actions de Dessin

### Dessiner du Texte
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_text` |
| **Icône** | 📝 |
| **Preset** | Avancé |

**Description :** Dessine du texte à l'écran.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Nombre | 0 | Position X |
| `y` | Nombre | 0 | Position Y |
| `text` | Chaîne | "" | Texte à dessiner |
| `color` | Couleur | white | Couleur du texte |

---

### Dessiner un Rectangle
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_rectangle` |
| **Icône** | ⬛ |
| **Preset** | Avancé |

**Description :** Dessine un rectangle.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x1` | Nombre | 0 | X gauche |
| `y1` | Nombre | 0 | Y haut |
| `x2` | Nombre | 32 | X droite |
| `y2` | Nombre | 32 | Y bas |
| `color` | Couleur | white | Couleur de remplissage |
| `outline` | Booléen | false | Contour uniquement |

---

### Dessiner un Cercle
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_circle` |
| **Icône** | ⚪ |
| **Preset** | Avancé |

**Description :** Dessine un cercle.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `x` | Nombre | 0 | Centre X |
| `y` | Nombre | 0 | Centre Y |
| `radius` | Nombre | 16 | Rayon |
| `color` | Couleur | white | Couleur de remplissage |
| `outline` | Booléen | false | Contour uniquement |

---

### Définir l'Alpha
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `set_alpha` |
| **Icône** | 👻 |
| **Preset** | Avancé |

**Description :** Définit la transparence du dessin.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `alpha` | Nombre | 1.0 | Transparence (0.0=invisible, 1.0=opaque) |

---

## Actions de Contrôle de Flux

### Si Collision À
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `if_collision_at` |
| **Icône** | 🎯 |
| **Preset** | Avancé |

**Description :** Vérifie une collision à une position.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `x` | Expression | Position X à vérifier |
| `y` | Expression | Position Y à vérifier |
| `object_type` | Choix | `any` ou `solid` |
| `then_actions` | Liste d'Actions | Si collision trouvée |
| `else_actions` | Liste d'Actions | Si pas de collision |

---

## Actions de Sortie

### Afficher un Message
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `show_message` |
| **Icône** | 💬 |
| **Preset** | Débutant |

**Description :** Affiche un message popup.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `message` | Chaîne | "Hello!" | Texte du message |

**Note :** Le jeu se met en pause pendant l'affichage du message.

---

### Exécuter du Code
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `execute_code` |
| **Icône** | 💻 |
| **Preset** | Débutant |

**Description :** Exécute du code Python personnalisé.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `code` | Code | "" | Code Python à exécuter |

**Avertissement :** Fonctionnalité avancée. À utiliser avec précaution.

---

### Terminer le Jeu
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `end_game` |
| **Icône** | 🚪 |
| **Preset** | Avancé |

**Description :** Termine le jeu et ferme la fenêtre.

**Paramètres :** Aucun

---

### Redémarrer le Jeu
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `restart_game` |
| **Icône** | 🔄 |
| **Preset** | Avancé |

**Description :** Redémarre le jeu depuis la première salle.

**Paramètres :** Aucun

---

## Actions par Preset

| Preset | Nombre d'Actions | Catégories |
|--------|-----------------|------------|
| **Débutant** | 17 | Mouvement, Instance, Score, Salle, Sortie |
| **Intermédiaire** | 29 | + Vies, Santé, Son, Temporisation |
| **Avancé** | 40+ | + Dessin, Contrôle de Flux, Jeu |

---

## Voir Aussi

- [Référence des Événements](Event-Reference_fr) - Liste complète des événements
- [Preset Débutant](Beginner-Preset_fr) - Actions essentielles pour les débutants
- [Preset Intermédiaire](Intermediate-Preset_fr) - Actions supplémentaires
- [Événements et Actions](Events-and-Actions_fr) - Vue d'ensemble des concepts de base
