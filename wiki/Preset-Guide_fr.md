# Guide des Préréglages

*[Français](Preset-Guide_fr) | [Retour à l'Accueil](Home_fr)*

PyGameMaker propose différents préréglages qui contrôlent quels événements et actions sont disponibles. Cela aide les débutants à se concentrer sur les fonctionnalités essentielles tout en permettant aux utilisateurs expérimentés d'accéder à l'ensemble des outils.

## Choisissez Votre Niveau

| Préréglage | Idéal Pour | Fonctionnalités |
|------------|------------|-----------------|
| [**Débutant**](Beginner-Preset_fr) | Nouveaux en développement de jeux | 4 événements, 17 actions - Mouvement, collisions, score, salles |
| [**Intermédiaire**](Intermediate-Preset_fr) | Quelques connaissances | +4 événements, +12 actions - Vies, santé, son, alarmes, dessin |
| **Avancé** | Utilisateurs expérimentés | Tous les 40+ événements et actions disponibles |

---

## Documentation des Préréglages

### Préréglages
| Page | Description |
|------|-------------|
| [Préréglage Débutant](Beginner-Preset_fr) | 4 événements, 17 actions - Fonctionnalités essentielles |
| [Préréglage Intermédiaire](Intermediate-Preset_fr) | +4 événements, +12 actions - Vies, santé, son |

### Référence
| Page | Description |
|------|-------------|
| [Référence des Événements](Event-Reference_fr) | Liste complète de tous les événements |
| [Référence des Actions](Full-Action-Reference_fr) | Liste complète de toutes les actions |

---

## Exemple de Démarrage Rapide

Voici un simple jeu de collecte de pièces utilisant uniquement les fonctionnalités Débutant:

### 1. Créer des Objets
- `obj_player` - Le personnage contrôlable
- `obj_coin` - Objets à collecter
- `obj_wall` - Obstacles solides

### 2. Ajouter des Événements au Joueur

**Clavier (Touches Directionnelles):**
```
Flèche Gauche  → Définir Vitesse Horizontale: -4
Flèche Droite  → Définir Vitesse Horizontale: 4
Flèche Haut    → Définir Vitesse Verticale: -4
Flèche Bas     → Définir Vitesse Verticale: 4
```

**Collision avec obj_coin:**
```
Ajouter Score: 10
Détruire Instance: other
```

**Collision avec obj_wall:**
```
Arrêter Mouvement
```

### 3. Créer une Salle
- Placez le joueur
- Ajoutez quelques pièces
- Ajoutez des murs autour des bords

### 4. Lancez le Jeu!
Appuyez sur le bouton Jouer pour tester votre jeu.

---

## Conseils pour Réussir

1. **Commencez Simple** - Utilisez d'abord le préréglage Débutant
2. **Testez Souvent** - Lancez votre jeu fréquemment pour détecter les problèmes
3. **Une Chose à la Fois** - Ajoutez des fonctionnalités progressivement
4. **Utilisez les Collisions** - La plupart des mécaniques de jeu impliquent des événements de collision
5. **Lisez la Documentation** - Consultez les pages de référence quand vous êtes bloqué

---

## Voir Aussi

- [Accueil](Home_fr) - Page principale du wiki
- [Premiers Pas](Demarrage_fr) - Installation et configuration
- [Événements et Actions](Evenements_Actions_fr) - Concepts de base
- [Créer Votre Premier Jeu](Premier_Jeu_fr) - Tutoriel
- [Tutoriel Casse-Briques](Tutorial-Breakout_fr) - Créez un jeu de casse-briques classique
- [Initiation à la Création de Jeux](Getting-Started-Breakout_fr) - Tutoriel complet pour débutants
