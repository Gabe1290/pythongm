# Pogled 3D (izrisovanje iz prve osebe z raycast)

*[Domov](Home_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl) | [Razširitve](Extensions_sl)*

---

PyGameMaker lahko sobo izriše kot **3D-pogled iz prve osebe v slogu
Doom/Wolfenstein** namesto običajnega pogleda od zgoraj — stene kot navpični pasovi,
obarvana ali teksturirana tla in strop, izbirno panoramsko nebo ter sprite-e
"panoje" (billboard) za predmete in pošasti. *Logika* igre (gibanje, trki, dogodki)
se ne spremeni; spremeni se le, **kako** je soba izrisana.

To zagotavlja vgrajena **razširitev 2.5D Raycast** (funkcija [Pogled 3D](Extensions_sl)),
ki je privzeto omogočena. Izvaža se v vse tri cilje — računalnik, HTML5 in
Kivy/Android — tako da igra iz prve osebe povsod deluje enako.

Priloženi primeri **`raycast_1`–`raycast_4`** so celoviti, igralni primeri (preprost
labirint, dvonivojska igra s predmeti in pošastjo, različica z zdravjem in kompleti
prve pomoči ter prikaz vrstice stanja v slogu DOOM).

---

## Kako deluje

- Soba postane prvoosebna, ko predmet izvede dejanje **Omogoči pogled Raycast**
  (običajno v svojem dogodku Ustvari). Ta predmet je privzeto **kamera** — njegov
  položaj je gledišče, njegov `facing_angle` (kot pogleda) pa je smer pogleda.
- **Stene so vaše trdne instance.** Izrisovalnik iz vsakega trdnega predmeta v sobi
  izpelje tanke *robove* sten na mreži, katere velikost je parameter `cell_size`
  dejanja (privzeto 32 — velikost, ki jo uporabljajo vsi primeri
  `maze_*`/`raycast_*`). Trden predmet s spriteom stene teksturira steno; sicer se
  uporabi enotna barva `wall_color`.
- **Kamera se obrača** s spreminjanjem `facing_angle` (glejte **Nastavi kot pogleda**)
  in se premika z običajnimi dejanji gibanja (npr. `set_direction_speed` z
  `direction = "facing_angle"` za hojo naprej).
- **Netrdne instance s spriteom** (cilji, predmeti, pošasti) se izrišejo kot proti
  kameri obrnjeni **panoji**, pravilno zakriti s stenami.

---

## Dejanja (kategorija **Pogled 3D**)

| Dejanje | Kaj počne |
|---------|-----------|
| **Omogoči pogled Raycast** (`enable_raycast_view`) | Preklopi trenutno sobo v prvoosebni pogled (ali nazaj) in konfigurira kamero: `camera_object`, `fov`, `render_distance`, `cell_size`, barve in teksture sten/tal/stropa, izbirno `sky_texture` in `viewport_height` (vrstica v slogu DOOM). |
| **Nastavi kot pogleda** (`set_facing_angle`) | Obrne kamero. Kot v stopinjah GameMaker (0 = desno, 90 = gor); `relative` prišteje trenutnemu kotu. |
| **Nariši mini zemljevid** (`draw_minimap`) | Nariše proti severu usmerjen mini zemljevid sten sobe z oznako "tukaj ste". Dejanje HUD — postavite ga v dogodek Nariši. |
| **Nariši HUD DOOM** (`draw_doom_hud`) | Nariše spodnjo vrstico stanja v slogu DOOM: vrstica zdravja + število, na zdravje odziven obraz, rezultat, življenja in števec cilja. Se ujema z `viewport_height` dejanja `enable_raycast_view`. |

Glejte [Popolno referenco dejanj](Full-Action-Reference_sl#3d-view) za vse parametre.

---

## Minimalni prvoosebni krmilnik

V predmetu igralca:

- **Ustvari:** `Omogoči pogled Raycast` (pustite `camera_object` prazen, da je igralec
  *kamera*).
- **Tipkovnica Levo / Desno:** `Nastavi kot pogleda` z vklopljenim `relative`
  (npr. ±3°).
- **Tipkovnica Gor:** `Nastavi smer in hitrost` z `direction = facing_angle` in
  majhno hitrostjo za hojo naprej.

Sobo zgradite iz trdnih predmetov-sten na mreži 32 pikslov, tako kot primeri
`maze_*` — raycaster te stene spremeni v 3D-hodnike.

---

## Opombe in omejitve

- Dejanja HUD (`draw_minimap`, `draw_doom_hud` in običajna `draw_score` /
  `draw_lives` / `draw_text`) se prekrivajo **čez** prvoosebno sliko, v zaslonskih
  koordinatah.
- Stene so za prvoosebni prehod statične — stene, ustvarjene/uničene po naložitvi
  sobe, ne preoblikujejo 3D-geometrije.
- Če je razširitev 2.5D Raycast **onemogočena**, se soba, ki omogoči pogled,
  preprosto izriše od zgoraj in IDE vas ob naložitvi opozori — glejte
  [Razširitve](Extensions_sl).

---

## Glejte tudi

- [Razširitve](Extensions_sl) — kako je Pogled 3D dostavljen in kako ga izklopiti
- [Popolna referenca dejanj](Full-Action-Reference_sl#3d-view) — štiri dejanja podrobno
- [Urejevalnik sob](Urejevalnik_Sob_sl) — postavljanje predmetov-sten, iz katerih je zgrajen pogled
