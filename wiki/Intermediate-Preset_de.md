# Fortgeschrittenen-Preset

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Anfänger-Preset](Beginner-Preset_de)*

> **Automatisch generiert** aus `get_intermediate()` in `config/blockly_config.py` von `tools/gen_preset_docs.py` — nicht von Hand bearbeiten; nach Änderungen am Preset den Generator erneut ausführen.

> **Was dieses Preset tatsächlich einschränkt:** Dieses Preset filtert SOWOHL die visuelle Blockly-Blockpalette ALS AUCH die Menüs „Ereignis hinzufügen“/„Aktion hinzufügen“ des strukturierten Ereignisse/Aktionen-Panels — unabhängig vom verwendeten Editor erscheinen nur die unten aufgeführten Ereignisse/Aktionen. Das Preset eines *Projekts* wird auf zwei Arten festgelegt: **`Einstellungen > IDE Edition`** legt den Standard für *neue* Projekte fest (Edition Anfänger -> dieses Preset; bestehende Projekte werden durch einen Editionswechsel nie verändert), und **`Werkzeuge > Aktionsblöcke konfigurieren...`** ändert das Preset des *aktuell geöffneten* Projekts jederzeit. Die Standard-Edition der IDE ist Anfänger, daher starten neue Projekte einer Neuinstallation genau auf dieser Liste.

## Übersicht

Dieses Preset aktiviert **21** Ereignistypen und **94** Aktionstypen.

---

## Ereignisse

| Ereignis | Blockname | Kategorie | Beschreibung |
|-------|------------|----------|-------------|
| Create | `create` | Objekt | Wird einmal ausgeführt, wenn die Instanz zum ersten Mal erstellt wird |
| Destroy | `destroy` | Objekt | Wird ausgeführt, wenn die Instanz zerstört wird |
| Step | `step` | Objekt | Wird bei jedem Bild ausgeführt (für fortlaufende Prüfungen) |
| Keyboard (held) | `keyboard` | Eingabe | Wird fortlaufend ausgeführt, solange eine Taste gedrückt gehalten wird (für flüssige Bewegung) |
| Keyboard <No Key> | `keyboard_no_key` | Eingabe | Wird ausgeführt, wenn aktuell keine Taste gedrückt ist |
| Keyboard Press | `keyboard_press` | Eingabe | Wird einmal ausgeführt, wenn eine Taste erstmals gedrückt wird (für gitterbasierte Bewegung) |
| Collision With... | `collision` | Kollision | Wird bei einer Kollision mit einem anderen Objekt ausgeführt |
| Begin Step | `begin_step` | Schritt | Wird am Anfang jedes Schritts ausgeführt, vor anderen Ereignissen |
| End Step | `end_step` | Schritt | Wird am Ende jedes Schritts ausgeführt, nach Kollisionen, aber vor dem Zeichnen |
| Alarm | `alarm` | Zeitsteuerung | Wird ausgeführt, wenn ein Alarm-Timer null erreicht |
| Draw | `draw` | Zeichnen | Wird beim Zeichnen des Objekts ausgeführt (ersetzt das Standard-Sprite-Zeichnen) |
| Draw GUI | `draw_gui` | Zeichnen | Wird über allem anderen gezeichnet (nicht von Kamera/Ansicht betroffen). Für HUD, Punktestand, Leben verwenden. |
| Room End | `room_end` | Raum | Wird ausgeführt, wenn der Raum endet |
| Room Start | `room_start` | Raum | Wird ausgeführt, wenn der Raum startet (nach den Create-Ereignissen) |
| Game End | `game_end` | Spiel | Wird ausgeführt, wenn das Spiel endet |
| Game Start | `game_start` | Spiel | Wird ausgeführt, wenn das Spiel startet (nur im ersten Raum) |
| Animation End | `animation_end` | Sonstiges | Wird ausgelöst, wenn die Sprite-Animation das letzte Bild erreicht und neu beginnt |
| Intersect Boundary | `intersect_boundary` | Sonstiges | Wird ausgeführt, wenn die Instanz den Raumrand berührt |
| No More Health | `no_more_health` | Sonstiges | Wird ausgeführt, wenn die Gesundheit 0 oder weniger erreicht |
| No More Lives | `no_more_lives` | Sonstiges | Wird ausgeführt, wenn die Leben 0 oder weniger erreichen |
| Outside Room | `outside_room` | Sonstiges | Wird ausgeführt, wenn die Instanz vollständig außerhalb des Raums ist |

---

## Aktionen

### Bewegung

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Abprallen | `bounce` | — |
| Zu Position springen | `jump_to_position` | `x`, `y`, `relative` |
| Zu zufälliger Position springen | `jump_to_random` | `snap_h`, `snap_v` |
| Zur Startposition springen | `jump_to_start` | — |
| Zu Punkt bewegen | `move_towards_point` | `x`, `y`, `speed` |
| Horizontal umkehren | `reverse_horizontal` | — |
| Vertikal umkehren | `reverse_vertical` | — |
| Richtung und Geschwindigkeit setzen | `set_direction_speed` | `direction`, `speed` |
| Reibung setzen | `set_friction` | `friction` |
| Schwerkraft setzen | `set_gravity` | `direction`, `gravity` |
| Horizontale Geschwindigkeit setzen | `set_hspeed` | `speed` |
| Vertikale Geschwindigkeit setzen | `set_vspeed` | `speed` |
| Losbewegen (Richtung) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Bewegung stoppen | `stop_movement` | — |

### Gitter

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Wenn am Gitter | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Am Gitter ausrichten | `snap_to_grid` | `grid_size` |
| Gitterausrichtung testen | `test_alignment` | `hsnap`, `vsnap` |

### Instanz

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Instanz ändern | `change_instance` | `object`, `perform_events` |
| Instanz erstellen | `create_instance` | `object`, `x`, `y`, `relative` |
| Bewegte Instanz erstellen | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Zufällige Instanz erstellen | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Instanz zerstören | `destroy_instance` | — |
| An Position zerstören | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Bildindex setzen | `set_image_index` | `frame` |
| Bildgeschwindigkeit setzen | `set_image_speed` | `speed` |
| Sprite setzen | `set_sprite` | `sprite`, `subimage`, `speed` |
| Animation starten | `start_animation` | — |
| Animation stoppen | `stop_animation` | — |
| Instanzanzahl testen | `test_instance_count` | `object`, `number`, `operation` |

### Punkte

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Bestenliste löschen | `clear_highscore` | — |
| Gesundheitsbalken zeichnen | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Leben zeichnen | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Punkte zeichnen | `draw_score` | `x`, `y`, `caption`, `relative` |
| Gesundheit setzen | `set_health` | `value`, `relative` |
| Leben setzen | `set_lives` | `value`, `relative` |
| Punkte setzen | `set_score` | `value`, `relative` |
| Bestenliste anzeigen | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Gesundheit testen | `test_health` | `operation`, `value` |
| Leben testen | `test_lives` | `value`, `operation` |
| Punkte testen | `test_score` | `value`, `operation` |

### Zeitsteuerung

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Wecker stellen | `set_alarm` | `alarm_number`, `steps` |
| Warten | `sleep` | `milliseconds` |

### Raum

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Raum prüfen | `check_room` | `room`, `not_flag` |
| Spiel beenden | `game_end` | — |
| Zu Raum gehen | `goto_room` | `room`, `transition` |
| Wenn nächster Raum existiert | `if_next_room_exists` | `then_actions`, `else_actions` |
| Wenn vorheriger Raum existiert | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Nächster Raum | `next_room` | — |
| Vorheriger Raum | `previous_room` | — |
| Raum neu starten | `restart_room` | — |
| Raumtitel festlegen | `set_room_caption` | `caption` |

### Audio

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Klangwiedergabe prüfen | `check_sound` | `sound`, `not_flag` |
| Musik abspielen | `play_music` | `music`, `loop`, `volume` |
| Klang abspielen | `play_sound` | `sound`, `volume` |
| Lautstärke setzen | `set_volume` | `volume` |
| Musik stoppen | `stop_music` | — |
| Klang stoppen | `stop_sound` | `sound` |

### Spiel

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Pfeil zeichnen | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Hintergrund zeichnen | `draw_background` | `background`, `x`, `y`, `tiled` |
| Ellipse zeichnen | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Linie zeichnen | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Skalierten Text zeichnen | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Sprite zeichnen | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Text zeichnen | `draw_text` | `text`, `x`, `y`, `relative` |
| Variable zeichnen | `draw_variable` | `x`, `y`, `variable` |
| Bildschirm mit Farbe füllen | `fill_color` | `color` |
| Webseite öffnen | `open_webpage` | `url` |
| Spiel neu starten | `restart_game` | — |
| Farbe setzen | `set_color` | `color`, `alpha` |
| Zeichenfarbe festlegen | `set_draw_color` | `color` |
| Zeichenschrift festlegen | `set_draw_font` | `font`, `halign`, `valign` |
| Fenstertitel festlegen | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Spielinfo anzeigen | `show_info` | — |
| Nachricht anzeigen | `show_message` | `message` |

### Steuerung

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Auf frei prüfen | `check_empty` | `x`, `y`, `relative`, `objects` |
| Kommentar | `comment` | `text` |
| Sonst | `else_action` | — |
| Block beenden | `end_block` | — |
| Code ausführen | `execute_code` | `code` |
| Skript ausführen | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Ereignis verlassen | `exit_event` | — |
| Wenn Schieben möglich | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Wenn Kollision | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Wenn Objekt existiert | `if_object_exists` | `object`, `not_flag` |
| Block beginnen | `start_block` | — |
| Zufall testen | `test_chance` | `sides` |
| Frage stellen | `test_question` | `question` |
| Variable testen | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Ansichten

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Ansichten aktivieren | `enable_views` | `enable` |
| Ansicht festlegen | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### 3D-Ansicht

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| DOOM-HUD zeichnen | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Minikarte zeichnen | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Raycast-Ansicht aktivieren | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Blickwinkel setzen | `set_facing_angle` | `angle`, `relative` |

---

## Siehe auch

- [Preset-Leitfaden](Preset-Guide_de) — was Presets sind und wie man sie ändert
- [Ereignisreferenz](Event-Reference_de) — vollständige Beschreibung jedes Ereignisses
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) — vollständige Parameterdetails für jede Aktion
- [Anfänger-Preset](Beginner-Preset_de) — die Stufe darunter
