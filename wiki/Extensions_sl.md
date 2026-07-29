# Razširitve

*[Domov](Home_sl) | [Pogled 3D](3D-View_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

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
- [Popolna referenca dejanj](Full-Action-Reference_sl) — tudi dejanja razširitev se pojavijo tukaj
- [Izvoz iger](Izvoz_Iger_sl) — funkcije razširitev se prenesejo v izvoze
