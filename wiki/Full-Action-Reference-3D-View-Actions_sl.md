# Pogled 3D

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Uporabi težnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `apply_gravity` |
| **Ikona** | ⬇️ |
| **Kategorija** | Pogled 3D |

Neprekinjena fizika padanja in pristajanja za kamero Block World: vstavi jo v dogodek Korak (in ne v dogodek pridržane tipke), da se izvede v vsaki sličici, ne glede na vnos premikanja. Nima učinka, dokler parameter Težnost v »Vklopi pogled Block World« ni večji od 0

*Parametri:* brez

### Razbij blok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `break_block` |
| **Ikona** | ⛏️ |
| **Kategorija** | Pogled 3D |

Odstrani blok, v katerega je usmerjena kamera; če je inventar v »Vklopi pogled Block World« vklopljen, ga tudi pobere v inventar primerka, ki izvaja dejanje, in ga noče odstraniti, če je blok zaščiten (»Nastavi zaščito blokov«) in zahtevanega ključa ni v inventarju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `reach` | Število | `5` | Doseg naprej, v celicah mreže; neobvezno |

### Izdelaj predmet

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `craft_item` |
| **Ikona** | ⚗️ |
| **Kategorija** | Pogled 3D |

Poskusi izdelati izdelek registriranega recepta iz zaloge instance, ki kliče akcijo: vse ali nič — porabi vse sestavine naenkrat, ali nobene, če katere zmanjka. Tiho ne stori ničesar, če za izdelek ni registriranega recepta ali če parameter Zaloga v »Vklopi pogled Block World« ni vklopljen

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `output` | Izbira | `brick` | Which registered recipe to attempt, by its output block type; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Nariši HUD Block World

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_block_world_hud` |
| **Ikona** | 🧰 |
| **Kategorija** | Pogled 3D |

Nariše merek in vrstico za hiter dostop (izbrano mesto je poudarjeno, ob vklopljenem inventarju pa je na vsakem mestu še števec): pokliči jo iz dogodka Nariši v samem objektu igralca oziroma kamere

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `slot_size` | Število | `40` | Širina in višina vsakega mesta v vrstici, v slikovnih točkah; neobvezno |
| `gap` | Število | `6` | Razmik med mesti v vrstici, v slikovnih točkah; neobvezno |
| `margin_bottom` | Število | `16` | Razmik med vrstico in spodnjim robom zaslona; neobvezno |
| `back_color` | Barva | `#202020` | Barva polnila neizbranega mesta; neobvezno |
| `selected_color` | Barva | `#ffd040` | Barva polnila trenutno izbranega mesta; neobvezno |
| `border_color` | Barva | `#ffffff` | Barva obrobe vseh mest; neobvezno |
| `text_color` | Barva | `#ffffff` | Barva oznake vrste bloka na vsakem mestu; neobvezno |
| `crosshair_size` | Število | `12` | Širina in višina merka na sredini, v slikovnih točkah; neobvezno |
| `crosshair_color` | Barva | `#ffffff` | Barva merka na sredini; neobvezno |

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
| `mark_object` | Predmet | — | Na zemljevid s piko označi tudi vsak primerek tega objekta (prazno = pokaži samo stene in igralca); neobvezno |
| `mark_color` | Barva | `#40e0ff` | Barva pik iz »Označi objekt«; neobvezno |
| `mark_object_2` | Predmet | — | Drug objekt, ki se označi s svojo barvo; neobvezno |
| `mark_color_2` | Barva | `#ff5050` | Barva pik iz »Označi objekt 2«; neobvezno |

### Vklopi pogled Block World

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `enable_block_world_view` |
| **Ikona** | 🧱 |
| **Kategorija** | Pogled 3D |

Sobo prikaže kot voksel pogled iz prve osebe (ena sama plast) namesto pogleda od zgoraj

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `enable` | Da/Ne | Da | Vklopljeno = pogled blokov iz prve osebe; izklopljeno = običajen pogled od zgoraj |
| `camera_object` | Predmet | — | Predmet, čigar položaj + kot pogleda je kamera (prazno = predmet, ki izvaja to dejanje); neobvezno |
| `z_layer` | Število | `0` | Katera plast sveta se nariše (faza 2a nariše natanko eno plast – pogleda gor in dol še ni); neobvezno |
| `fov` | Število | `66` | Vodoravno vidno polje v stopinjah; neobvezno |
| `render_distance` | Število | `10` | Max ray length in grid cells (lower = faster; distance fog hides where the world ends); neobvezno |
| `cell_size` | Število | `32` | Velikost celice mreže v slikovnih točkah (naj se ujema z mrežo za postavljanje blokov); neobvezno |
| `columns` | Število | `160` | Zaslonski stolpci za raycast (manj = hitreje/bolj grobo); neobvezno |
| `fog` | Da/Ne | Da | Fade distant blocks into the sky so the edge of the view looks like haze instead of a hard cut. Off restores the old flat look; neobvezno |
| `fog_color` | Barva | — | Colour the distance fades to; empty follows the Sky Color (a cave might want its own); neobvezno |
| `wall_color` | Barva | `#8a8a8a` | Enotna barva, uporabljena le, če so blokovne teksture izklopljene; neobvezno |
| `floor_color` | Barva | `#3a2f1c` | Enotna barva tal (faza 2a tal še ne teksturira); neobvezno |
| `ceiling_color` | Barva | `#87CEEB` | Enotna barva stropa oziroma neba (faza 2a neba še nima); neobvezno |
| `pitch` | Število | `0` | Stopinje za pogled navzgor (+) ali navzdol (−); 0 je vodoravno; neobvezno |
| `wall_textured` | Da/Ne | Da | Izklopljeno vsili enotne barve blokov, tudi če so na voljo prave teksture; neobvezno |
| `top_cast_res` | Število | `4` | Podrobnost teksture zgornjih in spodnjih ploskev: vzorčene vrstice na vsakih N zaslonskih vrstic (višje = hitreje in bolj grobo, 0 = enotna povprečna barva namesto teksture); neobvezno |
| `eye_height` | Število | `1.5` | Višina kamere nad plastjo, na kateri stoji, v celicah (1,5 = telo, visoko dva bloka, potrebno, da vidiš vrh bloka na svoji plasti in stopiš nanj); neobvezno |
| `gravity` | Število | `0` | Pospešek navzdol v celicah/korak² za dejanje »Skoči« ter za težnost in padanje (stopnja 7a). 0 (privzeto) ohrani izvorno hipno oprijemanje dejanja »Premakni s trkom«, brez skokov; običajna vrednost je okoli 0,04; neobvezno |
| `inventory` | Da/Ne | Ne | Vklopljeno = »Razbij blok« pobere, kar razbije, »Postavi blok« pa jemlje iz tega inventarja (stopnja 7c); izklopljeno (privzeto) = neomejeno postavljanje kot v ustvarjalnem načinu, tako kot pred stopnjo 7c; neobvezno |
| `generate` | Da/Ne | Ne | Vklopljeno = med raziskovanjem se okoli kamere proceduralno ustvarja valovit teren (stopnja 7e) z uporabo spodnjega semena; izklopljeno (privzeto) = obstajajo le ročno postavljeni ali naloženi bloki, tako kot pred stopnjo 7e; neobvezno |
| `seed` | Število | `0` | Seme sveta za »Ustvari teren« – isto seme na tej platformi vedno ustvari enak teren. Prezrto, dokler je ustvarjanje terena izklopljeno; neobvezno |

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

### Skoči

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `jump` |
| **Ikona** | ⬆️ |
| **Kategorija** | Pogled 3D |

Kameri Block World doda hitrost navzgor – le kadar stoji na trdnih tleh (brez dvojnih skokov in skokov v zraku). Zahteva nastavljeno težnost (»Vklopi pogled Block World«) in dejanje »Uporabi težnost« v dogodku Korak, sicer je nič ne spravi nazaj na tla

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `0.35` | Začetna hitrost navzgor, v celicah na korak; neobvezno |

### Naloži svet Block World

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `load_block_world` |
| **Ikona** | 📂 |
| **Kategorija** | Pogled 3D |

V trenutno sobo naloži vnaprej pripravljen svet (bloke, ki jih je postavil generator ali so napisani ročno) in nadomesti bloke, ki so bili v njej

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `data_file` | Besedilo | — | Pot do datoteke JSON s svetom blokov, glede na mapo projekta (npr. blocks/room1.json) |

### Poglej gor / dol

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_look_pitch` |
| **Ikona** | 🔭 |
| **Kategorija** | Pogled 3D |

Nagne pogled Block World navzgor ali navzdol

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `pitch` | Število | `0` | Stopinje za pogled navzgor (+) ali navzdol (−); 0 je vodoravno |
| `relative` | Da/Ne | Ne | Vklopljeno = prišteje trenutnemu kotu, za upravljanje pogleda s pridržanjem; izklopljeno = kot nastavi neposredno; neobvezno |

### Premakni s trkom

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_and_collide` |
| **Ikona** | 🚶 |
| **Kategorija** | Pogled 3D |

Naredi korak premika, preverjen glede na mrežo blokov, s samodejnim oprijemom (stopi za en blok navzgor, pade poljubno globoko): če je to kamera Block World, ji sledi tudi njen z_layer

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `dx` | Število | `0` | Za koliko se v tem koraku premakne po x, v slikovnih točkah |
| `dy` | Število | `0` | Za koliko se v tem koraku premakne po y, v slikovnih točkah |
| `collide` | Da/Ne | Da | Izklopljeno povsem prezre mrežo blokov (letenje / razhroščevanje); neobvezno |

### Postavi blok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `place_block` |
| **Ikona** | 🧱 |
| **Kategorija** | Pogled 3D |

Postavi blok v prazno celico, v katero je usmerjena kamera: brez omejitev, razen če je vklopljen inventar v »Vklopi pogled Block World« – takrat jemlje iz tega, kar je pobralo »Razbij blok«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block` | Izbira | `stone` | Katero vrsto bloka postaviti; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Število | `5` | Kako daleč naprej lahko gradiš, v celicah mreže; neobvezno |

### Izberi mesto v vrstici

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `select_hotbar_slot` |
| **Ikona** | 🔢 |
| **Kategorija** | Pogled 3D |

Izbere, kateri blok je izbran v vrstici za hiter dostop in s katerim bo gradilo »Postavi blok«: za to nastavi parameter Blok v »Postavi blok« na izraz »hotbar_block«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `index` | Število | `0` | Zaporedna številka mesta v vrstici za hiter dostop, ki se na obeh koncih ovije |
| `relative` | Da/Ne | Ne | Vklopljeno = prišteje trenutnemu mestu, za listanje s [ ] ali kolescem miške; izklopljeno = skoči neposredno nanj; neobvezno |

### Nastavi zaščito blokov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_block_protection` |
| **Ikona** | 🔒 |
| **Kategorija** | Pogled 3D |

Zahteva določeno vrsto bloka v inventarju, preden lahko »Razbij blok« odstrani izbrano vrsto bloka: pokliči enkrat za vsako zaščiteno vrsto; zahteva vklopljen inventar v »Vklopi pogled Block World«, sicer pogoja ni mogoče nikoli izpolniti

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block_type` | Izbira | `diamond_block` | Katera vrsta bloka postane zaščitena; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Izbira | `gold_block` | Katera vrsta bloka mora biti v inventarju, da ga je mogoče razbiti; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Nastavi nagrado za blok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_block_reward` |
| **Ikona** | 💎 |
| **Kategorija** | Pogled 3D |

Dodeli točke, ko »Razbij blok« uspešno odstrani izbrano vrsto bloka: pokliči enkrat za vsako nagrajeno vrsto (na primer v dogodku Ustvari v sobi, takoj za »Vklopi pogled Block World«). Rudo ali dragi kamen za izkopavanje postavi v teren, vpiši njegovo nagrado – in razbijanje samodejno dodeli točke

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block_type` | Izbira | `diamond_block` | Katera vrsta bloka ob razbitju prinese točke; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Število | `10` | Točke za vsak razbit blok te vrste |

### Nastavi recept za izdelavo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_crafting_recipe` |
| **Ikona** | 🛠️ |
| **Kategorija** | Pogled 3D |

Registrira recept, ki ga lahko uporabi »Izdelaj predmet«: pokliči enkrat za vsako vrsto izdelka (na primer v dogodku Ustvari v sobi, takoj za »Vklopi pogled Block World«). Do tri reže za sestavine; pusti reži 2/3 prazni, če recept potrebuje le eno ali dve

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `output` | Izbira | `brick` | Which block type this recipe produces; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `output_count` | Število | `1` | How many of Output Block one craft produces |
| `input_1` | Izbira | `stone` | First required block type; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `input_1_count` | Število | `1` | How many of Input 1 the recipe consumes |
| `input_2` | Izbira | — | Second required block type (blank = unused); Izbire: ``, `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow`; neobvezno |
| `input_2_count` | Število | `1` | How many of Input 2 the recipe consumes; neobvezno |
| `input_3` | Izbira | — | Third required block type (blank = unused); Izbire: ``, `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow`; neobvezno |
| `input_3_count` | Število | `1` | How many of Input 3 the recipe consumes; neobvezno |

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
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (15)
- [Delci](Full-Action-Reference-Particles_sl) (8)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
