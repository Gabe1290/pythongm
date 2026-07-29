# Pogosto zastavljena vprašanja (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Nazaj na začetno stran](Home_sl)

Odgovori na pogosta vprašanja o pyGM.

## Splošna vprašanja

### Kaj je pyGM?
pyGM je vizualni urejevalnik za razvoj iger v Pythonu. Omogoča ustvarjanje 2D iger brez obsežnega znanja programiranja.

### Ali je pyGM brezplačen?
Da, pyGM je odprtokoden in popolnoma brezplačen.

### Kateri programski jezik se uporablja?
pyGM temelji na Pythonu. Lahko uporabite vizualno programiranje ali neposredno pišete Python kodo.

### Za katere platforme lahko razvijam?
- Windows
- macOS
- Linux
- Splet (HTML5)
- Mobilne naprave (Kivy/Android)

## Namestitev

### Kako namestim pyGM?
```bash
pip install pygm
```

### Katero verzijo Pythona potrebujem?
Python 3.10 ali višji.

### pyGM se ne zažene. Kaj naj storim?
1. Preverite verzijo Pythona
2. Ponovno namestite odvisnosti
3. Zaženite iz ukazne vrstice za ogled napak

## Razvoj

### Kako ustvarim nov projekt?
Zaženite pyGM in izberite "Nov projekt" ali uporabite Datoteka > Novo.

### Kako dodam sprite?
1. Desni klik na "Spriti" v drevesu virov
2. Izberite "Nov sprite"
3. Uvozite sliko ali jo ustvarite

### Kako ustvarim animacije?
1. Odprite sprite
2. Dodajte več okvirjev
3. Nastavite hitrost animacije

### Kako programiram obnašanje objektov?
1. Odprite objekt
2. Dodajte dogodke (npr. Create, Step)
3. Dodajte akcije dogodkom
4. Ali uporabite vizualni urejevalnik Blockly

## Viri

### Kateri formati slik so podprti?
- PNG (priporočeno)
- JPG
- GIF
- BMP

### Kateri zvočni formati so podprti?
- WAV
- MP3
- OGG

### Kako optimiziram svoje vire?
- Uporabite primerne velikosti slik
- Stisnite zvočne datoteke
- Odstranite neuporabljene vire

## Igranje

### Kako implementiram zaznavanje trkov?
1. Ustvarite dogodek trka v objektu
2. Izberite drugi objekt
3. Dodajte akcije za odziv

### Kako ustvarim več nivojev?
1. Ustvarite več sob
2. Uporabite akcijo "Pojdi v sobo"
3. Ali "Pojdi v naslednjo sobo"

### Kako shranim napredek igre?
Uporabite vgrajene funkcije shranjevanja:
- `save_game()`: Shrani igro
- `load_game()`: Naloži igro

## Izvoz

### Kako izvozim svojo igro?
1. Pojdite na Datoteka → Izvozi projekt…
2. Izberite ciljno platformo
3. Nastavite možnosti
4. Kliknite "Izvozi"

### Zakaj je izvožena datoteka tako velika?
- Vključuje Python runtime
- Vsi viri so vgrajeni
- Nasvet: Optimizirajte vire

### Ali lahko izvozim za mobilne naprave?
Da, prek izvoza Kivy/Android. Spletni izvoz deluje tudi na mobilnih brskalnikih.

## Odpravljanje težav

### Moja igra je počasna
- Zmanjšajte kodo v dogodkih Step
- Optimizirajte velikosti spritov
- Izogibajte se preveč instancam

### Spriti se ne prikazujejo
- Preverite pot do sprita
- Prepričajte se, da je Viden=true
- Preverite vrstni red risanja (globina)

### Trki ne delujejo
- Preverite maske trkov
- Prepričajte se, da so objekti trdni (če je potrebno)
- Preverite nastavitve dogodkov

## Skupnost

### Kje najdem pomoč?
- Uradna dokumentacija
- GitHub Issues
- Forumi skupnosti

### Kako lahko prispevam?
- Prijavite napake na GitHub
- Pošljite Pull Requeste
- Izboljšajte dokumentacijo

## Glej tudi

- [Začetek](Zacetek_sl)
- [Ustvarite svojo prvo igro](Prva_Igra_sl)
- [Dogodki in akcije](Dogodki_in_Akcije_sl)
