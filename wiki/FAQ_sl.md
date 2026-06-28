# Pogosto zastavljena vprasanja (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Nazaj na zacetno stran](Home_sl)

Odgovori na pogosta vprasanja o pyGM.

## Splosna vprasanja

### Kaj je pyGM?
pyGM je vizualni urejevalnik za razvoj iger v Pythonu. Omogoca ustvarjanje 2D iger brez obseznega znanja programiranja.

### Ali je pyGM brezplacen?
Da, pyGM je odprtokoden in popolnoma brezplacen.

### Kateri programski jezik se uporablja?
pyGM temelji na Pythonu. Lahko uporabite vizualno programiranje ali neposredno pisete Python kodo.

### Za katere platforme lahko razvijam?
- Windows
- macOS
- Linux
- Splet (HTML5)

## Namestitev

### Kako namestim pyGM?
```bash
pip install pygm
```

### Katero verzijo Pythona potrebujem?
Python 3.8 ali visji.

### pyGM se ne zazene. Kaj naj storim?
1. Preverite verzijo Pythona
2. Ponovno namestite odvisnosti
3. Zazenite iz ukazne vrstice za ogled napak

## Razvoj

### Kako ustvarim nov projekt?
Zazenite pyGM in izberite "Nov projekt" ali uporabite Datoteka > Novo.

### Kako dodam sprite?
1. Desni klik na "Spriti" v drevesu virov
2. Izberite "Nov sprite"
3. Uvozite sliko ali jo ustvarite

### Kako ustvarim animacije?
1. Odprite sprite
2. Dodajte vec okvirjev
3. Nastavite hitrost animacije

### Kako programiram obnasanje objektov?
1. Odprite objekt
2. Dodajte dogodke (npr. Create, Step)
3. Dodajte akcije dogodkom
4. Ali uporabite vizualni urejevalnik Blockly

## Viri

### Kateri formati slik so podprti?
- PNG (priporoceno)
- JPG
- GIF
- BMP

### Kateri zvocni formati so podprti?
- WAV
- MP3
- OGG

### Kako optimiziram svoje vire?
- Uporabite primerne velikosti slik
- Stisnite zvocne datoteke
- Odstranite neuporabljene vire

## Igranje

### Kako implementiram zaznavanje trkov?
1. Ustvarite dogodek trka v objektu
2. Izberite drugi objekt
3. Dodajte akcije za odziv

### Kako ustvarim vec nivojev?
1. Ustvarite vec sob
2. Uporabite akcijo "Pojdi v sobo"
3. Ali "Pojdi v naslednjo sobo"

### Kako shranim napredek igre?
Uporabite vgrajene funkcije shranjevanja:
- `save_game()`: Shrani igro
- `load_game()`: Nalozi igro

## Izvoz

### Kako izvozim svojo igro?
1. Pojdite na Datoteka > Izvozi
2. Izberite ciljno platformo
3. Nastavite moznosti
4. Kliknite "Izvozi"

### Zakaj je izvozena datoteka tako velika?
- Vkljucuje Python runtime
- Vsi viri vgrajeni
- Nasvet: Optimizirajte vire

### Ali lahko izvozim za mobilne naprave?
Trenutno ni neposredno podprto. Spletni izvoz deluje na mobilnih brskalnikih.

## Odpravljanje tezav

### Moja igra je pocasna
- Zmanjsajte kodo v dogodkih Step
- Optimizirajte velikosti spritov
- Izogibajte se prevec instancam

### Spriti se ne prikazujejo
- Preverite pot do sprita
- Prepricajte se, da je Viden=true
- Preverite vrstni red risanja (globina)

### Trki ne delujejo
- Preverite maske trkov
- Prepricajte se, da so objekti trdni (ce je potrebno)
- Preverite nastavitve dogodkov

## Skupnost

### Kje najdem pomoc?
- Uradna dokumentacija
- GitHub Issues
- Forumi skupnosti

### Kako lahko prispevam?
- Prijavite napake na GitHub
- Posljite Pull Requeste
- Izboljsajte dokumentacijo

## Glej tudi

- [Zacetek](Zacetek_sl)
- [Ustvarite svojo prvo igro](Prva_Igra_sl)
- [Dogodki in akcije](Dogodki_in_Akcije_sl)
