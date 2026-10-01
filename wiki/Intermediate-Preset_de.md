# Fortgeschrittenen-Preset

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Anfänger-Preset](Beginner-Preset_de)*

> **Automatisch generiert** aus `get_intermediate()` in `config/blockly_config.py` von `tools/gen_preset_docs.py` — nicht von Hand bearbeiten; nach Änderungen am Preset den Generator erneut ausführen.

> **Was dieses Preset tatsächlich einschränkt:** Dieses Preset filtert SOWOHL die visuelle Blockly-Blockpalette ALS AUCH die Menüs „Ereignis hinzufügen“/„Aktion hinzufügen“ des strukturierten Ereignisse/Aktionen-Panels — unabhängig vom verwendeten Editor erscheinen nur die unten aufgeführten Ereignisse/Aktionen. Das Preset eines *Projekts* wird auf zwei Arten festgelegt: **`Einstellungen > IDE Edition`** legt den Standard für *neue* Projekte fest (Edition Anfänger -> dieses Preset; bestehende Projekte werden durch einen Editionswechsel nie verändert), und **`Werkzeuge > Aktionsblöcke konfigurieren...`** ändert das Preset des *aktuell geöffneten* Projekts jederzeit. Die Standard-Edition der IDE ist Anfänger, daher starten neue Projekte einer Neuinstallation genau auf dieser Liste.

## Übersicht

Dieses Preset aktiviert **21** Ereignistypen und **118** Aktionstypen.

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
| Auf Gitter bewegen | `move_grid` | `direction`, `grid_size` |
| Zu Punkt bewegen | `move_towards_point` | `x`, `y`, `speed` |
| Bis zum Kontakt bewegen | `move_to_contact` | `direction`, `max_distance`, `object` |
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
| Zeitleiste anhalten | `pause_timeline` | — |
| Wecker stellen | `set_alarm` | `alarm_number`, `steps` |
| Zeitleiste festlegen | `set_timeline` | `timeline` |
| Position der Zeitleiste festlegen | `set_timeline_position` | `position`, `relative` |
| Geschwindigkeit der Zeitleiste festlegen | `set_timeline_speed` | `speed` |
| Warten | `sleep` | `milliseconds` |
| Zeitleiste starten | `start_timeline` | — |
| Zeitleiste stoppen | `stop_timeline` | — |

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
| Hintergrund setzen | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |
| Hintergrundfarbe setzen | `set_background_color` | `color`, `show_color` |
| Raumtitel festlegen | `set_room_caption` | `caption` |
| Raum-Persistenz setzen | `set_room_persistent` | `persistent` |
| Raumgeschwindigkeit setzen | `set_room_speed` | `speed` |

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
| Text zeichnen | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Variable zeichnen | `draw_variable` | `x`, `y`, `variable` |
| Bildschirm mit Farbe füllen | `fill_color` | `color` |
| Spiel laden | `load_game` | `filename` |
| Webseite öffnen | `open_webpage` | `url` |
| Spiel neu starten | `restart_game` | — |
| Spiel speichern | `save_game` | `filename` |
| Farbe setzen | `set_color` | `color`, `alpha` |
| Zeichenfarbe festlegen | `set_draw_color` | `color` |
| Zeichenschrift festlegen | `set_draw_font` | `font`, `halign`, `valign` |
| Fenstertitel festlegen | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Spielinfo anzeigen | `show_info` | — |
| Nachricht anzeigen | `show_message` | `message` |
| Video abspielen | `show_video` | `filename`, `fullscreen` |
| Startbild: Bild zeigen | `splash_show_image` | `image` |
| Startbild: Text zeigen | `splash_show_text` | `text` |

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
| Wenn Kollision bei | `if_collision_at` | `x`, `y`, `object_type`, `then_actions`, `else_actions` |
| Wenn Objekt existiert | `if_object_exists` | `object`, `not_flag` |
| Wiederholen | `repeat` | `times`, `actions` |
| Block beginnen | `start_block` | — |
| Zufall testen | `test_chance` | `sides` |
| Ausdruck testen | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Frage stellen | `test_question` | `question` |
| Variable testen | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Ansichten

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Ansichten aktivieren | `enable_views` | `enable` |
| Ansicht festlegen | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Partikel

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Partikel ausstoßen | `burst_particles` | `particle_type`, `number` |
| Partikel löschen | `clear_particles` | — |
| Emitter erstellen | `create_emitter` | `x`, `y`, `width`, `height`, `shape` |
| Partikelsystem erstellen | `create_particle_system` | `depth` |
| Partikeltyp erstellen | `create_particle_type` | `sprite`, `size_min`, `size_max`, `size_increase`, `color`, `alpha`, `speed_min`, `speed_max`, `direction_min`, `direction_max`, `life_min`, `life_max` |
| Emitter entfernen | `destroy_emitter` | — |
| Partikelsystem entfernen | `destroy_particle_system` | — |
| Partikel strömen lassen | `stream_particles` | `particle_type`, `number` |

---

## Siehe auch

- [Preset-Leitfaden](Preset-Guide_de) — was Presets sind und wie man sie ändert
- [Ereignisreferenz](Event-Reference_de) — vollständige Beschreibung jedes Ereignisses
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) — vollständige Parameterdetails für jede Aktion
- [Anfänger-Preset](Beginner-Preset_de) — die Stufe darunter
