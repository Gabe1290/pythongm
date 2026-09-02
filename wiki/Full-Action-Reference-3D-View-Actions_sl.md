# Pogled 3D

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Apply Gravity

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `apply_gravity` |
| **Ikona** | ⬇️ |
| **Kategorija** | Pogled 3D |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Parametri:* brez

### Break Block

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `break_block` |
| **Ikona** | ⛏️ |
| **Kategorija** | Pogled 3D |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `reach` | Število | `5` | How many cells ahead you can reach, in grid cells; neobvezno |

### Draw Block World HUD

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_block_world_hud` |
| **Ikona** | 🧰 |
| **Kategorija** | Pogled 3D |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `slot_size` | Število | `40` | Width and height of each hotbar slot, in pixels; neobvezno |
| `gap` | Število | `6` | Space between hotbar slots, in pixels; neobvezno |
| `margin_bottom` | Število | `16` | Space between the hotbar and the bottom of the screen; neobvezno |
| `back_color` | Barva | `#202020` | Fill colour of an unselected slot; neobvezno |
| `selected_color` | Barva | `#ffd040` | Fill colour of the currently selected slot; neobvezno |
| `border_color` | Barva | `#ffffff` | Outline colour of every slot; neobvezno |
| `text_color` | Barva | `#ffffff` | Colour of each slot's block-type label; neobvezno |
| `crosshair_size` | Število | `12` | Width and height of the centre crosshair, in pixels; neobvezno |
| `crosshair_color` | Barva | `#ffffff` | Colour of the centre crosshair; neobvezno |

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
| `mark_object` | Predmet | — | Also dot every instance of this object onto the map (blank = show walls and player only); neobvezno |
| `mark_color` | Barva | `#40e0ff` | Colour of the Mark Object dots; neobvezno |
| `mark_object_2` | Predmet | — | A second object to dot on, in its own colour; neobvezno |
| `mark_color_2` | Barva | `#ff5050` | Colour of the Mark Object 2 dots; neobvezno |

### Enable Block World View

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `enable_block_world_view` |
| **Ikona** | 🧱 |
| **Kategorija** | Pogled 3D |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `enable` | Da/Ne | Da | On = first-person block view; off = normal top-down |
| `camera_object` | Predmet | — | Predmet, čigar položaj + kot pogleda je kamera (prazno = predmet, ki izvaja to dejanje); neobvezno |
| `z_layer` | Število | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); neobvezno |
| `fov` | Število | `66` | Vodoravno vidno polje v stopinjah; neobvezno |
| `render_distance` | Število | `20` | Največja dolžina žarka v celicah mreže; neobvezno |
| `cell_size` | Število | `32` | Grid cell size in pixels (match the block-placement grid); neobvezno |
| `columns` | Število | `320` | Zaslonski stolpci za raycast (manj = hitreje/bolj grobo); neobvezno |
| `wall_color` | Barva | `#8a8a8a` | Flat colour used only if Textured Blocks is off; neobvezno |
| `floor_color` | Barva | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); neobvezno |
| `ceiling_color` | Barva | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); neobvezno |
| `pitch` | Število | `0` | Degrees to look up (+) or down (-); 0 is level; neobvezno |
| `wall_textured` | Da/Ne | Da | Off forces flat block colours even though real textures are available; neobvezno |
| `top_cast_res` | Število | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); neobvezno |
| `eye_height` | Število | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); neobvezno |
| `gravity` | Število | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; neobvezno |
| `inventory` | Da/Ne | Ne | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; neobvezno |
| `generate` | Da/Ne | Ne | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; neobvezno |
| `seed` | Število | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; neobvezno |

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

### Jump

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `jump` |
| **Ikona** | ⬆️ |
| **Kategorija** | Pogled 3D |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `0.35` | Initial upward velocity, in cells/step; neobvezno |

### Load Block World

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `load_block_world` |
| **Ikona** | 📂 |
| **Kategorija** | Pogled 3D |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `data_file` | Besedilo | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_look_pitch` |
| **Ikona** | 🔭 |
| **Kategorija** | Pogled 3D |

Tilt the block-world view up or down

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `pitch` | Število | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Da/Ne | Ne | On = add to the current angle, for a look control you can hold down; off = set it outright; neobvezno |

### Move And Collide

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_and_collide` |
| **Ikona** | 🚶 |
| **Kategorija** | Pogled 3D |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `dx` | Število | `0` | How far to move on x this step, in pixels |
| `dy` | Število | `0` | How far to move on y this step, in pixels |
| `collide` | Da/Ne | Da | Off ignores the block grid entirely (flying/debug); neobvezno |

### Place Block

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `place_block` |
| **Ikona** | 🧱 |
| **Kategorija** | Pogled 3D |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block` | Izbira | `stone` | Which kind of block to place; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Število | `5` | How many cells ahead you can build, in grid cells; neobvezno |

### Select Hotbar Slot

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `select_hotbar_slot` |
| **Ikona** | 🔢 |
| **Kategorija** | Pogled 3D |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `index` | Število | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Da/Ne | Ne | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; neobvezno |

### Set Block Protection

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_block_protection` |
| **Ikona** | 🔒 |
| **Kategorija** | Pogled 3D |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block_type` | Izbira | `diamond_block` | Which block type becomes protected; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Izbira | `gold_block` | Which block type must be in inventory to break it; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_block_reward` |
| **Ikona** | 💎 |
| **Kategorija** | Pogled 3D |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `block_type` | Izbira | `diamond_block` | Which block type awards score when broken; Izbire: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Število | `10` | Score awarded per block of this type broken |

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
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
