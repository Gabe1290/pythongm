# Ploščad — 1. stopnja

Minimalna platformerska igra z bočnim rolanjem, uvožena iz GameMaker
8.x (`samples/plateforme_1.gmk`). Krogla, ki jo upravlja igralec
(`obj_balle`), plezajo po enem zaslonu opečnih ploščadi (`obj_brique`)
z uporabo sond `if_collision` v slogu GameMakerja za premikanje v
korakih 4px/sličico in pade pod gravitacijo šele, ko pod njo ni nič
trdnega — ročno napisana shema gibanja AABB namesto vgrajene fizike
motorja.

**Kje se to umešča:** del družine `plateforme_*`, vendar pri svojem
minimumu — za razliko od `plateforme_2`/`plateforme_3` ta stopnja
nima slike ozadja in **nima tlakovanega ozadja** (polje `tiles` sobe
je prazno); zgrajena je samo iz GameObjects + sprite-ov, enako kot
`maze_1`. Glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za primerjavo celotne družine z `maze_*` in `match3_*`.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Puščica levo/desno** — premakne kroglo za 4px na pritisk tipke,
  blokirano s trdnimi opekami.
- **Puščica gor** — skok (nastavi `vspeed` na -10), samo medtem ko
  stoji na trdni opeki.
- V tej stopnji ni izrecnega ciljnega objekta, kovanca ali izhoda —
  gre za navpičen opečni labirint za plezanje. Prav tako ni objekta
  pošasti/nevarnosti, tako da ni pogoja poraza; gre za prosto
  raziskovanje mehanike trkov/gravitacije.

## Struktura projekta

| Datoteka | Namen |
|---|---|
| `project.json` | Manifest projekta — nastavitve okna/sobe, vgrajene kopije virov (glejte opombo spodaj). |
| `rooms/niveau_01.json` | Edina soba: 800×640, 120 instanc (večinoma zidovi/ploščadi `obj_brique` plus ena `obj_balle`). |
| `objects/obj_balle.json` | Logika igralne krogle (gibanje, gravitacija, skok). |
| `objects/obj_brique.json` | Statična trdna opeka, brez dogodkov. |
| `sprites/` | `spr_balle.png` (krogla) in `spr_32x32_noir.png` (opeka), vsak s svojo pripadajočo datoteko `.json`. |

`objects/*.json` in `rooms/niveau_01.json` sta trenutni stranski
datoteki po posameznem viru; njuna vsebina se ujema s tem, kar je
vgrajeno v `project.json` za ta vzorec (ni najdenih razhajanj), a po
konvenciji repozitorija sta stranski datoteki vir resnice, če bi se
kdaj razšli.

## Objekti

| Objekt | Vloga | Ključni dogodki |
|---|---|---|
| `obj_balle` | Krogla, ki jo upravlja igralec; gravitacija, gibanje s poznavanjem trkov, skok | create (brez definicij), step, collision_with_obj_brique, keyboard (left, right, up) |
| `obj_brique` | Statična trdna ploščad/ploščica zidu | *(nič — brez definiranih dogodkov)* |

## Viri

2 sprite-a (`spr_balle`, `spr_32x32_noir`), 0 zvokov. Oba sprite-a sta
izpeljani deli umetniškega dela igre Pingus, licencirana pod
GPL-3.0-or-later — glejte `CREDITS.txt` v tej mapi za celotno
obvestilo in navedbo izvornih avtorjev; ne obravnavajte ju kot
zajeta z licenco MIT urejevalnika.

## Kaj prilagoditi

- Dogodek step objekta `obj_balle`: gravitacija je `0,45` px/sličico²
  in vspeed je omejen na `24` — dvignite/znižajte katerega koli za
  spremembo teže padca in končne hitrosti.
- Impulz skoka je fiksen `vspeed = -10` (tipkovnica "gor") — večja
  velikost skoči višje.
- Vodoravni korak premika je `4` px na pritisk tipke (tipkovnica
  "levo"/"desno") — večji koraki delujejo bolj odzivno, a lahko
  predrejo skozi tanke reže.
- Soba je 800×640 pri `room_speed: 30`; postavitev opek v
  `rooms/niveau_01.json` je mogoče prosto preurediti, saj `obj_brique`
  nima lastne logike.

## Stanje izvoza

Ta vzorec je naveden na seznamu `SAMPLES` v
`tools/smoke_run_samples.py`, tako da je pokrit z ogrodjem
smoke-testov brez grafičnega vmesnika (poganja pravo zanko igre za
~180 sličic z vbrizganim vnosom tipkovnice). Ni bil posebej preverjen
glede na cilja izvoza Kivy ali splet. Izpostavljen je v zavihku
Welcome urejevalnika kot **"Platform — Level 1"**
(`widgets/welcome_tab.py`).
