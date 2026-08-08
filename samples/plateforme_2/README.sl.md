# Ploščad — 2. stopnja

Platformerska igra z bočnim rolanjem, uvožena iz GameMaker 8.x
(`samples/plateforme_2.gmk`). V primerjavi z minimalno prvo stopnjo ta
poveča nabor objektov z osamljenega igralca + enega bloka na štiri
objekte (osnovna ploščad plus vodoravna in navpična velikostna
različica, ki dedujeta od nje), razporejene v sobo s 126 instancami,
zgrajeno iz snežno tematiziranega nabora avtomatskih ploščic namesto
nekaj ročno postavljenih blokov.

**Kje se to umešča:** del družine `plateforme_*`, in — za razliko od
minimalne `plateforme_1` — tukaj se pojavi **tlakovano ozadje**: 127
posamično postavljenih kosov ploščic ozadja (polje `tiles` sobe) plus
slika ozadja z gradientom (`fond_degrade`), naloženo pod trdnimi
*objekti* opeke, ki še vedno obravnavajo trke. To je korak, ki ga
`plateforme_*` doda onkraj `maze_*`; glejte
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
za celoten potek.

**Zvok in glasba:** nič — nobena zvočna datoteka ni priložena temu vzorcu.

## Kako igrati

- **Puščica levo/desno** — premika pingvina (`obj_personnage`) levo/desno.
- **Puščica gor** — skok, a samo medtem ko stoji na trdni ploščadi
  (preverjeno s testom trka en piksel pod igralcem).
- **Cilj** — v tem vzorcu ni ciljnega objekta/zastave; gre za
  platformersko postavitev za raziskovanje/prehod po ploščadih
  `obj_brique*`.
- **Pogoj poraza** — ni definiran (brez nevarnosti, brez smrtonosnih
  objektov, brez preverjanja smrti ob padcu); spodnja vrsta opek sobe
  deluje kot tla.

## Struktura projekta

| Datoteka | Namen |
| --- | --- |
| `project.json` | Manifest projekta — nastavitve okna/sobe, vgrajene kopije virov. |
| `rooms/niveau_01.json` | Edina soba: 800×640, 126 instanc + 127 ploščic ozadja. Vir resnice za vsebino sobe (vgrajeni seznam `instances` v `project.json` je prazen). |
| `objects/*.json` | Stranske datoteke po posameznem objektu za 4 objekte; ob pisanju tega besedila identične vgrajenim kopijam v `project.json`. |
| `sprites/` | 5 sprite virov (trakovi hoje igralca + trdni ploščadni bloki). |
| `backgrounds/` | Nabor snežnih ploščic (`tuiles_neige.png`, uporabljen kot vir avtomatskih ploščic) in majhen navpičen gradient (`fond_degrade.png`), raztegnjen kot ozadje sobe. |
| `CREDITS.txt` | Obvestilo o licenciranju umetniškega dela spritov/ozadja (glejte Vire spodaj). |

## Objekti

| Objekt | Vloga | Ključni dogodki |
| --- | --- | --- |
| `obj_personnage` | Igralec (pingvin) — gibanje, skok, gravitacija, zaznavanje tal | create, step, collision_with_obj_brique, keyboard (left, right, up), keyboard_release (LEFT, RIGHT) |
| `obj_brique` | Osnoven trden ploščadni blok (32×32) | nič (brez dogodkov; samo zastavica solid) |
| `obj_brique_h` | Široka trdna ploščadna različica (32×16), otrok `obj_brique` | nič |
| `obj_brique_v` | Ozka trdna ploščadna različica (8×16), otrok `obj_brique`; definirana, a ni postavljena v `niveau_01` | nič |

## Viri

5 sprite-ov (trakovi hoje `spr_pingus_dr`/`spr_pingus_ga` z 8
sličicami, plus trije ograjniki polne barve v velikosti 32×32 /
32×16 / 8×16) in 2 ozadji; brez zvokov. Umetniško delo spritov in
ozadja je prilagojeno iz projekta Pingus (GPL-3.0-or-later) — glejte
`CREDITS.txt` za polno navedbo in licenčne pogoje; ta README teh
trditev ne ponavlja niti jim ne dodaja.

## Kaj prilagoditi

- Vodoravna hitrost igralca je fiksna `hspeed = 4` v dogodkih tipkovnice.
- Impulz skoka je `vspeed = -10`; gravitacija padca je `0,45`
  (uporabljena samo v zraku), z omejitvijo končne hitrosti na
  `vspeed = 24`.
- Velikost sobe je 800×640 pri `room_speed = 30`.

## Stanje izvoza

Ta vzorec je naveden na seznamu `SAMPLES` v
`tools/smoke_run_samples.py`, tako da ob vsakem teku tega ogrodja
dobi smoke-prehod brez grafičnega vmesnika (prava zanka igre teče za
~180 sličic z vbrizganim vnosom tipkovnice). Za ta vzorec posebej ni
bilo izvedeno preverjanje glede na ciljna izvoza (Kivy/HTML5).
Izpostavljen je v zavihku Welcome urejevalnika kot "Platform —
Level 2" (`widgets/welcome_tab.py`).
