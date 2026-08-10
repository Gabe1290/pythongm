# Vizualno programiranje

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Nazaj na začetno stran](Home_sl)

PyGameMaker vključuje Google Blockly za vizualno programiranje s povleci in spusti. Igralno logiko gradite s povezovanjem blokov, namesto s pisanjem kode.

---

## Dostop do Blockly

1. Odprite objekt v Object Editorju
2. Kliknite na zavihek **🧩 Blockly** (poleg Event List in Urejevalnika Kode)
3. Prikaže se delovno področje Blockly z orodno vrstico na levi

![Zavihki Event List / Blockly / Urejevalnik Kode Urejevalnika Objektov
— klik na Blockly preklopi akcije istega dogodka v pogled blokov
povleci-in-spusti](images/object-editor.png)

*(Delovno področje Blockly samo je spletna komponenta in tukaj ni
zajeto s posnetkom zaslona — glejte [[Code-Editor_sl|Urejevalnik Kode]]
za izgled ustrezne generirane Python kode za isti dogodek.)*

**Kateri bloki so vidni, je odvisno od vaše prednastavitve.**
`Tools > Configure Action Blocks...` (ali `Preferences > IDE Edition`,
ki določa privzeto prednastavitev za nove projekte) nadzoruje nabor
blokov — za podrobnosti glejte [Vodnik po
Prednastavitvah](Preset-Guide_sl). Spodnje tabele naštevajo vse bloke,
ki obstajajo v katerikoli prednastavitvi; konkreten projekt jih lahko
prikaže manj.

---

## Delovno Področje Blockly

### Orodna Vrstica
Levi panel vsebuje kategorije blokov:
- **Events** - Bloki sprožilcev dogodkov
- **Control** - Pogoji, spremenljivke in združevanje (pogojni bloki
  tega projekta so bloki za zlaganje, ne klasični vsebniki If/Else —
  glejte "Vrste Blokov" spodaj)
- **Movement** - Bloki za gibanje, hitrost in fiziko
- **Timing** - Alarmi
- **Drawing** - Bloki za besedilo in oblike
- **Score/Lives/Health** - Bloki stanja igre
- **Instance** - Ustvarjanje/uničevanje objektov
- **Room** - Navigacija med sobami
- **Values** - Vrednostni bloki (položaj, hitrost, rezultat, življenja,
  zdravje, miška)
- **Sound** - Predvajanje zvoka
- **Output** - Sporočila in prilagojena Python koda
- **Game** - Zaključi/ponastavi igro, lestvica najboljših

Ločene kategorije Math, Text ali Logic ni — numerična/besedilna polja
se izpolnijo neposredno na vsakem bloku, ravno tako ne obstaja
generičen logični/primerjalni vrednostni blok. Glejte "Vrste Blokov"
spodaj, kako namesto tega delujejo pogoji.

### Delovna Površina
Osrednje območje, kjer gradite svoj program:
- S povlekom blokov iz orodne vrstice
- S povezovanjem blokov med seboj
- Z nastavljanjem parametrov blokov

### Koš
Povlecite neželene bloke sem, da jih izbrišete, ali pritisnite tipko Delete.

---

## Vrste Blokov

### Bloki s Klobukom (Events)
Bloki s klobukom imajo zaobljen vrh in začnejo zaporedje. Predstavljajo dogodke:

```
┌─────────────────┐
│ When Create     │
└─────────────────┘
```

### Bloki za Zlaganje (Akcije)
Bloki za zlaganje imajo zareze, ki se povežejo z drugimi bloki. Skoraj
vsi bloki zunaj kategorije Values so bloki za zlaganje — vključno s
pogojnimi bloki:

```
├─────────────────┤
│ Set Horizontal Speed [5] │
├─────────────────┤
```

### Vrednostni Bloki (Values)
Vrednostni bloki so zaobljeni in se vstavijo v numerično polje
drugega bloka (npr. polje hitrosti Move Direction ali polje vrednosti
Set Variable). Ta projekt jih ima 9 — X Position, Y Position,
Horizontal Speed, Vertical Speed, Score, Lives, Health, Mouse X,
Mouse Y:

```
( X Position )    ( Score )    ( 100 )
```

Generičnega vrednostnega bloka `( speed )` ali `( direction )` ni —
teh konceptov ta pogon ne sledi kot enotno vrednost (hitrost/smer
gibanja izhajata skupaj iz Horizontal Speed + Vertical Speed), prav
tako ne obstaja vrednostni blok za prilagojene spremenljivke
(preberite jih namesto tega prek primerjave Test Variable).

### Pogoji — bloki za zlaganje, ne vsebniki v obliki C
Za razliko od vizualnih jezikov v slogu Scratch so bloki If Condition /
Test Variable tega projekta **bloki za zlaganje z enim samim slotom
"then"**, ne dvostranski vsebniki If/Else, prav tako ne obstaja
šesterokotni logični blok za vstavljanje — primerjava se gradi
neposredno prek polj na bloku:

```
┌───────────────────────────────────┐
│ If count of [obj_coin] [==] [0]   │
├───────────────────────────────────┤
│  then [akcije tukaj]              │
└───────────────────────────────────┘
```

Za dodajanje veje "else" ali izvajanje več akcij na eni strani ga
kombinirajte s še tremi bloki Control:
- **Else** - izvede svoj naslednji blok samo, če je bil prejšnji test neresničen
- **Start Block** / **End Block** - združita več akcij, tako da
  prejšnji test (ali Else) deluje na celotno skupino, ne le na
  naslednji blok

To je isti ravni, GM80-slogovni pogojni potek, ki ga uporablja tudi
strukturirani panel Events/Actions (glejte [Dogodki in
Akcije](Dogodki_in_Akcije_sl)) — Blockly je vmesnik za povleci in
spusti nad istim osnovnim seznamom akcij, ne ločen model izvajanja.

---

## Bloki Dogodkov

### Dogodek Create
```
┌─────────────────────┐
│ When Create         │
├─────────────────────┤
│ [akcije tukaj]        │
└─────────────────────┘
```

### Dogodek Step
```
┌─────────────────────┐
│ When Step            │
├─────────────────────┤
│ [vsako sličico]        │
└─────────────────────┘
```

### Dogodki Tipkovnice
Obstajajo štirje ločeni bloki s klobukom za tipkovnico — Held, Press,
Release in No Key — vsak z spustnim menijem za ime tipke (No Key ga
nima, ker se sproži, ko ni ničesar pritisnjenega):
```
┌─────────────────────────┐
│ When key [held: left] ▼ │
├─────────────────────────┤
│ [akcije tukaj]             │
└─────────────────────────┘
```

### Dogodki Trkov
```
┌────────────────────────────┐
│ When colliding with [obj] ▼│
├────────────────────────────┤
│ [akcije tukaj]                │
└────────────────────────────┘
```

---

## Bloki za Gibanje

| Blok | Opis |
|------|-------------|
| `Set Horizontal Speed [4]` | Nastavi hitrost X |
| `Set Vertical Speed [-5]` | Nastavi hitrost Y |
| `Stop Movement` | Izniči obe hitrosti |
| `Move [direction ▼] speed [3]` | Premik v eno od 4 smeri (ali diagonale, ali "stop") |
| `Move Free [direction] [speed]` | Premik s poljubnim kotom in hitrostjo |
| `Set Speed [5]` | Nastavi velikost hitrosti, ohrani trenutno smer |
| `Set Direction [90]` | Nastavi kot smeri, ohrani trenutno hitrost |
| `Move Towards x:[100] y:[200] speed:[3]` | Premik proti točki |
| `Snap to Grid` | Poravna položaj na mrežo |
| `Jump to Position x:[100] y:[200]` | Trenutni teleport |
| `Move Grid [direction]` | Premik natanko za eno celico mreže |
| `Stop if No Keys` / `Check Keys and Move` / `If On Grid` | Pomožni bloki za gibanje po mreži |
| `Set Gravity` | Vsako sličico uporabi konstantno silo (navzdol ali v poljubno smer) |
| `Set Friction` | Vsako sličico zmanjša hitrost |
| `Reverse Horizontal` / `Reverse Vertical` | Obrne smer X ali Y |
| `Bounce` | Odbije od trdnih objektov |
| `Wrap Around Room` | Ponovno se pojavi na nasprotni strani |
| `Move to Contact` | Premik do stika z nečim |

Bloka "Jump to Start Position" ali "Jump to Random Position" ni — ti
dve akciji obstajata samo v strukturiranem panelu, ne v Blockly.

---

## Bloki za Risanje

| Blok | Opis |
|------|-------------|
| `Draw Text [Živjo] at x:[10] y:[10]` | Prikaže besedilo |
| `Draw Rectangle from x1,y1 to x2,y2` | Nariše zapolnjen pravokotnik |
| `Draw Circle at x,y radius [r]` | Nariše zapolnjen krog |
| `Set Sprite [spr]` | Spremeni sprite instance |
| `Set Transparency [0-1]` | Nastavi alfa |

Bloka "Draw Sprite na Položaju" ali "Set Drawing Color" v Blockly ni
(oba obstajata samo v strukturiranem panelu). Draw Score/Draw Lives/
Draw Health Bar so navedeni spodaj pod Score/Lives/Health, ne tukaj.

---

## Bloki Score/Lives/Health

| Blok | Opis |
|------|-------------|
| `Set Score [100]` | Natančno nastavi rezultat |
| `Add to Score [10]` | Poveča/zmanjša rezultat |
| `Set Lives [3]` | Natančno nastavi življenja |
| `Add to Lives [-1]` | Poveča/zmanjša življenja |
| `Set Health [100]` | Natančno nastavi zdravje |
| `Add to Health [-25]` | Poveča/zmanjša zdravje |
| `Draw Score` | Prikaže besedilo rezultata |
| `Draw Lives` | Prikaže življenja kot ponavljajoče se ikone |
| `Draw Health Bar` | Prikaže zdravje kot dvobarvni pas |

---

## Bloki za Instance

| Blok | Opis |
|------|-------------|
| `Create Instance [obj] at x:[100] y:[200]` | Ustvari novo instanco |
| `Destroy Instance` | Odstrani samega sebe |
| `Destroy Other` | Odstrani instanco v trku (v dogodku Collision) |
| `Change Instance [obj]` | Se preobrazi v drugo vrsto objekta |
| `If Can Push [obj] [direction]` | Preverjanje potiskanja v slogu Sokoban |

Bloka "uniči vse ene vrste" ali "ustvari na tem položaju" ni.

---

## Bloki za Sobo

| Blok | Opis |
|------|-------------|
| `Next Room` | Nadaljuj na naslednjo sobo |
| `Previous Room` | Vrni se na prejšnjo sobo |
| `Restart Room` | Ponastavi trenutno sobo |
| `Go to Room [room_name]` | Skoči na določeno sobo |
| `If Next Room Exists` / `If Previous Room Exists` | Zaščiti navigacijo med več sobami |

---

## Bloki za Zvok

| Blok | Opis |
|------|-------------|
| `Play Sound [snd]` | Predvaja zvočni učinek |
| `Play Music [music]` | Predvaja glasbo v ozadju (v zanki) |
| `Stop Music` | Ustavi glasbo |

Bloka "Stop Sound" (za posamezen zvok) ali "Ustavi vse zvoke" v
Blockly ni (samo Stop Music, ki ustavi izključno glasbo).

---

## Bloki za Nadzor

| Blok | Opis |
|------|-------------|
| `If count of [obj] [==] [0] then...` | Primerja število instanc objekta; izvede naslednji blok(e), če je resnično |
| `If variable [var] [==] [value] then...` | Primerja prilagojeno spremenljivko; izvede naslednji blok(e), če je resnično |
| `Set Variable [name] to [value]` | Dodeli spremenljivko instance ali globalno |
| `Check Empty at x,y` | Resnično, če na položaju ni trka (gibanje po mreži) |
| `Exit Event` | Ustavi preostale akcije tega dogodka |
| `Else` | Izvede svoj naslednji blok, če je bil prejšnji test neresničen |
| `Start Block` / `End Block` | Združi več akcij pod Test/Else |

---

## Bloki Output in Game

| Blok | Opis |
|------|-------------|
| `Show Message [text]` | Prikaže pojavno sporočilo |
| `Execute Code` | Izvede pravi Python (glejte [Dogodki in Akcije](Dogodki_in_Akcije_sl)) |
| `End Game` | Zapre igro |
| `Restart Game` | Ponovno zažene od prve sobe |
| `Show Highscore` / `Clear Highscore` | Prikaže ali počisti lestvico najboljših |

---

## Vrednostni Bloki

Vrednostni bloki — vstavite jih v numerično polje drugega bloka:

| Blok | Opis |
|------|-------------|
| `X Position` | Koordinata X te instance |
| `Y Position` | Koordinata Y te instance |
| `Horizontal Speed` | Hitrost X te instance |
| `Vertical Speed` | Hitrost Y te instance |
| `Score` | Trenutni rezultat |
| `Lives` | Trenutna življenja |
| `Health` | Trenutno zdravje |
| `Mouse X` / `Mouse Y` | Trenutni položaj miške |

---

## Primer: Gibanje Igralca

```
┌──────────────────────────┐
│ When key [held: left]    │
├──────────────────────────┤
│ Set Horizontal Speed [-4]│
└──────────────────────────┘

┌──────────────────────────┐
│ When key [held: right]   │
├──────────────────────────┤
│ Set Horizontal Speed [4] │
└──────────────────────────┘

┌──────────────────────────┐
│ When key [no key]        │
├──────────────────────────┤
│ Set Horizontal Speed [0] │
└──────────────────────────┘
```

---

## Primer: Zbiranje Kovancev

```
┌─────────────────────────────┐
│ When colliding with obj_coin│
├─────────────────────────────┤
│ Add to Score [10]           │
├─────────────────────────────┤
│ Play Sound [snd_coin]       │
├─────────────────────────────┤
│ Destroy Other                │
└─────────────────────────────┘
```

---

## Nasveti

1. **Začnite z Events** - Vedno začnite z blokom Event (blok s klobukom)
2. **Povezujte navpično** - Bloki za zlaganje se povezujejo od zgoraj navzdol
3. **Uporabljajte barve** - Barve blokov označujejo njihovo kategorijo
4. **Desni klik** - Dostop do Duplicate, Delete in Help
5. **Zoom** - Za velike programe uporabite kolešček miške ali gumbe za povečavo
6. **Preklopite na strukturirani panel** - Vse, kar zmore Blockly,
   ustreza akciji v zavihku Events strukturiranega panela, obratno pa
   ne velja (npr. Jump to Start/Random Position in Stop Sound za
   posamezen zvok nimata bloka v Blockly) — v takih primerih namesto
   Blockly uporabite strukturirani panel.

---

## Naslednji Koraki

- [[Dogodki_in_Akcije_sl]] - Poglejte enakovreden seznam akcij
- [[Prva_Igra_sl]] - Zgradite celotno igro
- [[Urejevalnik_Objektov_sl]] - Kje je Blockly vgrajen
- [[Preset-Guide_sl]] - Kateri bloki so na voljo v vašem projektu
