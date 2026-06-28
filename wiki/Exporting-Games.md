# Exporting Games

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Back to Home](Home)

PyGameMaker can export your game to multiple platforms. This guide covers each export option and how to use them.

---

## Export Overview

| Platform | Format | Requirements |
|----------|--------|--------------|
| **Windows** | .exe | PyInstaller |
| **HTML5** | .html | Modern browser |
| **Linux** | Binary | Python 3.10+ |
| **Kivy** | .apk/.ipa | Buildozer |

---

## Windows EXE Export

Create a standalone Windows executable that runs without Python installed.

### How to Export

1. Go to **File > Export > Windows EXE**
2. Choose an output folder
3. Wait for the build process to complete
4. Find the .exe file in the output folder

### What's Created

```
output_folder/
├── MyGame.exe        # Main executable
├── _internal/        # Required libraries
└── assets/          # Game resources
```

### Requirements

- PyInstaller (installed via `pip install pyinstaller`)
- Windows OS for building (cross-compilation not supported)

### Distribution

To share your game:
1. Zip the entire output folder
2. Distribute the zip file
3. Users extract and run the .exe

### Troubleshooting

**Missing DLLs:** Make sure all dependencies are included. Check the PyInstaller output for warnings.

**Antivirus flags:** Some antivirus programs flag PyInstaller executables. This is a false positive. You may need to sign your executable.

**Large file size:** The _internal folder contains Python and all libraries. Consider using `--onefile` mode for a single larger executable.

---

## HTML5 Export

Create a single HTML file that runs in web browsers.

### How to Export

1. Go to **File > Export > HTML5**
2. Choose an output location
3. Select options (compression, etc.)
4. Click Export

### What's Created

```
output_folder/
└── MyGame.html       # Single-file game
```

### Features

- Runs in any modern browser (Chrome, Firefox, Edge, Safari)
- No installation required
- Compressed with gzip for fast loading
- Mobile-friendly with touch controls

### Hosting Your Game

Upload the HTML file to:
- Your own web server
- GitHub Pages (free)
- itch.io (game-focused hosting)
- Any static file hosting

### Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome 80+ | Full |
| Firefox 75+ | Full |
| Edge 80+ | Full |
| Safari 13+ | Full |
| Mobile Chrome | Full |
| Mobile Safari | Full |

### Limitations

- Some features may not work (file system access, etc.)
- Audio may require user interaction to start
- Performance depends on device/browser

---

## Linux Export

Create a native Linux executable.

### How to Export

1. Go to **File > Export > Linux**
2. Choose an output folder
3. Wait for the build process

### Requirements

- Linux OS for building
- Python 3.10+
- PyInstaller

### Distribution

```bash
# Make the file executable
chmod +x MyGame

# Run the game
./MyGame
```

Distribute as a .tar.gz archive:
```bash
tar -czvf MyGame-linux.tar.gz MyGame/
```

---

## Kivy Export (Mobile)

Create mobile apps for iOS and Android using the Kivy framework.

### How to Export

1. Go to **File > Export > Kivy**
2. Choose output folder
3. Configure mobile settings
4. Export the Kivy project

### Building for Android

The exported Kivy project uses Buildozer to create APKs:

```bash
cd exported_project
pip install buildozer
buildozer init
buildozer android debug
```

### Building for iOS

Requires a Mac with Xcode:

```bash
cd exported_project
pip install kivy-ios
toolchain build python3 kivy
toolchain create MyGame ~/ios_project
```

### Mobile Considerations

- Touch controls are automatically mapped
- Screen scaling is handled automatically
- Test on multiple screen sizes
- Optimize asset sizes for mobile

---

## Export Settings

### General Settings

| Setting | Description |
|---------|-------------|
| **Game Name** | Name shown in title bar/app |
| **Icon** | Application icon (Windows/mobile) |
| **Version** | Version number (1.0.0) |
| **Author** | Developer name |

### Windows Settings

| Setting | Description |
|---------|-------------|
| **Console** | Show console window (for debugging) |
| **One File** | Single .exe vs. folder with _internal |
| **UPX** | Compress with UPX (smaller size) |

### HTML5 Settings

| Setting | Description |
|---------|-------------|
| **Compression** | Enable gzip compression |
| **Fullscreen** | Start in fullscreen mode |
| **Touch Controls** | Show on-screen controls |

---

## Pre-Export Checklist

Before exporting, verify:

- [ ] All assets are included in the project
- [ ] Game runs correctly in the IDE
- [ ] No debug messages or test code
- [ ] Room order is correct (starting room first)
- [ ] Audio files are in supported formats
- [ ] Sprites are optimized for file size

---

## Optimizing File Size

### Sprites
- Use appropriate dimensions (not oversized)
- Compress PNG files
- Consider JPEG for non-transparent images

### Audio
- Use OGG/MP3 for music (not WAV)
- Keep sound effects short
- Lower sample rates for simple sounds

### General
- Remove unused assets
- Minimize room sizes
- Test on target platforms

---

## Testing Exports

Always test your exported game:

1. **Windows:** Test on a clean PC without Python
2. **HTML5:** Test in multiple browsers
3. **Linux:** Test on different distros if possible
4. **Mobile:** Test on real devices, not just emulators

---

## Distribution Platforms

### itch.io
- Free hosting for indie games
- Supports HTML5, Windows, Linux, Mac
- Built-in payment system

### Steam
- Requires Steamworks SDK integration
- Use PyInstaller with Steam API
- Paid publishing fee

### Google Play (Android)
- Requires developer account ($25)
- Build signed APK with Buildozer
- Follow content guidelines

### App Store (iOS)
- Requires Apple Developer account ($99/year)
- Build with kivy-ios
- Submit through App Store Connect

---

## Next Steps

- [[Getting-Started]] - Review the basics
- [[FAQ]] - Common export questions
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Report export problems
