# Référence des Événements

*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

Cette page documente tous les événements disponibles dans PyGameMaker. Les événements sont des déclencheurs qui exécutent des actions lorsque des conditions spécifiques se produisent dans votre jeu.

## Catégories d'Événements

- [Événements d'Objet](Event-Reference-Object_fr) - Create, Step, Destroy
- [Événements d'Entrée](Event-Reference-Input_fr) - Clavier, Souris
- [Événements de Collision](Event-Reference-Collision_fr) - Collisions d'objets
- [Événements de Temps](Event-Reference-Timing_fr) - Alarmes, Variantes de Step
- [Événements de Dessin](Event-Reference-Drawing_fr) - Rendu personnalisé
- [Événements de Salle](Event-Reference-Room_fr) - Transitions de salles
- [Événements de Jeu](Event-Reference-Game_fr) - Début/Fin de jeu
- [Autres Événements](Event-Reference-Other_fr) - Limites, Vies, Santé

---

## Événements Réseau

Fournis par l'extension intégrée **Réseau (multijoueur LAN)** — ne font
partie d'aucun préréglage (le multijoueur est une fonctionnalité de projet
avancé), et ne prennent sens qu'une fois qu'un jeu a exécuté **Héberger une
partie** ou **Rejoindre une partie**. Voir [Réseau](Network_fr) pour la vue
d'ensemble.

| Événement | Se déclenche quand |
|-----------|---------------------|
| **Réseau prêt** | Un client termine sa connexion à l'hôte |
| **Joueur connecté** | Un nouveau joueur se connecte |
| **Joueur déconnecté** | Un joueur se déconnecte |
| **Message réseau** | Un **Envoyer un message réseau** personnalisé arrive |
| **Partie réseau démarrée** | L'hôte exécute **Démarrer la partie en réseau** |
| **Connexion perdue** | La connexion d'un client à l'hôte est coupée |

---

## Ordre d'Exécution des Événements

Comprendre quand les événements se déclenchent aide à créer un comportement
de jeu prévisible (confirmé dans la boucle principale de
`runtime/game_runner.py`) :

1. **Begin Step** — Début de la frame
2. **Alarm** — Toutes les alarmes déclenchées comptent à rebours et se déclenchent
3. **Step** (et **Keyboard (maintenue)**) — Logique de jeu principale, puis
   vérification continue des touches maintenues pour la même instance
4. **Keyboard Press/Release, Mouse** — Les événements d'entrée en file
   d'attente pour la frame sont distribués (cela se produit *après* Step,
   pas avant — le code de Step réagit aux touches déjà maintenues au
   *début* de la frame, pas à celles pressées pendant celle-ci)
5. **Movement, puis Collision** — La physique (gravité/friction/hspeed/vspeed)
   est appliquée, puis les collisions sont détectées et leurs événements se déclenchent
6. **End Step** (et **Destroy**) — Après les collisions
7. **Draw** — Phase de rendu

---

## Événements par Préréglage

Confirmé via `events.event_types.get_available_events()` alimenté par
chaque préréglage réel de `config/blockly_config.py` — voir le
[Guide des Préréglages](Preset-Guide_fr) pour ce qu'un « préréglage »
restreint réellement (à la fois le sélecteur Blockly et le panneau
structuré Événements/Actions) et comment le préréglage d'un projet est défini.

| Préréglage | Événements inclus |
|------------|-------------------|
| **Débutant** (19 événements) | Create, Step, Keyboard (maintenue), Keyboard \<No Key\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermédiaire** (21 événements) | + Destroy, Keyboard Press |
| **Full** (édition Développement uniquement, 23 événements) | + Keyboard Release, Mouse |

---

## Voir Aussi

- [Référence Complète des Actions](Full-Action-Reference_fr) - Liste complète des actions
- [Préréglage Débutant](Beginner-Preset_fr) - Événements essentiels pour débutants
- [Préréglage Intermédiaire](Intermediate-Preset_fr) - Événements supplémentaires
- [Événements et Actions](Evenements_Actions_fr) - Aperçu des concepts de base
- [Réseau](Network_fr) - Multijoueur LAN, dont les six événements réseau ci-dessus
