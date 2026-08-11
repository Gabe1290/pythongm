# Pogled 3D

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Nariši HUD DOOM

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_doom_hud` |
| **Ikona** | 🎯 |
| **Kategorija** | Pogled 3D |

Nariši spodnjo vrstico stanja v slogu DOOM (vrstica zdravja + število, rezultat, življenja, števec cilja in na zdravje odziven obraz) čez pogled raycast

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Levi rob vrstice, v zaslonskih pikslih |
| `y` | Število | `-1` | Zgornji rob vrstice; negativna vrednost jo samodejno poravna na dno okna, pod pomanjšanim pogledom; neobvezno |
| `width` | Število | `0` | Širina vrstice (0 = polna širina okna); neobvezno |
| `height` | Število | `42` | Višina vrstice; ohranjajte jo usklajeno s pasom viewport_height, rezerviranim v enable_raycast_view; neobvezno |
| `back_color` | Barva | `#101010` | Plošča ozadja vrstice; neobvezno |
| `divider_color` | Barva | `#505050` | Zgornji rob in ozadje vrstice zdravja; neobvezno |
| `text_color` | Barva | `#ffffff` | Barva vsega besedila vrstice; neobvezno |
| `health_label` | Besedilo | `Health` | neobvezno |
| `health_bar_width` | Število | `90` | neobvezno |
| `health_bar_height` | Število | `14` | neobvezno |
| `bar_color` | Barva | `#20c020` | Barva polnila vrstice zdravja; neobvezno |
| `face_sprite` | Sprite | — | Vodoravni pas sličic obraza, najbolj zdrav prvi (prazno = brez ikone obraza); neobvezno |
| `face_frames` | Število | `4` | Koliko sličic ima pas obraza; zdravje je enakomerno razporejeno mednje; neobvezno |
| `score_label` | Besedilo | `Score: ` | neobvezno |
| `lives_sprite` | Sprite | — | Sprite, narisan enkrat na vsako preostalo življenje; neobvezno |
| `lives_scale` | Število | `1.0` | neobvezno |
| `objective_value` | Besedilo | `0` | Izraz, prikazan za oznako cilja (povežite svojo spremenljivko ključa/naloge); neobvezno |
| `objective_label` | Besedilo | `Keys: ` | neobvezno |

### Nariši mini zemljevid

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_minimap` |
| **Ikona** | 🗺️ |
| **Kategorija** | Pogled 3D |

Nariši proti severu usmerjen mini zemljevid sten sobe raycast, z oznako, ki prikazuje, kje je kamera in kam je usmerjena

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Levi rob mini zemljevida, v zaslonskih pikslih |
| `y` | Število | `0` | Zgornji rob mini zemljevida, v zaslonskih pikslih |
| `size` | Število | `120` | Širina in višina kvadrata mini zemljevida, v pikslih; neobvezno |
| `back_color` | Barva | `#101018` | Barva plošče za zemljevidom; neobvezno |
| `wall_color` | Barva | `#8080a0` | Barva črt sten; neobvezno |
| `player_color` | Barva | `#ffd040` | Barva oznake kamere in njene smerne črte; neobvezno |

### Omogoči pogled Raycast

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `enable_raycast_view` |
| **Ikona** | 🕹️ |
| **Kategorija** | Pogled 3D |

Izriši sobo kot 3D-pogled iz prve osebe v slogu Doom/Wolfenstein (stene, nebo, tla) namesto pogleda od zgoraj

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `enable` | Da/Ne | Da | Vklop = pogled raycast iz prve osebe; izklop = običajni pogled od zgoraj |
| `camera_object` | Predmet | — | Predmet, čigar položaj + kot pogleda je kamera (prazno = predmet, ki izvaja to dejanje); neobvezno |
| `fov` | Število | `66` | Vodoravno vidno polje v stopinjah; neobvezno |
| `render_distance` | Število | `20` | Največja dolžina žarka v celicah mreže; neobvezno |
| `cell_size` | Število | `32` | Velikost celice mreže v pikslih (ujema se z mrežo postavitve sten); neobvezno |
| `columns` | Število | `320` | Zaslonski stolpci za raycast (manj = hitreje/bolj grobo); neobvezno |
| `wall_color` | Barva | `#993333` | Enotna barva sten, ko tekstura stene ni nastavljena; neobvezno |
| `floor_color` | Barva | `#464632` | Enotna barva tal, ko tekstura tal ni nastavljena; neobvezno |
| `ceiling_color` | Barva | `#87CEEB` | Enotna barva stropa, ko tekstura neba/stropa ni nastavljena; neobvezno |
| `wall_texture` | Sprite | — | Sprite za teksturiranje vsake stene (prazno = enotna barva); neobvezno |
| `sky_texture` | Sprite | — | Sprite za panoramsko nebo nad stropom (prazno = enotno); neobvezno |
| `floor_texture` | Sprite | — | Sprite, projiciran na tla (prazno = enotna barva); neobvezno |
| `ceiling_texture` | Sprite | — | Sprite, projiciran na strop, ko nebo ni nastavljeno; neobvezno |
| `wall_textured` | Da/Ne | Da | Izklop vsili enotne barve sten, tudi ko je tekstura nastavljena; neobvezno |
| `floor_cast_res` | Število | `4` | Podvzorčenje projiciranih tal (višje = hitreje + bolj grobo); neobvezno |
| `viewport_height` | Število | `0` | Skrči 3D-pogled na to višino v pikslih (letterbox), pri čemer se pod njim rezervira pas za vrstico stanja v slogu DOOM (0 = polna višina okna, nespremenjeno); neobvezno |

### Nastavi kot pogleda

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_facing_angle` |
| **Ikona** | 🧭 |
| **Kategorija** | Pogled 3D |

Nastavi smer pogleda instance za kamero raycast (iz prve osebe) — neodvisno od hitrosti gibanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `angle` | Število | `0` | Stopinje (0=desno, 90=gor, 180=levo, 270=dol) |
| `relative` | Da/Ne | Ne | Prištej trenutnemu kotu pogleda namesto zamenjave; neobvezno |

---

## Druge Kategorije

- [Gibanje](Full-Action-Reference-Movement_sl) (20)
- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (2)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (20)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
