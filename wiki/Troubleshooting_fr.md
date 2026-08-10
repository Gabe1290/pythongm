# Dépannage

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt) | [Русский](Troubleshooting_ru)

---

> [Retour à l'accueil](Home_fr)

Problèmes courants et où chercher. Pour les problèmes liés à
l'installation (Python introuvable, dépendances manquantes, bibliothèques
d'affichage Linux), voir d'abord la section Dépannage de
[[Demarrage_fr|Premiers Pas]] — cette page couvre les problèmes qui
surviennent une fois PyGameMaker déjà lancé.

---

## Mon jeu plante ou se ferme immédiatement quand j'appuie sur Tester le Jeu (F5)

**Lancez l'IDE depuis un terminal, pas depuis un raccourci de bureau, pour
voir l'erreur.** La trace d'un sous-processus de test de jeu qui plante
est enregistrée dans la sortie console de l'IDE elle-même
(`python main.py` dans un terminal) — si vous avez lancé l'IDE sans
console visible (par exemple un raccourci Windows), ce message n'a nulle
part où apparaître. Relancez depuis un terminal et reproduisez le plantage
pour voir la vraie trace Python.

Causes courantes :
- Une action **Exécuter du Code** ou du code personnalisé dans l'Éditeur
  de Code avec une erreur de syntaxe ou une faute de frappe dans un appel
  `game.*`/`self.*`
- Une action de collision ou de comparaison référençant un objet qui a
  depuis été renommé ou supprimé

---

## L'IDE elle-même a planté quand j'ai essayé d'ouvrir un éditeur

Vérifiez **`~/pygamemaker_crash.log`** (dans votre dossier personnel) —
les plantages des éditeurs d'objet/salle/sprite y sont écrits
spécifiquement pour rester visibles même quand l'IDE a été lancée sans
fenêtre de console. Incluez la section pertinente de ce fichier si vous
signalez le bug.

---

## L'export dit « X introuvable » / une dépendance manque

Les exports bureau et mobile (.exe Windows, .app macOS, binaire Linux,
Kivy/Android/iOS) intègrent un environnement d'exécution via PyInstaller
ou Buildozer, et ces outils doivent être installés dans le **même Python
qui exécute l'IDE** — une installation système ailleurs sur la machine ne
compte pas. Le message d'erreur de la boîte de dialogue d'export donne la
solution exacte, mais en résumé :

- **Aucun droit administrateur nécessaire.** Soit activez votre
  environnement virtuel et lancez `pip install <paquet>`, soit installez
  dans votre propre compte avec `pip install --user <paquet>` — les deux
  fonctionnent sans droits admin.
- Tout installer d'un coup : `pip install -r requirements.txt`
- **Aucune installation du tout ?** Utilisez plutôt l'export **HTML5
  (Navigateur Web)** — il ne nécessite rien d'installé localement et le
  résultat fonctionne dans n'importe quel navigateur. (Notez que ceci ne
  s'applique qu'à la *fabrication* de l'export — un `.exe`/`.app`
  terminé ne nécessite rien d'installé sur la machine qui l'*exécute*
  simplement.)

---

## J'ai reçu un avertissement avant l'Export (« X utilise Y mais il n'y a pas de Z »)

L'export lance d'abord une validation du projet et affiche tout ce qu'il
trouve avant que la boîte de dialogue d'Export n'apparaisse — par exemple
un objet utilisant **Salle Suivante** dans un projet avec une seule
salle, ce qui n'aurait aucun effet. Ce sont des **avertissements, pas des
erreurs** : cliquez sur OK et l'export continue ; ils signalent une
logique qui ne fera probablement pas ce que vous attendez, sans vous
empêcher de publier.

---

## Un sprite affiche un badge rouge « (non importé) » dans l'arborescence des ressources

Cela signifie que le fichier image du sprite est absent du disque
(généralement parce qu'un projet a été copié ou partagé sans son dossier
`sprites/`). C'est purement informatif — l'exécution et l'export
l'ignorent — et **se corrige automatiquement à la prochaine sauvegarde**,
une fois le fichier réellement présent à nouveau. Aucune correction
manuelle nécessaire au-delà de s'assurer que le fichier image se trouve
là où le sprite l'attend.

---

## Autre chose ne va pas

- Consultez la [[FAQ_fr|FAQ]] pour les questions courantes
- Signalez les bugs sur le [Suivi des Problèmes GitHub](https://github.com/Gabe1290/pythongm/issues) — incluez votre OS, votre version de Python, et (si pertinent) la sortie console ou `~/pygamemaker_crash.log`

---

## Étapes Suivantes

- [[Demarrage_fr|Premiers Pas]] - Dépannage lié à l'installation
- [[Exportation_fr|Exporter des Jeux]] - Référence complète de l'export
- [[FAQ_fr|FAQ]] - Questions fréquemment posées
