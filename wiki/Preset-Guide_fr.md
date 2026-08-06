# Guide des Préréglages

*[Français](Preset-Guide_fr) | [Retour à l'Accueil](Home_fr)*

PyGameMaker propose différents préréglages qui contrôlent quels événements et actions sont disponibles — à la fois dans le sélecteur de blocs visuels Blockly et dans le panneau structuré Événements/Actions (« Ajouter un événement »/« Ajouter une action ») que tous les tutoriels de ce wiki utilisent. Cela aide les débutants à se concentrer sur les fonctionnalités essentielles tout en permettant aux utilisateurs expérimentés d'accéder à l'ensemble des outils.

Le préréglage d'un projet se règle de deux façons : **`Préférences > Édition de l'IDE`** choisit le préréglage par défaut des *nouveaux* projets (les projets existants ne sont jamais modifiés en changeant l'édition), et **`Outils > Configurer les blocs d'action...`** change le préréglage du projet *actuellement ouvert* à tout moment. L'édition par défaut de l'IDE est Débutant, donc les nouveaux projets d'une installation fraîche démarrent déjà sur le préréglage Débutant.

## Choisissez Votre Niveau

| Édition de l'IDE | Idéal Pour | Préréglage utilisé |
|------------|------------|-----------------|
| **Débutant** (par défaut) | Nouveaux en développement de jeux | [Préréglage Débutant](Beginner-Preset_fr) — mouvement de base, collisions, score, salles |
| **Avancé** | Quelques connaissances | [Préréglage Intermédiaire](Intermediate-Preset_fr) — + vies, santé, son, alarmes, mouvement sur grille |
| **Développement** | Utilisateurs expérimentés | Le préréglage `full` — tous les événements et actions disponibles |

Les noms ne correspondent pas exactement : l'édition « Avancé » utilise le préréglage `intermediate` (il n'existe pas de préréglage « avancé » séparé) — voir [Préréglage Débutant](Beginner-Preset_fr)/[Préréglage Intermédiaire](Intermediate-Preset_fr) pour les décomptes exacts et toujours à jour d'événements et d'actions de chacun.

---

## Documentation des Préréglages

### Préréglages
| Page | Description |
|------|-------------|
| [Préréglage Débutant](Beginner-Preset_fr) | Fonctionnalités essentielles — décomptes exacts sur cette page |
| [Préréglage Intermédiaire](Intermediate-Preset_fr) | Ajoute vies, santé, son, alarmes, mouvement sur grille — décomptes exacts sur cette page |

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
