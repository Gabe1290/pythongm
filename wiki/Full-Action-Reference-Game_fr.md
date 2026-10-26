# Jeu

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence des Événements](Event-Reference_fr)*

> **Généré automatiquement** à partir du registre d'actions de l'IDE par `tools/gen_action_reference.py` — ne pas modifier à la main ; relancez le générateur après avoir changé les actions. Les traductions proviennent de `tools/action_ref_i18n.py`.

### Dessiner un cercle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_circle` |
| **Icône** | ⭕ |
| **Catégorie** | Jeu |

Dessiner un cercle plein ou en contour

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x` | Nombre | `0` | X du centre |
| `y` | Nombre | `0` | Y du centre |
| `radius` | Nombre | `50` | Rayon du cercle |
| `filled` | Oui/Non | Oui | Plein, ou contour seulement; optionnel |

### Dessiner un rectangle

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_rectangle` |
| **Icône** | 🟥 |
| **Catégorie** | Jeu |

Dessiner un rectangle plein ou en contour

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `x1` | Nombre | `0` | X gauche |
| `y1` | Nombre | `0` | Y supérieur |
| `x2` | Nombre | `100` | X droit |
| `y2` | Nombre | `100` | Y inférieur |
| `filled` | Oui/Non | Oui | Plein, ou contour seulement; optionnel |

### Dessiner du texte

| Propriété | Valeur |
|----------|-------|
| **Nom** | `draw_text` |
| **Icône** | 🖍️ |
| **Catégorie** | Jeu |

Dessiner une chaîne de texte à une position

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Texte à dessiner (prend en charge les expressions) |
| `x` | Nombre | `0` | Position X |
| `y` | Nombre | `0` | Position Y |
| `relative` | Oui/Non | Non | Dessiner par rapport à la position de cette instance au lieu de coordonnées d'écran absolues; optionnel |
| `color` | Couleur | — | Couleur du texte (par ex. #ffffff). Vide = la couleur de dessin active, sinon noir.; optionnel |

### Charger la partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `load_game` |
| **Icône** | 📂 |
| **Catégorie** | Jeu |

Restaure la salle, le score, les vies, la santé, les variables globales et l'état des instances depuis un fichier de sauvegarde

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `filename` | Texte | `savegame.sav` | Nom du fichier de sauvegarde à charger (dans le dossier saves/ du projet) |

### Ouvrir une page web

| Propriété | Valeur |
|----------|-------|
| **Nom** | `open_webpage` |
| **Icône** | 🌐 |
| **Catégorie** | Jeu |

Ouvrir une URL dans le navigateur par défaut

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `url` | Texte | — | Adresse web à ouvrir |

### Redémarrer le jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `restart_game` |
| **Icône** | 🔁🎮 |
| **Catégorie** | Jeu |

Redémarrer le jeu depuis la salle de départ

*Paramètres:* aucun

### Sauvegarder la partie

| Propriété | Valeur |
|----------|-------|
| **Nom** | `save_game` |
| **Icône** | 💾 |
| **Catégorie** | Jeu |

Enregistre dans un fichier la salle courante, le score, les vies, la santé, les variables globales et l'état des instances

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `filename` | Texte | `savegame.sav` | Nom du fichier de sauvegarde (écrit dans le dossier saves/ du projet) |

### Définir l'alpha

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_alpha` |
| **Icône** | 🌫️ |
| **Catégorie** | Jeu |

Définir la transparence de dessin pour les dessins suivants

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `alpha` | Nombre | `1.0` | Opacité de 0.0 (transparent) à 1.0 (opaque) |

### Définir le titre de la fenêtre

| Propriété | Valeur |
|----------|-------|
| **Nom** | `set_window_caption` |
| **Icône** | 🪟 |
| **Catégorie** | Jeu |

Configurer l'affichage du score/des vies/de la santé dans le titre de la fenêtre

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `show_score` | Oui/Non | Oui | Ajouter le score actuel au titre de la fenêtre |
| `show_lives` | Oui/Non | Oui | Ajouter le nombre de vies actuel au titre de la fenêtre |
| `show_health` | Oui/Non | Non | Ajouter la valeur de santé actuelle au titre de la fenêtre |
| `caption` | Texte | — | Préfixe de titre optionnel affiché avant les compteurs; optionnel |

### Afficher les infos du jeu

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_info` |
| **Icône** | ℹ️ |
| **Catégorie** | Jeu |

Afficher l'écran d'informations du jeu

*Paramètres:* aucun

### Afficher un message

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_message` |
| **Icône** | 💬 |
| **Catégorie** | Jeu |

Afficher un message

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `message` | Texte | `Hello!` | Texte du message |

### Afficher une vidéo

| Propriété | Valeur |
|----------|-------|
| **Nom** | `show_video` |
| **Icône** | 🎬 |
| **Catégorie** | Jeu |

Lit un fichier vidéo dans le lecteur vidéo par défaut du système : il s'ouvre dans une fenêtre séparée, il n'est pas dessiné dans le jeu lui-même

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `filename` | Texte | — | Chemin vers le fichier vidéo |
| `fullscreen` | Oui/Non | Non | Demander une lecture en plein écran (selon ce que permet le lecteur de votre système); optionnel |

### Écran d'accueil : afficher une image

| Propriété | Valeur |
|----------|-------|
| **Nom** | `splash_show_image` |
| **Icône** | 🖼️ |
| **Catégorie** | Jeu |

Affiche un sprite en plein écran et met le jeu en pause jusqu'à ce que le joueur le referme

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `image` | Sprite | — | Sprite à afficher en plein écran |

### Écran d'accueil : afficher un texte

| Propriété | Valeur |
|----------|-------|
| **Nom** | `splash_show_text` |
| **Icône** | 💬 |
| **Catégorie** | Jeu |

Affiche un message et met le jeu en pause jusqu'à ce que le joueur le referme

| Paramètre | Type | Défaut | Remarques |
|-----------|------|---------|-------|
| `text` | Texte | — | Message à afficher |

---

## Autres Catégories

- [Mouvement](Full-Action-Reference-Movement_fr) (21)
- [Instance](Full-Action-Reference-Instance_fr) (12)
- [Score](Full-Action-Reference-Score_fr) (6)
- [Salle](Full-Action-Reference-Room_fr) (13)
- [Minuterie](Full-Action-Reference-Timing_fr) (8)
- [Audio](Full-Action-Reference-Audio_fr) (6)
- [Contrôle](Full-Action-Reference-Control_fr) (19)
- [Grille](Full-Action-Reference-Grid_fr) (3)
- [Vues](Full-Action-Reference-Views_fr) (2)
- [Vue 3D](Full-Action-Reference-3D-View-Actions_fr) (18)
- [Dessin](Full-Action-Reference-Drawing_fr) (11)
- [Réseau](Full-Action-Reference-Network-Actions_fr) (22)
- [Particules](Full-Action-Reference-Particles_fr) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_fr) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_fr) (16)

[← Retour à la Référence Complète des Actions](Full-Action-Reference_fr)
