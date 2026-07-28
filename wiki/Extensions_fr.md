# Extensions

*[Accueil](Home_fr) | [Vue 3D](3D-View_fr) | [Référence Complète des Actions](Full-Action-Reference_fr)*

---

Une **extension** est un module d'extension autonome qui ajoute des capacités à
PyGameMaker sans modifier le moteur de base. Une extension peut apporter :

- de nouvelles **actions** (elles apparaissent dans le sélecteur d'actions comme
  n'importe quelle action intégrée),
- une nouvelle façon de **dessiner une salle** (un moteur de rendu personnalisé), et
- le **code d'exportation** correspondant, afin que les jeux qui l'utilisent
  s'exportent toujours vers HTML5 et Kivy/Android.

L'extension intégrée **2.5D Raycast** (la fonctionnalité [Vue 3D](3D-View_fr)) est
l'exemple de référence : elle ajoute quatre actions « Vue 3D » et un moteur de
rendu à la première personne, et elle s'exporte vers les trois cibles.

---

## Activer et désactiver

Les extensions sont livrées **activées**. Vous pouvez en désactiver une (ou
activer une extension livrée désactivée) sans modifier le moindre code, grâce à la
clé `extensions` de votre configuration — une table `nom de dossier → activé/désactivé` :

```json
"extensions": { "raycast_2_5d": false }
```

Une entrée **absente** signifie « utiliser la valeur par défaut de l'extension »,
de sorte que rien ne disparaît jamais parce qu'une clé manquait. Les changements
prennent effet au démarrage suivant (les actions s'enregistrent au lancement).

Avec l'extension 2.5D Raycast désactivée, une salle qui active la vue à la
première personne s'affiche simplement en vue du dessus.

---

## Quand un projet a besoin d'une extension

Comme une extension peut être désactivée, PyGameMaker vous aide à éviter les
mauvaises surprises :

- **Au chargement**, si un projet utilise des actions issues d'une extension
  actuellement désactivée, l'IDE affiche un avertissement nommant l'extension et
  les fonctionnalités concernées (pour qu'un jeu 3D ne s'affiche pas
  silencieusement en vue du dessus).
- **À l'enregistrement**, le projet consigne les extensions dont ses actions
  dépendent dans `project.json` (une liste `requires_extensions`) — une note
  durable que toute personne à qui vous partagez le projet peut voir. Un projet
  qui n'utilise aucune action d'extension omet simplement ce champ.

---

## Extensions et modules d'extension (plugins)

Les deux ajoutent des actions ; ils ne diffèrent que par leur conditionnement :

| | Plugin | Extension |
|---|--------|-----------|
| Forme | un unique fichier `.py` dans `plugins/` | un dossier dans `extensions/` avec un manifeste |
| Idéal pour | un petit ensemble d'actions | une fonctionnalité répartie sur plusieurs fichiers et/ou qui dessine/exporte |
| Exemple | les actions **Audio** (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## À quoi ressemble un dossier d'extension

Pour les curieux (et pour quiconque en écrit une), une extension est un dossier
lisible :

```
extensions/raycast_2_5d/
├── extension.json     # manifeste : nom, version, activé, provides_actions
├── actions.py         # les schémas d'actions (affichés dans le sélecteur)
├── handlers.py        # ce que font les actions à l'exécution
├── renderer.py        # le moteur de rendu de salle personnalisé (le raycaster)
├── state.py           # l'état par salle (rangé sous la salle)
├── hud.py             # les générateurs de géométrie mini-carte / barre DOOM
├── export_html5.js    # le portage HTML5, injecté dans l'export web
├── export_kivy.py     # le portage Kivy, injecté dans l'export mobile/ordinateur
└── README.md          # comment tout cela s'articule
```

La liste `provides_actions` du manifeste est ce qui permet à l'IDE de nommer
l'extension exacte lorsqu'un projet a besoin d'une extension désactivée.

---

## Voir aussi

- [Vue 3D](3D-View_fr) — la fonctionnalité fournie par l'extension intégrée
- [Référence Complète des Actions](Full-Action-Reference_fr) — les actions d'extension y figurent aussi
- [Exporter des Jeux](Exportation_fr) — les fonctionnalités d'extension sont conservées dans les exports
