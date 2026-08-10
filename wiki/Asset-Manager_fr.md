# Gestionnaire de Ressources

> [English](Asset-Manager) | [Français](Asset-Manager_fr) | [Deutsch](Asset-Manager_de)

---

> [Retour à l'accueil](Home_fr)

Au-delà du créer/renommer/supprimer quotidien de l'arborescence des
ressources, PyGameMaker suit **où chaque ressource est réellement
utilisée**, garde les ressources supprimées récupérables au lieu de les
perdre définitivement, et peut trouver aussi bien les ressources inutilisées
que les fichiers orphelins qui encombrent le dossier du projet. Tout cela
se trouve dans le menu **Outils**.

---

## Filtrer l'Arborescence des Ressources

Tapez dans la zone de filtre au-dessus de l'arborescence des ressources
pour la restreindre aux noms correspondants au fur et à mesure de la
saisie. La correspondance ignore la casse et porte sur le nom brut de la
ressource ; une catégorie (Sprites, Objets, ...) se masque une fois que
tous ses éléments enfants sont filtrés, et réapparaît dès qu'un élément
correspond à nouveau.

---

## Suivi d'Utilisation

Chaque suppression de ressource vérifie désormais où cette ressource est
réellement référencée — autres objets, salles, actions — avant que vous
confirmiez. Si `spr_joueur` est utilisé par 3 objets, la confirmation de
suppression le précise au lieu d'un avertissement générique, afin que vous
le sachiez *avant* de supprimer quelque chose qui casserait d'autres
parties du projet, pas après.

**Limite connue :** cette analyse ne voit que ce que les structures de
données de PyGameMaker peuvent voir — paramètres d'action, cibles de
collision, instances de salle, champs sprite/parent. Un nom de ressource
utilisé uniquement dans une chaîne Python brute dans l'[[Code-Editor_fr|Éditeur de Code]]
ou l'action Exécuter du Code (par exemple `game.sounds['explosion'].play()`)
n'est pas visible pour cette analyse.

---

## Restaurer des Ressources Supprimées (Corbeille)

**Outils > Restaurer les Ressources Supprimées...**

Supprimer une ressource ne l'efface pas immédiatement — ses fichiers sont
déplacés vers une Corbeille locale au projet et PyGameMaker garde une
trace de ce qui a été supprimé, où ses fichiers sont allés, et toute
référence croisée qui a été effacée (par exemple, le champ sprite d'un
objet remis à vide parce que le sprite qu'il pointait a été supprimé).
Cette boîte de dialogue liste tout ce qui se trouve actuellement dans la
Corbeille avec trois actions :

| Action | Effet |
|--------|-------|
| **Restaurer** | Ramène la ressource exactement telle qu'elle était. Refuse d'écraser si une nouvelle ressource du même nom existe désormais — la restauration n'est pas destructrice non plus. |
| **Supprimer Définitivement** | Retire une seule entrée de la corbeille pour de bon |
| **Vider la Corbeille** | Retire tout ce qui se trouve actuellement dans la Corbeille |

Les références croisées effacées lors de la suppression ne sont **pas**
automatiquement rétablies à la restauration — vous verrez ce qui a
changé, afin de décider vous-même s'il faut reconnecter plutôt que de
laisser PyGameMaker deviner.

Les fichiers mis à la corbeille sont exclus des exports de projet
(zip/HTML5/etc.) — une ressource supprimée ne réapparaît jamais
discrètement dans un jeu publié.

---

## Trouver les Ressources Inutilisées

**Outils > Trouver les Ressources Inutilisées...**

Analyse tout le projet via la même analyse d'utilisation ci-dessus et
liste chaque ressource sans aucune référence, groupée par catégorie,
chacune avec une case à cocher. Sélectionnez celles que vous voulez
vraiment supprimer (ou **Tout Sélectionner**) et **Déplacer la Sélection
vers la Corbeille** — même filet de sécurité que toute autre suppression.

**Les salles sont traitées avec précaution.** Une salle vers laquelle
personne ne navigue explicitement par son nom — un jeu à une seule salle,
ou la toute première salle d'un jeu — apparaît légitimement comme
« inutilisée » sous un simple comptage de références, mais la supprimer
casserait le jeu. Les salles sont étiquetées *« Salles — non naviguées
explicitement »* plutôt que simplement « inutilisées », et **Tout
Sélectionner ignore les salles** exprès ; vous pouvez toujours en cocher
une individuellement si vous êtes sûr.

---

## Trouver les Fichiers Orphelins

**Outils > Trouver les Fichiers Orphelins...**

Le problème inverse : des fichiers présents dans le dossier du projet
(`sprites/`, `sounds/`, `backgrounds/`, `fonts/`, `thumbnails/`) qui n'ont
**aucune** entrée correspondante dans le projet du tout — laissés par une
opération interrompue, ou déposés à la main en dehors de l'IDE. Les liste
par catégorie avec le même modèle case à cocher / Tout Sélectionner /
**Déplacer la Sélection vers la Corbeille** que les ressources inutilisées,
et inclut son propre mini-panneau Corbeille (Restaurer / Supprimer
Définitivement / Vider) dans la même boîte de dialogue — les fichiers
orphelins utilisent un stockage de corbeille séparé de celui des
suppressions normales de ressources, puisqu'ils n'ont jamais été une
véritable entrée project.json au départ.

---

## Nettoyer le Projet

**Outils > Nettoyer le Projet**

Un balayage en un clic des fichiers `.tmp` restants — les fichiers
temporaires que le processus de sauvegarde atomique de PyGameMaker crée
et supprime normalement lui-même. Seuls les fichiers vieux d'environ une
minute sont touchés, pour qu'une sauvegarde en cours ne soit jamais mise
en danger. Indique combien de fichiers ont été supprimés, ou qu'il n'y
avait rien à nettoyer. Contrairement aux boîtes de dialogue ci-dessus, ces
fichiers ne passent jamais par le système de ressources ni la Corbeille —
un fichier `.tmp` n'est jamais la copie de référence de quoi que ce soit,
il est donc supprimé directement.

---

## Étapes Suivantes

- [[Editeur_Salles_fr|Éditeur de Salles]] / [[Editeur_Objets_fr|Éditeur d'Objets]] - D'où proviennent la plupart des références de ressources
- [[FAQ_fr|FAQ]] - Questions courantes, y compris sur la sécurité des données
