# Anfänger-Preset

*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | [Fortgeschrittenen-Preset](Intermediate-Preset_de)*

> **Automatisch generiert** aus `get_beginner()` in `config/blockly_config.py` von `tools/gen_preset_docs.py` — nicht von Hand bearbeiten; nach Änderungen am Preset den Generator erneut ausführen.

> **Was dieses Preset tatsächlich einschränkt:** Dieses Preset filtert SOWOHL die visuelle Blockly-Blockpalette ALS AUCH die Menüs „Ereignis hinzufügen“/„Aktion hinzufügen“ des strukturierten Ereignisse/Aktionen-Panels — unabhängig vom verwendeten Editor erscheinen nur die unten aufgeführten Ereignisse/Aktionen. Das Preset eines *Projekts* wird auf zwei Arten festgelegt: **`Einstellungen > IDE Edition`** legt den Standard für *neue* Projekte fest (Edition Anfänger -> dieses Preset; bestehende Projekte werden durch einen Editionswechsel nie verändert), und **`Werkzeuge > Aktionsblöcke konfigurieren...`** ändert das Preset des *aktuell geöffneten* Projekts jederzeit. Die Standard-Edition der IDE ist Anfänger, daher starten neue Projekte einer Neuinstallation genau auf dieser Liste.

## Übersicht

Dieses Preset aktiviert **19** Ereignistypen und **54** Aktionstypen.

---

## Ereignisse

| Ereignis | Blockname | Kategorie | Beschreibung |
|-------|------------|----------|-------------|
| Create | `create` | Objekt | Wird einmal ausgeführt, wenn die Instanz zum ersten Mal erstellt wird |
| Step | `step` | Objekt | Wird bei jedem Bild ausgeführt (für fortlaufende Prüfungen) |
| Keyboard (held) | `keyboard` | Eingabe | Wird fortlaufend ausgeführt, solange eine Taste gedrückt gehalten wird (für flüssige Bewegung) |
| Keyboard <No Key> | `keyboard_no_key` | Eingabe | Wird ausgeführt, wenn aktuell keine Taste gedrückt ist |
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
| Zur Startposition springen | `jump_to_start` | — |
| Bis zum Kontakt bewegen | `move_to_contact` | `direction`, `max_distance`, `object` |
| Horizontal umkehren | `reverse_horizontal` | — |
| Vertikal umkehren | `reverse_vertical` | — |
| Richtung und Geschwindigkeit setzen | `set_direction_speed` | `direction`, `speed` |
| Schwerkraft setzen | `set_gravity` | `direction`, `gravity` |
| Horizontale Geschwindigkeit setzen | `set_hspeed` | `speed` |
| Vertikale Geschwindigkeit setzen | `set_vspeed` | `speed` |
| Losbewegen (Richtung) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Bewegung stoppen | `stop_movement` | — |

### Gitter

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Gitterausrichtung testen | `test_alignment` | `hsnap`, `vsnap` |

### Instanz

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Instanz ändern | `change_instance` | `object`, `perform_events` |
| Instanz erstellen | `create_instance` | `object`, `x`, `y`, `relative` |
| Instanz zerstören | `destroy_instance` | — |
| An Position zerstören | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Instanzanzahl testen | `test_instance_count` | `object`, `number`, `operation` |

### Punkte

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Leben zeichnen | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Punkte zeichnen | `draw_score` | `x`, `y`, `caption`, `relative` |
| Leben setzen | `set_lives` | `value`, `relative` |
| Punkte setzen | `set_score` | `value`, `relative` |
| Bestenliste anzeigen | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Zeitsteuerung

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Wecker stellen | `set_alarm` | `alarm_number`, `steps` |
| Warten | `sleep` | `milliseconds` |

### Raum

| Aktion | Blockname | Parameter |
|--------|------------|------------|
| Spiel beenden | `game_end` | — |
| Wenn nächster Raum existiert | `if_next_room_exists` | `then_actions`, `else_actions` |
| Wenn vorheriger Raum existiert | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Raum neu starten | `restart_room` | — |
| Hintergrund setzen | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

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
| Text zeichnen | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Spiel neu starten | `restart_game` | — |
| Zeichenfarbe festlegen | `set_draw_color` | `color` |
| Fenstertitel festlegen | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
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
| Wenn Kollision | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Wenn Objekt existiert | `if_object_exists` | `object`, `not_flag` |
| Block beginnen | `start_block` | — |
| Zufall testen | `test_chance` | `sides` |
| Ausdruck testen | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Variable testen | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Siehe auch

- [Preset-Leitfaden](Preset-Guide_de) — was Presets sind und wie man sie ändert
- [Ereignisreferenz](Event-Reference_de) — vollständige Beschreibung jedes Ereignisses
- [Vollständige Aktionsreferenz](Full-Action-Reference_de) — vollständige Parameterdetails für jede Aktion
- [Fortgeschrittenen-Preset](Intermediate-Preset_de) — die nächsthöhere Stufe
