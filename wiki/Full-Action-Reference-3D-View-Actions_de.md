# 3D-Ansicht

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Schwerkraft anwenden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `apply_gravity` |
| **Symbol** | ⬇️ |
| **Kategorie** | 3D-Ansicht |

Kontinuierliche Fall- und Landephysik für die Block-World-Kamera – im Schritt-Ereignis einbinden (nicht in einem Ereignis für gehaltene Tasten), damit sie unabhängig von der Bewegungseingabe in jedem Bild läuft. Ohne Wirkung, solange der Parameter „Schwerkraft“ von „Block-World-Ansicht aktivieren“ nicht größer als 0 ist

*Parameter:* keine

### Block abbauen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `break_block` |
| **Symbol** | ⛏️ |
| **Kategorie** | 3D-Ansicht |

Entfernt den Block, den die Kamera anvisiert – legt ihn außerdem ins Inventar der aufrufenden Instanz, wenn das Inventar von „Block-World-Ansicht aktivieren“ eingeschaltet ist, und verweigert den Abbau, wenn der Block geschützt ist („Blockschutz festlegen“) und der benötigte Block nicht im Inventar liegt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `reach` | Zahl | `5` | How many cells ahead you can reach, in grid cells; optional |

### Block-World-HUD zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_block_world_hud` |
| **Symbol** | 🧰 |
| **Kategorie** | 3D-Ansicht |

Zeichnet ein Fadenkreuz und eine Schnellzugriffsleiste (der gewählte Platz hervorgehoben, mit einer Anzahl pro Platz, sobald das Inventar aktiv ist) – aus dem Zeichnen-Ereignis des Spieler- bzw. Kameraobjekts aufrufen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `slot_size` | Zahl | `40` | Width and height of each hotbar slot, in pixels; optional |
| `gap` | Zahl | `6` | Space between hotbar slots, in pixels; optional |
| `margin_bottom` | Zahl | `16` | Space between the hotbar and the bottom of the screen; optional |
| `back_color` | Farbe | `#202020` | Fill colour of an unselected slot; optional |
| `selected_color` | Farbe | `#ffd040` | Fill colour of the currently selected slot; optional |
| `border_color` | Farbe | `#ffffff` | Outline colour of every slot; optional |
| `text_color` | Farbe | `#ffffff` | Colour of each slot's block-type label; optional |
| `crosshair_size` | Zahl | `12` | Width and height of the centre crosshair, in pixels; optional |
| `crosshair_color` | Farbe | `#ffffff` | Colour of the centre crosshair; optional |

### DOOM-HUD zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_doom_hud` |
| **Symbol** | 🎯 |
| **Kategorie** | 3D-Ansicht |

Eine untere Statusleiste im DOOM-Stil (Gesundheitsbalken + Zahl, Punkte, Leben, ein Zielzähler und ein auf die Gesundheit reagierendes Gesichtssymbol) über der Raycast-Ansicht zeichnen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Leiste, in Bildschirmpixeln |
| `y` | Zahl | `-1` | Oberer Rand der Leiste; ein negativer Wert richtet sie automatisch am unteren Fensterrand aus, unter dem verkleinerten Ansichtsfenster; optional |
| `width` | Zahl | `0` | Leistenbreite (0 = volle Fensterbreite); optional |
| `height` | Zahl | `42` | Leistenhöhe; halten Sie sie mit dem in enable_raycast_view reservierten viewport_height-Band abgestimmt; optional |
| `back_color` | Farbe | `#101010` | Hintergrundpanel der Leiste; optional |
| `divider_color` | Farbe | `#505050` | Oberer Rand und Hintergrund des Gesundheitsbalkens; optional |
| `text_color` | Farbe | `#ffffff` | Farbe des gesamten Leistentexts; optional |
| `health_label` | Text | `Health` | optional |
| `health_bar_width` | Zahl | `90` | optional |
| `health_bar_height` | Zahl | `14` | optional |
| `bar_color` | Farbe | `#20c020` | Füllfarbe des Gesundheitsbalkens; optional |
| `face_sprite` | Sprite | — | Horizontaler Streifen von Gesichtsbildern, das gesündeste zuerst (leer = kein Gesichtssymbol); optional |
| `face_frames` | Zahl | `4` | Wie viele Bilder der Gesichtsstreifen hat; die Gesundheit wird gleichmäßig auf sie verteilt; optional |
| `score_label` | Text | `Score: ` | optional |
| `lives_sprite` | Sprite | — | Sprite, das einmal pro verbleibendem Leben gezeichnet wird; optional |
| `lives_scale` | Zahl | `1.0` | optional |
| `objective_value` | Text | `0` | Ausdruck, der nach der Zielbeschriftung angezeigt wird (binden Sie Ihre eigene Schlüssel-/Quest-Variable ein); optional |
| `objective_label` | Text | `Keys: ` | optional |

### Minikarte zeichnen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `draw_minimap` |
| **Symbol** | 🗺️ |
| **Kategorie** | 3D-Ansicht |

Eine nach Norden ausgerichtete Minikarte der Wände des Raycast-Raums zeichnen, mit einer Markierung, die zeigt, wo die Kamera ist und in welche Richtung sie blickt

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `x` | Zahl | `0` | Linker Rand der Minikarte, in Bildschirmpixeln |
| `y` | Zahl | `0` | Oberer Rand der Minikarte, in Bildschirmpixeln |
| `size` | Zahl | `120` | Breite und Höhe des Minikarten-Quadrats, in Pixeln; optional |
| `back_color` | Farbe | `#101018` | Panelfarbe hinter der Karte; optional |
| `wall_color` | Farbe | `#8080a0` | Farbe der Wandlinien; optional |
| `player_color` | Farbe | `#ffd040` | Farbe der Kameramarkierung und ihrer Blickrichtungslinie; optional |
| `mark_object` | Objekt | — | Also dot every instance of this object onto the map (blank = show walls and player only); optional |
| `mark_color` | Farbe | `#40e0ff` | Colour of the Mark Object dots; optional |
| `mark_object_2` | Objekt | — | A second object to dot on, in its own colour; optional |
| `mark_color_2` | Farbe | `#ff5050` | Colour of the Mark Object 2 dots; optional |

### Block-World-Ansicht aktivieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `enable_block_world_view` |
| **Symbol** | 🧱 |
| **Kategorie** | 3D-Ansicht |

Stellt den Raum als First-Person-Voxelansicht (eine einzelne Ebene) dar statt in der Draufsicht

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `enable` | Ja/Nein | Ja | On = first-person block view; off = normal top-down |
| `camera_object` | Objekt | — | Objekt, dessen Position + Blickwinkel die Kamera ist (leer = das Objekt, das diese Aktion ausführt); optional |
| `z_layer` | Zahl | `0` | Which world layer to render (Phase 2a renders exactly one layer -- no looking up/down yet); optional |
| `fov` | Zahl | `66` | Horizontales Sichtfeld in Grad; optional |
| `render_distance` | Zahl | `20` | Maximale Strahllänge in Gitterzellen; optional |
| `cell_size` | Zahl | `32` | Grid cell size in pixels (match the block-placement grid); optional |
| `columns` | Zahl | `320` | Bildschirmspalten zum Raycasten (weniger = schneller/grobkörniger); optional |
| `wall_color` | Farbe | `#8a8a8a` | Flat colour used only if Textured Blocks is off; optional |
| `floor_color` | Farbe | `#3a2f1c` | Flat floor colour (Phase 2a has no floor texturing yet); optional |
| `ceiling_color` | Farbe | `#87CEEB` | Flat ceiling/sky colour (Phase 2a has no sky yet); optional |
| `pitch` | Zahl | `0` | Degrees to look up (+) or down (-); 0 is level; optional |
| `wall_textured` | Ja/Nein | Ja | Off forces flat block colours even though real textures are available; optional |
| `top_cast_res` | Zahl | `4` | Top/bottom face texture detail: rows sampled per N screen rows (higher = faster + chunkier, 0 = flat average colour instead of texture); optional |
| `eye_height` | Zahl | `1.5` | Camera height above the layer it stands on, in cells (1.5 = a two-block-tall body, needed to see the top of a block on your own layer and stack onto it); optional |
| `gravity` | Zahl | `0` | Downward acceleration in cells/step^2 for the Jump action + gravity/falling (Tier 7a). 0 (default) keeps Move And Collide's original instant-footing behaviour with no jumping; a typical value is around 0.04; optional |
| `inventory` | Ja/Nein | Nein | On = Break Block picks up what it breaks and Place Block consumes from that inventory (Tier 7c); off (default) = unlimited creative-mode placing, unchanged from before Tier 7c; optional |
| `generate` | Ja/Nein | Nein | On = procedurally generate rolling terrain around the camera as it explores (Tier 7e), using Seed below; off (default) = only hand-placed/loaded blocks exist, unchanged from before Tier 7e; optional |
| `seed` | Zahl | `0` | World seed for Generate Terrain -- the same seed always produces the same terrain on this target. Ignored unless Generate Terrain is on; optional |

### Raycast-Ansicht aktivieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `enable_raycast_view` |
| **Symbol** | 🕹️ |
| **Kategorie** | 3D-Ansicht |

Den Raum als First-Person-3D-Ansicht im Doom/Wolfenstein-Stil (Wände, Himmel, Boden) statt als Draufsicht darstellen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `enable` | Ja/Nein | Ja | An = First-Person-Raycast-Ansicht; aus = normale Draufsicht |
| `camera_object` | Objekt | — | Objekt, dessen Position + Blickwinkel die Kamera ist (leer = das Objekt, das diese Aktion ausführt); optional |
| `fov` | Zahl | `66` | Horizontales Sichtfeld in Grad; optional |
| `render_distance` | Zahl | `20` | Maximale Strahllänge in Gitterzellen; optional |
| `cell_size` | Zahl | `32` | Gitterzellengröße in Pixeln (an das Wandplatzierungsgitter angepasst); optional |
| `columns` | Zahl | `320` | Bildschirmspalten zum Raycasten (weniger = schneller/grobkörniger); optional |
| `wall_color` | Farbe | `#993333` | Einfarbige Wandfarbe, wenn keine Wandtextur gesetzt ist; optional |
| `floor_color` | Farbe | `#464632` | Einfarbige Bodenfarbe, wenn keine Bodentextur gesetzt ist; optional |
| `ceiling_color` | Farbe | `#87CEEB` | Einfarbige Deckenfarbe, wenn keine Himmel-/Deckentextur gesetzt ist; optional |
| `wall_texture` | Sprite | — | Sprite zum Texturieren jeder Wand (leer = einfarbig); optional |
| `sky_texture` | Sprite | — | Sprite für einen schwenkenden Himmel über der Decke (leer = einfarbig); optional |
| `floor_texture` | Sprite | — | Auf den Boden projiziertes Sprite (leer = einfarbig); optional |
| `ceiling_texture` | Sprite | — | Auf die Decke projiziertes Sprite, wenn kein Himmel gesetzt ist; optional |
| `wall_textured` | Ja/Nein | Ja | Aus erzwingt einfarbige Wandfarben, auch wenn eine Textur gesetzt ist; optional |
| `floor_cast_res` | Zahl | `4` | Boden-Downsampling (höher = schneller + grobkörniger); optional |
| `viewport_height` | Zahl | `0` | Die 3D-Ansicht auf diese Pixelhöhe verkleinern (Letterbox) und das Band darunter für eine DOOM-Statusleiste reservieren (0 = volle Fensterhöhe, unverändert); optional |

### Springen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `jump` |
| **Symbol** | ⬆️ |
| **Kategorie** | 3D-Ansicht |

Gibt der Block-World-Kamera Geschwindigkeit nach oben – nur solange sie auf festem Boden steht (kein Doppel- oder Luftsprung). Erfordert eine eingestellte Schwerkraft („Block-World-Ansicht aktivieren“) und „Schwerkraft anwenden“ im Schritt-Ereignis, sonst kommt nichts wieder herunter

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `speed` | Zahl | `0.35` | Initial upward velocity, in cells/step; optional |

### Block-World laden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `load_block_world` |
| **Symbol** | 📂 |
| **Kategorie** | 3D-Ansicht |

Lädt eine vorbereitete Welt (von einem Generator gesetzte oder von Hand erstellte Blöcke) in den aktuellen Raum und ersetzt dabei die vorhandenen Blöcke

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `data_file` | Text | — | Path to a block-world JSON file, relative to the project folder (e.g. blocks/room1.json) |

### Nach oben / unten schauen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_look_pitch` |
| **Symbol** | 🔭 |
| **Kategorie** | 3D-Ansicht |

Neigt die Block-World-Ansicht nach oben oder unten

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `pitch` | Zahl | `0` | Degrees to look up (+) or down (-); 0 is level |
| `relative` | Ja/Nein | Nein | On = add to the current angle, for a look control you can hold down; off = set it outright; optional |

### Bewegen mit Kollision

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `move_and_collide` |
| **Symbol** | 🚶 |
| **Kategorie** | 3D-Ansicht |

Bewegt diesen Schritt, gegen das Blockgitter geprüft, mit automatischem Tritt (einen Block hoch steigen, beliebig tief fallen) – die z_layer der Kamera folgt mit, wenn dies die Block-World-Kamera ist

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `dx` | Zahl | `0` | How far to move on x this step, in pixels |
| `dy` | Zahl | `0` | How far to move on y this step, in pixels |
| `collide` | Ja/Nein | Ja | Off ignores the block grid entirely (flying/debug); optional |

### Block setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `place_block` |
| **Symbol** | 🧱 |
| **Kategorie** | 3D-Ansicht |

Setzt einen Block in die leere Zelle, die die Kamera anvisiert – unbegrenzt, außer das Inventar von „Block-World-Ansicht aktivieren“ ist eingeschaltet; dann wird aus dem entnommen, was „Block abbauen“ eingesammelt hat

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `block` | Auswahl | `stone` | Which kind of block to place; Auswahl: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Zahl | `5` | How many cells ahead you can build, in grid cells; optional |

### Schnellleisten-Platz wählen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `select_hotbar_slot` |
| **Symbol** | 🔢 |
| **Kategorie** | 3D-Ansicht |

Wählt, welcher Block in der Schnellzugriffsleiste ausgewählt ist, damit „Block setzen“ damit baut – dazu den Block-Parameter von „Block setzen“ auf den Ausdruck „hotbar_block“ setzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `index` | Zahl | `0` | Hotbar slot index, wrapping around at either end |
| `relative` | Ja/Nein | Nein | On = add to the current slot, for cycling with [ ] / scroll-wheel style controls; off = jump to it; optional |

### Blockschutz festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_block_protection` |
| **Symbol** | 🔒 |
| **Kategorie** | 3D-Ansicht |

Verlangt einen bestimmten Blocktyp im Inventar, bevor „Block abbauen“ einen gewählten Blocktyp entfernen darf – einmal pro geschütztem Typ aufrufen; erfordert das eingeschaltete Inventar von „Block-World-Ansicht aktivieren“, sonst ist die Bedingung nie erfüllbar

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `block_type` | Auswahl | `diamond_block` | Which block type becomes protected; Auswahl: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Auswahl | `gold_block` | Which block type must be in inventory to break it; Auswahl: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Blockbelohnung festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_block_reward` |
| **Symbol** | 💎 |
| **Kategorie** | 3D-Ansicht |

Vergibt Punkte, wenn „Block abbauen“ einen gewählten Blocktyp erfolgreich entfernt – einmal pro belohntem Typ aufrufen (z. B. im Erstellen-Ereignis des Raums, direkt nach „Block-World-Ansicht aktivieren“). Ein abbaubarer Erz- oder Edelsteinblock: im Gelände platzieren, seine Belohnung eintragen, und das Abbauen vergibt die Punkte automatisch

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `block_type` | Auswahl | `diamond_block` | Which block type awards score when broken; Auswahl: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Zahl | `10` | Score awarded per block of this type broken |

### Blickwinkel setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_facing_angle` |
| **Symbol** | 🧭 |
| **Kategorie** | 3D-Ansicht |

Die Blickrichtung der Instanz für eine Raycast-Kamera (First-Person) festlegen — unabhängig von der Bewegungsgeschwindigkeit

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `angle` | Zahl | `0` | Grad (0=rechts, 90=oben, 180=links, 270=unten) |
| `relative` | Ja/Nein | Nein | Zum aktuellen Blickwinkel addieren, statt ihn zu ersetzen; optional |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [Network](Full-Action-Reference-Network-Actions_de) (15)
- [Particles](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
