# Événements de Dessin

*[Accueil](Home_fr) | [Référence des Événements](Event-Reference_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

### Draw
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw` |
| **Icône** | 🎨 |
| **Catégorie** | Dessin |
| **Préréglage** | Débutant |

**Description :** Se déclenche pendant la phase de rendu.

**Important :** Ajouter un événement Draw désactive le dessin automatique du sprite. Vous devez dessiner le sprite manuellement si vous voulez qu'il soit visible.

**Utilisations courantes :**
- Rendu personnalisé
- Dessiner des formes
- Afficher du texte
- Barres de vie
- Éléments d'interface

**Actions de dessin disponibles :**
- Dessiner un sprite
- Dessiner du texte
- Dessiner un rectangle
- Dessiner un cercle
- Dessiner une ligne
- Dessiner la barre de santé

---

### Draw GUI
| Propriété | Valeur |
|-----------|--------|
| **Nom** | `draw_gui` |
| **Icône** | 🖥️ |
| **Catégorie** | Dessin |
| **Préréglage** | Débutant |

**Description :** Dessine dans l'**espace écran (GUI)**, par-dessus la salle et sans être affecté par le défilement des vues/de la caméra.

**Différence avec Draw :** l'événement Draw habituel est en coordonnées de salle (il défile avec la vue) ; Draw GUI reste fixe à l'écran — à utiliser pour les ATH (HUD), les scores et les menus.

---

## Autres Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

[← Retour à la Référence des Événements](Event-Reference_fr)
