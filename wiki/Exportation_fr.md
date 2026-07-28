# Exporter vos jeux

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Retour à l'accueil](Home_fr)

PyGameMaker peut exporter votre jeu vers plusieurs plateformes. Ce guide couvre chaque option d'exportation et comment l'utiliser.

---

## Aperçu de l'exportation

| Plateforme | Format | Prérequis |
|------------|--------|-----------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (sur un Mac) |
| **HTML5** | .html | Navigateur moderne |
| **Linux** | Binaire | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Source / .apk | Buildozer |
| **Projet (.zip)** | .zip | — (partager le projet modifiable) |

> **Rien n'est supprimé silencieusement.** Si votre jeu utilise une action qu'une
> cible ne peut pas reproduire (par exemple, quelques actions ne sont pas prises en
> charge par l'export Kivy/Android), l'export réussit tout de même mais vous indique
> exactement quelles actions ont été **ignorées**, afin que vous puissiez ajuster. Si
> votre projet utilise une [extension](Extensions_fr) désactivée (par ex. la Vue 3D),
> l'IDE vous en avertit au chargement.

---

## Exportation Windows EXE

Créez un exécutable Windows autonome qui fonctionne sans Python installé.

### Comment exporter

1. Ouvrez **Fichier → Exporter le projet…** (Ctrl+E) et choisissez **Windows**
2. Choisissez un dossier de sortie
3. Attendez la fin du processus de compilation
4. Trouvez le fichier .exe dans le dossier de sortie

### Ce qui est créé

```
dossier_sortie/
├── MonJeu.exe        # Exécutable principal
├── _internal/        # Bibliothèques requises
└── assets/           # Ressources du jeu
```

### Prérequis

- PyInstaller (installé via `pip install pyinstaller`)
- Système Windows pour la compilation (la compilation croisée n'est pas supportée)

### Distribution

Pour partager votre jeu :
1. Compressez tout le dossier de sortie en zip
2. Distribuez le fichier zip
3. Les utilisateurs extraient et exécutent le .exe

### Dépannage

**DLL manquantes :** Assurez-vous que toutes les dépendances sont incluses. Vérifiez la sortie de PyInstaller pour les avertissements.

**Signalement antivirus :** Certains antivirus signalent les exécutables PyInstaller. C'est un faux positif. Vous devrez peut-être signer votre exécutable.

---

## Exportation d'application macOS

Créez un paquet `.app` natif pour macOS avec PyInstaller.

### Comment exporter

1. Ouvrez **Fichier → Exporter le projet…** (Ctrl+E) et choisissez **macOS**
2. Choisissez un dossier de sortie
3. Attendez la fin de la compilation
4. Trouvez `MonJeu.app` dans le dossier de sortie

### Prérequis

- Un **Mac** pour la compilation (la compilation croisée depuis Windows/Linux n'est pas supportée)
- PyInstaller et Kivy installés dans le Python de compilation

### Distribution

Compressez le paquet `.app` en zip pour le partager. Les applications non signées
déclenchent Gatekeeper sur les autres Mac — les utilisateurs font un clic droit →
**Ouvrir** la première fois, ou vous signez/notariez l'application avec un compte
Apple Developer.

---

## Exportation HTML5

Créez un fichier HTML unique qui fonctionne dans les navigateurs web.

### Comment exporter

1. Allez dans **Fichier → Exporter en HTML5…**
2. Choisissez un emplacement de sortie
3. Sélectionnez les options (compression, etc.)
4. Cliquez sur Exporter

### Ce qui est créé

```
dossier_sortie/
└── MonJeu.html       # Jeu en fichier unique
```

### Caractéristiques

- Fonctionne dans tout navigateur moderne (Chrome, Firefox, Edge, Safari)
- Aucune installation requise
- Compressé avec gzip pour un chargement rapide
- Compatible mobile avec contrôles tactiles

### Héberger votre jeu

Téléchargez le fichier HTML sur :
- Votre propre serveur web
- GitHub Pages (gratuit)
- itch.io (hébergement orienté jeux)
- Tout hébergement de fichiers statiques

### Compatibilité navigateur

| Navigateur | Support |
|------------|---------|
| Chrome 80+ | Complet |
| Firefox 75+ | Complet |
| Edge 80+ | Complet |
| Safari 13+ | Complet |
| Chrome Mobile | Complet |
| Safari Mobile | Complet |

### Limitations

- Certaines fonctionnalités peuvent ne pas fonctionner (accès au système de fichiers, etc.)
- L'audio peut nécessiter une interaction utilisateur pour démarrer
- Les performances dépendent de l'appareil/navigateur

---

## Exportation Linux

Créez un exécutable Linux natif.

### Comment exporter

1. Ouvrez **Fichier → Exporter le projet…** (Ctrl+E) et choisissez **Linux**
2. Choisissez un dossier de sortie
3. Attendez le processus de compilation

### Prérequis

- Système Linux pour la compilation
- Python 3.10+
- PyInstaller

### Distribution

```bash
# Rendre le fichier exécutable
chmod +x MonJeu

# Lancer le jeu
./MonJeu
```

Distribuez sous forme d'archive .tar.gz :
```bash
tar -czvf MonJeu-linux.tar.gz MonJeu/
```

---

## Exportation Kivy (Mobile)

Créez des applications mobiles pour iOS et Android en utilisant le framework Kivy.

### Comment exporter

1. Allez dans **Fichier → Exporter vers Kivy…**
2. Choisissez le dossier de sortie
3. Configurez les paramètres mobiles
4. Exportez le projet Kivy

### Compiler pour Android

Le projet Kivy exporté utilise Buildozer pour créer des APK :

```bash
cd projet_exporte
pip install buildozer
buildozer init
buildozer android debug
```

### Compiler pour iOS

Nécessite un Mac avec Xcode :

```bash
cd projet_exporte
pip install kivy-ios
toolchain build python3 kivy
toolchain create MonJeu ~/projet_ios
```

### Considérations mobiles

- Les contrôles tactiles sont automatiquement mappés
- La mise à l'échelle de l'écran est gérée automatiquement
- Testez sur plusieurs tailles d'écran
- Optimisez les tailles des ressources pour mobile

---

## Exportation du projet (.zip)

Partagez le **projet modifiable** lui-même (pas un jeu compilé) : utilisez
**Fichier → Exporter le projet…** (Ctrl+E) pour créer une archive `.zip` que
quelqu'un d'autre peut rouvrir dans PyGameMaker. Idéal pour la collaboration, les
sauvegardes ou la remise d'un travail scolaire.

---

## Paramètres d'exportation

### Paramètres généraux

| Paramètre | Description |
|-----------|-------------|
| **Nom du jeu** | Nom affiché dans la barre de titre/l'app |
| **Icône** | Icône de l'application (Windows/mobile) |
| **Version** | Numéro de version (1.0.0) |
| **Auteur** | Nom du développeur |

### Paramètres Windows

| Paramètre | Description |
|-----------|-------------|
| **Console** | Afficher la fenêtre console (pour le débogage) |
| **Un fichier** | Un seul .exe vs. dossier avec _internal |
| **UPX** | Compresser avec UPX (taille réduite) |

### Paramètres HTML5

| Paramètre | Description |
|-----------|-------------|
| **Compression** | Activer la compression gzip |
| **Plein écran** | Démarrer en mode plein écran |
| **Contrôles tactiles** | Afficher les contrôles à l'écran |

---

## Liste de vérification avant exportation

Avant d'exporter, vérifiez :

- [ ] Toutes les ressources sont incluses dans le projet
- [ ] Le jeu fonctionne correctement dans l'IDE
- [ ] Pas de messages de débogage ou de code de test
- [ ] L'ordre des salles est correct (salle de départ en premier)
- [ ] Les fichiers audio sont dans des formats supportés
- [ ] Les sprites sont optimisés pour la taille de fichier

---

## Optimiser la taille des fichiers

### Sprites
- Utilisez des dimensions appropriées (pas surdimensionnées)
- Compressez les fichiers PNG
- Envisagez le JPEG pour les images sans transparence

### Audio
- Utilisez OGG/MP3 pour la musique (pas WAV)
- Gardez les effets sonores courts
- Taux d'échantillonnage plus bas pour les sons simples

### Général
- Supprimez les ressources inutilisées
- Minimisez les tailles des salles
- Testez sur les plateformes cibles

---

## Tester les exportations

Testez toujours votre jeu exporté :

1. **Windows :** Testez sur un PC propre sans Python
2. **HTML5 :** Testez dans plusieurs navigateurs
3. **Linux :** Testez sur différentes distributions si possible
4. **Mobile :** Testez sur de vrais appareils, pas seulement des émulateurs

---

## Plateformes de distribution

### itch.io
- Hébergement gratuit pour les jeux indépendants
- Prend en charge HTML5, Windows, Linux, Mac
- Système de paiement intégré

### Steam
- Nécessite l'intégration du SDK Steamworks
- Utilisez PyInstaller avec l'API Steam
- Frais de publication payants

### Google Play (Android)
- Nécessite un compte développeur (25 $)
- Compilez un APK signé avec Buildozer
- Suivez les directives de contenu

### App Store (iOS)
- Nécessite un compte Apple Developer (99 $/an)
- Compilez avec kivy-ios
- Soumettez via App Store Connect

---

## Prochaines étapes

- [[Demarrage_fr]] - Revoir les bases
- [[FAQ_fr]] - Questions courantes sur l'exportation
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Signaler des problèmes d'exportation
