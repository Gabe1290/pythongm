# Éditeur de Code

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de) | [Italiano](Code-Editor_it) | [Español](Code-Editor_es) | [Português](Code-Editor_pt)

---

> [Retour à l'accueil](Home_fr)

Chaque objet de PyGameMaker possède un onglet **Éditeur de Code** à côté
de la Liste d'Événements et de Blockly — une troisième façon de travailler
avec les mêmes événements et actions, cette fois en vrai Python. Ce n'est
pas un export à sens unique : le code que vous écrivez ici est réanalysé
et transformé en événements et actions structurés, il reste donc
synchronisé avec les deux autres vues.

---

## Ouvrir l'Éditeur de Code

1. Ouvrez un objet dans l'Éditeur d'Objets
2. Cliquez sur l'onglet **💻 Éditeur de Code**

![L'Éditeur de Code en mode "Voir le Code Généré" : une classe avec une
méthode par événement (on_create, on_step, on_collision_obj_power, ...),
montrant le vrai Python que compilent vos événements et actions
visuels](images/code-editor.png)

---

## Deux Modes

Un menu déroulant en haut permet de basculer entre eux :

### 📖 Voir le Code Généré

Lecture seule. Montre le Python vers lequel compilent les événements et
actions actuels de votre objet — une méthode par événement (`on_create`,
`on_step`, `on_collision_obj_ennemi`, ...), appelant `self.*` et `game.*`
exactement comme le fait le moteur d'exécution. Une action pour laquelle
le générateur n'a pas d'équivalent Python propre apparaît quand même,
signalée par un commentaire (`# Unknown action: ...`) au-dessus de la
ligne qu'elle a produite — rien n'est caché, même pour les cas limites.
Cliquez sur **🔄 Rafraîchir** pour régénérer après avoir modifié des
événements ailleurs.

### ✏️ Modifier du Code Personnalisé

Modifiable, avec coloration syntaxique Python. Commencez à taper (ou
modifiez le code de départ repris du mode Voir) et PyGameMaker analyse
votre classe environ 1,5 seconde après que vous arrêtez d'écrire — une
pastille de statut à côté de la barre d'outils affiche **idle / busy /
error / empty** pendant ce temps. Une fois l'analyse réussie, vos méthodes
**remplacent** les événements et actions de l'objet (pas de fusion) —
quels que soient les événements que votre code définit, ils deviennent la
liste d'événements de cet objet, visible immédiatement dans les onglets
Liste d'Événements et Blockly.

Si l'analyse échoue (erreur de syntaxe, ou code que l'analyseur ne peut
pas relier à des événements), la pastille de statut affiche l'erreur et
rien n'est appliqué — les événements de votre objet restent tels quels
jusqu'à ce que le code s'analyse correctement.

---

## Pourquoi l'Utiliser

- **Rapidité** — certaines logiques (un calcul à branches multiples, une
  boucle, une formule ponctuelle) se tapent plus vite qu'elles ne
  s'assemblent avec des blocs ou une liste d'actions.
- **Pont d'apprentissage** — basculez les événements d'un objet construit
  par un débutant en mode Voir pour voir l'équivalent en code réel, une
  étape naturelle pour un élève qui passe de la programmation visuelle à
  Python.
- **Précision** — tout ce qui s'exprime comme une simple méthode Python
  sur l'objet fonctionne, sans attendre qu'une action visuelle
  correspondante existe.

C'est le même mécanisme sous-jacent que l'action **Exécuter du Code**
disponible depuis la liste d'actions / Blockly (catégorie *Contrôle*) —
l'onglet Éditeur de Code fonctionne simplement à l'échelle d'un objet
entier plutôt qu'une action à la fois.

---

## Étapes Suivantes

- [[Editeur_Objets_fr|Éditeur d'Objets]] - Où se trouve l'onglet Éditeur de Code
- [[Programmation_Visuelle_fr|Programmation Visuelle]] - La vue Blockly des mêmes événements
- [[Evenements_Actions_fr|Événements et Actions]] - Ce que fait chaque action
