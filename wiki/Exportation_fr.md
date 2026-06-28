# Exporter vos jeux

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Retour a l'accueil](Home_fr)

PyGameMaker peut exporter votre jeu vers plusieurs plateformes. Ce guide couvre chaque option d'exportation et comment les utiliser.

---

## Apercu de l'exportation

| Plateforme | Format | Prerequis |
|------------|--------|-----------|
| **Windows** | .exe | PyInstaller |
| **HTML5** | .html | Navigateur moderne |
| **Linux** | Binaire | Python 3.10+ |
| **Kivy** | .apk/.ipa | Buildozer |

---

## Exportation Windows EXE

Creez un executable Windows autonome qui fonctionne sans Python installe.

### Comment exporter

1. Allez dans **Fichier > Exporter > Windows EXE**
2. Choisissez un dossier de sortie
3. Attendez la fin du processus de compilation
4. Trouvez le fichier .exe dans le dossier de sortie

### Ce qui est cree

```
dossier_sortie/
+-- MonJeu.exe        # Executable principal
+-- _internal/        # Bibliotheques requises
+-- assets/           # Ressources du jeu
```

### Prerequis

- PyInstaller (installe via `pip install pyinstaller`)
- Systeme Windows pour la compilation (la compilation croisee n'est pas supportee)

### Distribution

Pour partager votre jeu:
1. Compressez tout le dossier de sortie en zip
2. Distribuez le fichier zip
3. Les utilisateurs extraient et executent le .exe

### Depannage

**DLLs manquantes:** Assurez-vous que toutes les dependances sont incluses. Verifiez la sortie de PyInstaller pour les avertissements.

**Signalement antivirus:** Certains antivirus signalent les executables PyInstaller. C'est un faux positif. Vous devrez peut-etre signer votre executable.

---

## Exportation HTML5

Creez un fichier HTML unique qui fonctionne dans les navigateurs web.

### Comment exporter

1. Allez dans **Fichier > Exporter > HTML5**
2. Choisissez un emplacement de sortie
3. Selectionnez les options (compression, etc.)
4. Cliquez sur Exporter

### Ce qui est cree

```
dossier_sortie/
+-- MonJeu.html       # Jeu en fichier unique
```

### Caracteristiques

- Fonctionne dans tout navigateur moderne (Chrome, Firefox, Edge, Safari)
- Aucune installation requise
- Compresse avec gzip pour un chargement rapide
- Compatible mobile avec controles tactiles

### Heberger votre jeu

Telechargez le fichier HTML sur:
- Votre propre serveur web
- GitHub Pages (gratuit)
- itch.io (hebergement oriente jeux)
- Tout hebergement de fichiers statiques

### Compatibilite navigateur

| Navigateur | Support |
|------------|---------|
| Chrome 80+ | Complet |
| Firefox 75+ | Complet |
| Edge 80+ | Complet |
| Safari 13+ | Complet |
| Chrome Mobile | Complet |
| Safari Mobile | Complet |

### Limitations

- Certaines fonctionnalites peuvent ne pas fonctionner (acces au systeme de fichiers, etc.)
- L'audio peut necessiter une interaction utilisateur pour demarrer
- Les performances dependent de l'appareil/navigateur

---

## Exportation Linux

Creez un executable Linux natif.

### Comment exporter

1. Allez dans **Fichier > Exporter > Linux**
2. Choisissez un dossier de sortie
3. Attendez le processus de compilation

### Prerequis

- Systeme Linux pour la compilation
- Python 3.10+
- PyInstaller

### Distribution

```bash
# Rendre le fichier executable
chmod +x MonJeu

# Lancer le jeu
./MonJeu
```

Distribuez sous forme d'archive .tar.gz:
```bash
tar -czvf MonJeu-linux.tar.gz MonJeu/
```

---

## Exportation Kivy (Mobile)

Creez des applications mobiles pour iOS et Android en utilisant le framework Kivy.

### Comment exporter

1. Allez dans **Fichier > Exporter > Kivy**
2. Choisissez le dossier de sortie
3. Configurez les parametres mobiles
4. Exportez le projet Kivy

### Compiler pour Android

Le projet Kivy exporte utilise Buildozer pour creer des APKs:

```bash
cd projet_exporte
pip install buildozer
buildozer init
buildozer android debug
```

### Compiler pour iOS

Necessite un Mac avec Xcode:

```bash
cd projet_exporte
pip install kivy-ios
toolchain build python3 kivy
toolchain create MonJeu ~/projet_ios
```

### Considerations mobiles

- Les controles tactiles sont automatiquement mappes
- La mise a l'echelle de l'ecran est geree automatiquement
- Testez sur plusieurs tailles d'ecran
- Optimisez les tailles des ressources pour mobile

---

## Parametres d'exportation

### Parametres generaux

| Parametre | Description |
|-----------|-------------|
| **Nom du jeu** | Nom affiche dans la barre de titre/app |
| **Icone** | Icone de l'application (Windows/mobile) |
| **Version** | Numero de version (1.0.0) |
| **Auteur** | Nom du developpeur |

### Parametres Windows

| Parametre | Description |
|-----------|-------------|
| **Console** | Afficher la fenetre console (pour debogage) |
| **Un fichier** | Un seul .exe vs. dossier avec _internal |
| **UPX** | Compresser avec UPX (taille reduite) |

### Parametres HTML5

| Parametre | Description |
|-----------|-------------|
| **Compression** | Activer la compression gzip |
| **Plein ecran** | Demarrer en mode plein ecran |
| **Controles tactiles** | Afficher les controles a l'ecran |

---

## Liste de verification avant exportation

Avant d'exporter, verifiez:

- [ ] Toutes les ressources sont incluses dans le projet
- [ ] Le jeu fonctionne correctement dans l'IDE
- [ ] Pas de messages de debogage ou de code de test
- [ ] L'ordre des salles est correct (salle de depart en premier)
- [ ] Les fichiers audio sont dans des formats supportes
- [ ] Les sprites sont optimises pour la taille de fichier

---

## Optimiser la taille des fichiers

### Sprites
- Utilisez des dimensions appropriees (pas surdimensionnees)
- Compressez les fichiers PNG
- Considerez JPEG pour les images sans transparence

### Audio
- Utilisez OGG/MP3 pour la musique (pas WAV)
- Gardez les effets sonores courts
- Taux d'echantillonnage plus bas pour les sons simples

### General
- Supprimez les ressources inutilisees
- Minimisez les tailles des salles
- Testez sur les plateformes cibles

---

## Tester les exportations

Testez toujours votre jeu exporte:

1. **Windows:** Testez sur un PC propre sans Python
2. **HTML5:** Testez dans plusieurs navigateurs
3. **Linux:** Testez sur differentes distributions si possible
4. **Mobile:** Testez sur de vrais appareils, pas seulement des emulateurs

---

## Plateformes de distribution

### itch.io
- Hebergement gratuit pour les jeux independants
- Supporte HTML5, Windows, Linux, Mac
- Systeme de paiement integre

### Steam
- Necessite l'integration du SDK Steamworks
- Utilisez PyInstaller avec l'API Steam
- Frais de publication payants

### Google Play (Android)
- Necessite un compte developpeur (25$)
- Compilez un APK signe avec Buildozer
- Suivez les directives de contenu

### App Store (iOS)
- Necessite un compte Apple Developer (99$/an)
- Compilez avec kivy-ios
- Soumettez via App Store Connect

---

## Prochaines etapes

- [[Demarrage_fr]] - Revoir les bases
- [[FAQ_fr]] - Questions courantes sur l'exportation
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Signaler des problemes d'exportation
