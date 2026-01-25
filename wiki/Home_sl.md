# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Vizualno razvojno okolje za igre, navdihnjeno z GameMaker 7.0**

PyGameMaker je odprtokodni IDE, ki omogoča dostopno ustvarjanje 2D iger z vizualnim blokovnim programiranjem (Google Blockly) in sistemom dogodkov-akcij. Ustvarite igre brez poglobljenega znanja programiranja, nato pa jih izvozite za Windows, Linux, HTML5 ali mobilne platforme.

---

## Izberite Svojo Raven

PyGameMaker uporablja **prednastavitve** za nadzor, kateri dogodki in akcije so na voljo. To pomaga začetnikom, da se osredotočijo na bistvene funkcije, medtem ko izkušenim uporabnikom omogoča dostop do celotnega nabora orodij.

| Prednastavitev | Primerno Za | Funkcije |
|----------------|-------------|----------|
| [**Začetnik**](Beginner-Preset_sl) | Novi v razvoju iger | 4 dogodki, 17 akcij - Gibanje, trki, rezultat, sobe |
| [**Srednji**](Intermediate-Preset_sl) | Nekaj izkušenj | +4 dogodki, +12 akcij - Življenja, zdravje, zvok, alarmi, risanje |
| **Napreden** | Izkušeni uporabniki | Vsi 40+ dogodki in akcije na voljo |

**Novi uporabniki:** Začnite s [Prednastavitvijo za Začetnike](Beginner-Preset_sl), da se naučite osnov brez preobremenjenosti.

Glejte [Vodnik po Prednastavitvah](Preset-Guide_sl) za popoln pregled sistema prednastavitev.

---

## Funkcije na Hitro

| Funkcija | Opis |
|----------|------|
| **Vizualno Programiranje** | Povleci-in-spusti kodiranje z Google Blockly 12.x |
| **Sistem Dogodkov-Akcij** | Logika, ki temelji na dogodkih, združljiva z GameMaker 7.0 |
| **Prednastavitve po Ravneh** | Nabori funkcij za Začetnike, Srednje in Napredne |
| **Večplatformni Izvoz** | Windows EXE, HTML5, Linux, Kivy (mobilno/namizno) |
| **Upravljanje Virov** | Sprite-i, zvoki, ozadja, pisave in sobe |
| **Večjezični Vmesnik** | Angleščina, Francoščina, Nemščina, Italijanščina, Španščina, Portugalščina, Slovenščina, Ukrajinščina, Ruščina |
| **Razširljivo** | Sistem vtičnikov za prilagojene dogodke in akcije |

---

## Kako Začeti

### Sistemske Zahteve

- **Python** 3.10 ali novejši
- **Operacijski Sistem:** Windows, Linux ali macOS

### Namestitev

1. Klonirajte repozitorij:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Ustvarite virtualno okolje (priporočeno):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ali
   venv\Scripts\activate     # Windows
   ```

3. Namestite odvisnosti:
   ```bash
   pip install -r requirements.txt
   ```

4. Zaženite PyGameMaker:
   ```bash
   python main.py
   ```

---

## Temeljni Koncepti

### Objekti
Igralne entitete s sprite-i, lastnostmi in vedenji. Vsak objekt ima lahko več dogodkov s povezanimi akcijami.

### Dogodki
Sprožilci, ki izvršijo akcije, ko se pojavijo določeni pogoji:
- **Create** - Ko je instanca ustvarjena
- **Step** - Vsako sličico (običajno 60 FPS)
- **Draw** - Faza prilagojenega izrisovanja
- **Destroy** - Ko je instanca uničena
- **Keyboard** - Tipka pritisnjena, sproščena ali držana
- **Mouse** - Kliki, premikanje, vstop/izstop
- **Collision** - Ko se instance dotaknejo
- **Alarm** - Časovniki odštevanja (12 na voljo)

Glejte [Referenco Dogodkov](Event-Reference_sl) za popolno dokumentacijo.

### Akcije
Operacije, ki se izvedejo, ko se dogodki sprožijo. 40+ vgrajenih akcij za:
- Gibanje in fiziko
- Risanje in sprite-e
- Rezultat, življenja in zdravje
- Zvok in glasbo
- Upravljanje instanc in sob

Glejte [Popolno Referenco Akcij](Full-Action-Reference_sl) za popolno dokumentacijo.

### Sobe
Igralni nivoji, kjer postavite instance objektov, nastavite ozadja in definirate igralno območje.

---

## Vizualno Programiranje z Blockly

PyGameMaker vključuje Google Blockly za vizualno programiranje. Bloki so organizirani v kategorije:

- **Dogodki** - Create, Step, Draw, Keyboard, Mouse
- **Gibanje** - Hitrost, smer, položaj, gravitacija
- **Časovniki** - Alarmi in zamiki
- **Risanje** - Oblike, besedilo, sprite-i
- **Rezultat/Življenja/Zdravje** - Sledenje stanja igre
- **Instanca** - Ustvarjanje in uničenje objektov
- **Soba** - Navigacija in upravljanje
- **Vrednosti** - Spremenljivke in izrazi
- **Zvok** - Predvajanje zvoka
- **Izhod** - Razhroščevanje in prikaz

---

## Možnosti Izvoza

### Windows EXE
Samostojne Windows izvedljive datoteke z uporabo PyInstaller. Na ciljnem računalniku ni potreben Python.

### HTML5
Spletne igre v eni datoteki, ki delujejo v kateremkoli sodobnem brskalniku. Stisnjene z gzip za hitro nalaganje.

### Linux
Izvorne Linux izvedljive datoteke za okolja Python 3.10+.

### Kivy
Večplatformne aplikacije za mobilne naprave (iOS/Android) in namizje prek Buildozer.

---

## Struktura Projekta

```
ime_projekta/
├── project.json      # Konfiguracija projekta
├── backgrounds/      # Slike ozadij in metapodatki
├── data/             # Prilagojene podatkovne datoteke
├── fonts/            # Definicije pisav
├── objects/          # Definicije objektov (JSON)
├── rooms/            # Postavitve sob (JSON)
├── scripts/          # Prilagojene skripte
├── sounds/           # Zvočne datoteke in metapodatki
├── sprites/          # Slike sprite-ov in metapodatki
└── thumbnails/       # Ustvarjene sličice virov
```

---

## Vsebina Wikija

### Prednastavitve in Reference
- [Vodnik po Prednastavitvah](Preset-Guide_sl) - Pregled sistema prednastavitev
- [Prednastavitev za Začetnike](Beginner-Preset_sl) - Bistvene funkcije za nove uporabnike
- [Prednastavitev za Srednje](Intermediate-Preset_sl) - Dodatne funkcije
- [Referenca Dogodkov](Event-Reference_sl) - Popolna dokumentacija dogodkov
- [Referenca Akcij](Full-Action-Reference_sl) - Popolna dokumentacija akcij

### Vadnice in Vodniki
- [**Vadnice**](Tutorials_sl) - Vse vadnice na enem mestu
- [Kako Začeti](Kako_Zaceti_sl) - Prvi koraki s PyGameMaker
- [Ustvarite Svojo Prvo Igro](Prva_Igra_sl) - Vadnica korak za korakom
- [Vadnica Pong](Tutorial-Pong_sl) - Ustvarite klasično igro Pong za dva igralca
- [Vadnica Breakout](Tutorial-Breakout_sl) - Ustvarite klasično igro Breakout
- [Uvod v Ustvarjanje Iger](Getting-Started-Breakout_sl) - Celovita vadnica za začetnike
- [Urejevalnik Objektov](Urejevalnik_Objektov_sl) - Delo z igralnimi objekti
- [Urejevalnik Sob](Urejevalnik_Sob_sl) - Oblikovanje nivojev
- [Dogodki in Akcije](Dogodki_in_Akcije_sl) - Referenca igralne logike
- [Vizualno Programiranje](Vizualno_Programiranje_sl) - Uporaba Blockly blokov
- [Izvoz Iger](Izvoz_Iger_sl) - Gradnja za različne platforme
- [FAQ](FAQ_sl) - Pogosta vprašanja

---

## Prispevanje

Prispevki so dobrodošli! Glejte naše smernice za prispevanje za:
- Poročila o napakah in zahteve za funkcije
- Prispevke kode
- Prevode
- Izboljšave dokumentacije

---

## Licenca

PyGameMaker je licenciran pod **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Povezave

- [GitHub Repozitorij](https://github.com/Gabe1290/pythongm)
- [Sledilnik Napak](https://github.com/Gabe1290/pythongm/issues)
- [Izdaje](https://github.com/Gabe1290/pythongm/releases)
