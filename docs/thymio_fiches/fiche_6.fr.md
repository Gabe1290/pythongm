# Fiche 6 : Variables et conditions

**Exemple à ouvrir :** Thymio — Activités : arène libre  ·  **Durée :** 30 minutes

## Ce que tu vas apprendre

- ranger un nombre dans une **variable** ;
- l'augmenter, le diminuer, le **comparer** ;
- faire réagir le robot selon une valeur.

## 1. Une variable, c'est une boîte

Une variable a un **nom** et contient un **nombre** qui peut changer. Ici, la variable s'appelle **compteur**. Si on n'a rien mis dedans, elle vaut **0**.

| Action | Effet |
|---|---|
| **Définir une variable** (Nom de la variable = compteur, Valeur = 0) | met 0 dans la boîte |
| **Augmenter une variable** (Nom de la variable = compteur, Quantité = 1) | ajoute 1 |
| **Diminuer une variable** (Nom de la variable = compteur, Quantité = 1) | enlève 1 |
| **Si variable** (Nom de la variable = compteur, Comparaison = **>=**, Valeur = 3) | vrai si le contenu est au moins 3 |

## 2. Un compteur de pressions

Le robot doit compter les appuis sur **↑** et afficher **vert** à partir de 3, **rouge** avant.

- [ ] Dans **Bouton avant**, mets dans cet ordre :

| N° | Ce que tu ajoutes |
|---|---|
| 1 | **Si bouton appuyé** (Bouton = avant) |
| 2 | **Augmenter une variable** (compteur, 1) |
| 3 | **Si variable** (compteur **>=** 3) |
| 4 | **Régler la LED du dessus** vert (0, 32, 0) |
| 5 | **Si variable** (compteur **<** 3) |
| 6 | **Régler la LED du dessus** rouge (32, 0, 0) |

- [ ] Teste : appuie trois fois sur **↑**. À quel appui la LED devient-elle verte ?
- [ ] Pourquoi le compteur n'augmente-t-il **qu'une fois** par appui, alors que l'événement se déclenche aussi au relâchement ? (Regarde la ligne 1.)

> TIP: chaque condition s'applique à l'action juste en dessous d'elle. Ici elles sont à la suite : le robot teste les deux à chaque appui.

## 3. Remettre à zéro et reculer

- [ ] **Bouton arrière** : **Si bouton appuyé**, **Diminuer une variable** (compteur, 1), puis les mêmes lignes 3 à 6 pour mettre à jour la couleur.
- [ ] **Bouton central** : **Si bouton appuyé**, **Définir une variable** (compteur = 0), puis LED rouge.
- [ ] Appuie : ↑ ↑ ↑ (vert), ↓ (rouge), espace (rouge, compteur à 0).

> DONE: tu sais mémoriser une information et prendre une décision à partir d'elle.

## Pour aller plus loin

- Fais que le seuil soit **5** au lieu de 3. Combien de lignes dois-tu changer ?
- Fais afficher la valeur du compteur sur le cercle de LED : une LED de plus allumée à chaque appui (indice : **Si variable** compteur **==** 1, puis **Régler une LED du cercle** 0, etc.).
- Que se passe-t-il si tu appuies plusieurs fois sur ↓ à partir de 0 ?
