# Pogosto Zastavljena Vprašanja (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Nazaj na začetno stran](Home_sl)

---

## Splošna Vprašanja

### Kaj je PyGameMaker?

PyGameMaker je odprtokoden IDE za razvoj iger, navdihnjen z GameMaker 7.0. Omogoča vam ustvarjanje 2D iger z vizualnim programiranjem (Google Blockly) ali sistemom dogodkov-akcij, brez pisanja kode.

### Ali je PyGameMaker brezplačen?

Da! PyGameMaker je popolnoma brezplačen in odprtokoden — izvorna koda je pod licenco MIT, dokumentacija pa pod CC BY 4.0.

### Za katere platforme lahko izvažam?

- Windows (samostojna .exe)
- HTML5 (spletni brskalniki)
- Linux (izvorna binarna datoteka)
- Mobilne naprave (iOS/Android prek Kivy)

### Ali potrebujem izkušnje s programiranjem?

Ne! PyGameMaker je zasnovan za začetnike. Igre lahko ustvarjate z:
- Bloki Blockly za povleci-in-spusti
- Sistemom dogodkov/akcij point-and-click
- Brez pisanja kode

### Ali je združljiv z datotekami GameMaker?

PyGameMaker je navdihnjen z GameMaker 7.0, vendar uporablja svoj lasten format projekta. Datotek GameMaker ne morete uvoziti neposredno, vendar so koncepti in potek dela podobni.

---

## Namestitev

### Kakšne so sistemske zahteve?

- Python 3.10 ali novejši
- Windows, Linux ali macOS
- Najmanj 4 GB RAM-a (priporočeno 8 GB)
- ~500 MB prostora na disku

### Kako namestim PyGameMaker?

Za podrobna navodila za namestitev glejte [[Zacetek_sl]]. Kratka različica:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # ali venv\Scripts\activate na Windows
pip install -r requirements.txt
python main.py
```

### Python ni prepoznan / ni najden

Prepričajte se, da je Python nameščen in dodan v PATH sistema. Preverite z ukazom:

```bash
python --version
```

Če to ne uspe, ponovno namestite Python in med namestitvijo aktivirajte "Add Python to PATH".

### Ob zagonu dobim napake pri uvozu

Poskusite ponovno namestiti odvisnosti:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projekti

### Kje se shranjujejo moji projekti?

Projekti se shranjujejo v mape, ki jih izberete sami. Vsak projekt vsebuje:
- `project.json` - Glavno datoteko projekta
- Mape za sprite-e, zvoke, objekte, sobe itd.

### Ali lahko imam odprtih več projektov hkrati?

Trenutno PyGameMaker odpre en projekt naenkrat. Za preklapljanje med projekti uporabite **File > Open Project**.

### Kako naredim varnostno kopijo projekta?

Preprosto kopirajte celotno mapo projekta. Vsi viri in nastavitve so vsebovani v njej. Razmislite tudi o uporabi git za nadzor različic:

```bash
cd moj_projekt
git init
git add .
git commit -m "Začetna varnostna kopija"
```

### Moj projekt se ne odpre / je poškodovan

Poskusite naslednje korake:
1. Preverite, ali `project.json` obstaja in ni prazen
2. Odprite `project.json` v urejevalniku besedila in preverite napake JSON
3. Če je na voljo, obnovite iz varnostne kopije
4. Preverite izpis konzole za specifična sporočila o napakah

---

## Objekti in Dogodki

### Kakšna je razlika med objektom in instanco?

- **Objekt**: Predloga/model, ki določa obnašanje
- **Instanca**: Specifična kopija objekta, postavljena v sobi

Na primer, `obj_sovraznik` je objekt. Postavitev 5 sovražnikov v sobo ustvari 5 instanc objekta `obj_sovraznik`.

### Zakaj se moj dogodek ne sproži?

Pogosti vzroki:
1. **Napačna vrsta dogodka**: Prepričajte se, da uporabljate pravi dogodek (npr. "Key Press" namesto "Keyboard")
2. **Brez instanc**: Objekt mora imeti instance v sobi
3. **Objekt ni viden**: Preverite lastnost visible
4. **Vrstni red izvajanja**: Nekateri dogodki se izvedejo pred drugimi

### Kako naredim, da objekti medsebojno vplivajo?

Uporabite dogodke trkov:
1. Odprite objekt, ki naj zazna trk
2. Dodajte dogodek **Collision with [drug_objekt]**
3. Dodajte akcije za to, kaj se zgodi ob trku

### Kakšna je razlika med dogodkoma "Keyboard" in "Key Press"?

- **Keyboard [tipka]**: Sproži se vsako sličico, dokler je tipka pritisnjena
- **Key Press [tipka]**: Sproži se enkrat, ko je tipka prvič pritisnjena
- **Key Release [tipka]**: Sproži se enkrat, ko je tipka spuščena

---

## Sobe

### Katera soba se naloži prva?

Prva soba v drevesu virov (na vrhu seznama) se naloži ob zagonu igre. Sobe povlecite, da jih preuredite.

### Kako menjam sobo?

Uporabite akcije sobe:
- **Next Room**: Nadaljuj na naslednjo sobo po vrstnem redu
- **Previous Room**: Pojdi na prejšnjo sobo
- **Go to Room**: Skoči na določeno sobo

### Objekti izginejo, ko zamenjam sobo

Objekti so uničeni ob izstopu iz sobe, razen če so v svojih lastnostih označeni kot **Persistent**.

### Moja soba je na zaslonu prevelika/premajhna

Velikost okna igre ustreza dimenzijam prve sobe. Lahko:
- Spremenite velikost sobe, da ustreza želeni velikosti okna
- Uporabite Views, da prikažete samo del sobe

---

## Grafika in Sprite-i

### Kateri formati slik so podprti?

- PNG (priporočeno, podpira prosojnost)
- JPEG/JPG
- BMP
- GIF (samo prva sličica)

### Moj sprite se prikaže na napačnem položaju

Preverite nastavitev **Origin** v urejevalniku spritov. Izhodišče je sidrna točka za postavljanje. Pogoste nastavitve:
- Zgoraj levo (0, 0): Privzeto
- Sredina: Dobro za vrteče se objekte
- Sredina spodaj: Dobro za like

### Kako animiram sprite?

1. Ustvarite sprite z več sličicami (vodoravni trak)
2. V lastnostih spritea nastavite **Number of Frames**
3. Prilagodite **Animation Speed** (sličic na sekundo)

### Sprite-i so zamegljeni

To se zgodi pri spreminjanju velikosti spritov. Za pixel art onemogočite interpolacijo/glajenje v nastavitvah igre, če je na voljo.

---

## Zvok in Glasba

### Kateri zvočni formati so podprti?

- WAV (nekomprimiran)
- OGG (priporočeno za glasbo)
- MP3

### Zvok se ne predvaja

Preverite:
1. Ali zvočna datoteka obstaja v mapi sounds
2. Ali je format datoteke podprt
3. Ali v akcijah uporabljate pravilno ime zvoka
4. Brskalnik lahko zahteva interakcijo uporabnika (za HTML5)

### Kako naredim, da se glasba v ozadju predvaja v zanki?

Uporabite akcijo **Play Music** z aktivirano možnostjo zanke, ali **Play Sound** s parametrom loop nastavljenim na true.

---

## Izvoz

### Moja izvožena igra ne deluje

Pogoste težave:
- **Windows**: Manjkajoče DLL-je — poskrbite, da je vključena celotna izhodna mapa
- **HTML5**: Brskalnik blokira lokalne datoteke — gostite jo na strežniku
- **Manjkajoči viri**: Preverite, da so vključene vse datoteke

### Izvožena datoteka je ogromna

Velikost igre vključuje Python in vse knjižnice. Za zmanjšanje:
- Odstranite neuporabljene vire
- Stisnite slike in zvok
- Uporabite primerne formate (OGG namesto WAV)
- Za Windows izgradnje aktivirajte stiskanje UPX

### Ali lahko prodam igre, izdelane s PyGameMaker?

Da! Igre, ki jih ustvarite, so v celoti vaše in jih lahko prodajate. Izvorna koda PyGameMaker je pod permisivno licenco MIT, zato jo lahko prosto uporabljate v komercialnih projektih — in za razliko od licenc copyleft vam ni treba odpreti kode svojih lastnih sprememb.

---

## Blockly / Vizualno Programiranje

### Kje najdem urejevalnik Blockly?

1. Odprite objekt
2. V urejevalniku objektov kliknite na zavihek **Blockly**
3. Prikaže se delovno področje vizualnega programiranja

### Kako preklapljam med Blockly in dogodki?

Oba sistema delujeta na istem objektu. Zavihka Blockly in Events prikazujeta različna pogleda iste logike. Spremembe v enem se odražajo v drugem.

### Moji bloki Blockly so izginili

Preverite:
1. Ali gledate pravi objekt
2. Premaknite se po delovnem področju (bloki so lahko zunaj zaslona)
3. Preverite stopnjo povečave

---

## Zmogljivost

### Moja igra je počasna

Nasveti za boljšo zmogljivost:
1. Zmanjšajte število instanc
2. Izogibajte se zahtevnim izračunom v dogodkih Step
3. Uporabite alarme namesto štetja sličic
4. Optimizirajte velikosti spritov
5. Uničite instance, ki zapustijo sobo

### Dogodek Step se izvaja prepogosto

Dogodek Step se izvede vsako sličico (privzeto 60-krat na sekundo). Uporabite:
- Alarme za zakasnjene akcije
- Pogoje, ki se preverijo pred zahtevnimi operacijami
- Nižjo hitrost sobe, če je primerno

---

## Pridobivanje Pomoči

### Kje lahko prijavim napake?

Napake prijavite na strani [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Vključite:
- Kaj ste pričakovali, da se bo zgodilo
- Kaj se je dejansko zgodilo
- Korake za ponovitev težave
- Vaš operacijski sistem in verzijo Pythona

### Kje se lahko naučim več?

- [[Zacetek_sl]] - Namestitev in osnove
- [[Prva_Igra_sl]] - Vadnica korak za korakom
- [[Dogodki_in_Akcije_sl]] - Popolna referenca
- [[Vizualno_Programiranje_sl]] - Vodnik po Blockly
