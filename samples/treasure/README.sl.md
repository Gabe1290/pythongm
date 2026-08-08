# Zaklad

Lov v labirintu v slogu Pac-Man: **raziskovalec** tava po labirintu,
obdanem z zidovi, in zbira **točke zaklada**, medtem ko ga
zasledujejo **pošasti**, ki na vsakem križišču izberejo novo smer.
Poberite **pilulo moči** (`pil`) in se razmerje moči obrne — vsaka
pošast postane **prestrašena** in jo je mogoče pojesti za bonus točke,
dokler učinek ne mine. To je izvorni projekt pygm2, uvožen iz
`treasure.gmk` (GameMaker 8.x); sam projekt je napisan/shranjen v
lastnem formatu JSON pygm2.

**Kje se to umešča:** `treasure` se umešča ob družino `maze_*` —
zgrajena z GameObjects + vgrajenimi dejanji in vizualnim urejevalnikom
dogodkov — a doda **skript na ravni projekta** (`adapt_direction`, IA
pošasti na križiščih) in cikel stanj v slogu GM
**"lov / okrepitev / beg"** skozi svoje objekte. Bila je eden od dveh
vzorcev, odstranjenih v rc.12 zaradi napak pri uvozu GMK, in
**ponovno dodana po utrjevanju uvoznika** (16.07.2026); glejte
[`../../docs/GMK_IMPORTER_HARDENING_PLAN.md`](../../docs/GMK_IMPORTER_HARDENING_PLAN.md)
in [`../../docs/treasure_testing_pass.md`](../../docs/treasure_testing_pass.md).

**Zvok in glasba:** priloženih je 6 zvočnih učinkov (pobiranje,
pilula moči, pojedanje pošasti, smrt, …). Starejša skladba iz dobe
GM8 (`music`) je v formatu, ki ga pygame ne more naložiti, in je
izpuščena med tekom — enako kot glasba ozadja pri drugih vzorcih
labirinta; igra ni prizadeta.

## Kako igrati

- **Tipke s puščicami** premikajo raziskovalca skozi labirint;
  zidovi blokirajo gibanje.
- Zberite vsako **točko zaklada**, da dokončate stopnjo (skupno 4 sobe).
- **Pošasti** vas zasledujejo; dotik ene običajno stane življenje.
- Poberite **pilulo moči** in pošasti postanejo **prestrašene**
  (njihov sprite se spremeni) za nekaj sekund — dotaknite se takrat
  prestrašene pošasti, da jo **pojeste** (+točke; teleportira se
  nazaj na svoj začetek kot navadna pošast). Učinek mine po
  časovniku.

## IA pošasti (skript `adapt_direction`)

Vsaka pošast kliče skript projekta `adapt_direction` iz svojih
dogodkov step/trka. Je prava Python koda pygm2 — na morebitnem
križišču naključno razmišlja o obratu, preverjajoč
`game.check_collision_at_position(...)` glede zidu, preden se
zaveže, tako da pošasti tavajo po labirintu namesto da bi tekle v
ravni črti. Odprite vir **Scripts**, da ga preberete; dejanje
`execute_script` v dogodkih pošasti pokaže, kje je klican.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest — nastavitve okna/sobe, vgrajeni viri, skript `adapt_direction`, in vrstni red sob |
| `rooms/room0..3.json` | Štiri stopnje labirinta (instance po sobah) |
| `objects/*.json` | 7 definicij objektov (vir resnice; ob nalaganju združene z vgrajenimi kopijami) |
| `sprites/` | 10 slikovnih datotek PNG spritov + metapodatki `.json` |
| `sounds/` | 6 zvočnih učinkov |
| `backgrounds/` | 1 ozadje |
| `CREDITS.txt` | Obvestilo o licenciranju virov |

## Objekti

| Objekt | Vloga |
|---|---|
| `explorer` | Lik igralca; zbira zaklade, poje prestrašene pošasti, umre ob stiku z navadnimi |
| `monster` | Zasledovalec; tava prek `adapt_direction`; se spremeni v `scared` s pilulo moči |
| `scared` | Pošast v stanju bega; jestljiva; se vrne v `monster` po časovniku |
| `pil` | Pilula moči — prestraši vsako pošast ob pobiranju |
| `point` | Zaklad za zbiranje |
| `bonus` | Dodaten zbirljiv predmet |
| `wall` | Statičen trden zid labirinta |

## Viri

10 sprite-ov, 6 zvokov, 1 ozadje — vse uvoženo iz `treasure.gmk`.
Za poreklo glejte `CREDITS.txt` in
[`../../docs/ASSET_LICENSES.md`](../../docs/ASSET_LICENSES.md).

## Kaj prilagoditi

- **Trajanje prestrašitve** — alarm pilule moči je `160` sličic v
  dogodku `collision_with_pil` objekta `explorer`; povečajte ga za
  daljšo fazo bega.
- **Verjetnost obrata pošasti** — preizkusi
  `random.random() * 3 < 1` v skriptu `adapt_direction` določajo, kako
  pogosto se pošasti obrnejo na križišču.
- **Vrednosti točk** — točke zaklada in pojedanja pošasti so dejanja
  `set_score` (relativna) v ustreznih dogodkih trka.

## Stanje izvoza

Pokrito z zbirko smoke-testov brez grafičnega vmesnika
(`tools/smoke_run_samples.py`, ki navaja `treasure`) in zbirko
regresije uvoza (`tests/test_gmk_treasure_maze4_import.py` +
`tests/test_gmk_applies_to.py`). Preverjeno v ročnem preizkusu igre
med utrjevanjem uvoznika julija 2026 (glejte dokument o testiranju).
Izpostavljeno v zavihku Welcome kot **"Treasure"**.

## Ponovno generiranje iz izvirnika `.gmk`

Sosednja datoteka `../treasure.gmk` je vir GameMaker 8.x. Za ponovno generiranje:

```bash
python3 -c "from importers.gmk_importer import import_gmk_detailed; \
  import_gmk_detailed('samples/treasure.gmk', '/tmp/treasure_reimport')"
```

Svež uvoz je zvest izvirni igri od utrjevanja uvoznika julija 2026
(na tem vzorcu ni bil uporabljen noben ročni popravek).
