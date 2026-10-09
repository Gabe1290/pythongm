# PyGameMaker — Tutoriel 15 : Fusion de Fruits — Guide de l'enseignant·e

Accompagne le tutoriel intégré (**Aide > Tutoriels > Fusion de Fruits : Attrape et Fusionne !**, 5 pages) ainsi que la fiche élève et la feuille d'exercices correspondantes. Aucun tutoriel précédent n'est nécessaire — c'est un bon premier projet, y compris pour les plus jeunes élèves (8-9 ans), car il n'exige jamais de lire des instructions denses sans aide : chaque phase répète la même recette en quatre étapes avec de nouveaux noms et nombres.

## Aperçu

Les élèves construisent un jeu de « fusion » dans le style des jeux mobiles populaires (attraper un fruit qui correspond, il fusionne en quelque chose de plus gros) sans aucune vraie physique d'empilement. Quatre phases : un panier mobile ; une première fusion (cerise vers fraise) ; une deuxième fusion (fraise vers orange), construite en répétant littéralement la recette de la première fusion ; et une fusion finale (orange vers pastèque) qui fait aussi gagner la partie. Nouvelles idées : une **variable qui se souvient d'un état** (`held_level`), un bloc **Si / Sinon**, et **changer le sprite d'un objet pendant que le jeu tourne**.

> INFO: Demande « comment le panier se souvient-il de ce qu'il tient ? » La réponse, « un nombre que nous inventons nous-mêmes, `held_level` », est l'idée clé de la leçon — et la raison pour laquelle il n'y a aucun état de « panier vide » à expliquer (il commence en tenant une cerise, c'est-à-dire `held_level` = 1).

## Minutage suggéré (45 minutes)

Le tutoriel indique 20 à 25 minutes pour un élève à l'aise ; prévois du temps supplémentaire pour le premier bloc Si/Sinon, car il est nouveau.

| Segment | Temps | Ce qui se passe |
| Récap et prédiction | 5 min | Montre le jeu terminé ; demande comment le panier pourrait « se souvenir » de ce qu'il tient |
| Phase 1 : panier mobile | 5-10 min | Page 2 |
| Phase 2 : première fusion | 10-15 min | Page 3 (la page la plus lente — le Si/Sinon est nouveau) |
| Phase 3 : deuxième fusion | 5-10 min | Page 4 (même recette, devrait être plus rapide) |
| Phase 4 : gagner la partie | 10 min | Page 5 |
| Feuille d'exercices / billet de sortie | 5 min | Parties A-C de la feuille |

## Déroulement pas à pas et problèmes fréquents

**Phase 1 : panier mobile**

- Trois événements clavier, exactement comme au Tutoriel 2 / Tutoriel 9. Le panier peut sortir de l'écran ; c'est normal et n'est pas corrigé dans ce tutoriel.
- Le sprite est `spr_basket_empty` à ce stade — aucune notion de fusion n'a encore été introduite, donc il n'y a rien à tenir.

**Phase 2 : première fusion**

- C'est la phase qui introduit toutes les nouvelles idées à la fois : `held_level`, le changement du sprite de départ du panier vers `spr_basket_cherry`, et le Si/Sinon de la collision. Prévois le plus de temps ici.
- **Le sprite du panier change vers `spr_basket_cherry` AVANT tout jeu** — c'est un changement de sprite manuel, ponctuel, dans les propriétés de l'objet, pas une action. Un élève qui le saute aura un panier qui ne montre jamais visuellement ce qu'il tient, même si la logique en dessous est correcte ; le jeu continuera à compter les points correctement, ce qui peut rendre l'erreur facile à manquer.
- `held_level` est défini dans **Quand créé**, nulle part ailleurs. Un élève qui le définit par erreur dans le générateur ou dans l'objet fruit le verra se réinitialiser de façon inattendue.
- La branche *Si held_level est égal à 1* de la collision doit contenir les trois actions (définir `held_level`, ajouter au score, définir le sprite) — un élève qui place l'action de score ou de sprite dans la mauvaise branche (ou en dehors du Si) obtient un jeu qui compte correctement les points mais ne montre jamais la fusion, ou la montre à chaque capture, même les mauvaises.
- *Détruire l'autre instance*, pas *Détruire cette instance* — l'erreur fréquente d'une seule lettre qui détruit le panier au lieu du fruit attrapé.

**Phase 3 : deuxième fusion**

- Délibérément la phase rapide : exactement les quatre mêmes étapes que la Phase 2, avec « cerise » renommé en « fraise » et 1/2 changé en 2/3. Si un élève a eu du mal avec le Si/Sinon de la Phase 2, c'est ici que ça clique, car il reconstruit la même forme avec des noms différents.
- Une erreur de copier-coller fréquente : oublier de changer la condition *Si held_level est égal à 1* en *égal à 2*. Le symptôme est qu'attraper une fraise ne fait rien d'utile (held_level n'est jamais 1 une fois qu'une cerise a déjà fusionné), ce qui ressemble à un bug plus gros qu'il ne l'est.

**Phase 4 : gagner la partie**

- La condition de victoire n'est **pas** une vérification séparée ailleurs — *Aller à la salle room_win* est juste une action de plus dans la branche *Si* de la collision avec l'orange, exécutée exactement une fois, au moment où la quatrième fusion se produit. Les élèves venant de la vérification de victoire séparée du Tutoriel 9 (dans un événement Pas) cherchent parfois un équivalent ici et n'en ont pas besoin.
- Il n'y a délibérément aucun sprite ni générateur de pastèque qui tombe. Si un élève demande « où est le fruit pastèque », la réponse est : il n'existe jamais que comme l'apparence finale du panier, jamais comme quelque chose qui tombe.
- `obj_win_text` dessine son message à des coordonnées fixes dans la salle de 640x480 que ce tutoriel utilise partout (pas le 1024x768 par défaut d'autres tutoriels) — un élève qui tape de mémoire les coordonnées du Tutoriel 9 verra un texte mal placé ou hors écran.

> TIP: **Projets de référence.** Télécharge les projets de contrôle depuis le wiki (`15_fruit_fusion_checkpoints.zip`) : un projet pour la fin de chaque phase. Donne à un élève bloqué la phase précédente plutôt que de dépanner son Si/Sinon à partir de rien.

## Vocabulaire introduit

| Terme | Ce que cela veut dire ici |
| Fruit tenu | Le fruit que le panier porte actuellement, dont on se souvient dans `held_level` |
| Fusion | Attraper un fruit qui correspond pour qu'il devienne le fruit suivant, plus gros |
| Si / Sinon | Un bloc qui fait une chose quand quelque chose est vrai, et une autre chose sinon |
| Générateur | Un objet invisible dont le seul rôle est de créer d'autres objets selon une minuterie |
| Changement de sprite en jeu | Changer quelle image un objet montre pendant que le jeu tourne, comme retour visuel |

## Questions de discussion

- Pourquoi le panier a-t-il besoin d'une variable (`held_level`) plutôt que de simplement vérifier son sprite actuel ?
- Qu'est-ce qui changerait si les types de fruits tombaient d'un seul générateur choisissant un type au hasard, plutôt que trois générateurs séparés ?
- Pourquoi une mauvaise capture ne peut-elle jamais terminer la partie dans cette version ? Qu'est-ce qui changerait si elle le pouvait ?
- Quels autres jeux utilisent « combiner deux choses qui correspondent pour en faire une plus grosse » comme idée centrale ?

## Différenciation

- **Soutien :** donne le point de contrôle de la Phase 2, pour qu'un élève en difficulté n'ait qu'à construire la deuxième et la troisième fusion en reproduisant le motif de la première.
- **Extension :** un quatrième générateur et un palier de fruit entre l'orange et la pastèque ; des vies qui diminuent sur des mauvaises captures répétées ; un deuxième panier pour une fusion compétitive à deux joueurs.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-A, 4-B.

**Partie B :** 1. `obj_player`, Collision avec `obj_fruit_cherry`. 2. `obj_spawn_cherry`, Alarme 0. 3. `obj_fruit_cherry` (et `obj_fruit_strawberry`, `obj_fruit_orange`), Hors de la salle. 4. `obj_win_text`, Quand dessiner. 5. `obj_win_text`, Touche pressée : Espace.

**Partie C :**

1. La branche *Si* de la collision vérifie seulement `held_level == 3` (tenir une orange) ; si `held_level` est différent, le *Si* est faux et la branche *Sinon* s'exécute à la place — le type du fruit lui-même ne change jamais, seul ce que l'on tient change, et une cerise ne peut jamais correspondre qu'à un panier tenant déjà une cerise.
2. La fusion en pastèque ne se déclencherait jamais : une capture correspondante ajouterait encore 50 points et changerait le sprite seulement si ces actions étaient (aussi) laissées dans la branche *Si*, mais *Aller à la salle room_win* placé dans *Sinon* se déclencherait à la place à chaque MAUVAISE capture, envoyant le joueur vers la salle de victoire sans jamais vraiment terminer la fusion — l'inverse du comportement voulu.
3. Un générateur par type signifie que l'événement de collision pour cet objet précis (`obj_fruit_cherry`, par exemple) identifie déjà le palier, sans conditionnel supplémentaire nécessaire. Un seul générateur aléatoire exigerait que le fruit généré porte sa propre variable « quel palier suis-je », et chaque vérification de collision devrait lire la variable de `other` avant de la comparer à `held_level` — plus de pièces mobiles pour le même résultat.

**Parties D et E :** réalisation et réflexion.

## Grille d'évaluation : Fusion de Fruits

| Niveau | Ce que le jeu montre |
| 4 - Complet | Le panier se déplace ; trois types de fruits tombent et sont chacun gérés par sa propre collision ; une capture correcte fait fusionner le panier d'un palier avec le bon bonus de score et le bon changement de sprite ; une mauvaise capture n'ajoute que 1 point ; fusionner une orange affiche VOUS AVEZ GAGNÉ ! et ESPACE redémarre |
| 3 - Fonctionnel | Le déplacement et la première fusion fonctionnent ; la deuxième ou la troisième fusion, ou l'écran de victoire, est manquant ou incorrect |
| 2 - Partiellement là | Le panier se déplace et des fruits tombent, mais aucune fusion ne fonctionne correctement |
| 1 - Commencé | Le panier existe et se déplace ; rien ne tombe |

## Liste de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la Phase 2 (une fusion fonctionne de bout en bout)
- [ ] Note qui a besoin du projet de contrôle la prochaine fois
