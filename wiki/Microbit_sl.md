# micro:bit (simulator BBC micro:bita)

*[Domov](Home_sl) | [Popolna referenca dejanj](Full-Action-Reference-Microbit-Actions_sl) | [Razširitve](Extensions_sl)*

---

PyGameMaker lahko v okno vaše igre postavi **simuliran BBC micro:bit**: zaslon
5×5 LED, gumba **A** in **B**, občutljiv logotip, priključke 0/1/2,
pospeškomer, tipala za svetlobo, temperaturo, kompas in zvok, zvočnik in radio —
vse narisano na zaslonu in programirano z istimi dogodki in dejanji kot preostali
del IDE-ja. Strojne opreme ne potrebujete. Omogoča ga vgrajena
[razširitev](Extensions_sl) **micro:bit**, ki je privzeto vklopljena.

Priloženi primer **`microbit_1`** (»Kocka in razpoloženja«) je popolna igra: A in
B prikažeta vesel in žalosten obraz, tresenje vrže kocko, dotik logotipa pa
premakne naprej število vaših metov.

---

## Prvi koraki

1. Ustvarite predmet, katerega **ime se začne z `microbit`** (na primer
   `microbit_1`), in v sobo postavite en njegov primerek. Ta predmet *je*
   micro:bit: pogon čezenj nariše ploščico in izvaja njegov simulator.
2. V **Nastavitve projekta → Razširitve** obkljukajte **micro:bit**. (Projekt, ki
   že uporablja dejanje micro:bita, ga ima vklopljenega samodejno; projekt, ki
   ga ne, nikoli ne vidi blokov ali dejanj micro:bita.)
3. Dogodke dajte **na isti predmet**: vsako dejanje micro:bita deluje na tisti
   micro:bit, ki ga izvaja. Na primer *Button A Pressed* → *Show Image* `HAPPY`.
4. **Testiraj igro.** Kliknite gumbe na ploščici.

Predmet lahko postane micro:bit tudi tako, da pri njegovem primerku v sobi
obkljukate `is_microbit`. Več micro:bitov v isti sobi je povsem v redu — prav to
naredi radio uporaben.

---

## Ploščica in kako jo upravljati

| Na zaslonu | Miška | Tipkovnica (neobvezno) |
|---|---|---|
| Gumb **A** / **B** | Klik (drži se, dokler je gumb miške pritisnjen) | `A` / `B` |
| **A+B** hkrati | Desni klik na enega od gumbov | drži `A` in `B` |
| Občutljiv **logotip** (zlat, nad zaslonom) | Klik | — |
| Priključki **0, 1, 2** (ploščice ob spodnjem robu) | Klik | — |
| **Ploskev nagiba** | Vleci; rob je en g, ob spustitvi se vrne v vodoravno lego | smerne tipke |
| Gumb **SHAKE** | Klik | `S` |
| Drsniki **Light / Temp / Compass / Sound** | Vleci; vrednost ostane | — |

Bližnjice na tipkovnici so **privzeto izklopljene**, da nikoli ne vzamejo tipk
vaše igre. Za ploščico jih vklopite z lastnostjo predmeta `microbit_keyboard`
(deluje tudi istoimenska spremenljivka primerka).

Druge lastnosti predmeta: `microbit_scale` (množitelj velikosti, privzeto
`1.0`, približno 220 px v širino) in `microbit_show_sensors` (nastavite na
`false`, da skrijete vrstico tipal). Če ima predmet **sprite**, služi kot telo
ploščice, čezenj pa se narišejo le LED-i in upravljalni elementi.

Klik na ploščico ne sproži še vaših lastnih dogodkov miške.

---

## Dejanja (kategorija **micro:bit**)

| Dejanje | Kaj naredi |
|---------|------------|
| **Show Image** (`microbit_show_image`) | Ime vgrajene slike (`HEART`, `HAPPY`, `SAD`, `YES`, `NO`, `ARROW_N`, `SKULL`… skupaj 64) ali pet vrstic s po petimi števkami svetlosti, na primer `09090:99999:99999:09990:00900`. |
| **Scroll Text** (`microbit_scroll_text`) | Pomakne besedilo čez zaslon (privzeto 150 ms na stolpec). |
| **Show Number** (`microbit_show_number`) | Ena števka obstane; daljše število se pomika. |
| **Set LED** (`microbit_set_pixel`) | Takoj prižge en LED: `x`, `y` od 0 do 4, svetlost 0–9. |
| **Clear Display** (`microbit_clear_display`) | Ugasne vse LED-e in zavrže vse, kar je čakalo v vrsti. |
| **Set Display Brightness** (`microbit_set_brightness`) | Splošna svetlost, 0–255. |
| **Play Tone** (`microbit_play_tone`) | Pisk s frekvenco za določeno število milisekund. |
| **Play Melody** (`microbit_play_melody`) | Ena od 21 vgrajenih melodij (`DADADADUM`, `ENTERTAINER`, `POWER_UP`…) ali vaše note: `"C4:4 E G C5:8 R:4"` (nota, oktava, `:dolžina`; `R` je pavza). |
| **Stop Sound** (`microbit_stop_sound`) | Utiša zvočnik in zavrže zvoke v vrsti. |
| **Set Radio Group** (`microbit_radio_set_group`) | Izbere radijsko skupino, 0–255. |
| **Send Radio Message** (`microbit_radio_send`) | Pošlje število ali besedilo drugim micro:bitom v skupini. |
| **Read Sensor** (`microbit_read_sensor`) | Odčitek (pospeškomer x/y/z, jakost, kompas, svetloba, temperatura, raven zvoka, analogni priključek 0–2) zapiše v spremenljivko — ali v globalno spremenljivko, če se ime začne z `global.`. |
| **If Button Pressed** (`microbit_if_button`) | Pogoj: A, B, A+B ali logotip so pridržani. |
| **If Gesture** (`microbit_if_gesture`) | Pogoj: ploščica je v kretnji ali legi (`shake`, `up`, `down`, `left`, `right`, `face up`, `face down`, `freefall`, `2g`…`8g`). |
| **If Tilt** (`microbit_if_tilt`) | Pogoj: primerja os pospeškomera (v mili-g) z vrednostjo. |
| **If LED Brightness** (`microbit_if_pixel`) | Pogoj: primerja svetlost enega LED-a z vrednostjo. |

Pogoji varujejo dejanje ali blok, ki jim sledi, v slogu GameMakerja. Vse
parametre najdete v
[Popolni referenci dejanj](Full-Action-Reference-Microbit-Actions_sl).

> **Besedilo gre v dvojne narekovaje.** `Scroll Text` in `Send Radio Message`
> prebereta vrednost kot vsak drug izraz, zato je `Score - 3` računanje.
> Dobesedno besedilo zapišite kot `"Živjo"`. Zaslon ima le izpisljivi ASCII;
> črke z diakritičnimi znamenji (č, š, ž …) se prikažejo kot `?`, tako kot na
> pravi ploščici.

---

## Dogodki

Sprožijo se na predmetu samega micro:bita:

| Dogodek | Sproži se, ko |
|---------|---------------|
| **Button A Pressed**, **Button B Pressed**, **Buttons A+B Pressed** | Pritisnete gumb(e). |
| **Logo Touched** | Se dotaknete logotipa. |
| **Pin 0 / 1 / 2 Touched** | Se dotaknete tega priključka. |
| **Shake**, **Logo Up**, **Logo Down**, **Tilt Left**, **Tilt Right**, **Screen Up**, **Screen Down**, **Free Fall**, **2g / 3g / 6g / 8g Impact** | Ploščica zazna to kretnjo (isti algoritem kot pri pravem micro:bitu). |
| **Loud Sound** / **Quiet Sound** | Raven mikrofona prečka prag glasnega / tihega zvoka. |
| **Display Finished** | Je vrsta zaslona vse predvajala. |
| **Sound Finished** | So vsi toni in melodije v vrsti predvajani. |
| **Radio Message Received** | Je drug micro:bit v isti skupini poslal sporočilo. |

»Forever« je navadni dogodek **Step**.

### Radio

Vsaka ploščica se začne v skupini 0. **Send Radio Message** dostavi sporočilo
vsakemu *drugemu* micro:bitu v isti skupini (ploščica nikoli ne sliši same sebe,
druga skupina pa ne sliši ničesar). Prejemnik dobi dogodek in dve spremenljivki:
`radio_number` (0, če besedilo ni število) in `radio_string` (vedno besedilo).
Besedilo se skrajša na 32 znakov, kot pri pravem radiu.

---

## Čas: vrsta zaslona in zvoka

Na pravem micro:bitu pomikanje besedila program *blokira*. Igra se ne sme
blokirati, zato se dejanja zaslona **postavijo v vrsto** in se predvajajo drugo za
drugim (največ 16; zahteva po tem, kar je že prikazano, ne naredi ničesar).
**Clear Display** vrsto izprazni, **Display Finished** pa sporoči, kdaj se je
izpraznila, tako da lahko animacije povezujete v verigo. Zvoki se v vrsto postavijo enako, s
**Stop Sound** in **Sound Finished**.

Zvok je pravokotni val, kot pri brenčalu ploščice. Če računalnik nima zvočne
naprave, se zvok tiho preskoči (simulator ga vseeno spremlja).

---

## Izvozi

**Namizni** izvoz (Windows, Linux, macOS) zapakira pravi pogon, zato micro:bit
deluje popolnoma enako kot v »Testiraj igro«. Tudi izvoz **HTML5** ima
simulator: ploščica in vrstica tipal se narišeta v brskalniku, gumbe, logotip in
priključke lahko kliknete ali se jih dotaknete, ploskev nagiba in drsnike
vlečete, zvočnik pa piska (brskalniki dovolijo zvok šele po prvem kliku ali
pritisku tipke). Tudi izvoz **Android/Kivy** ga ima: ploščica in vrstica tipal
se narišeta (v poenostavljeni podobi, z oglatimi vogali), dotaknete se lahko
gumbov, logotipa, priključkov, ploskve nagiba, gumba za tresenje in drsnikov,
dogodki se sprožijo, zvočnik pa predvaja svoje note. Bližnjice na tipkovnici
delujejo le za ploščico, pri kateri je vklopljena lastnost (ali spremenljivka)
`microbit_keyboard`. Ploščico prepoznamo po imenu njenega predmeta (mora se
začeti z `microbit`) ali po `is_microbit` pri njenem primerku v sobi.

---

## Izvoz v MicroPython (na pravi micro:bit)

To je izvoz druge vrste. Namesto igre za drug računalnik pretvori program vaših
predmetov micro:bit v pravo kodo **MicroPython**, ki teče na fizični ploščici.

1. Odprite **Datoteka → Izvozi kodo micro:bit (MicroPython)...** (projekt mora
   biti odprt).
2. Povejte, katero ploščico imate: **V2 (2020 ali novejša)**, **V1 (izvirna,
   2016-2020)** ali **Obe (ena datoteka .hex za plošči V1 in V2)**.
3. Izberite mapo. Vsak predmet micro:bit dobi svoj program,
   `<mapa>/<ime predmeta>/main.py`.
4. Če je bil izvožen natanko en predmet, IDE ponudi dva načina, kako ga dati na
   ploščico. **Kopirati na micro:bit?** kopira `main.py` na ploščico, ki je prek
   USB priključena in že poganja MicroPython (program se nato zažene sam).
   **Ustvariti datoteko .hex, pripravljeno za nalaganje?** naredi datoteko
   `.hex`, ki jo povlečete na USB-pogon **MICROBIT** ploščice — to deluje tudi
   na novi ploščici, ki še nikoli ni poganjala MicroPythona.

Prevedena so vsa dejanja in pogoji micro:bita, pa tudi *Set Variable*, *Test
Variable*, bloki in komentarji. Vsak dogodek postane preverjanje znotraj ene
same zanke. Igralna dejanja, ki na ploščici ne pomenijo nič (sobe, spriti,
točke …), se ne izvozijo. V izrazih delujejo `irandom`, `random` in `choose`;
druge funkcije GameMakerja se ne prevedejo.

Pogovorno okno izvoza našteje, česar ni bilo mogoče izvoziti:

- **Display Finished** in **Sound Finished** (klici zaslona in zvoka na
  ploščici že sami počakajo do konca).
- Na ploščici V1 tisto, kar potrebuje V2: branje ravni zvoka, občutljivi
  logotip (*If Button Pressed* z logotipom, **Logo Touched**) in dogodka
  **Loud Sound** / **Quiet Sound**.
- Vse drugo, kar nima ustreznice v MicroPythonu.

**Velikost:** program mora stati v 8.187 bajtov na ploščici V1 in v 20.150
bajtov na V2. **Obe** naredi eno samo datoteko Universal Hex, zato jo omejuje
velikost V1 in se izvozi po pravilih V1.

> Datoteke `.hex` so preverjene z resnično strojno programsko opremo micro:bita,
> vendar še ne na fizični ploščici.

---

## Kaj sledi

- V zavihku dobrodošlice odprite primer **`microbit_1`** in preberite njegov
  vodnik.
- Preizkusite dve ploščici v isti sobi, vsako s svojim *Set Radio Group*, in
  pošljite sporočilo s tipke.
- Načrtovano: neposredna povezava s pravim micro:bitom prek USB. Zaenkrat še ni
  na voljo.

Glej tudi: [Razširitve](Extensions_sl), [Popolna referenca dejanj](Full-Action-Reference-Microbit-Actions_sl), [Referenca dogodkov](Event-Reference_sl).
