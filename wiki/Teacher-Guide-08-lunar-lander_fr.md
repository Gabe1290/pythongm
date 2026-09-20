# PyGameMaker — Tutoriel 8 : Alunissage — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-08-lunar-lander_fr.pdf) · [ODT](downloads/Teacher-Guide-08-lunar-lander_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/08_lunar_lander_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > Lunar Lander : Atterrir sur la Lune**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves doivent avoir terminé le Tutoriel 7 (gravité, touches maintenues, collisions).

## Vue d'ensemble

Les élèves construisent un jeu d'alunissage en trois phases : un atterrisseur avec gravité et poussée, une aire d'atterrissage et la détection des crashs, et un ATH avec un titre. Notions nouvelles : une **gravité très faible**, la **poussée** comme changement de vitesse verticale, les **collisions de réussite et d'échec**, et le dessin de texte sur une **salle noire**.

> **Info:** C'est une leçon à saveur de physique. Demandez « pourquoi la gravité de la Lune vaut-elle 0.05 ? » (environ un sixième de celle de la Terre ; le jeu de plateforme utilisait 0.5 pour un rendu plus vif) et laissez les élèves essayer d'autres valeurs.

## Durée suggérée (45 minutes)

Le tutoriel annonce 20 à 25 minutes pour un élève à l'aise.

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Comparez avec le jeu de plateforme : qu'est-ce qui change quand il y a presque pas de gravité ? |
| Phase 1 : atterrisseur qui vole | 10-15 min | Pages 1-2 |
| Phase 2 : atterrir et s'écraser | 10-15 min | Page 3 ; inclut le point sur la gravité coupée ci-dessous |
| Phase 3 : contrôleur et ATH | 5 min | Page 4 |
| Jouer et comparer | 5 min | Les élèves essaient les niveaux des autres |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : un atterrisseur qui vole**

- La gravité est réglée dans **Création** : direction **270**, force **0.05**. À 0.05, l'atterrisseur atteint une vitesse d'environ 2.5 après 50 pas et d'environ 5 après 100 pas : lent et flottant.
- **Haut (maintenue)** *règle* la vitesse verticale à -2 (une montée régulière) ; il n'accélère pas. Après le relâchement, la gravité annule peu à peu la montée (environ 40 pas pour s'arrêter), puis l'atterrisseur retombe.
- **Aucune touche** ne doit remettre à zéro que la vitesse **horizontale**. *Arrêter le mouvement* effacerait la vitesse verticale et l'atterrisseur resterait suspendu.
- Dans cette phase, il n'y a pas de collision avec le sol : l'atterrisseur tombe **à travers** le sol. C'est normal.
- Utilisez un arrière-plan de salle **noir** (l'espace).

**Phase 2 : atterrir et s'écraser**

- Le sol et l'aire doivent être **Solides**, et l'atterrisseur a besoin d'un événement de collision pour chacun.
- Tout contact avec le sol est un crash, et tout contact avec l'aire est un atterrissage, **à n'importe quelle vitesse et de n'importe quel côté**. Un atterrissage brutal sur l'aire affiche quand même « Landing successful! ». L'atterrissage limité en vitesse est l'idée de défi du tutoriel.
- **Coupez la gravité après l'atterrissage.** Sinon, la gravité pousse en continu l'atterrisseur posé contre l'aire, la collision se redéclenche à chaque image, et le message « Landing successful! » réapparaît sans arrêt (dans le projet de référence, il est apparu 190 fois en quelques secondes). Le tutoriel inclut maintenant *Définir la gravité force 0* dans l'événement de l'aire. C'est la cause la plus probable de « le jeu reste bloqué sur des messages ».
- Après le message de crash, la salle recommence : l'atterrisseur repart du haut.
- Une aire d'un ou deux blocs est un défi raisonnable.

**Phase 3 : contrôleur et ATH**

- Le contrôleur doit être placé dans la salle.
- Le texte est dessiné en **noir par défaut**, donc invisible sur la salle noire ; l'événement Dessin commence donc par *Définir la couleur de dessin* en blanc. Sans cela, le titre et les instructions ne s'affichent pas.
- Le *Définir le score 0* du contrôleur ne sert pas plus loin dans ce tutoriel (il n'y a pas encore de score) ; un score selon le carburant restant est un défi.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`08_lunar_lander_checkpoints.zip`) : un projet pour la fin de chaque phase, avec un niveau où l'aire est dans un trou. Donnez à un élève bloqué la phase précédente.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Poussée | Une impulsion vers le haut contre la gravité |
| Force de gravité | La vitesse ajoutée vers le bas à chaque pas |
| Aire d'atterrissage | Un objet dont la collision signifie la réussite |
| ATH | Du texte à l'écran pour le joueur |
| Couleur de dessin | La couleur utilisée par les actions de dessin qui suivent |


## Questions de discussion

- Que change-t-on si l'on double la gravité ? Si l'on divise la poussée par deux ?
- Pourquoi une gravité très faible est-elle plus difficile à contrôler qu'il n'y paraît ?
- Comment le jeu pourrait-il distinguer un atterrissage doux d'un atterrissage brutal ? (Comparer la vitesse verticale à une limite.)
- Pourquoi coupe-t-on la gravité après l'atterrissage ?

## Différenciation

- **Soutien :** donnez le projet de la phase 1 ; utilisez le niveau de référence avec son aire.
- **Approfondissement :** un compteur de carburant ; un atterrissage limité en vitesse ; une aire plus petite ; plus de niveaux ; un score selon le carburant restant.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-B, 3-D, 4-A.

**Partie B :** 1. Création (Définir la gravité). 2. Clavier : Flèche haut (maintenue). 3. En collision avec `obj_pad`. 4. En collision avec `obj_ground` (avec Recommencer la salle). 5. Dessin (sur le contrôleur).

**Partie C :**

1. La vitesse verticale reste proche de -2 et la gravité n'ajoute que 0.05 à chaque pas : il faut environ 40 pas pour que la montée s'arrête. C'est pourquoi l'atterrisseur continue de monter avant de tomber.
2. Non, la vitesse n'a pas d'importance dans le jeu du tutoriel. Pour qu'un atterrissage brutal soit un crash, testez la vitesse verticale dans l'événement de l'aire : au-dessus d'une limite, c'est un crash ; sinon, un atterrissage.
3. La gravité pousse en continu l'atterrisseur contre l'aire, donc l'événement de collision se redéclenche sans cesse. Coupez la gravité (force 0) dans l'événement de l'aire.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : Alunissage

| Niveau | Ce que montre le jeu |
|---|---|
| 4 - Complet | Gravité lente, poussée et direction fonctionnent ; l'aire donne un seul message d'atterrissage et arrête l'atterrisseur ; le sol fait s'écraser et recommencer ; le texte de l'ATH est visible |
| 3 - Fonctionnel | Vol, atterrissage et crash fonctionnent ; l'ATH manque ou est invisible, ou le message d'atterrissage se répète |
| 2 - À moitié | L'atterrisseur vole, mais l'atterrissage ou le crash ne fonctionne pas |
| 1 - Commencé | L'atterrisseur existe mais ne tombe pas ou ne peut pas être dirigé |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a atteint au moins la phase 1 (piloter l'atterrisseur)
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
