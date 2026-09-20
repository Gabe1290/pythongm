# PyGameMaker — Tutoriel 12 : 2.5D, textures, ciel et sol — Guide de l'enseignant·e

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Teacher-Guide-12-raycast-textures_fr.pdf) · [ODT](downloads/Teacher-Guide-12-raycast-textures_fr.odt) · [Projets de référence (ZIP)](downloads/solutions/12_raycast_textures_checkpoints.zip)

---

Document d'accompagnement du tutoriel intégré (**Aide > Tutoriels > 2.5D : Textures, ciel et sol**, 4 pages) et de la fiche élève et de la feuille d'exercices correspondantes. Les élèves poursuivent leur projet du Tutoriel 11. Les leçons 2.5D sont **masquées dans l'édition débutant** : changez d'abord l'édition.

## Vue d'ensemble

Les élèves habillent la salle à la première personne avec des textures. Notions nouvelles : une **texture n'est qu'un sprite** choisi dans *Activer la vue Raycast*, un **ciel défilant**, un **sol dallé**, des **couleurs de secours**, et les réglages **détail contre vitesse**. Le jeu ne change pas : c'est donc une bonne leçon d'arts visuels et de conception.

## Durée suggérée (45 minutes)

| Séquence | Durée | Ce qui se passe |
|---|---|---|
| Rappel et hypothèses | 5 min | Montrez des murs gris unis et texturés ; demandez ce qui fait « vrai » |
| Phase 1 : murs texturés | 10-15 min | Pages 1-2 ; dessiner la brique prend du temps, sinon importez une image |
| Phase 2 : ciel et sol | 15 min | Page 3 |
| Phase 3 : régler l'apparence | 10 min | Page 4 |
| Feuille d'exercices / ticket de sortie | 5 min | Parties A à C de la feuille |


## Déroulé étape par étape et difficultés fréquentes

**Phase 1 : murs texturés**

- Une texture est un sprite ordinaire. Réglez **Wall Texture** sur *Activer la vue Raycast* sur le nom exact du sprite. Les images **carrées** comme 64×64 rendent le mieux.
- Si **Wall Texture** est vide, les murs sont dessinés avec la **Wall Color** unie. **Textured Walls = non** force la couleur unie même si une texture est définie (pratique pour comparer).
- Les murs tournés à l'opposé de la lumière sont dessinés plus sombres ; c'est une astuce d'ombrage normale qui donne du volume aux coins.

**Phase 2 : ciel et sol**

- Le **ciel** est une image large (256×64). Il défile latéralement quand on tourne (un tour complet fait passer l'image une fois) mais ne change pas de taille quand on marche, comme un horizon lointain.
- La **dalle** du sol doit faire 32×32, une case de la grille. Elle se répète une fois par case et s'aligne sur le bas des murs.
- **Ceiling Texture** n'est utilisée que **s'il n'y a pas de ciel** ; une Sky Texture l'emporte toujours.
- Des noms vides donnent les couleurs de secours (Wall, Floor et Ceiling Color). Dans le projet de référence, vider les noms de texture redonne les couleurs unies.

**Phase 3 : régler l'apparence**

- **Columns** (320 par défaut) et **Floor Detail** (4 par défaut) échangent du détail contre de la vitesse : moins de colonnes et un Floor Detail plus haut sont plus rapides mais plus grossiers. Bon ordre sur un ordinateur lent : monter Floor Detail à 6-8 d'abord, puis baisser Columns.
- Les fautes de frappe dans les noms de texture sont le problème le plus courant ; faites copier les noms.

> **Astuce:** **Projets de référence.** Téléchargez les projets par étapes sur le wiki (`12_raycast_textures_checkpoints.zip`) : le projet au début de la leçon (le résultat du Tutoriel 11) et le projet terminé, texturé. Les textures du projet de référence sont de simples images générées ; les élèves doivent dessiner ou importer les leurs.

## Vocabulaire introduit

| Terme | Ce que cela signifie ici |
|---|---|
| Texture | Un sprite utilisé pour recouvrir un mur, le sol ou le plafond |
| Panorama | Une image large qui défile quand on tourne (le ciel) |
| Dalle | Une petite image répétée sur le sol |
| Couleur de secours | La couleur unie utilisée quand une texture n'est pas définie |
| Columns / Floor Detail | Les deux réglages vitesse contre détail |


## Questions de discussion

- Pourquoi le ciel bouge-t-il quand on tourne mais pas quand on marche ?
- Pourquoi une dalle de sol doit-elle correspondre à la taille d'une case de la grille ?
- Comment les vieux jeux s'en sortaient-ils avec des images aussi simples ?
- Que changeriez-vous pour faire un niveau qui fait peur ?

## Différenciation

- **Soutien :** fournissez des images de texture prêtes à importer ; partez du projet terminé et changez une texture.
- **Approfondissement :** plusieurs aspects de mur ; un plafond intérieur ; une grotte avec des couleurs sombres et une Render Distance courte.

## Corrigé de la feuille d'exercices

**Partie A :** 1-C, 2-D, 3-A, 4-B.

**Partie B :** 1. Wall Texture. 2. Sky Texture. 3. Floor Texture. 4. Mettre Textured Walls sur non. 5. Monter Floor Detail.

**Partie C :**

1. Le ciel : une Sky Texture l'emporte toujours sur une Ceiling Texture.
2. Le sol est dessiné une dalle par case : une dalle de 32×32 s'aligne donc sur les cases et le bas des murs, et le sol ne semble pas glisser.
3. Que le nom de la texture est écrit exactement comme le sprite, et que **Textured Walls** est activé.

**Parties D et E :** réalisation et bilan.

## Grille d'évaluation : 2.5D, textures

| Niveau | Ce que montre le projet |
|---|---|
| 4 - Complet | Des murs texturés, un ciel qui défile et un sol dallé ; l'élève sait expliquer les couleurs de secours et les réglages de détail |
| 3 - Fonctionnel | Les murs et soit le ciel soit le sol sont texturés |
| 2 - À moitié | Seuls les murs sont texturés, ou des noms sont faux donc certaines textures ne s'affichent pas |
| 1 - Commencé | La salle montre encore des couleurs unies |


## Liste de vérification de fin de séance

- [ ] Chaque élève a un projet enregistré (`Ctrl+S`)
- [ ] Chaque élève a vu un mur texturé
- [ ] Notez qui aura besoin du projet par étapes la prochaine fois
