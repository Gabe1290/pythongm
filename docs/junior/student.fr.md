# PyGameMaker Junior : crée ton propre jeu

## Comment utiliser cette fiche

Garde cette feuille à côté de ton ordinateur. Fais chaque partie sur
l'écran, puis coche la case. Si tu es bloqué, demande d'abord à ton voisin,
puis à ton enseignant.

## Partie 1 : tes outils

Regarde en haut de la fenêtre. Voici les boutons que tu vas utiliser :

- **Nouveau** (une page blanche) : commencer un nouveau jeu
- **Ouvrir** (un dossier) : ouvrir un jeu enregistré
- **Enregistrer** (une disquette) : sauvegarder ton jeu. Fais-le souvent !
- **Triangle vert** : **lancer ton jeu** (ou la touche **F5**)
- **Coche** : partager ton jeu sous forme de page web

À gauche, tu vois tes **ressources** : sprites, objets et salles.

- Un **sprite** est une image.
- Un **objet** est quelque chose dans ton jeu qui fait des choses.
- Une **salle** est un niveau où se passe le jeu.

## Partie 2 : dessiner un sprite

- [ ] Clique sur **Ressources > Créer un sprite**.
- [ ] Écris un nom, par exemple `spr_hero`, puis clique sur OK.
- [ ] Une fenêtre de dessin s'ouvre. Choisis une couleur et dessine avec le crayon.
- [ ] Clique sur **Enregistrer** quand tu es content de ton dessin.

> TIP : les noms commencent par `spr_` pour les sprites et `obj_` pour les
> objets. Utilise seulement des lettres et des chiffres, sans espace.

Tu peux aussi cliquer sur **Ressources > Importer un sprite** pour utiliser
une image qui est dans un fichier. Pour modifier un sprite plus tard,
**double-clique** dessus dans la liste de gauche.

## Partie 3 : faire bouger un objet

- [ ] Clique sur **Ressources > Créer un objet** et appelle-le `obj_hero`.
- [ ] Dans **Sprite**, choisis ton sprite.
- [ ] Dans la zone **Blockly**, glisse des blocs depuis la gauche pour
      construire ce qui se passe. Par exemple : **Clavier: Gauche** puis
      **définir vitesse horizontale à**.
- [ ] Ajoute **Clavier: Aucune touche** puis **arrêter le mouvement**, pour
      que ton héros s'arrête.

> TIP : fais un clic droit sur un bloc pour le **dupliquer** ou le **supprimer**.

## Partie 4 : construire une salle et jouer

- [ ] Clique sur **Ressources > Créer une salle**.
- [ ] Clique sur un objet dans la liste, puis clique dans la salle pour le placer.
- [ ] Appuie sur le **triangle vert** (ou **F5**) pour jouer.

> DONE : tu dois voir ton sprite dans le jeu et pouvoir le déplacer.

## Partie 5 : partager ton jeu

- [ ] Clique sur **Fichier > Exporter en HTML5**.
- [ ] Choisis un dossier où l'enregistrer.
- [ ] Clique sur **Oui** pour l'ouvrir dans ton navigateur.

Tu obtiens un seul fichier qui se termine par `.html`. Envoie-le à un ami :
il pourra y jouer dans n'importe quel navigateur !

## Tu es bloqué ?

| Ce qui se passe | Essaie ceci |
|---|---|
| Mon objet ne bouge pas | As-tu mis un bloc sous l'événement **Clavier** ? L'objet est-il dans la salle ? |
| Mon héros ne s'arrête jamais | Ajoute **Clavier: Aucune touche** et **arrêter le mouvement** |
| Je ne vois pas mon sprite dans le jeu | As-tu choisi le sprite dans la case **Sprite** de l'objet ? |
| J'ai supprimé quelque chose par erreur | **Outils > Restaurer les ressources supprimées** le ramène |
| Le jeu affiche une fenêtre grise | Attends quelques secondes, puis réessaie |

## Mots à connaître

- **Sprite** : une image utilisée dans ton jeu
- **Objet** : quelque chose dans ton jeu qui peut faire des choses
- **Salle** : un niveau
- **Événement** : « quand quelque chose arrive », comme appuyer sur une touche
- **Action** : « faire quelque chose », comme bouger
- **Bloc** : une pièce de ton programme

## Défis

- **Essaie (5 min) :** dessine un deuxième sprite et crée un deuxième objet.
- **Va plus loin :** fais aussi bouger ton héros vers le haut et vers le bas.
- **Invente :** crée un objet mur qui arrête ton héros.

## Réfléchis

1. À quoi sert un événement **Clavier** ?
2. Quelle est la différence entre un sprite et un objet ?
3. Comment montrerais-tu ton jeu à quelqu'un à la maison ?

## Mes notes

[[notes:6]]
