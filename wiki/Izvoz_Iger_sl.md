# Izvoz iger

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

[Nazaj na zacetno stran](Home_sl)

Naucite se izvazati vase pyGM igre za razlicne platforme.

## Pregled

pyGM omogoca izvoz za:
- Windows (EXE)
- macOS (APP)
- Linux
- Splet (HTML5)

## Priprava na izvoz

### Pred izvozom preverite
1. **Vsi viri prisotni**: Spriti, zvoki itd.
2. **Igra testirana**: Brez kriticnih napak
3. **Nastavitve optimizirane**: Locljivost, celozaslonski nacin

### Nastavitve projekta
- **Ime igre**: Prikazano ime
- **Verzija**: Stevilka verzije
- **Ikona**: Ikona aplikacije
- **Zacetni zaslon**: Splash Screen

## Izvoz za Windows

### Predpogoji
- pyinstaller namescan
- Sistem Windows ali navzkrizno prevajanje

### Koraki
1. Pojdite na Datoteka > Izvozi
2. Izberite "Windows Executable"
3. Nastavite moznosti:
   - Datoteka ikone
   - Skrij okno konzole
   - Ena EXE datoteka
4. Kliknite "Izvozi"

### Izhod
- Ena EXE datoteka
- Ali mapa z odvisnostmi

## Izvoz za macOS

### Predpogoji
- Sistem macOS priporocen
- py2app ali pyinstaller

### Koraki
1. Datoteka > Izvozi > macOS
2. Vnesite ime App Bundle
3. Izberite ikono (format ICNS)
4. Izvozi

## Izvoz za Linux

### Moznosti
- AppImage (priporoceno)
- Paket Debian
- Izvrsljiva datoteka

### Koraki
1. Datoteka > Izvozi > Linux
2. Izberite format
3. Izvozi

## Spletni izvoz (HTML5)

### Prednosti
- Deluje v brskalniku
- Enostavno za deljenje
- Ni potrebna namestitev

### Koraki
1. Datoteka > Izvozi > Splet
2. Nastavite:
   - Velikost platna
   - Nalagalni zaslon
   - Kompresija
3. Izvozi

### Izhod
- HTML datoteka
- JavaScript datoteke
- Mapa virov

### Gostovanje
- Nalozite na spletni streznik
- Uporabite itch.io
- Uporabite GitHub Pages

## Moznosti izvoza

### Splosne
- **Kompresija**: Zmanjsaj velikost datoteke
- **Nacin razhroscevanja**: Ohrani za teste
- **Vgradi vire**: Vse v eno datoteko

### Specificne za platformo
- **Windows**: UAC manifest
- **macOS**: Podpisovanje kode
- **Splet**: WebGL verzija

## Odpravljanje tezav

### Pogoste tezave

**Izvoz ne uspe**
- Preverite sporocila o napakah
- Posodobite pyinstaller

**Manjkajo viri**
- Preverite poti
- Ponovno vkljucite vire

**Igra se ne zazene**
- Testirajte v nacinu razhroscevanja
- Preverite odvisnosti

## Optimizacija

1. **Optimizirajte velikosti slik**: Stisnite sprite
2. **Stisnite zvok**: MP3 namesto WAV
3. **Odstranite neuporabljene vire**
4. **Optimizirajte kodo**: Izboljsajte ucinkovitost

## Glej tudi

- [FAQ](FAQ_sl)
- [Ustvarite svojo prvo igro](Prva_Igra_sl)
- [Zacetek](Zacetek_sl)
