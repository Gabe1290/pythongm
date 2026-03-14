# PyGameMaker IDE Uporabniški priročnik

**Različica 1.0.0-rc.4**
**Razvojno okolje za vizualno ustvarjanje 2D iger s Pythonom, navdahnjeno z GameMakerjem**

---

## Kazalo vsebine

1. [Uvod](#1-uvod)
2. [Namestitev in nastavitev](#2-namestitev-in-nastavitev)
3. [Pregled razvojnega okolja](#3-pregled-razvojnega-okolja)
4. [Delo s projekti](#4-delo-s-projekti)
5. [Sličice (Sprites)](#5-sličice-sprites)
6. [Zvoki](#6-zvoki)
7. [Ozadja](#7-ozadja)
8. [Objekti](#8-objekti)
9. [Sobe](#9-sobe)
10. [Referenca dogodkov](#10-referenca-dogodkov)
11. [Referenca akcij](#11-referenca-akcij)
12. [Testiranje in zagon iger](#12-testiranje-in-zagon-iger)
13. [Izvoz iger](#13-izvoz-iger)
14. [Blockly vizualno programiranje](#14-blockly-vizualno-programiranje)
15. [Podpora za robota Thymio](#15-podpora-za-robota-thymio)
16. [Nastavitve in možnosti](#16-nastavitve-in-možnosti)
17. [Bližnjice na tipkovnici](#17-bližnjice-na-tipkovnici)
18. [Vadnice](#18-vadnice)
19. [Odpravljanje težav](#19-odpravljanje-težav)

---

## 1. Uvod

PyGameMaker je izobraževalno razvojno okolje za igre, navdahnjeno z GameMakerjem. Omogoča vam vizualno ustvarjanje 2D iger z uporabo sistema povleci-in-spusti za dogodke/akcije, brez pisanja kode. Zasnovano je z dvema ciljema:

- **Poučevanje razvoja iger** vizualno skozi intuitiven vmesnik
- **Poučevanje programiranja v Pythonu** skozi odprtokodno kodo razvojnega okolja

PyGameMaker uporablja PySide6 (Qt) za vmesnik razvojnega okolja in Pygame za izvajalno okolje iger. Igre je mogoče izvoziti kot samostojne izvršljive datoteke, mobilne aplikacije ali HTML5 spletne igre.

### Ključne funkcionalnosti

- Vizualno programiranje z dogodki/akcijami (80+ vgrajenih akcij)
- Urejevalnik sličic s podporo za animacije
- Urejevalnik sob z namestitvijo primerkov, plastmi ploščic in drsečimi ozadji
- Predogled igre v realnem času s tipko F5
- Izvoz za Windows EXE, mobilne naprave (Android/iOS prek Kivy), HTML5 in robote Thymio
- Integracija z Google Blockly za vizualne bloke kode
- Simulator izobraževalnega robota Thymio
- Večjezični vmesnik (8+ jezikov)
- Temna in svetla tema

---

## 2. Namestitev in nastavitev

### Zahteve

- Python 3.10 ali novejši
- PySide6
- Pygame
- Pillow (PIL)

### Namestitev odvisnosti

```bash
pip install PySide6 pygame Pillow
```

### Neobvezne odvisnosti

Za funkcije izvoza:

```bash
pip install pyinstaller    # For EXE export
pip install kivy           # For mobile export
pip install buildozer      # For Android builds
pip install jinja2         # For code generation templates
```

### Zagon razvojnega okolja

```bash
python main.py
```

Okno razvojnega okolja se odpre s privzetimi dimenzijami 1400x900 slikovnih pik. Položaj in velikost okna se shranita med sejami.

---

## 3. Pregled razvojnega okolja

### Razporeditev okna

Razvojno okolje uporablja razporeditev s tremi paneli:

```
+-------------------+---------------------------+------------------+
|   Drevo sredstev  |      Območje urejevalnika |   Lastnosti      |
|   (Levi panel)    |      (Sredinski panel)    |   (Desni panel)  |
|                   |                           |                  |
|   - Sličice       |   Urejevalniki z zavihki  |   Kontekstno     |
|   - Zvoki         |   za sličice, objekte     |   odvisne         |
|   - Ozadja        |   in sobe                 |   lastnosti       |
|   - Objekti       |                           |                  |
|   - Sobe          |                           |                  |
|   - Skripte       |                           |                  |
|   - Pisave        |                           |                  |
+-------------------+---------------------------+------------------+
|                       Vrstica stanja                              |
+-------------------------------------------------------------------+
```

- **Levi panel (Drevo sredstev):** Prikazuje vsa sredstva projekta, organizirana po vrsti. Dvokliknite sredstvo, da ga odprete v urejevalniku.
- **Sredinski panel (Območje urejevalnika):** Delovni prostor z zavihki, kjer urejate sličice, objekte in sobe. Privzeto je prikazan pozdravni zavihek.
- **Desni panel (Lastnosti):** Prikazuje kontekstno odvisne lastnosti za trenutno aktiven urejevalnik. Lahko ga skrijete.
- **Vrstica stanja:** Prikazuje stanje trenutne operacije in ime projekta.

### Menijska vrstica

#### Meni Datoteka

| Ukaz | Bližnjica | Opis |
|------|-----------|------|
| Nov projekt... | Ctrl+N | Ustvari nov projekt |
| Odpri projekt... | Ctrl+O | Odpri obstoječ projekt |
| Shrani projekt | Ctrl+S | Shrani trenutni projekt |
| Shrani projekt kot... | Ctrl+Shift+S | Shrani na novo lokacijo |
| Nedavni projekti | | Podmeni z do 10 nedavnimi projekti |
| Izvozi kot HTML5... | | Izvozi igro kot eno HTML datoteko |
| Izvozi kot Zip... | | Zapakiraj projekt kot ZIP arhiv |
| Izvozi za Kivy... | | Izvozi za mobilno namestitev |
| Izvozi projekt... | Ctrl+E | Odpri pogovorno okno za izvoz |
| Odpri Zip projekt... | | Odpri ZIP-zapakiran projekt |
| Samodejno shrani v Zip | | Preklopi samodejno shranjevanje v ZIP |
| Omogoči samodejno shranjevanje | | Preklopi samodejno shranjevanje projekta |
| Nastavitve samodejnega shranjevanja... | | Nastavi interval samodejnega shranjevanja |
| Nastavitve projekta... | | Odpri konfiguracijo projekta |
| Izhod | Ctrl+Q | Zapri razvojno okolje |

#### Meni Urejanje

| Ukaz | Bližnjica | Opis |
|------|-----------|------|
| Razveljavi | Ctrl+Z | Razveljavi zadnje dejanje |
| Uveljavi | Ctrl+Y | Uveljavi zadnje razveljavljeno dejanje |
| Izreži | Ctrl+X | Izreži izbrano |
| Kopiraj | Ctrl+C | Kopiraj izbrano |
| Prilepi | Ctrl+V | Prilepi iz odložišča |
| Podvoji | Ctrl+D | Podvoji izbrane elemente |
| Najdi... | Ctrl+F | Odpri pogovorno okno za iskanje |
| Najdi in zamenjaj... | Ctrl+H | Odpri pogovorno okno za iskanje in zamenjavo |

#### Meni Sredstva

| Ukaz | Opis |
|------|------|
| Uvozi sličico... | Uvozi slike sličic (PNG, JPG, BMP, GIF) |
| Uvozi zvok... | Uvozi zvočne datoteke |
| Uvozi ozadje... | Uvozi slike ozadij |
| Ustvari objekt... | Ustvari nov igralni objekt |
| Ustvari sobo... (Ctrl+R) | Ustvari novo igralno sobo |
| Ustvari skripto... | Ustvari novo skriptno datoteko |
| Ustvari pisavo... | Ustvari novo sredstvo pisave |
| Uvozi paket objekta... | Uvozi paket .gmobj |
| Uvozi paket sobe... | Uvozi paket .gmroom |

#### Meni Gradnja

| Ukaz | Bližnjica | Opis |
|------|-----------|------|
| Testiraj igro | F5 | Zaženi igro v testnem načinu |
| Razhroščuj igro | F6 | Zaženi igro z razhroščevalnim izpisom |
| Zgradi igro... | F7 | Odpri konfiguracijo gradnje |
| Zgradi in zaženi | F8 | Zgradi in takoj zaženi |
| Izvozi igro... | | Izvozi prevedeno igro |

#### Meni Orodja

| Ukaz | Opis |
|------|------|
| Možnosti... | Odpri možnosti razvojnega okolja |
| Upravljalnik sredstev... | Odpri okno za upravljanje sredstev |
| Nastavi akcijske bloke... | Nastavi bloke Blockly |
| Nastavi bloke Thymio... | Nastavi bloke robota Thymio |
| Preveri projekt | Preveri projekt za napake |
| Počisti projekt | Odstrani začasne datoteke |
| Preseli na modularno strukturo | Nadgradi format projekta |
| Jezik | Spremeni jezik vmesnika |
| Programiranje Thymio | Podmeni za programiranje robota |

#### Meni Pomoč

| Ukaz | Bližnjica | Opis |
|------|-----------|------|
| Dokumentacija | F1 | Odpri dokumentacijo pomoči |
| Vadnice | | Odpri vadnice |
| O PyGameMaker | | Podatki o različici in licenci |

### Orodna vrstica

Orodna vrstica omogoča hiter dostop do pogostih dejanj (od leve proti desni):

| Gumb | Dejanje |
|------|---------|
| Novo | Ustvari nov projekt |
| Odpri | Odpri obstoječ projekt |
| Shrani | Shrani trenutni projekt |
| Testiraj | Zaženi igro (F5) |
| Razhroščuj | Razhroščuj igro (F6) |
| Izvozi | Izvozi igro |
| Uvozi sličico | Uvozi sliko sličice |
| Uvozi zvok | Uvozi zvočno datoteko |
| Thymio | Dodaj dogodek robota Thymio |

### Drevo sredstev

Drevo sredstev v levem panelu organizira sredstva projekta v kategorije:

**Medijska sredstva:**
- **Sličice** - Slike in animacijski trakovi za igralne objekte
- **Zvoki** - Zvočni učinki in glasbene datoteke
- **Ozadja** - Slike ozadij in nabori ploščic

**Logika igre:**
- **Objekti** - Definicije igralnih objektov z dogodki in akcijami
- **Sobe** - Igralne ravni/prizori z nameščenimi primerki

**Sredstva kode:**
- **Skripte** - Datoteke s kodo
- **Pisave** - Sredstva pisav po meri

**Operacije kontekstnega menija:**
- Z desnim klikom na glavo kategorije ustvarite ali uvozite sredstva
- Z desnim klikom na sredstvo ga preimenujete, izbrišete, izvozite ali si ogledate lastnosti
- Dvokliknite sredstvo, da ga odprete v urejevalniku
- Sredstva sob je mogoče prerazporediti (Premakni gor/dol/na vrh/na dno)

---

## 4. Delo s projekti

### Ustvarjanje novega projekta

1. Izberite **Datoteka > Nov projekt** (Ctrl+N)
2. Vnesite **Ime projekta**
3. Izberite **Lokacijo** za mapo projekta
4. Izberite **Predlogo** (neobvezno):
   - **Prazen projekt** - Prazen projekt
   - **Predloga platformske igre** - Vnaprej nastavljeno za platformske igre
   - **Predloga igre z zgornjim pogledom** - Vnaprej nastavljeno za igre z zgornjim pogledom
5. Kliknite **Ustvari projekt**

### Struktura projekta

```
MyProject/
├── project.json          # Main project file
├── sprites/              # Sprite images and metadata
│   ├── player.png
│   └── player.json
├── objects/              # Object definitions
│   └── obj_player.json
├── rooms/                # Room layout data
│   └── room_start.json
├── sounds/               # Audio files and metadata
├── backgrounds/          # Background images
└── thumbnails/           # Auto-generated previews
```

### Shranjevanje projektov

- **Ctrl+S** shrani projekt na trenutno lokacijo
- **Ctrl+Shift+S** shrani na novo lokacijo
- **Samodejno shranjevanje** lahko omogočite v Datoteka > Omogoči samodejno shranjevanje
- Interval samodejnega shranjevanja nastavite v Datoteka > Nastavitve samodejnega shranjevanja

### Odpiranje projektov

- **Ctrl+O** odpre mapo projekta
- Nedavni projekti so navedeni v **Datoteka > Nedavni projekti**
- ZIP projekte lahko odprete z **Datoteka > Odpri Zip projekt**

---

## 5. Sličice (Sprites)

Sličice so vizualne slike, ki jih uporabljajo igralni objekti. Lahko so statične slike ali animacijski trakovi z več okvirji.

### Ustvarjanje sličice

1. Z desnim klikom na **Sličice** v drevesu sredstev izberite **Uvozi sličico...**
2. Izberite slikovno datoteko (PNG, JPG, BMP ali GIF)
3. Sličica se pojavi v drevesu sredstev in se odpre v urejevalniku sličic

### Urejevalnik sličic

Urejevalnik sličic ima štiri glavna območja:

- **Plošča z orodji (levo):** Orodja za risanje
- **Platno (sredina):** Območje za urejanje s povečavo in mrežo
- **Barvna paleta (desno):** Barve ospredja/ozadja in vzorci
- **Časovnica okvirjev (spodaj):** Upravljanje animacijskih okvirjev

#### Orodja za risanje

| Orodje | Bližnjica | Opis |
|--------|-----------|------|
| Svinčnik | P | Standardno risanje slikovnih pik |
| Radirka | E | Odstrani slikovne pike (naredi prozorne) |
| Izbirnik barve | I | Zajemi barvo s platna |
| Zalivanje | G | Zapolni povezana območja |
| Črta | L | Riši ravne črte |
| Pravokotnik | R | Riši pravokotnike (obroba ali zapolnjeni) |
| Elipsa | O | Riši elipse (obroba ali zapolnjene) |
| Izbira | S | Izberi, izreži, kopiraj, prilepi območja |

#### Velikost čopiča

Velikost čopiča se giblje od 1 do 16 slikovnih pik in vpliva na orodja Svinčnik, Radirka in Črta.

#### Način zapolnjevanja

Preklapljajte med obrobo in zapolnjenim načinom za orodji Pravokotnik in Elipsa z gumbom **Zapolnjeno**.

#### Barvna paleta

- **Levi klik** na vzorec ospredja za izbiro barve risanja
- **Desni klik** na vzorec ozadja za izbiro sekundarne barve
- **Gumb X** zamenja barvi ospredja in ozadja
- Kliknite katero koli barvo v hitri paleti, da jo izberete
- Dvokliknite vzorec palete, da ga prilagodite
- Popoln izbirnik barv RGBA s podporo za alfa (prosojnost)

### Animacijski okvirji

Sličice imajo lahko več animacijskih okvirjev, razporejenih kot horizontalni trak.

**Kontrole časovnice okvirjev:**
- **+ (Dodaj):** Dodaj nov prazen okvir
- **D (Podvoji):** Kopiraj trenutni okvir
- **- (Izbriši):** Odstrani trenutni okvir (najmanj 1 okvir)
- **Predvajaj/Ustavi:** Predogled animacije
- Števec okvirjev prikazuje trenutni/skupno število okvirjev

**Lastnosti animacije:**
- **Število okvirjev:** Število animacijskih okvirjev
- **Hitrost animacije:** Okvirji na sekundo (privzeto: 10 FPS)
- **Vrsta animacije:** single, strip_h (horizontalni), strip_v (vertikalni) ali grid

**Podpora za animirane GIF-e:** Uvozite animirane GIF datoteke neposredno. Vsi okvirji se samodejno izvlečejo z obravnavo prosojnosti.

### Izhodišče sličice

Izhodiščna točka je sidrna pozicija, ki se uporablja za namestitev in vrtenje v igri.

**Prednastavljena položaji:**
- Zgoraj-levo (0, 0)
- Zgoraj-sredina
- Sredina (privzeto za večino sličic)
- Sredina-spodaj
- Spodaj-levo
- Spodaj-desno
- Po meri (ročni vnos X/Y)

Izhodišče je na platnu prikazano kot križec.

### Kontrole platna

- **Ctrl+kolesce miške:** Povečaj/pomanjšaj (1x do 64x)
- **Preklop mreže:** Prikaži/skrij mrežo slikovnih pik (vidna pri 4x povečavi in več)
- **Zrcali H/V:** Obrni trenutni okvir vodoravno ali navpično
- **Spremeni velikost/Povečaj:** Spremeni dimenzije sličice z možnostmi povečave ali spremembe velikosti platna

### Lastnosti sličice (shranjene)

| Lastnost | Opis |
|----------|------|
| name | Ime sredstva |
| file_path | Pot do datoteke PNG traku |
| width | Celotna širina traku |
| height | Višina okvirja |
| frame_width | Širina posameznega okvirja |
| frame_height | Višina posameznega okvirja |
| frames | Število okvirjev |
| animation_type | single, strip_h, strip_v, grid |
| speed | FPS animacije |
| origin_x | X koordinata izhodišča |
| origin_y | Y koordinata izhodišča |

---

## 6. Zvoki

Zvoki so zvočne datoteke, ki se uporabljajo za zvočne učinke in glasbo v ozadju.

### Uvoz zvokov

1. Z desnim klikom na **Zvoki** v drevesu sredstev izberite **Uvozi zvok...**
2. Izberite zvočno datoteko (WAV, OGG, MP3)
3. Zvok se doda projektu

### Lastnosti zvoka

| Lastnost | Opis |
|----------|------|
| name | Ime zvočnega sredstva |
| file_path | Pot do zvočne datoteke |
| kind | "sound" (učinek) ali "music" (pretočno) |
| volume | Privzeta glasnost (0.0 do 1.0) |

**Zvočni učinki** se naložijo v pomnilnik za takojšnje predvajanje. **Glasbene** datoteke se pretakajo z diska in hkrati se lahko predvaja le ena.

---

## 7. Ozadja

Ozadja so slike, ki se uporabljajo za igralnimi objekti. Služijo lahko tudi kot nabori ploščic za ravni na osnovi ploščic.

### Uvoz ozadij

1. Z desnim klikom na **Ozadja** v drevesu sredstev izberite **Uvozi ozadje...**
2. Izberite slikovno datoteko

### Konfiguracija nabora ploščic

Ozadja se lahko nastavijo kot nabori ploščic z naslednjimi lastnostmi:

| Lastnost | Opis |
|----------|------|
| tile_width | Širina posamezne ploščice (privzeto: 16) |
| tile_height | Višina posamezne ploščice (privzeto: 16) |
| h_offset | Vodoravni odmik do prve ploščice |
| v_offset | Navpični odmik do prve ploščice |
| h_sep | Vodoravni razmak med ploščicami |
| v_sep | Navpični razmak med ploščicami |
| use_as_tileset | Omogoči način nabora ploščic |

---

## 8. Objekti

Objekti definirajo igralne entitete z lastnostmi, dogodki in akcijami. Vsak objekt ima lahko sličico za vizualni prikaz in vsebuje obdelovalce dogodkov, ki določajo njegovo vedenje.

### Ustvarjanje objekta

1. Z desnim klikom na **Objekti** v drevesu sredstev izberite **Ustvari objekt...**
2. Vnesite ime objekta
3. Objekt se odpre v urejevalniku objektov

### Lastnosti objekta

| Lastnost | Privzeto | Opis |
|----------|----------|------|
| Sličica | Brez | Vizualna sličica za prikaz |
| Viden | Da | Ali se primerki izrisujejo |
| Trden | Ne | Ali objekt blokira gibanje |
| Trajen | Ne | Ali primerki preživijo menjavo sob |
| Globina | 0 | Vrstni red izrisovanja (višje = zadaj, nižje = spredaj) |
| Nadrejeni | Brez | Nadrejeni objekt za dedovanje |

### Nadrejeni objekti

Objekti lahko dedujejo od nadrejenega objekta. Podrejeni objekti prejmejo vse trkovne dogodke nadrejenega. To je uporabno za ustvarjanje hierarhij, kot so:

```
obj_enemy (parent - has collision with obj_player)
  ├── obj_enemy_melee (inherits collision handling)
  └── obj_enemy_ranged (inherits collision handling)
```

### Dodajanje dogodkov

1. Odprite urejevalnik objektov
2. Kliknite **Dodaj dogodek** v panelu dogodkov
3. Izberite vrsto dogodka s seznama (glejte [Referenca dogodkov](#10-referenca-dogodkov))
4. Dogodek se pojavi v drevesu dogodkov

### Dodajanje akcij k dogodkom

1. Izberite dogodek v drevesu dogodkov
2. Kliknite **Dodaj akcijo** ali z desnim klikom izberite **Dodaj akcijo**
3. Izberite vrsto akcije iz kategoriziranega seznama
4. Nastavite parametre akcije v pogovornem oknu
5. Kliknite V redu za dodajanje akcije

Akcije se izvajajo po vrstnem redu od zgoraj navzdol, ko se dogodek sproži.

### Pogojna logika

Akcije podpirajo pogojni tok if/else:

1. Dodajte pogojno akcijo (npr. **Če trk na**, **Testiraj spremenljivko**)
2. Dodajte akcijo **Začni blok** (odpiralni oklepaj)
3. Dodajte akcije, ki se izvedejo, ko je pogoj izpolnjen
4. Dodajte akcijo **Sicer** (neobvezno)
5. Dodajte **Začni blok** za vejo sicer
6. Dodajte akcije za primer, ko pogoj ni izpolnjen
7. Dodajte akcije **Končaj blok** za zaprtje vsakega bloka

Primer zaporedja akcij:
```
If Collision At (self.x, self.y + 1, "solid")
  Start Block
    Set Vertical Speed (0)
  End Block
Else
  Start Block
    Set Vertical Speed (vspeed + 0.5)
  End Block
```

### Ogled kode

Označite možnost **Ogled kode** v urejevalniku objektov, da vidite generirano kodo Python za vse dogodke in akcije. To je uporabno za razumevanje, kako se vizualne akcije prevedejo v kodo.

---

## 9. Sobe

Sobe so prizori ali ravni vaše igre. Vsaka soba ima ozadje, nameščene primerke objektov in neobvezne plasti ploščic.

### Ustvarjanje sobe

1. Z desnim klikom na **Sobe** v drevesu sredstev izberite **Ustvari sobo...**
2. Vnesite ime sobe
3. Soba se odpre v urejevalniku sob

### Lastnosti sobe

| Lastnost | Privzeto | Opis |
|----------|----------|------|
| Širina | 1024 | Širina sobe v slikovnih pikah |
| Višina | 768 | Višina sobe v slikovnih pikah |
| Barva ozadja | #87CEEB (nebeško modra) | Barva zapolnitve za vsem |
| Slika ozadja | Brez | Neobvezna slika ozadja |
| Trajna | Ne | Ohrani stanje ob odhodu |

### Nameščanje primerkov

1. Kliknite objekt v **Paleti objektov** (leva stran urejevalnika sob)
2. Kliknite na platno sobe, da namestite primerek
3. Nadaljujte s kliki za namestitev več kopij
4. Izberite nameščene primerke, da jih premaknete ali nastavite

### Lastnosti primerka

Ko izberete nameščen primerek:

| Lastnost | Razpon | Opis |
|----------|--------|------|
| Položaj X | 0-9999 | Vodoravni položaj |
| Položaj Y | 0-9999 | Navpični položaj |
| Viden | Da/Ne | Vidnost primerka |
| Vrtenje | 0-360 | Vrtenje v stopinjah |
| Merilo X | 10%-1000% | Vodoravno merilo |
| Merilo Y | 10%-1000% | Navpično merilo |

### Mreža in pripenjanje

- **Preklop mreže:** Kliknite gumb mreže za prikaz/skritje mreže za nameščanje
- **Preklop pripenjanja:** Kliknite gumb pripenjanja za omogočanje/onemogočanje pripenjanja na mrežo
- **Velikost mreže:** Privzeto 32x32 slikovnih pik (nastavljivo v Možnostih)

### Operacije s primerki

| Dejanje | Bližnjica | Opis |
|---------|-----------|------|
| Premakni | Povleci | Premakni primerek na nov položaj |
| Izberi več | Shift+klik | Dodaj/odstrani iz izbire |
| Izbira z okvirjem | Povleci prazno območje | Izberi vse primerke v pravokotniku |
| Izbriši | Tipka Delete | Odstrani izbrane primerke |
| Izreži | Ctrl+X | Izreži v odložišče |
| Kopiraj | Ctrl+C | Kopiraj v odložišče |
| Prilepi | Ctrl+V | Prilepi iz odložišča |
| Podvoji | Ctrl+D | Podvoji izbrane primerke |
| Počisti vse | Gumb v orodni vrstici | Odstrani vse primerke (s potrditvijo) |

### Plasti ozadja

Sobe podpirajo do 8 plasti ozadja (indeksirane 0-7), vsaka z neodvisnimi nastavitvami:

| Lastnost | Opis |
|----------|------|
| Slika ozadja | Katero sredstvo ozadja uporabiti |
| Vidna | Prikaži/skrij plast |
| Ospredje | Če da, se izriše pred primerki |
| Ploščenje vodoravno | Ponovi čez širino sobe |
| Ploščenje navpično | Ponovi čez višino sobe |
| Hitrost vodoravnega drsenja | Vodoravno drsenje slikovnih pik na okvir |
| Hitrost navpičnega drsenja | Navpično drsenje slikovnih pik na okvir |
| Raztegni | Povečaj za zapolnitev celotne sobe |
| Odmik X / Y | Odmik položaja plasti |

### Plasti ploščic

Za ravni na osnovi ploščic:

1. Kliknite **Paleta ploščic...** za odprtje izbirnika ploščic
2. Izberite nabor ploščic (ozadje, označeno kot nabor ploščic)
3. Nastavite širino in višino ploščice
4. Kliknite ploščico v paleti, da jo izberete
5. Kliknite v sobo za namestitev ploščic
6. Izberite **Plast** (0-7) za ploščice

### Vrstni red sob

Sobe se izvajajo v vrstnem redu, v katerem se pojavljajo v drevesu sredstev. Prva soba je začetna soba.

- Z desnim klikom na sobo uporabite **Premakni gor/dol/na vrh/na dno** za prerazporeditev
- Uporabite akciji **Naslednja soba** in **Prejšnja soba** za navigacijo med sobami med izvajanjem

### Sistem pogledov

Sobe podpirajo do 8 pogledov kamere (kot GameMaker):

| Lastnost | Opis |
|----------|------|
| Viden | Omogoči/onemogoči ta pogled |
| Pogled X/Y | Položaj kamere v sobi |
| Pogled Š/V | Velikost vidnega polja kamere |
| Vrata X/Y | Položaj na zaslonu za ta pogled |
| Vrata Š/V | Velikost na zaslonu za ta pogled |
| Sledi objektu | Objekt za sledenje s kamero |
| Rob V/N | Rob drsenja okoli spremljanega objekta |
| Hitrost V/N | Največja hitrost drsenja kamere (-1 = takojšnje) |

---

## 10. Referenca dogodkov

Dogodki določajo, kdaj se akcije izvedejo. Vsak dogodek se sproži pod določenimi pogoji.

### Dogodki objektov

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Ustvari | Objekt | Se primerek prvič ustvari |
| Uniči | Objekt | Se primerek uniči |
| Korak | Korak | Vsak okvir igre (~60 FPS) |
| Začetni korak | Korak | Na začetku vsakega okvirja, pred fiziko |
| Končni korak | Korak | Na koncu vsakega okvirja, po trkih |

### Trkovni dogodki

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Trk z... | Trk | Se dva primerka prekrijeta (izberite ciljni objekt) |

### Dogodki tipkovnice

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Tipkovnica | Vnos | Je tipka držana neprekinjeno (za gladko gibanje) |
| Pritisk tipkovnice | Vnos | Se tipka prvič pritisne (enkrat na pritisk) |
| Spust tipkovnice | Vnos | Se tipka spusti |

**Razpoložljive tipke:** A-Z, 0-9, puščične tipke, preslednica, Enter, Escape, Tab, Backspace, Delete, F1-F12, tipke numerične tipkovnice, Shift, Ctrl, Alt in več (76+ tipk skupaj).

**Posebni dogodki tipkovnice:**
- **Brez tipke** - Se sproži, ko nobena tipka ni pritisnjena
- **Katerakoli tipka** - Se sproži, ko je pritisnjena katerakoli tipka

### Dogodki miške

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Pritisk leve/desne/srednje tipke miške | Vnos | Tipka kliknjena na primerku |
| Spust leve/desne/srednje tipke miške | Vnos | Tipka spuščena na primerku |
| Leva/desna/srednja tipka miške držana | Vnos | Tipka držana na primerku |
| Vstop miške | Vnos | Kazalec vstopi v okvir primerka |
| Izstop miške | Vnos | Kazalec zapusti okvir primerka |
| Kolesce miške gor/dol | Vnos | Drsno kolesce na primerku |
| Globalni pritisk miške | Vnos | Tipka kliknjena kjerkoli v sobi |
| Globalni spust miške | Vnos | Tipka spuščena kjerkoli v sobi |

### Časovni dogodki

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Alarm 0-11 | Čas | Odštevalnik alarma doseže nič (12 neodvisnih alarmov) |

### Dogodki izrisovanja

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Izriši | Izrisovanje | Se primerek izriše (nadomesti privzeto izrisovanje sličice) |
| Izriši GUI | Izrisovanje | Se izriše nad vsem (za vmesnik, prikaz točk) |

### Dogodki sobe

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Začetek sobe | Soba | Se soba začne (po dogodkih ustvarjanja) |
| Konec sobe | Soba | Se soba skoraj konča |

### Dogodki igre

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Začetek igre | Igra | Se igra inicializira (samo prva soba) |
| Konec igre | Igra | Se igra zapira |

### Drugi dogodki

| Dogodek | Kategorija | Se sproži, ko |
|---------|------------|----------------|
| Izven sobe | Drugo | Je primerek popolnoma izven meja sobe |
| Presek meje | Drugo | Se primerek dotakne roba sobe |
| Ni več življenj | Drugo | Vrednost življenj doseže 0 ali manj |
| Ni več zdravja | Drugo | Vrednost zdravja doseže 0 ali manj |
| Konec animacije | Drugo | Animacija sličice doseže zadnji okvir |
| Uporabniški dogodek 0-15 | Drugo | 16 dogodkov po meri, sproženih s kodo |

---

## 11. Referenca akcij

Akcije so gradniki vedenja igre. Nameščene so znotraj dogodkov in se izvajajo po vrstnem redu.

### Akcije gibanja

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Premakni po mreži | direction (levo/desno/gor/dol), grid_size (privzeto: 32) | Premakni se za eno mrežno enoto v smer |
| Nastavi vodoravno hitrost | speed (slikovnih pik/okvir) | Nastavi hspeed za gladko vodoravno gibanje |
| Nastavi navpično hitrost | speed (slikovnih pik/okvir) | Nastavi vspeed za gladko navpično gibanje |
| Ustavi gibanje | (brez) | Nastavi obe hitrosti na nič |
| Premakni fiksno | directions (8-smerno), speed | Začni se premikati v fiksni smeri |
| Premakni prosto | direction (0-360 stopinj), speed | Premikaj se pod natančnim kotom |
| Premakni proti | x, y, speed | Premakni se proti ciljnemu položaju |
| Nastavi gravitacijo | direction (270=dol), gravity | Uporabi stalno pospeševanje |
| Nastavi trenje | friction | Uporabi pojemanje vsak okvir |
| Obrni vodoravno | (brez) | Obrni smer hspeed |
| Obrni navpično | (brez) | Obrni smer vspeed |
| Nastavi hitrost | speed | Nastavi velikost gibanja |
| Nastavi smer | direction (stopinje) | Nastavi kot gibanja |
| Skoči na položaj | x, y | Teleportiraj na položaj |
| Skoči na začetek | (brez) | Teleportiraj na začetni položaj |
| Odbij | (brez) | Obrni hitrost ob trku |

### Akcije mreže

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Pripni na mrežo | grid_size | Poravnaj položaj na najbližjo mrežno točko |
| Če na mreži | grid_size | Preveri, ali je poravnano z mrežo (pogojno) |
| Ustavi, če ni tipk | grid_size | Ustavi na mreži, ko se tipke za gibanje spustijo |

### Akcije primerkov

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Ustvari primerek | object, x, y, relative | Ustvari nov primerek objekta |
| Uniči primerek | target (self/other) | Odstrani primerek iz igre |
| Spremeni sličico | sprite | Spremeni prikazano sličico |
| Nastavi vidnost | visible (true/false) | Prikaži ali skrij primerek |
| Nastavi merilo | scale_x, scale_y | Spremeni velikost primerka |

### Akcije točk, življenj in zdravja

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Nastavi točke | value | Nastavi točke na določeno vrednost |
| Dodaj k točkam | value | Dodaj točke (lahko negativno) |
| Nastavi življenja | value | Nastavi število življenj |
| Dodaj življenja | value | Dodaj/odvzemi življenja |
| Nastavi zdravje | value | Nastavi zdravje (0-100) |
| Dodaj zdravje | value | Dodaj/odvzemi zdravje |
| Prikaži tabelo najboljših rezultatov | (brez) | Prikaži tabelo najboljših rezultatov |

### Akcije sobe in igre

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Ponovno naloži sobo | (brez) | Ponovno naloži trenutno sobo |
| Naslednja soba | (brez) | Pojdi v naslednjo sobo po vrsti |
| Prejšnja soba | (brez) | Pojdi v prejšnjo sobo |
| Pojdi v sobo | room | Skoči v določeno sobo |
| Če naslednja soba obstaja | (brez) | Pogojno: ali obstaja naslednja soba? |
| Če prejšnja soba obstaja | (brez) | Pogojno: ali obstaja prejšnja soba? |
| Ponovno zaženi igro | (brez) | Ponovno zaženi od prve sobe |
| Končaj igro | (brez) | Zapri igro |

### Časovne akcije

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Nastavi alarm | alarm_number (0-11), steps | Zaženi odštevalnik (30 korakov = 0,5 s pri 60 FPS) |
| Zamakni akcijo | action, delay_frames | Izvedi akcijo po zamiku |

### Akcije sporočil in prikaza

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Prikaži sporočilo | message | Prikaži pojavno sporočilo |
| Izriši besedilo | text, x, y, color, size | Izriši besedilo na zaslon (uporabi v dogodku Izriši) |
| Izriši pravokotnik | x1, y1, x2, y2, color, filled | Izriši pravokotnik |
| Izriši krog | x, y, radius, color, filled | Izriši krog |
| Izriši elipso | x1, y1, x2, y2, color, filled | Izriši elipso |
| Izriši črto | x1, y1, x2, y2, color | Izriši črto |
| Izriši sličico | sprite_name, x, y, subimage | Izriši sličico na položaju |
| Izriši ozadje | background_name, x, y, tiled | Izriši sliko ozadja |
| Izriši točke | x, y, caption | Izriši vrednost točk na zaslon |
| Izriši življenja | x, y, sprite | Izriši življenja kot ikone sličic |
| Izriši vrstico zdravja | x, y, width, height | Izriši vrstico zdravja na zaslon |

### Zvočne akcije

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Predvajaj zvok | sound, loop | Predvajaj zvočni učinek |
| Ustavi zvok | sound | Ustavi predvajajoč zvok |
| Predvajaj glasbo | music | Predvajaj glasbo v ozadju (pretočno) |
| Ustavi glasbo | (brez) | Ustavi glasbo v ozadju |
| Nastavi glasnost | sound, volume (0.0-1.0) | Prilagodi glasnost zvoka |

### Akcije nadzora toka

| Akcija | Parametri | Opis |
|--------|-----------|------|
| Če trk na | x, y, object_type | Preveri trk na položaju |
| Če lahko potisne | direction, object_type | Preverjanje potiskanja v slogu Sokoban |
| Nastavi spremenljivko | name, value, scope, relative | Nastavi vrednost spremenljivke |
| Testiraj spremenljivko | name, value, scope, operation | Primerjaj spremenljivko |
| Testiraj izraz | expression | Ovrednoti logični izraz |
| Preveri prazno | x, y, only_solid | Preveri, ali je položaj prost |
| Preveri trk | x, y, only_solid | Preveri trk na položaju |
| Začni blok | (brez) | Začni blok akcij (odpiralni oklepaj) |
| Končaj blok | (brez) | Končaj blok akcij (zapiralni oklepaj) |
| Sicer | (brez) | Označi vejo sicer pogojnega stavka |
| Ponovi | times | Ponovi naslednjo akcijo/blok N-krat |
| Zapusti dogodek | (brez) | Prenehaj izvajati preostale akcije |

### Obseg spremenljivk

Do spremenljivk lahko dostopate z uporabo obsežnih referenc:

| Obseg | Sintaksa | Opis |
|-------|----------|------|
| Lastni | `self.variable` ali samo `variable` | Spremenljivka trenutnega primerka |
| Drugi | `other.variable` | Drugi primerek v trku |
| Globalni | `global.variable` | Spremenljivka celotne igre |

Vgrajene spremenljivke primerka: `x`, `y`, `hspeed`, `vspeed`, `direction`, `speed`, `gravity`, `friction`, `visible`, `depth`, `image_index`, `image_speed`, `scale_x`, `scale_y`

---

## 12. Testiranje in zagon iger

### Hitri test (F5)

Pritisnite **F5** ali kliknite gumb **Testiraj**, da takoj zaženete svojo igro. Odpre se ločeno okno Pygame, ki prikazuje vašo igro.

- Pritisnite **Escape**, da ustavite igro in se vrnete v razvojno okolje
- Vrstica stanja razvojnega okolja prikazuje "Igra se izvaja...", medtem ko je igra aktivna

### Razhroščevalni način (F6)

Pritisnite **F6** za razhroščevalni način, ki prikazuje dodaten izpis v konzolo, vključno z:
- Beleženjem izvajanja dogodkov
- Podrobnostmi zaznavanja trkov
- Vrednostmi parametrov akcij
- Ustvarjanjem in uničenjem primerkov

### Vrstni red izvajanja igre

Vsak okvir sledi vrstnemu redu dogodkov GameMaker 7.0:

1. Dogodki **Začetni korak**
2. Odštevanje in sprožitev **alarmov**
3. Dogodki **Korak**
4. Vnosni dogodki **tipkovnice/miške**
5. **Gibanje** (fizika: gravitacija, trenje, hspeed/vspeed)
6. Zaznavanje **trkov** in dogodki
7. Dogodki **Končni korak**
8. Dogodki **Uniči** za označene primerke
9. Dogodki **Izriši** in upodabljanje

### Naslov okna

Naslov okna igre lahko prikazuje vrednosti točk, življenj in zdravja. To omogočite z nastavitvami prikaza naslova v nastavitvah projekta ali z uporabo akcij točk/življenj/zdravja.

---

## 13. Izvoz iger

### Izvoz HTML5

**Datoteka > Izvozi kot HTML5**

Ustvari eno samostojno HTML datoteko, ki se izvaja v kateremkoli spletnem brskalniku.

- Vse sličice so vdelane kot podatki base64
- Podatki igre so stisnjeni z gzip
- Pogon JavaScript skrbi za upodabljanje prek HTML5 Canvas
- Strežnik ni potreben - preprosto odprite datoteko v brskalniku

### Izvoz EXE (Windows)

**Datoteka > Izvozi projekt** ali **Gradnja > Izvozi igro**

Ustvari samostojno izvršljivo datoteko za Windows z uporabo PyInstaller.

**Zahteve:** PyInstaller in Kivy morata biti nameščena.

**Postopek:**
1. Generira igro na osnovi Kivy iz vašega projekta
2. Združi izvajalno okolje Python in vse odvisnosti
3. Ustvari eno datoteko EXE (lahko traja 5-10 minut)

**Možnosti:**
- Razhroščevalna konzola (prikaže terminalsko okno za razhroščevanje)
- Ikona po meri
- Stiskanje UPX (zmanjša velikost datoteke)

### Izvoz za mobilne naprave (Kivy)

**Datoteka > Izvozi za Kivy**

Generira projekt Kivy za mobilno namestitev.

**Izhod vključuje:**
- Kodo igre Python, prilagojeno za Kivy
- Paket sredstev, optimiziran za mobilne naprave
- Konfiguracijo `buildozer.spec` za gradnjo za Android/iOS

**Za gradnjo za Android:**
```bash
cd exported_project
buildozer android debug
```

### Izvoz ZIP

**Datoteka > Izvozi kot Zip**

Zapakira celoten projekt kot ZIP arhiv za deljenje ali varnostno kopijo. ZIP se lahko ponovno odpre z **Datoteka > Odpri Zip projekt**.

### Izvoz Aseba (robot Thymio)

Za projekte robota Thymio izvozi datoteke kode AESL, združljive z Aseba Studio.

---

## 14. Blockly vizualno programiranje

PyGameMaker integrira Google Blockly za vizualno programiranje z bloki kode.

### Nastavitev blokov

Odprite **Orodja > Nastavi akcijske bloke**, da prilagodite, kateri bloki so na voljo.

### Prednastavitve blokov

| Prednastavitev | Opis |
|----------------|------|
| Polna (vsi bloki) | Vseh 173 blokov omogočenih |
| Začetnik | Samo bistveni bloki (dogodki, osnovno gibanje, točke, sobe) |
| Srednji | Doda izrisovanje, več gibanja, življenja, zdravje, zvok |
| Platformska igra | Osredotočeno na fiziko: gravitacija, trenje, trki |
| RPG na mreži | Gibanje po mreži, zdravje, prehodi med sobami |
| Sokoban (uganka s škatlami) | Gibanje po mreži, mehanika potiskanja |
| Testiranje | Samo preverjeni bloki |
| Samo implementirani | Izključuje neimplementirane bloke |
| Urejevalnik kode | Za programiranje na osnovi besedila |
| Urejevalnik Blockly | Za razvoj z vizualnim pristopom |
| Po meri | Vaša lastna izbira |

### Kategorije blokov

Bloki so organizirani v barvno kodirane kategorije:

| Kategorija | Barva | Bloki |
|------------|-------|-------|
| Dogodki | Rumena | 13 blokov dogodkov |
| Gibanje | Modra | 14 blokov gibanja |
| Čas | Rdeča | Bloki časovnikov in alarmov |
| Izrisovanje | Vijolična | Izrisovanje oblik in besedila |
| Točke/Življenja/Zdravje | Zelena | Bloki sledenja točkam |
| Primerek | Roza | Ustvarjanje/uničenje primerkov |
| Soba | Rjava | Navigacija po sobah |
| Vrednosti | Temno modra | Spremenljivke in izrazi |
| Zvok | | Predvajanje zvoka |
| Izhod | | Sporočila in prikaz |

### Odvisnosti blokov

Nekateri bloki zahtevajo druge bloke za delovanje. Pogovorno okno za nastavitev prikazuje opozorila, ko odvisnosti manjkajo. Na primer, blok **Izriši točke** zahteva, da sta bloka **Nastavi točke** in **Dodaj k točkam** omogočena.

---

## 15. Podpora za robota Thymio

PyGameMaker vključuje podporo za izobraževalnega robota Thymio, kar vam omogoča simulacijo in programiranje robotov Thymio znotraj razvojnega okolja.

### Kaj je Thymio?

Thymio je majhen izobraževalni robot s senzorji, LED-diodami, motorji in gumbi. PyGameMaker lahko simulira vedenje robota Thymio in izvozi kodo za zagon na pravih robotih.

### Omogočanje Thymio

Pojdite v **Orodja > Programiranje Thymio > Prikaži zavihek Thymio v urejevalniku objektov**, da omogočite funkcionalnosti Thymio v urejevalniku objektov.

### Simulator Thymio

Simulator modelira fizičnega robota Thymio:

**Specifikacije:**
- Velikost robota: 110x110 slikovnih pik (11 cm x 11 cm)
- Medosna razdalja koles: 95 slikovnih pik
- Razpon hitrosti motorja: -500 do +500

### Senzorji Thymio

| Senzor | Število | Razpon | Opis |
|--------|---------|--------|------|
| Bližinski | 7 | 0-4000 | Vodoravni senzorji razdalje (doseg 10 cm) |
| Talni | 2 | 0-1023 | Zaznava svetle/temne površine |
| Gumbi | 5 | 0/1 | Naprej, nazaj, levo, desno, sredina |

### Dogodki Thymio

| Dogodek | Se sproži, ko |
|---------|----------------|
| Gumb naprej/nazaj/levo/desno/sredina | Je kapacitivni gumb pritisnjen |
| Katerikoli gumb | Se stanje kateregakoli gumba spremeni |
| Posodobitev bližinskih senzorjev | Se bližinski senzorji posodobijo (10 Hz) |
| Posodobitev talnih senzorjev | Se talni senzorji posodobijo (10 Hz) |
| Dotik | Pospeškometer zazna dotik/udarec |
| Zaznan zvok | Mikrofon zazna zvok |
| Časovnik 0/1 | Obdobje časovnika poteče |
| Zvok končan | Predvajanje zvoka se konča |
| Sporočilo prejeto | IR komunikacija prejeta |

### Akcije Thymio

**Nadzor motorja:**
- Nastavi hitrost motorja (levi, desni neodvisno)
- Premakni naprej / nazaj
- Obrni levo / desno
- Ustavi motorje

**Nadzor LED-diod:**
- Nastavi zgornjo LED (barva RGB)
- Nastavi spodnjo levo/desno LED
- Nastavi krožne LED (8 LED-diod po obodu)
- Izklopi vse LED-diode

**Zvok:**
- Predvajaj ton (frekvenca, trajanje)
- Predvajaj sistemski zvok
- Ustavi zvok

**Pogoji senzorjev:**
- Če bližinski (senzor, prag, primerjava)
- Če tlo temno / svetlo
- Če gumb pritisnjen / spuščen

**Časovnik:**
- Nastavi obdobje časovnika (časovnik 0 ali 1, obdobje v ms)

### Izvoz na pravega robota Thymio

1. Izvozite svoj projekt Thymio prek izvoznika Aseba
2. Odprite generirano datoteko `.aesl` v Aseba Studio
3. Povežite svojega robota Thymio prek USB
4. Kliknite **Naloži** in nato **Zaženi**

---

## 16. Nastavitve in možnosti

Odprite **Orodja > Možnosti**, da nastavite razvojno okolje.

### Zavihek Videz

| Nastavitev | Možnosti | Privzeto |
|------------|----------|----------|
| Velikost pisave | 8-24 pt | 10 |
| Družina pisave | System Default, Segoe UI, Arial, Ubuntu, Helvetica, SF Pro Text, Roboto | System Default |
| Tema | Default, Dark, Light | Default |
| Merilo vmesnika | 0,5x - 2,0x | 1,0x |
| Prikaži namige | Da/Ne | Da |

### Zavihek Urejevalnik

| Nastavitev | Možnosti | Privzeto |
|------------|----------|----------|
| Omogoči samodejno shranjevanje | Da/Ne | Da |
| Interval samodejnega shranjevanja | 1-30 minut | 5 min |
| Prikaži mrežo | Da/Ne | Da |
| Velikost mreže | 8-128 px | 32 |
| Pripni na mrežo | Da/Ne | Da |
| Prikaži trkovne okvirje | Da/Ne | Ne |

### Zavihek Projekt

| Nastavitev | Možnosti | Privzeto |
|------------|----------|----------|
| Privzeta mapa projektov | Pot | ~/PyGameMaker Projects |
| Omejitev nedavnih projektov | 5-50 | 10 |
| Ustvari varnostno kopijo ob shranjevanju | Da/Ne | Da |

### Zavihek Napredno

| Nastavitev | Možnosti | Privzeto |
|------------|----------|----------|
| Razhroščevalni način | Da/Ne | Ne |
| Prikaži izpis konzole | Da/Ne | Da |
| Največje število razveljavitev | 10-200 | 50 |

### Konfiguracijska datoteka

Nastavitve so shranjene v `~/.pygamemaker/config.json` in se ohranijo med sejami.

### Sprememba jezika

Pojdite v **Orodja > Jezik** in izberite želeni jezik.

**Podprti jeziki:**
- English
- Francais
- Espanol
- Deutsch
- Italiano
- Русский (Russian)
- Slovenscina (Slovenian)
- Українська (Ukrainian)

Vmesnik se takoj posodobi. Nekatere spremembe morda zahtevajo ponovni zagon razvojnega okolja.

---

## 17. Bližnjice na tipkovnici

### Globalne bližnjice

| Bližnjica | Dejanje |
|-----------|---------|
| Ctrl+N | Nov projekt |
| Ctrl+O | Odpri projekt |
| Ctrl+S | Shrani projekt |
| Ctrl+Shift+S | Shrani projekt kot |
| Ctrl+E | Izvozi projekt |
| Ctrl+Q | Zapri razvojno okolje |
| Ctrl+R | Ustvari sobo |
| F1 | Dokumentacija |
| F5 | Testiraj igro |
| F6 | Razhroščuj igro |
| F7 | Zgradi igro |
| F8 | Zgradi in zaženi |

### Bližnjice urejevalnika

| Bližnjica | Dejanje |
|-----------|---------|
| Ctrl+Z | Razveljavi |
| Ctrl+Y | Uveljavi |
| Ctrl+X | Izreži |
| Ctrl+C | Kopiraj |
| Ctrl+V | Prilepi |
| Ctrl+D | Podvoji |
| Ctrl+F | Najdi |
| Ctrl+H | Najdi in zamenjaj |
| Delete | Izbriši izbrano |

### Bližnjice urejevalnika sličic

| Bližnjica | Dejanje |
|-----------|---------|
| P | Orodje svinčnik |
| E | Orodje radirka |
| I | Izbirnik barve (kapalka) |
| G | Orodje za zalivanje (vedro) |
| L | Orodje za črte |
| R | Orodje za pravokotnike |
| O | Orodje za elipse |
| S | Orodje za izbiro |
| Ctrl+kolesce miške | Povečaj/pomanjšaj |

---

## 18. Vadnice

PyGameMaker vključuje vgrajene vadnice, ki vam pomagajo začeti. Dostopajte do njih iz **Pomoč > Vadnice** ali iz mape Vadnice v namestitvenem imeniku.

### Razpoložljive vadnice

| # | Vadnica | Opis |
|---|---------|------|
| 01 | Začetek | Uvod v razvojno okolje in prvi projekt |
| 02 | Prva igra | Ustvarjanje vaše prve igralne igre |
| 03 | Pong | Klasična igra Pong z loparjem in žogo |
| 04 | Breakout | Igra razbijanja opek v slogu Breakout |
| 05 | Sokoban | Uganka s potiskanjem škatel |
| 06 | Labirint | Igra navigacije po labirintu |
| 07 | Platformska igra | Stransko drseča platformska igra |
| 08 | Pristajalnik na Luni | Igra pristajanja na osnovi gravitacije |

Vadnice so na voljo v več jezikih (angleščina, nemščina, španščina, francoščina, italijanščina, ruščina, slovenščina, ukrajinščina).

---

## 19. Odpravljanje težav

### Igra se ne zažene (F5)

- Preverite, da ima vaš projekt vsaj eno sobo s primerki
- Preverite, da imajo objekti dodeljene sličice
- Poglejte izpis konzole (razhroščevalni način F6) za sporočila o napakah

### Sličice se ne prikazujejo

- Potrdite, da datoteka sličice obstaja v mapi `sprites/`
- Preverite, da ima objekt dodeljeno sličico v svojih lastnostih
- Preverite, da je primerek nastavljen na `visible = true`

### Trki ne delujejo

- Prepričajte se, da je ciljni objekt označen kot **Trden**, če uporabljate trke na osnovi trdnosti
- Preverite, da imate nastavljen dogodek **Trk z** za pravilen objekt
- Preverite, da se primerki dejansko prekrivajo (uporabite razhroščevalni način)

### Zvok se ne predvaja

- Preverite, da zvočna datoteka obstaja in je v podprtem formatu (WAV, OGG, MP3)
- Preverite, da se je pygame.mixer uspešno inicializiral (glejte izpis konzole)
- Glasbene datoteke se pretakajo z diska - prepričajte se, da je pot do datoteke pravilna

### Izvoz ne uspe

- **Izvoz EXE:** Prepričajte se, da je PyInstaller nameščen (`pip install pyinstaller`)
- **Izvoz Kivy:** Prepričajte se, da je Kivy nameščen (`pip install kivy`)
- **Izvoz HTML5:** Preverite konzolo za morebitne napake kodiranja
- Vsi izvozi zahtevajo veljaven projekt z vsaj eno sobo

### Težave z zmogljivostjo

- Zmanjšajte število primerkov v sobah
- Uporabite sistem trkov s prostorsko mrežo (privzeto omogočen)
- Izogibajte se zahtevnim operacijam v dogodkih Korak (izvajajo se 60-krat na sekundo)
- Za periodične naloge uporabite alarme namesto štetja okvirjev v Koraku

---

**PyGameMaker IDE** - Različica 1.0.0-rc.4
Copyright 2024-2025 Gabriel Thullen
Licencirano pod GNU General Public License v3 (GPLv3)
GitHub: https://github.com/Gabe1290/pythongm
