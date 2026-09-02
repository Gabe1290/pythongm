# Vista 3D

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Apply Gravity

| Proprietà | Valore |
|----------|-------|
| **Nome** | `apply_gravity` |
| **Icona** | ⬇️ |
| **Categoria** | Vista 3D |

Continuous falling/landing physics for the block-world camera -- bind in the Step event (not a keyboard-held event) so it runs every frame regardless of movement input. No-op unless Enable Block World View's Gravity parameter is set above 0

*Parametri:* nessuno

### Break Block

| Proprietà | Valore |
|----------|-------|
| **Nome** | `break_block` |
| **Icona** | ⛏️ |
| **Categoria** | Vista 3D |

Remove the block the camera is looking at -- also picks it up into the calling instance's inventory if Enable Block World View's Inventory is on, and refuses if the block is protected (Set Block Protection) and the required key isn't in inventory

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `reach` | Numero | `5` | How many cells ahead you can reach, in grid cells; facoltativo |

### Draw Block World HUD

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_block_world_hud` |
| **Icona** | 🧰 |
| **Categoria** | Vista 3D |

Draw a crosshair plus a hotbar strip (the selected slot highlighted, with a count on each slot once Inventory is on) -- call from the player/camera object's own Draw event

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `slot_size` | Numero | `40` | Width and height of each hotbar slot, in pixels; facoltativo |
| `gap` | Numero | `6` | Space between hotbar slots, in pixels; facoltativo |
| `margin_bottom` | Numero | `16` | Space between the hotbar and the bottom of the screen; facoltativo |
| `back_color` | Colore | `#202020` | Fill colour of an unselected slot; facoltativo |
| `selected_color` | Colore | `#ffd040` | Fill colour of the currently selected slot; facoltativo |
| `border_color` | Colore | `#ffffff` | Outline colour of every slot; facoltativo |
| `text_color` | Colore | `#ffffff` | Colour of each slot's block-type label; facoltativo |
| `crosshair_size` | Numero | `12` | Width and height of the centre crosshair, in pixels; facoltativo |
| `crosshair_color` | Colore | `#ffffff` | Colour of the centre crosshair; facoltativo |

### Disegna HUD DOOM

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_doom_hud` |
| **Icona** | 🎯 |
| **Categoria** | Vista 3D |

Disegna una barra di stato inferiore in stile DOOM (barra della salute + numero, punteggio, vite, un contatore di obiettivo e un'icona del volto reattiva alla salute) sopra la vista raycast

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della barra, in pixel schermo |
| `y` | Numero | `-1` | Bordo superiore della barra; un valore negativo la allinea automaticamente in fondo alla finestra, sotto la vista ridotta; facoltativo |
| `width` | Numero | `0` | Larghezza della barra (0 = larghezza piena della finestra); facoltativo |
| `height` | Numero | `42` | Altezza della barra; mantienila coerente con la fascia viewport_height riservata in enable_raycast_view; facoltativo |
| `back_color` | Colore | `#101010` | Pannello di sfondo della barra; facoltativo |
| `divider_color` | Colore | `#505050` | Bordo superiore e sfondo della barra della salute; facoltativo |
| `text_color` | Colore | `#ffffff` | Colore di tutto il testo della barra; facoltativo |
| `health_label` | Testo | `Health` | facoltativo |
| `health_bar_width` | Numero | `90` | facoltativo |
| `health_bar_height` | Numero | `14` | facoltativo |
| `bar_color` | Colore | `#20c020` | Colore di riempimento della barra della salute; facoltativo |
| `face_sprite` | Sprite | — | Striscia orizzontale di fotogrammi del volto, il più sano per primo (vuoto = nessuna icona del volto); facoltativo |
| `face_frames` | Numero | `4` | Quanti fotogrammi ha la striscia del volto; la salute è distribuita uniformemente tra essi; facoltativo |
| `score_label` | Testo | `Score: ` | facoltativo |
| `lives_sprite` | Sprite | — | Sprite disegnato una volta per ogni vita rimanente; facoltativo |
| `lives_scale` | Numero | `1.0` | facoltativo |
| `objective_value` | Testo | `0` | Espressione mostrata dopo l'etichetta dell'obiettivo (associa la tua variabile chiave/missione); facoltativo |
| `objective_label` | Testo | `Keys: ` | facoltativo |

### Disegna minimappa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_minimap` |
| **Icona** | 🗺️ |
| **Categoria** | Vista 3D |

Disegna una minimappa orientata a nord dei muri della stanza raycast, con un indicatore che mostra dove si trova la camera e in quale direzione guarda

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della minimappa, in pixel schermo |
| `y` | Numero | `0` | Bordo superiore della minimappa, in pixel schermo |
| `size` | Numero | `120` | Larghezza e altezza del quadrato della minimappa, in pixel; facoltativo |
| `back_color` | Colore | `#101018` | Colore del pannello dietro la mappa; facoltativo |
| `wall_color` | Colore | `#8080a0` | Colore delle linee dei muri; facoltativo |
| `player_color` | Colore | `#ffd040` | Colore dell'indicatore della camera e della sua linea di direzione; facoltativo |
| `mark_object` | Oggetto | — | Also dot every instance of this object onto the map (blank = show walls and player only); facoltativo |
| `mark_color` | Colore | `#40e0ff` | Colour of the Mark Object dots; facoltativo |
| `mark_object_2` | Oggetto | — | A second object to dot on, in its own colour; facoltativo |
| `mark_color_2` | Colore | `#ff5050` | Colour of the Mark Object 2 dots; facoltativo |

### Enable Block World View

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_block_world_view` |
| **Icona** | 🧱 |
| **Categoria** | Vista 3D |

Render the room as a first-person voxel view (single layer) instead of the top-down view

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | On = first-person block view; off = normal top-down |
| `camera_object` | Oggetto | — | Oggetto la cui posizione + angolo di sguardo è la camera (vuoto = l'oggetto che esegue questa azione); facoltativo |
| `z_layer` | Numero | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); facoltativo |
| `fov` | Numero | `66` | Campo visivo orizzontale in gradi; facoltativo |
| `render_distance` | Numero | `20` | Lunghezza massima del raggio in celle della griglia; facoltativo |
| `cell_size` | Numero | `32` | Grid cell size in pixels (match the block-placement grid); facoltativo |
| `columns` | Numero | `320` | Colonne dello schermo per il raycast (meno = più veloce/più grezzo); facoltativo |
| `wall_color` | Colore | `#8a8a8a` | Flat colour used only if Textured Blocks is off; facoltativo |
| `floor_color` | Colore | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); facoltativo |
| `ceiling_color` | Colore | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); facoltativo |
| `pitch` | Numero | `0` | Degrees to look up (+) or down (-); 0 is level; facoltativo |
| `wall_textured` | Sì/No | Sì | Off forces flat block colours even though real textures are available; facoltativo |
| `top_cast_res` | Numero | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); facoltativo |
| `eye_height` | Numero | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); facoltativo |
| `gravity` | Numero | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; facoltativo |
| `inventory` | Sì/No | No | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; facoltativo |
| `generate` | Sì/No | No | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; facoltativo |
| `seed` | Numero | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; facoltativo |

### Abilita vista Raycast

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_raycast_view` |
| **Icona** | 🕹️ |
| **Categoria** | Vista 3D |

Renderizza la stanza come vista 3D in prima persona in stile Doom/Wolfenstein (muri, cielo, pavimento) invece della vista dall'alto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = vista raycast in prima persona; disattivo = normale vista dall'alto |
| `camera_object` | Oggetto | — | Oggetto la cui posizione + angolo di sguardo è la camera (vuoto = l'oggetto che esegue questa azione); facoltativo |
| `fov` | Numero | `66` | Campo visivo orizzontale in gradi; facoltativo |
| `render_distance` | Numero | `20` | Lunghezza massima del raggio in celle della griglia; facoltativo |
| `cell_size` | Numero | `32` | Dimensione della cella della griglia in pixel (corrisponde alla griglia di posizionamento dei muri); facoltativo |
| `columns` | Numero | `320` | Colonne dello schermo per il raycast (meno = più veloce/più grezzo); facoltativo |
| `wall_color` | Colore | `#993333` | Colore uniforme dei muri quando non è impostata una texture di muro; facoltativo |
| `floor_color` | Colore | `#464632` | Colore uniforme del pavimento quando non è impostata una texture di pavimento; facoltativo |
| `ceiling_color` | Colore | `#87CEEB` | Colore uniforme del soffitto quando non è impostata una texture di cielo/soffitto; facoltativo |
| `wall_texture` | Sprite | — | Sprite per texturizzare ogni muro (vuoto = colore uniforme); facoltativo |
| `sky_texture` | Sprite | — | Sprite per un cielo panoramico sopra il soffitto (vuoto = uniforme); facoltativo |
| `floor_texture` | Sprite | — | Sprite proiettato sul pavimento (vuoto = colore uniforme); facoltativo |
| `ceiling_texture` | Sprite | — | Sprite proiettato sul soffitto quando non è impostato un cielo; facoltativo |
| `wall_textured` | Sì/No | Sì | Disattivo forza colori uniformi dei muri anche quando è impostata una texture; facoltativo |
| `floor_cast_res` | Numero | `4` | Sottocampionamento del pavimento proiettato (più alto = più veloce + più grezzo); facoltativo |
| `viewport_height` | Numero | `0` | Riduci la vista 3D a questa altezza in pixel (letterbox), riservando la fascia sottostante per una barra di stato in stile DOOM (0 = altezza piena della finestra, invariato); facoltativo |

### Jump

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump` |
| **Icona** | ⬆️ |
| **Categoria** | Vista 3D |

Give the block-world camera upward velocity -- only while standing on solid ground (no double/air jumps). Needs Gravity configured (Enable Block World View) and Apply Gravity bound in the Step event, or nothing brings it back down

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0.35` | Initial upward velocity, in cells/step; facoltativo |

### Load Block World

| Proprietà | Valore |
|----------|-------|
| **Nome** | `load_block_world` |
| **Icona** | 📂 |
| **Categoria** | Vista 3D |

Load a pre-authored world (blocks placed by a generator or hand-authored file) into the current room, replacing whatever blocks are there

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `data_file` | Testo | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Look Up / Down

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_look_pitch` |
| **Icona** | 🔭 |
| **Categoria** | Vista 3D |

Tilt the block-world view up or down

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `pitch` | Numero | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Sì/No | No | On = add to the current angle, for a look control you can hold down; off = set it outright; facoltativo |

### Move And Collide

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_and_collide` |
| **Icona** | 🚶 |
| **Categoria** | Vista 3D |

Move this step, checked against the block grid, with automatic footing (step up one block, drop any distance) -- the camera's z_layer follows if this is the block-world camera

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `dx` | Numero | `0` | How far to move on x this step, in pixels |
| `dy` | Numero | `0` | How far to move on y this step, in pixels |
| `collide` | Sì/No | Sì | Off ignores the block grid entirely (flying/debug); facoltativo |

### Place Block

| Proprietà | Valore |
|----------|-------|
| **Nome** | `place_block` |
| **Icona** | 🧱 |
| **Categoria** | Vista 3D |

Put a block in the empty cell the camera is looking at -- unlimited unless Enable Block World View's Inventory is on, which draws from what Break Block has picked up

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block` | Scelta | `stone` | Which kind of block to place; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Numero | `5` | How many cells ahead you can build, in grid cells; facoltativo |

### Select Hotbar Slot

| Proprietà | Valore |
|----------|-------|
| **Nome** | `select_hotbar_slot` |
| **Icona** | 🔢 |
| **Categoria** | Vista 3D |

Choose which block the hotbar has selected, for place_block to build with -- bind Place Block's Block parameter to the expression "hotbar_block" to use it

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `index` | Numero | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Sì/No | No | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; facoltativo |

### Set Block Protection

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_block_protection` |
| **Icona** | 🔒 |
| **Categoria** | Vista 3D |

Require a specific block type in inventory before Break Block can remove a chosen block type -- call once per protected type, needs Enable Block World View's Inventory on or the requirement can never be satisfied

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block_type` | Scelta | `diamond_block` | Which block type becomes protected; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Scelta | `gold_block` | Which block type must be in inventory to break it; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Set Block Reward

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_block_reward` |
| **Icona** | 💎 |
| **Categoria** | Vista 3D |

Award score when Break Block successfully removes a chosen block type -- call once per rewarded type (e.g. in the room's create event, right after Enable Block World View). A mine-to-collect ore/gem block: place it in the terrain, register its reward, and breaking it awards the points automatically

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block_type` | Scelta | `diamond_block` | Which block type awards score when broken; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Numero | `10` | Score awarded per block of this type broken |

### Imposta angolo di sguardo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_facing_angle` |
| **Icona** | 🧭 |
| **Categoria** | Vista 3D |

Imposta la direzione dello sguardo dell'istanza per una camera raycast (in prima persona) — indipendente dalla velocità di movimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `angle` | Numero | `0` | Gradi (0=destra, 90=su, 180=sinistra, 270=giù) |
| `relative` | Sì/No | No | Aggiungi all'angolo di sguardo attuale invece di sostituirlo; facoltativo |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Particles](Full-Action-Reference-Particles_it) (8)
- [Réseau](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
