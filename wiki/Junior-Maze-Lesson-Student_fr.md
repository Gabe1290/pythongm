# Mon premier labyrinthe : crée un jeu auquel tu peux jouer sur téléphone

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Junior-Maze-Lesson-Student_fr.pdf) · [ODT](downloads/Junior-Maze-Lesson-Student_fr.odt)

---

## Comment utiliser cette fiche

Tu as environ 90 minutes. Fais chaque partie sur ton écran, puis coche la case.
Si tu es bloqué, demande d'abord à ton voisin, puis à ton enseignant. À la
fin, tu auras un jeu qui marche dans un navigateur web, et même sur un
téléphone !

## Partie 1 : ouvre ton labyrinthe (5 min)

- [ ] Clique sur **Fichier > Ouvrir un projet** et ouvre le dossier **My Maze**.
- [ ] Regarde la liste à gauche. Tu as un **spr_wall** (une image), un
      **obj_wall** (le mur) et une salle appelée **room0**.
- [ ] Appuie sur le triangle vert (ou sur **F5**) pour tester. Tu vois une boîte
      vide. Ferme la fenêtre du jeu.

> TIP : appuie souvent sur **Enregistrer**. Le bouton avec la disquette
> sauvegarde ton jeu.

## Partie 2 : dessine ton héros et ton but (15 min)

- [ ] Clique sur **Ressources > Créer un sprite**. Appelle-le `spr_hero`, puis OK.
- [ ] Dessine ton héros ! Remplis le carré. Clique sur **Enregistrer**.
- [ ] Recommence pour le but. Appelle-le `spr_goal`. Fais-le différent du héros
      et des murs.

> TIP : les noms utilisent seulement des lettres, des chiffres et `_`. Pas
> d'espace !

## Partie 3 : fais bouger le héros (20 min)

- [ ] Clique sur **Ressources > Créer un objet**. Appelle-le `obj_hero`.
- [ ] Dans **Sprite**, choisis `spr_hero`.
- [ ] Dans la zone **Blockly**, construis ces blocs. Glisse-les depuis la gauche.

| Quand ça arrive | Fais ceci |
|---|---|
| **Clavier:** Flèche gauche (maintenue) | **définir vitesse horizontale à** -4 |
| **Clavier:** Flèche droite (maintenue) | **définir vitesse horizontale à** 4 |
| **Clavier:** Flèche haut (maintenue) | **définir vitesse verticale à** -4 |
| **Clavier:** Flèche bas (maintenue) | **définir vitesse verticale à** 4 |
| **Clavier: Aucune touche** | **arrêter le mouvement** |
| **Quand collision avec** obj_wall | **arrêter le mouvement** |

- [ ] Clique sur **Enregistrer**.

> TIP : fais un clic droit sur un bloc pour le **dupliquer**. C'est plus rapide
> que de glisser un nouveau bloc à chaque fois.

> INFO : un signe moins fait aller le héros vers la gauche ou vers le haut. Un
> nombre sans signe l'envoie vers la droite ou vers le bas.

## Partie 4 : fais le but (10 min)

- [ ] Crée un objet appelé `obj_goal`. Donne-lui `spr_goal`.
- [ ] Construis ces blocs :

| Quand ça arrive | Fais ceci |
|---|---|
| **Quand collision avec** obj_hero | **Afficher message** "Tu as gagné !" |
| (le même événement) | **Redémarrer le niveau** |

Mets les deux blocs l'un sous l'autre, sous le même événement.

## Partie 5 : construis ton labyrinthe (20 min)

- [ ] Ouvre **room0** (double-clique dessus dans la liste).
- [ ] Clique sur **obj_wall**. Garde le bouton de la souris enfoncé et **glisse**
      pour peindre un mur.
- [ ] Clique sur **obj_hero**, puis clique une fois en haut à gauche dans la salle.
- [ ] Clique sur **obj_goal**, puis clique une fois loin de ton héros.
- [ ] Appuie sur **F5** et joue ! Peux-tu atteindre le but ?

> INFO : fais **tous les chemins larges de deux carrés**. Ton héros fait un
> carré de large et ne s'arrête pas toujours au milieu d'un chemin. Dans un
> chemin d'un seul carré, le héros peut rester coincé.

> DONE : tu dois voir ton héros, ton but et tes murs. Le héros s'arrête devant
> un mur. Quand tu touches le but, « Tu as gagné ! » apparaît.

## Partie 6 : partage ton jeu (10 min)

- [ ] Clique sur **Fichier > Exporter en HTML5**.
- [ ] Choisis un dossier. Clique sur **Oui** pour ouvrir le jeu dans ton navigateur.
- [ ] Regarde dans le dossier : tu as **un seul fichier** qui finit par `.html`.
      C'est ton jeu !
- [ ] Joue-y. Puis montre-le à un ami.

> TIP : sur un téléphone ou une tablette, des boutons flèches apparaissent sur
> l'écran. Garde un bouton appuyé pour avancer.

## Tu es bloqué ?

| Ce qui se passe | Essaie ceci |
|---|---|
| Le héros ne bouge pas | Le héros est-il dans la salle ? Y a-t-il un bloc sous **Clavier** ? |
| Le héros ne s'arrête jamais | Ajoute **Clavier: Aucune touche** avec **arrêter le mouvement** |
| Le héros traverse les murs | Ajoute **Quand collision avec** obj_wall avec **arrêter le mouvement** |
| Le héros est coincé dans un chemin | Fais le chemin large de deux carrés |
| Rien ne se passe au but | Le but a besoin de **Quand collision avec** obj_hero |
| J'ai supprimé quelque chose par erreur | **Outils > Restaurer les ressources supprimées** |

## Mots à connaître

- **Sprite** : une image
- **Objet** : quelque chose dans ton jeu qui peut faire des choses
- **Salle** : un niveau
- **Événement** : « quand quelque chose arrive »
- **Collision** : quand deux choses se touchent
- **Exporter** : faire une copie de ton jeu qui marche toute seule

## Défis

- **Essaie (5 min) :** change le message pour écrire quelque chose de drôle.
- **Va plus loin :** fais un deuxième but, ou dessine un plus beau mur.
- **Invente :** change d'ordinateur avec un ami et essaie de finir son labyrinthe.

## Réfléchis

1. Pourquoi le héros doit-il s'arrêter quand il touche un mur ?
2. Que fait le but quand le héros le touche ?
3. Pourquoi faisons-nous les chemins larges de deux carrés ?
