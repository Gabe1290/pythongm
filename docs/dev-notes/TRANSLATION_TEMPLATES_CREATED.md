# Translation Templates Created ✅

**Date:** November 17, 2025
**Status:** ✅ **READY FOR TRANSLATION** - 7 language template files created

---

## Summary

Successfully created translation template files for all 7 additional languages supported by PyGameMaker IDE. Each file contains **289 translatable strings** covering all menus, dialogs, and UI messages.

---

## Languages Created

| Language | Code | Flag | Status | File Size | File Path |
|----------|------|------|--------|-----------|-----------|
| **English** | `en` | 🇬🇧 | ✅ Built-in | - | (no translation needed) |
| **French** | `fr` | 🇫🇷 | ✅ **COMPLETE** | 64 KB | [translations/pygamemaker_fr.ts](translations/pygamemaker_fr.ts) |
| **Spanish** | `es` | 🇪🇸 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_es.ts](translations/pygamemaker_es.ts) |
| **German** | `de` | 🇩🇪 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_de.ts](translations/pygamemaker_de.ts) |
| **Italian** | `it` | 🇮🇹 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_it.ts](translations/pygamemaker_it.ts) |
| **Portuguese** | `pt` | 🇵🇹 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_pt.ts](translations/pygamemaker_pt.ts) |
| **Russian** | `ru` | 🇷🇺 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_ru.ts](translations/pygamemaker_ru.ts) |
| **Chinese** | `zh` | 🇨🇳 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_zh.ts](translations/pygamemaker_zh.ts) |
| **Japanese** | `ja` | 🇯🇵 | ⚠️ Template Ready | 56 KB | [translations/pygamemaker_ja.ts](translations/pygamemaker_ja.ts) |

---

## What Was Created

Each `.ts` file contains **289 translatable strings** extracted from:
- `core/*.py` - Main window, IDE window, menus
- `widgets/*.py` - UI widgets, panels, tabs
- `dialogs/*.py` - Dialogs and preferences
- `editors/*.py` - Object editors, room editors
- `events/*.py` - Event system UI

All strings are currently marked as `<translation type="unfinished"></translation>` and need to be filled in by translators.

---

## Template File Format

Each translation file uses Qt Linguist XML format (`.ts`):

```xml
<message>
    <location filename="../core/ide_window.py" line="123"/>
    <source>Export to Kivy...</source>
    <translation type="unfinished"></translation>
</message>
```

After translation:

```xml
<message>
    <location filename="../core/ide_window.py" line="123"/>
    <source>Export to Kivy...</source>
    <translation>Exportar a Kivy...</translation>
</message>
```

---

## How to Translate

### Option 1: Using Qt Linguist (Recommended)

Qt Linguist is a visual translation tool that makes translation easy:

```bash
# Install Qt Linguist
sudo apt install qttools5-dev-tools  # Ubuntu/Debian
# or
brew install qt  # macOS

# Open translation file
linguist translations/pygamemaker_es.ts
```

**Advantages:**
- Visual interface
- Shows context and location
- Validates translations
- Auto-saves progress
- Shows completion percentage

### Option 2: Using Python Script (Automated)

Create a translation dictionary and use a Python script similar to `update_french_translations.py`:

```python
#!/usr/bin/env python3
"""
Spanish translation script
"""
import xml.etree.ElementTree as ET
from pathlib import Path

TRANSLATIONS = {
    "File": "Archivo",
    "Edit": "Editar",
    "Export to Kivy...": "Exportar a Kivy...",
    "Save Project": "Guardar proyecto",
    # ... add all 289 translations
}

ts_file = Path("translations/pygamemaker_es.ts")
tree = ET.parse(ts_file)
root = tree.getroot()

updated = 0
for context in root.findall('context'):
    for message in context.findall('message'):
        source = message.find('source')
        translation = message.find('translation')

        if source.text in TRANSLATIONS:
            translation.text = TRANSLATIONS[source.text]
            if 'type' in translation.attrib:
                del translation.attrib['type']
            updated += 1

tree.write(ts_file, encoding='utf-8', xml_declaration=True)
print(f"✓ Updated {updated} translations!")
```

Then compile:
```bash
lrelease translations/pygamemaker_es.ts -qm translations/pygamemaker_es.qm
```

### Option 3: Manual XML Editing

Edit the `.ts` file directly in a text editor:

```bash
nano translations/pygamemaker_es.ts
```

Find `<translation type="unfinished"></translation>` entries and fill them in.

---

## Compiling Translations

After translating strings, compile the `.ts` file to `.qm` format (binary):

```bash
# Spanish
lrelease translations/pygamemaker_es.ts -qm translations/pygamemaker_es.qm

# German
lrelease translations/pygamemaker_de.ts -qm translations/pygamemaker_de.qm

# Italian
lrelease translations/pygamemaker_it.ts -qm translations/pygamemaker_it.qm

# Portuguese
lrelease translations/pygamemaker_pt.ts -qm translations/pygamemaker_pt.qm

# Russian
lrelease translations/pygamemaker_ru.ts -qm translations/pygamemaker_ru.qm

# Chinese
lrelease translations/pygamemaker_zh.ts -qm translations/pygamemaker_zh.qm

# Japanese
lrelease translations/pygamemaker_ja.ts -qm translations/pygamemaker_ja.qm
```

The IDE will automatically detect and load the `.qm` files when users select the language.

---

## Testing Translations

1. **Translate at least some strings** in your language file
2. **Compile to `.qm`** format
3. **Run the IDE:**
   ```bash
   python3 main.py
   ```
4. **Change language:**
   - Go to menu: **Tools → 🌐 Language → [Your Language]**
   - Restart the IDE
5. **Verify translations appear** in menus and dialogs

---

## Strings to Translate (289 total)

### Main Categories

#### 1. Main Menu Items (7 menus)
- File, Edit, Assets, Build, Tools, Language, Help

#### 2. File Menu (~10 items)
- New Project, Open Project, Save Project, Recent Projects
- Export to Kivy, Export as HTML5, Export as Zip
- Project Settings, Exit

#### 3. Edit Menu (~8 items)
- Undo, Redo, Cut, Copy, Paste, Duplicate
- Find, Find and Replace

#### 4. Assets Menu (~10 items)
- Import Sprite, Import Sound, Import Background
- Create Object, Create Room, Create Script, Create Font
- Import Object Package, Import Room Package

#### 5. Build Menu (~5 items)
- Test Game, Debug Game, Build Game
- Build and Run, Export Game

#### 6. Tools Menu (~4 items)
- Preferences, Asset Manager
- Validate Project, Clean Project

#### 7. Help Menu (~4 items)
- Documentation, Tutorials
- About PyGameMaker, About Qt

#### 8. Dialogs (~50 items)
- Preferences dialog
- Auto-Save dialog
- Project settings
- Export dialogs
- Asset import dialogs

#### 9. Status Messages (~30 items)
- Ready, Loading, Saving, Exporting
- Project saved, Project loaded
- Game started, Game stopped

#### 10. Error Messages (~40 items)
- Error, Warning, Failed to save
- No project loaded
- Please open a project first

#### 11. UI Labels & Buttons (~100 items)
- OK, Cancel, Apply, Browse
- Select, Choose, Create
- Font Settings, Theme Settings

#### 12. Welcome Screen (~10 items)
- Welcome message
- Quick Actions
- Recent projects

#### 13. Tooltips & Help Text (~25 items)
- Quick help messages
- Keyboard shortcuts
- Feature descriptions

---

## Translation Guidelines

### 1. Consistency
- Use the same terms throughout (e.g., "Project" should always translate the same way)
- Follow existing French translation as a reference

### 2. Technical Terms
Some terms are commonly used in English in the game dev community:
- "Sprite" (often kept as-is or loan word)
- "Debug" (use native verb form)
- File formats like "ZIP", "HTML5" (usually not translated)

### 3. Menu Items
- Keep menu items short and clear
- Use standard translations for common menus (File, Edit, etc.)
- Follow your OS/platform conventions

### 4. Keyboard Shortcuts
- Don't translate the shortcut keys themselves (Ctrl+S stays Ctrl+S)
- Translate the description of what they do

### 5. Tone
- Professional and friendly
- Use "you" form appropriate to your language (formal vs informal)
- Be concise in UI labels

### 6. Proper Nouns
- "PyGameMaker" - never translated
- "Qt" - never translated
- "Kivy", "HTML5" - usually not translated

---

## Examples from French Translation

Good examples of professional translations:

| English | French | Notes |
|---------|--------|-------|
| Export to Kivy... | Exporter vers Kivy... | Action verb + preposition |
| Save Project | Enregistrer le projet | Formal verb |
| Please open a project first | Veuillez d'abord ouvrir un projet | Polite "please" form |
| Failed to save project | Échec de l'enregistrement du projet | Native expression |
| Drag and drop | Glisser-déposer | Compound verb |

---

## Translation Priority

If translating all 289 strings is too much, prioritize these:

### High Priority (Core UI - ~80 strings)
1. Main menu items (File, Edit, etc.)
2. Common dialogs (OK, Cancel, Save, etc.)
3. Project operations (New, Open, Save)
4. Export menu items

### Medium Priority (Features - ~120 strings)
1. Asset menu items
2. Build menu items
3. Preferences dialog
4. Status messages

### Low Priority (Help & Advanced - ~89 strings)
1. Error messages
2. Tooltips
3. Welcome screen
4. Tutorial text

---

## File Locations

```
pygm2/
├── translations/
│   ├── pygamemaker_fr.ts    ✅ French (COMPLETE)
│   ├── pygamemaker_fr.qm    ✅ French (COMPILED)
│   ├── pygamemaker_es.ts    ⚠️ Spanish (template)
│   ├── pygamemaker_de.ts    ⚠️ German (template)
│   ├── pygamemaker_it.ts    ⚠️ Italian (template)
│   ├── pygamemaker_pt.ts    ⚠️ Portuguese (template)
│   ├── pygamemaker_ru.ts    ⚠️ Russian (template)
│   ├── pygamemaker_zh.ts    ⚠️ Chinese (template)
│   └── pygamemaker_ja.ts    ⚠️ Japanese (template)
│
├── core/
│   └── language_manager.py  # Language switching logic
│
├── update_french_translations.py  # Example translation script
└── complete_french_translation.py # Example batch script
```

---

## Workflow Summary

For each language:

1. **Get the template file:**
   - Already created: `translations/pygamemaker_XX.ts`

2. **Choose translation method:**
   - Qt Linguist (GUI tool)
   - Python script (automated)
   - Manual XML editing

3. **Translate strings:**
   - All 289 strings, or prioritize core UI first
   - Follow guidelines above

4. **Compile to binary:**
   ```bash
   lrelease translations/pygamemaker_XX.ts -qm translations/pygamemaker_XX.qm
   ```

5. **Test in IDE:**
   - Run IDE: `python3 main.py`
   - Switch language: Tools → Language → [Your Language]
   - Restart IDE
   - Verify translations

6. **Iterate:**
   - Find missing/incorrect translations
   - Update `.ts` file
   - Recompile to `.qm`
   - Test again

---

## Updating Translations

When the IDE code changes and new translatable strings are added:

```bash
# Update translation file (adds new strings, keeps existing translations)
pylupdate6 --no-obsolete --ts translations/pygamemaker_es.ts core/*.py widgets/*.py dialogs/*.py editors/*.py events/*.py

# Translate new strings (only ones marked type="unfinished")
linguist translations/pygamemaker_es.ts

# Recompile
lrelease translations/pygamemaker_es.ts -qm translations/pygamemaker_es.qm
```

---

## Contribution

If you complete a translation:

1. Translate the `.ts` file
2. Compile to `.qm` format
3. Test in the IDE
4. Submit both `.ts` and `.qm` files
5. Include screenshots showing the translation in action

---

## Need Help?

- **French translation reference**: See `FRENCH_TRANSLATION_COMPLETE.md`
- **Translation scripts**: See `update_french_translations.py`
- **Qt Linguist docs**: https://doc.qt.io/qt-6/linguist-translators.html
- **File format**: Qt `.ts` XML format

---

## Status Summary

| Item | Status |
|------|--------|
| Template files created | ✅ 7 languages |
| Strings per language | 289 |
| French translation | ✅ 100% complete |
| Other languages | ⚠️ 0% (ready for translators) |
| Compilation ready | ✅ Yes (lrelease) |
| IDE integration | ✅ Done (automatic) |

---

## Next Steps

1. **Find translators** for each language
2. **Translate the 289 strings** using one of the methods above
3. **Compile to `.qm`** format
4. **Test** in the IDE
5. **Share** completed translations

Once a language is translated and compiled, users can immediately switch to it via:
**Tools → 🌐 Language → [Language Name]**

---

**Languages Ready:** 🇫🇷 **1/8 complete**
**Languages Pending:** 🇪🇸 🇩🇪 🇮🇹 🇵🇹 🇷🇺 🇨🇳 🇯🇵

**Volunteers welcome!** 🌍
