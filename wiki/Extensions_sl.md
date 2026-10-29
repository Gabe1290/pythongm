# Razširitve

*[Domov](Home_sl) | [Pogled 3D](3D-View_sl) | [Omrežje](Network_sl) | [micro:bit](Microbit_sl) | [File Exchange Multiplayer](FileExchange) (v angleščini) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

---

**Razširitev** je samostojen dodatek, ki PyGameMakerju doda zmožnosti, ne da bi
spremenil osnovni pogon. Razširitev lahko prispeva:

- nova **dejanja** (pojavijo se v izbirniku dejanj kot vsako vgrajeno dejanje),
- nov način **risanja sobe** (izrisovalnik po meri), in
- ustrezno **izvozno kodo**, tako da se igre, ki jo uporabljajo, še vedno izvozijo v
  HTML5 in Kivy/Android.

Vgrajena razširitev **2.5D Raycast** (funkcija [Pogled 3D](3D-View_sl)) je delan
primer: doda štiri dejanja "Pogled 3D" in prvoosebni izrisovalnik ter se izvozi v
vse tri cilje.

Vgrajena razširitev **LAN Multiplayer** (funkcija [Omrežje](Network_sl)) je druga, večja: doda 15 dejanj »Omrežje« in šest dogodkov ter igro poveže prek lokalnega omrežja iz izvoza za namizje (kot gostitelj ali odjemalec) in izvoza HTML5 (kot odjemalec).

Razširitev **File Exchange Multiplayer** (funkcija [File Exchange Multiplayer](FileExchange), v angleščini) je potezni sorodnik razširitve LAN Multiplayer: doda 7 dejanj »Omrežje« in šest dogodkov ter si stanje igre izmenjuje prek datotek na skupnem pogonu namesto z živo povezavo — za učilnico, kjer požarni zid blokira neposredne povezave razširitve LAN Multiplayer. Samo izvoz za namizje — glejte opombo »Why not every export« na sami strani.

Vgrajena razširitev **micro:bit** (funkcija [micro:bit](Microbit_sl)) postavi simuliran BBC micro:bit v okno igre: 16 dejanj, 24 dogodkov, narisana ploščica s gumbi, na katere lahko kliknete, in vrstica tipal, zvok in radio. Priložena je vklopljena, vendar se vklaplja za vsak projekt posebej (**Nastavitve projekta → Razširitve**) in deluje v »Testiraj igro« ter v izvozih za namizje, HTML5 in Android (Kivy).

---

## Omogočanje in onemogočanje

Razširitve so dostavljene **omogočene**. Eno lahko onemogočite (ali omogočite tako, ki
je dostavljena onemogočena) brez urejanja kode, prek ključa `extensions` v vaši
konfiguraciji — preslikave `ime mape → vklop/izklop`:

```json
"extensions": { "raycast_2_5d": false }
```

**Odsoten** vnos pomeni "uporabi privzeto vrednost razširitve", tako da nikoli nič ne
izgine, ker je ključ manjkal. Spremembe začnejo veljati ob naslednjem zagonu (dejanja
se registrirajo ob zagonu).

Z onemogočeno razširitvijo 2.5D Raycast se soba, ki omogoči prvoosebni pogled,
preprosto izriše od zgoraj.

---

## Kdaj projekt potrebuje razširitev

Ker je razširitev mogoče izklopiti, vam PyGameMaker pomaga preprečiti presenečenja:

- **Ob naložitvi**, če projekt uporablja dejanja iz trenutno onemogočene razširitve,
  IDE prikaže opozorilo, ki poimenuje razširitev in prizadete funkcije (da se 3D-igra
  ne izriše tiho od zgoraj).
- **Ob shranjevanju** projekt zabeleži razširitve, od katerih so odvisna njegova
  dejanja, v `project.json` (seznam `requires_extensions`) — trajno opombo, ki jo vidi
  vsak, s komer delite projekt. Projekt, ki ne uporablja dejanj razširitev, polje
  preprosto izpusti.

---

## Razširitve in vtičniki

Oboje dodaja dejanja; razlikujeta se le v pakiranju:

| | Vtičnik | Razširitev |
|---|--------|-----------|
| Oblika | ena sama datoteka `.py` v `plugins/` | mapa v `extensions/` z manifestom |
| Najbolje za | majhen nabor dejanj | funkcijo, ki zajema več datotek in/ali riše/izvaža |
| Primer | dejanja **Audio** (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## Kako izgleda mapa razširitve

Za radovedne (in za tiste, ki jo pišejo) je razširitev berljiva mapa:

```
extensions/raycast_2_5d/
├── extension.json     # manifest: ime, različica, omogočeno, provides_actions
├── actions.py         # sheme dejanj (prikazane v izbirniku)
├── handlers.py        # kaj dejanja počnejo med izvajanjem
├── renderer.py        # izrisovalnik sobe po meri (raycaster)
├── state.py           # stanje za posamezno sobo (v imenskem prostoru sobe)
├── hud.py             # generatorji geometrije mini zemljevida / vrstice DOOM
├── export_html5.js    # port HTML5, vbrizgan v spletni izvoz
├── export_kivy.py     # port Kivy, vbrizgan v mobilni/računalniški izvoz
└── README.md          # kako se vse sestavi
```

Seznam `provides_actions` v manifestu je tisto, kar IDE omogoča, da poimenuje točno
razširitev, ko projekt potrebuje onemogočeno.

---

## Glejte tudi

- [Pogled 3D](3D-View_sl) — funkcija, ki jo zagotavlja vgrajena razširitev
- [Omrežje](Network_sl) — funkcija, ki jo zagotavlja razširitev LAN Multiplayer
- [micro:bit](Microbit_sl) — funkcija, ki jo zagotavlja razširitev micro:bit
- [File Exchange Multiplayer](FileExchange) (v angleščini) — funkcija, ki jo zagotavlja razširitev File Exchange Multiplayer
- [Popolna referenca dejanj](Full-Action-Reference_sl) — tudi dejanja razširitev se pojavijo tukaj
- [Izvoz iger](Izvoz_Iger_sl) — funkcije razširitev se prenesejo v izvoze
