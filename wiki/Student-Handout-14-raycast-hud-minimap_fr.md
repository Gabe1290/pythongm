# PyGameMaker — Tutoriel 14 : 2.5D, ATH et minicarte

*[Accueil](Home_fr) | [Ressources pour enseignants](Teacher-Resources_fr)*

**Télécharger :** [PDF](downloads/Student-Handout-14-raycast-hud-minimap_fr.pdf) · [ODT](downloads/Student-Handout-14-raycast-hud-minimap_fr.odt)

---

## Comment utiliser cette fiche

Cette fiche accompagne le tutoriel intégré **Aide > Tutoriels > 2.5D : ATH et minicarte** (4 pages, environ 25 minutes). Tu poursuis le jeu du Tutoriel 13. Cette leçon n'est pas dans l'édition débutant. Garde le tutoriel ouvert sur une moitié de ton écran. Coche chaque case quand l'étape est faite, et vérifie la ligne **Tu dois voir** à la fin de chaque phase. Si quelque chose ne correspond pas, regarde **Bloqué·e ?** avant d'appeler ton enseignant·e.

## Ce que tu vas créer

Un tableau de bord pour ton jeu à la première personne (un **ATH**, affichage tête haute) : score et vies à l'écran, une minicarte dans le coin, et une barre d'état façon DOOM avec un indicateur de santé.

## Phase 1 : Score et vies

- [ ] **1.** Ouvre `obj_player` et ajoute un événement **Quand dessiner**.
- [ ] **2.** Dedans : *Définir la couleur de dessin* en blanc (`#ffffff`) ; *Dessiner le score* à x 8, y 8, légende « Score : » ; *Dessiner les vies* à x 230, y 6 avec le sprite `spr_player`.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Le score est en haut à gauche, et une petite icône par vie en haut à droite. Ramasse une gemme et le score monte ; touche le monstre et une icône disparaît.

> **Astuce:** **Dessiner du texte est noir par défaut, Dessiner le score est blanc.** Règle la couleur une fois en haut de l'événement Dessin pour que tout soit prévisible. L'objet qui dessine l'ATH doit être **visible**.

## Phase 2 : La minicarte

- [ ] **3.** Dans le même événement **Quand dessiner**, après les autres actions, ajoute *Dessiner la mini-carte* avec X 230, Y 10, Size (taille) 80.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. Une petite carte des murs apparaît en haut à droite. Une flèche montre où tu es et regarde là où tu regardes. Le nord est toujours en haut ; la carte ne tourne pas, c'est la flèche qui tourne. Elle ne montre ni les gemmes ni les monstres.

## Phase 3 : La barre d'état

- [ ] **4.** Fais de la place : dans **Quand créé** de `obj_player`, sur *Activer la vue Raycast*, règle **Viewport Height** sur **256** (la salle fait 320 de haut et la barre 64).
- [ ] **5.** Dans **Game Start**, ajoute *Définir la santé* à 100 après le score et les vies.
- [ ] **6.** Dans l'événement **Quand dessiner**, remplace le score et les vies par *Dessiner l'ATH DOOM* : X 0, Y **-1** (bas de la fenêtre), Width **0** (pleine largeur), Height **64**, Health Label « SANTÉ », Score Label « SCORE ». Garde *Dessiner la mini-carte*.

> **Réussi:** **Tu dois voir :** appuie sur **F5**. La vue 3D est posée sur une barre sombre montrant une barre de santé verte avec son nombre, ton score et tes vies. La minicarte reste dans le coin.

## Bloqué·e ?

| Ce qui ne va pas | Cause la plus probable | Que faire |
|---|---|---|
| Je ne vois aucun ATH | L'objet de l'ATH est invisible, ou n'a pas d'événement **Quand dessiner** | Laisse **Visible** coché ; ajoute un événement Dessin |
| Mon texte est invisible | C'est du texte noir sur une scène sombre | Ajoute d'abord *Définir la couleur de dessin* en blanc |
| Le score ne change jamais | Pas d'événements de score (Tutoriel 13), ou l'objet n'est pas dans la salle | Vérifie les événements des gemmes |
| La barre d'état cache une partie de la vue | **Viewport Height** vaut 0 ou est trop grand | Règle-le sur la hauteur de la salle moins la barre (320 - 64 = 256) |
| La barre n'est pas au bon endroit | Y n'est pas -1, ou Height ne correspond pas | Utilise Y -1 et Height 64 |
| La barre de santé est vide | *Définir la santé* n'a pas été réglé | Ajoute *Définir la santé* 100 dans **Game Start** |
| La minicarte est dans le mauvais coin | X et Y sont faux | Utilise X 230, Y 10 pour une salle de 320 de large |
| La minicarte n'a pas de flèche | La caméra n'a pas été trouvée | Vérifie que le joueur exécute *Activer la vue Raycast* |


## Défis

- **Essaie (5 minutes) :** change la taille ou les couleurs de la minicarte.
- **Va plus loin :** le monstre retire 25 de santé au lieu d'une vie, et la santé se remplit quand une vie est perdue.
- **Invente :** une minicarte qu'on active et désactive avec la touche M, un visage dans la barre qui change avec la santé, ou un compteur d'objectif.

## Vocabulaire

| Terme | Ce que cela veut dire |
|---|---|
| ATH | Du texte et des images à l'écran qui informent le joueur |
| Événement Dessin | Dessine des éléments par-dessus la vue à chaque image |
| Minicarte | Une petite carte des murs vue du dessus, avec un repère pour toi |
| Zone d'affichage (viewport) | La partie de la fenêtre où la vue 3D est dessinée |
| Barre d'état | Un panneau en bas avec la santé, le score et les vies |


## Vérifie-toi

Écris tes réponses dans les notes ci-dessous.

1. Pourquoi l'objet qui dessine l'ATH doit-il être visible ?
2. Pourquoi la vue 3D a-t-elle besoin d'un **Viewport Height** pour la barre d'état ?
3. Pourquoi la minicarte ne montre-t-elle pas les gemmes ?

## Mes notes

<br>

<br>

<br>

<br>

<br>

<br>

