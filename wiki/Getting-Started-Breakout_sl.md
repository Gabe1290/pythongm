# Uvod v Ustvarjanje Videoiger s PyGameMaker

*[Home_sl](Home_sl) | [Beginner-Preset_sl](Beginner-Preset_sl) | [English](Getting-Started-Breakout) | [Français](Getting-Started-Breakout_fr)*

**Ekipa PyGameMaker**

---

V tem vodiču se bomo naučili osnov ustvarjanja iger s PyGameMaker. Ker gre za dokaj obsežno programsko opremo z veliko funkcijami, se bomo osredotočili le na tiste, ki nam bodo pomagale med tem vodičem.

Ustvarili bomo preprosto igro v slogu Breakout, ki bo videti takole:

![Koncept igre Breakout](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

Ta vodič je namenjen tudi vam, če nimate nobenega znanja programiranja, saj PyGameMaker omogoča začetnikom enostavno ustvarjanje iger ne glede na njihovo raven znanja.

V redu, začnimo z načrtovanjem naše igre!

---

## Korak 1: Začetek

Začnite z odprtjem PyGameMaker. Videli bi morali glavni vmesnik s plosčo **Sredstva** na levi strani, ki navaja različne kategorije virov: Sprites, Sounds, Backgrounds, Fonts, Objects in Rooms.

Preden karkoli naredimo, v videoigri igralec najprej opazi, kaj vidi na zaslonu. To je pravzaprav temelj igre: igra brez grafike ne obstaja (ali pa gre za zelo poseben primer). Zato bomo začeli z vstavljanjem slik v našo igro, ki bodo grafična predstavitev objektov, ki jih bo igralec videl na zaslonu. V terminologiji razvoja iger se te slike imenujejo **Sprite-i**.

---

## Korak 2: Ustvarjanje Sprite-ov

### 2.1 Ustvarjanje Sprite-a Loparja

1. Z desno miškino tipko kliknite na mapo **Sprites** na vrhu levega stolpca
2. Kliknite na **Create Sprite**
3. Odprlo se bo okno z imenom **Sprite Properties** - tukaj boste določili vse lastnosti vašega sprite-a
4. Uporabite vgrajeni urejevalnik za risanje vodoravnega pravokotnika (približno 64x16 slikovnih pik) v barvi, ki vam je všeč
5. **Pomembno:** Kliknite **Center** za nastavitev izhodišča na sredino vašega sprite-a
   > Izhodišče sprite-a je njegova središčna točka, njegove koordinate X:0 in Y:0. To so njegove osnovne koordinate.
6. Spremenite ime vašega sprite-a z uporabo besedilnega polja na vrhu in vnesite `spr_paddle`
   > To nima tehničnega vpliva - služi le za lažje navigiranje po datotekah, ko jih boste imeli več. Izberete lahko katero koli ime; to je le primer.
7. Kliknite **OK**

Pravkar ste ustvarili svoj prvi sprite! To je vaš lopar, objekt, ki ga bo igralec upravljal za lovljenje žoge.

### 2.2 Ustvarjanje Sprite-a Žoge

Nadaljujmo in dodajmo več sprite-ov. Ponovite enak postopek:

1. Z desno tipko kliknite na **Sprites** → **Create Sprite**
2. Narišite majhen krog (približno 16x16 slikovnih pik)
3. Kliknite **Center** za nastavitev izhodišča
4. Poimenujte ga `spr_ball`
5. Kliknite **OK**

### 2.3 Ustvarjanje Sprite-ov Opek

Potrebujemo tri vrste opek. Ustvarite jih eno za drugo:

**Prva Opeka (Uničljiva):**
1. Ustvarite nov sprite
2. Narišite pravokotnik (približno 48x24 slikovnih pik) - uporabite živo barvo, kot je rdeča
3. Kliknite **Center**, poimenujte ga `spr_brick_1`
4. Kliknite **OK**

**Druga Opeka (Uničljiva):**
1. Ustvarite nov sprite
2. Narišite pravokotnik (enake velikosti) - uporabite drugo barvo, kot je modra
3. Kliknite **Center**, poimenujte ga `spr_brick_2`
4. Kliknite **OK**

**Tretja Opeka (Neuničljiva Stena):**
1. Ustvarite nov sprite
2. Narišite pravokotnik (enake velikosti) - uporabite temnejšo barvo, kot je siva
3. Kliknite **Center**, poimenujte ga `spr_brick_3`
4. Kliknite **OK**

Zdaj bi morali imeti vse sprite-e za našo igro:
- `spr_paddle` - Igralčev lopar
- `spr_ball` - Odbijajoča žoga
- `spr_brick_1` - Prva uničljiva opeka
- `spr_brick_2` - Druga uničljiva opeka
- `spr_brick_3` - Neuničljiva opeka stene

> **Opomba:** V igrah sta na splošno dva glavna vira grafičnega upodabljanja: **Sprite-i** in **Ozadja**. To je vse, kar sestavlja tisto, kar vidite na zaslonu. Ozadje je, kot pove že ime, slika v ozadju.

---

## Korak 3: Razumevanje Objektov in Dogodkov

Kaj smo rekli na začetku? Prva stvar, ki jo igralec opazi, je tisto, kar vidi na zaslonu. Za to smo poskrbeli z našimi sprite-i. Ampak igra, sestavljena samo iz slik, ni igra - to je slika! Zdaj bomo prešli na naslednjo stopnjo: **Objekte**.

Objekt je entiteta v vaši igri, ki ima lahko vedenja, se odziva na dogodke in komunicira z drugimi objekti. Sprite je le vizualna predstavitev; objekt je tisto, kar mu daje življenje.

### Kako Deluje Logika Igre

Vse v programiranju iger sledi temu vzorcu: **Če se to zgodi, potem izvršim tisto.**

- Če igralec pritisne tipko, potem naredim to
- Če je ta spremenljivka enaka tej vrednosti, potem naredim tisto
- Če se dva objekta zaletita, potem se nekaj zgodi

Temu v PyGameMaker pravimo **Dogodki** in **Akcije**:
- **Dogodki** = Stvari, ki se lahko zgodijo (pritisk tipke, trčenje, časovnik itd.)
- **Akcije** = Stvari, ki jih želite narediti, ko se zgodijo dogodki (premik, uničenje, sprememba rezultata itd.)

---

## Korak 4: Ustvarjanje Objekta Loparja

Ustvarimo objekt, ki ga bo igralec upravljal: lopar.

### 4.1 Ustvarite Objekt

1. Z desno tipko kliknite na mapo **Objects** → **Create Object**
2. Poimenujte ga `obj_paddle`
3. V spustnem meniju **Sprite** izberite `spr_paddle` - zdaj ima naš objekt vizualni izgled!
4. Označite potrditveno polje **Solid** (to bomo potrebovali za trčenja)

### 4.2 Programiranje Gibanja

V igri Breakout moramo premikati lopar, da preprečimo žogi pobeg na dnu. Upravljali ga bomo s tipkovnico.

**Premikanje Desno:**
1. Kliknite **Add Event** → **Keyboard** → **Right Arrow**
2. Iz plošče akcij na desni dodajte akcijo **Set Horizontal Speed**
3. Nastavite **vrednost** na `5`
4. Kliknite **OK**

To pomeni: "Ko je pritisnjena tipka Puščica desno, nastavi vodoravno hitrost na 5 (premikanje desno)."

**Premikanje Levo:**
1. Kliknite **Add Event** → **Keyboard** → **Left Arrow**
2. Dodajte akcijo **Set Horizontal Speed**
3. Nastavite **vrednost** na `-5`
4. Kliknite **OK**

**Ustavljanje ob Sprostitvi Tipk:**

Če zdaj testiramo, bi se lopar še naprej premikal tudi po sprostitvi tipke! Popravimo to:

1. Kliknite **Add Event** → **Keyboard Release** → **Right Arrow**
2. Dodajte akcijo **Set Horizontal Speed** z vrednostjo `0`
3. Kliknite **OK**

4. Kliknite **Add Event** → **Keyboard Release** → **Left Arrow**
5. Dodajte akcijo **Set Horizontal Speed** z vrednostjo `0`
6. Kliknite **OK**

Zdaj se naš lopar premika, ko so tipke pritisnjene, in se ustavi, ko so sproščene. S tem objektom smo za zdaj končali!

---

## Korak 5: Ustvarjanje Objekta Opeke Stene

Ustvarimo neuničljivo opeko stene - ta bo tvorila meje našega igralnega področja.

1. Ustvarite nov objekt z imenom `obj_brick_3`
2. Dodelite sprite `spr_brick_3`
3. Označite potrditveno polje **Solid**

Žoga se bo odbijala od te opeke. Ker je le stena, ne potrebujemo nobenih dogodkov - le trdna mora biti. Kliknite **OK** za shranjevanje.

---

## Korak 6: Ustvarjanje Objekta Žoge

Zdaj ustvarimo žogo, bistveni element naše igre.

### 6.1 Ustvarite Objekt

1. Ustvarite nov objekt z imenom `obj_ball`
2. Dodelite sprite `spr_ball`
3. Označite potrditveno polje **Solid**

### 6.2 Začetno Gibanje

Želimo, da se žoga premika sama od začetka. Dajmo ji začetno hitrost in smer.

1. Kliknite **Add Event** → **Create**
   > Dogodek Create izvrši akcije, ko se objekt pojavi v igri, torej ko vstopi na prizorišče.
2. Dodajte akcijo **Set Horizontal Speed** z vrednostjo `4`
3. Dodajte akcijo **Set Vertical Speed** z vrednostjo `-4`
4. Kliknite **OK**

To da žogi diagonalno gibanje (desno in gor) na začetku igre.

### 6.3 Odbijanje od Loparja

Potrebujemo, da se žoga odbije, ko zadene lopar.

1. Kliknite **Add Event** → **Collision** → izberite `obj_paddle`
   > Ta dogodek se sproži, ko se žoga zaleti v lopar.
2. Dodajte akcijo **Reverse Vertical**
   > Ta obrne navpično smer, kar povzroči odboj žoge.
3. Kliknite **OK**

### 6.4 Odbijanje od Sten

Enaka operacija za opeke sten:

1. Kliknite **Add Event** → **Collision** → izberite `obj_brick_3`
2. Dodajte akcijo **Reverse Vertical**
3. Dodajte akcijo **Reverse Horizontal**
   > Dodamo obe, ker lahko žoga zadene steno iz različnih kotov.
4. Kliknite **OK**

---

## Korak 7: Testiranje Našega Napredka - Ustvarjanje Sobe

Po Sprite-ih in Objektih prihajajo **Sobe**. Soba je, kjer se igra dogaja: to je zemljevid, nivo. Tukaj postavite vse elemente igre, kjer organizirate, kaj se bo prikazalo na zaslonu.

### 7.1 Ustvarite Sobo

1. Z desno tipko kliknite na **Rooms** → **Create Room**
2. Poimenujte jo `room_game`

### 7.2 Postavite Svoje Objekte

Zdaj postavite svoje objekte z uporabo miške:
- **Levi klik** za postavitev objekta
- **Desni klik** za brisanje objekta

Izberite objekt za postavitev iz spustnega menija v urejevalniku sobe.

**Zgradite svoj nivo:**
1. Postavite instance `obj_brick_3` okrog robov (zgoraj, levo, desno) - dno pustite odprto!
2. Postavite `obj_paddle` na sredino spodaj
3. Postavite `obj_ball` nekam na sredino

### 7.3 Testirajte Igro!

Kliknite gumb **Play** (zelena puščica) v orodni vrstici. To vam omogoča testiranje igre kadarkoli.

Že se lahko zabavate z odbijanjem žoge od sten in loparja!

Minimalno je, ampak že dober začetek - imate temelje svoje igre!

---

## Korak 8: Dodajanje Uničljivih Opek

Dodajmo nekaj opek za razbijanje, da bo naša igra bolj zabavna.

### 8.1 Prva Uničljiva Opeka

1. Ustvarite nov objekt z imenom `obj_brick_1`
2. Dodelite sprite `spr_brick_1`
3. Označite **Solid**

Dodali bomo vedenje za samouničenje ob zadetku žoge:

1. Kliknite **Add Event** → **Collision** → izberite `obj_ball`
2. Dodajte akcijo **Destroy Instance** s ciljem **self**
   > Ta akcija odstrani objekt med igro - tukaj opeko samo.
3. Kliknite **OK**

In tako hitro imate svojo novo uničljivo opeko!

### 8.2 Druga Uničljiva Opeka (Z Uporabo Starša)

Zdaj bomo ustvarili drugo uničljivo opeko, vendar brez potrebe po ponovnem programiranju. Naredili jo bomo "klon" z uporabo funkcije **Starš**.

1. Ustvarite nov objekt z imenom `obj_brick_2`
2. Dodelite sprite `spr_brick_2`
3. Označite **Solid**
4. V spustnem meniju **Parent** izberite `obj_brick_1`

Kaj to pomeni? Preprosto, da bo tisto, kar smo programirali v `obj_brick_1`, podedovano s strani `obj_brick_2`, brez da bi to morali sami reproducirati. Razmerje starš-otrok omogoča objektom deljenje vedenj!

Kliknite **OK** za shranjevanje.

### 8.3 Poskrbite, da se Žoga Odbija od Novih Opek

Znova odprite `obj_ball` z dvojnim klikom nanj in dodajte dogodke trčenja za naše nove opeke:

1. Kliknite **Add Event** → **Collision** → izberite `obj_brick_1`
2. Dodajte akcijo **Reverse Vertical**
3. Kliknite **OK**

4. Kliknite **Add Event** → **Collision** → izberite `obj_brick_2`
5. Dodajte akcijo **Reverse Vertical**
6. Kliknite **OK**

---

## Korak 9: Konec Igre - Ponovni Zagon Sobe

Moramo ponovno zagnati nivo, če žoga pobegne z zaslona (če jo igralec ne ujame).

V `obj_ball`:

1. Kliknite **Add Event** → **Other** → **Outside Room**
2. Dodajte akcijo **Restart Room**
   > Ta akcija ponovno zažene trenutno sobo med igro.
3. Kliknite **OK**

---

## Korak 10: Končno Oblikovanje Nivoja

Zdaj postavite vse v svojo sobo za ustvaritev končnega Breakout nivoja:

1. Odprite `room_game`
2. Razporedite stene `obj_brick_3` okrog vrha in strani
3. Postavite vrste `obj_brick_1` in `obj_brick_2` v vzorce na vrhu
4. Ohranite `obj_paddle` na sredini spodaj
5. Postavite `obj_ball` nad lopar

**Primer razporeditve:**
```
[3][3][3][3][3][3][3][3][3][3]
[3][1][1][2][2][1][1][2][2][3]
[3][2][2][1][1][2][2][1][1][3]
[3][1][1][2][2][1][1][2][2][3]
[3]                        [3]
[3]                        [3]
[3]         (žoga)         [3]
[3]                        [3]
[3]        [lopar]         [3]
```

---

## Čestitke!

Vaša igra Breakout je dokončana! Zdaj lahko uživate v svojem delu z igranjem igre, ki ste jo pravkar ustvarili!

Lahko jo tudi še izboljšate, na primer z dodajanjem:
- **Zvočnih učinkov** za odbijanje in uničenje opek
- **Sledenja rezultatu** z uporabo akcije Add Score
- **Dodatnih vrst opek** z različnimi vedenji
- **Več nivojev** z različnimi razporeditvami

---

## Povzetek Naučenega

| Koncept | Opis |
|---------|------|
| **Sprite-i** | Vizualne slike, ki predstavljajo objekte v vaši igri |
| **Objekti** | Entitete igre z vedenji, ki združujejo sprite-e z dogodki in akcijami |
| **Dogodki** | Sprožilci, ki izvršijo akcije (Create, Keyboard, Collision itd.) |
| **Akcije** | Operacije za izvajanje (Move, Destroy, Bounce itd.) |
| **Solid** | Lastnost, ki omogoča zaznavanje trčenj |
| **Starš** | Omogoča objektom dedovanje vedenj od drugih objektov |
| **Sobe** | Nivoji igre, kjer postavljate instance objektov |

---

## Povzetek Objektov

| Objekt | Sprite | Solid | Dogodki |
|--------|--------|-------|---------|
| `obj_paddle` | `spr_paddle` | Da | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Da | Create, Collision (lopar, opeke), Outside Room |
| `obj_brick_1` | `spr_brick_1` | Da | Collision (žoga) - Uniči sebe |
| `obj_brick_2` | `spr_brick_2` | Da | Podeduje od `obj_brick_1` |
| `obj_brick_3` | `spr_brick_3` | Da | Brez (le stena) |

---

## Glejte Tudi

- [Beginner-Preset_sl](Beginner-Preset_sl) - Dogodki in akcije, ki so na voljo za začetnike
- [Event-Reference_sl](Event-Reference_sl) - Popoln seznam vseh dogodkov
- [Full-Action-Reference_sl](Full-Action-Reference_sl) - Popoln seznam vseh akcij
- [Tutorial-Breakout_sl](Tutorial-Breakout_sl) - Krajša verzija tega vodiča

---

Zdaj ste uvedeni v osnove ustvarjanja videoiger s PyGameMaker. Zdaj je na vrsti, da ustvarite svoje lastne igre!
