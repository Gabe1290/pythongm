# Vmesni Preset

*[Domov](Home_sl) | [Vodnik po Prednastavitvah](Preset-Guide_sl) | [Preset za Začetnike](Beginner-Preset_sl)*

> **Samodejno ustvarjeno** iz `get_intermediate()` v `config/blockly_config.py` s `tools/gen_preset_docs.py` — ne urejajte ročno; po spremembi presetov znova zaženite generator.

> **Kaj ta preset dejansko omejuje:** ta preset filtrira TAKO vizualno paleto blokov Blockly KOT menija "Dodaj dogodek"/"Dodaj dejanje" v strukturirani plošči Dogodki/Dejanja — ne glede na to, kateri urejevalnik uporabljate, se prikažejo samo spodaj navedeni dogodki/dejanja. Preset *projekta* je nastavljen na dva načina: **`Nastavitve > IDE Edition`** izbere privzeto vrednost za *nove* projekte (izdaja Začetnik -> ta preset; obstoječi projekti se z zamenjavo izdaje nikoli ne spremenijo), in **`Orodja > Nastavi akcijske bloke...`** kadar koli spremeni preset *trenutno odprtega* projekta. Privzeta izdaja IDE-ja je Začetnik, zato se novi projekti sveže namestitve začnejo prav na tem seznamu.

## Pregled

Ta preset omogoča **21** vrst dogodkov in **94** vrst dejanj.

---

## Dogodki

| Dogodek | Ime Bloka | Kategorija | Opis |
|-------|------------|----------|-------------|
| Create | `create` | Objekt | Izvede se enkrat, ko je instanca prvič ustvarjena |
| Destroy | `destroy` | Objekt | Izvede se, ko je instanca uničena |
| Step | `step` | Objekt | Izvede se pri vsaki sličici (uporabite za neprekinjena preverjanja) |
| Keyboard (held) | `keyboard` | Vnos | Izvaja se neprekinjeno, dokler je tipka pritisnjena (za gladko gibanje) |
| Keyboard <No Key> | `keyboard_no_key` | Vnos | Izvede se, ko trenutno ni pritisnjena nobena tipka |
| Keyboard Press | `keyboard_press` | Vnos | Izvede se enkrat, ko je tipka prvič pritisnjena (za gibanje po mreži) |
| Collision With... | `collision` | Trk | Izvede se ob trku z drugim objektom |
| Begin Step | `begin_step` | Korak | Izvede se na začetku vsakega koraka, pred drugimi dogodki |
| End Step | `end_step` | Korak | Izvede se na koncu vsakega koraka, po trkih, a pred risanjem |
| Alarm | `alarm` | Čas | Izvede se, ko alarm doseže nič |
| Draw | `draw` | Risanje | Izvede se ob risanju objekta (nadomesti privzeto risanje sličice) |
| Draw GUI | `draw_gui` | Risanje | Nariše se čez vse ostalo (nanj ne vpliva kamera/pogled). Uporabite za HUD, rezultat, življenja. |
| Room End | `room_end` | Soba | Izvede se, ko se soba konča |
| Room Start | `room_start` | Soba | Izvede se, ko se soba zažene (po dogodkih Create) |
| Game End | `game_end` | Igra | Izvede se, ko se igra konča |
| Game Start | `game_start` | Igra | Izvede se, ko se igra zažene (samo v prvi sobi) |
| Animation End | `animation_end` | Drugo | Sproži se, ko animacija sličice doseže zadnjo sličico in se ponovi |
| Intersect Boundary | `intersect_boundary` | Drugo | Izvede se, ko se instanca dotakne roba sobe |
| No More Health | `no_more_health` | Drugo | Izvede se, ko zdravje doseže 0 ali manj |
| No More Lives | `no_more_lives` | Drugo | Izvede se, ko življenja dosežejo 0 ali manj |
| Outside Room | `outside_room` | Drugo | Izvede se, ko je instanca popolnoma zunaj sobe |

---

## Dejanja

### Gibanje

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Odbij se | `bounce` | — |
| Skoči na položaj | `jump_to_position` | `x`, `y`, `relative` |
| Skoči na naključni položaj | `jump_to_random` | `snap_h`, `snap_v` |
| Skoči na začetni položaj | `jump_to_start` | — |
| Premakni proti točki | `move_towards_point` | `x`, `y`, `speed` |
| Obrni vodoravno | `reverse_horizontal` | — |
| Obrni navpično | `reverse_vertical` | — |
| Nastavi smer in hitrost | `set_direction_speed` | `direction`, `speed` |
| Nastavi trenje | `set_friction` | `friction` |
| Nastavi gravitacijo | `set_gravity` | `direction`, `gravity` |
| Nastavi vodoravno hitrost | `set_hspeed` | `speed` |
| Nastavi navpično hitrost | `set_vspeed` | `speed` |
| Začni se premikati (smer) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Ustavi gibanje | `stop_movement` | — |

### Mreža

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Če na mreži | `if_on_grid` | `grid_size`, `then_actions`, `else_actions` |
| Pripni na mrežo | `snap_to_grid` | `grid_size` |
| Preveri poravnavo na mrežo | `test_alignment` | `hsnap`, `vsnap` |

### Instanca

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Spremeni instanco | `change_instance` | `object`, `perform_events` |
| Ustvari instanco | `create_instance` | `object`, `x`, `y`, `relative` |
| Ustvari premikajočo se instanco | `create_moving_instance` | `object`, `x`, `y`, `speed`, `direction` |
| Ustvari naključno instanco | `create_random_instance` | `x`, `y`, `object1`, `object2`, `object3`, `object4` |
| Uniči instanco | `destroy_instance` | — |
| Uniči na položaju | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Nastavi indeks slike | `set_image_index` | `frame` |
| Nastavi hitrost slike | `set_image_speed` | `speed` |
| Nastavi sprite | `set_sprite` | `sprite`, `subimage`, `speed` |
| Zaženi animacijo | `start_animation` | — |
| Ustavi animacijo | `stop_animation` | — |
| Preveri število instanc | `test_instance_count` | `object`, `number`, `operation` |

### Rezultat

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Počisti tabelo rekordov | `clear_highscore` | — |
| Nariši vrstico zdravja | `draw_health_bar` | `x1`, `y1`, `x2`, `y2`, `back_color`, `bar_color` |
| Nariši življenja | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Nariši rezultat | `draw_score` | `x`, `y`, `caption`, `relative` |
| Nastavi zdravje | `set_health` | `value`, `relative` |
| Nastavi življenja | `set_lives` | `value`, `relative` |
| Nastavi rezultat | `set_score` | `value`, `relative` |
| Prikaži tabelo rekordov | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |
| Preveri zdravje | `test_health` | `operation`, `value` |
| Preveri življenja | `test_lives` | `value`, `operation` |
| Preveri rezultat | `test_score` | `value`, `operation` |

### Čas

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Nastavi budilko | `set_alarm` | `alarm_number`, `steps` |
| Premor | `sleep` | `milliseconds` |

### Soba

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Preveri sobo | `check_room` | `room`, `not_flag` |
| Končaj igro | `game_end` | — |
| Pojdi v sobo | `goto_room` | `room`, `transition` |
| Če obstaja naslednja soba | `if_next_room_exists` | `then_actions`, `else_actions` |
| Če obstaja prejšnja soba | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Naslednja soba | `next_room` | — |
| Prejšnja soba | `previous_room` | — |
| Znova zaženi sobo | `restart_room` | — |
| Nastavi naslov sobe | `set_room_caption` | `caption` |

### Zvok

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Preveri predvajanje zvoka | `check_sound` | `sound`, `not_flag` |
| Predvajaj glasbo | `play_music` | `music`, `loop`, `volume` |
| Predvajaj zvok | `play_sound` | `sound`, `volume` |
| Nastavi glasnost | `set_volume` | `volume` |
| Ustavi glasbo | `stop_music` | — |
| Ustavi zvok | `stop_sound` | `sound` |

### Igra

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Nariši puščico | `draw_arrow` | `x1`, `y1`, `x2`, `y2`, `tip_size` |
| Nariši ozadje | `draw_background` | `background`, `x`, `y`, `tiled` |
| Nariši elipso | `draw_ellipse` | `x1`, `y1`, `x2`, `y2`, `filled` |
| Nariši črto | `draw_line` | `x1`, `y1`, `x2`, `y2` |
| Nariši povečano besedilo | `draw_scaled_text` | `text`, `x`, `y`, `xscale`, `yscale` |
| Nariši sprite | `draw_sprite` | `sprite`, `x`, `y`, `subimage` |
| Nariši besedilo | `draw_text` | `text`, `x`, `y`, `relative` |
| Nariši spremenljivko | `draw_variable` | `x`, `y`, `variable` |
| Zapolni zaslon z barvo | `fill_color` | `color` |
| Odpri spletno stran | `open_webpage` | `url` |
| Znova zaženi igro | `restart_game` | — |
| Nastavi barvo | `set_color` | `color`, `alpha` |
| Nastavi barvo risanja | `set_draw_color` | `color` |
| Nastavi pisavo risanja | `set_draw_font` | `font`, `halign`, `valign` |
| Nastavi naslov okna | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
| Prikaži informacije o igri | `show_info` | — |
| Prikaži sporočilo | `show_message` | `message` |

### Nadzor

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Preveri, ali je prazno | `check_empty` | `x`, `y`, `relative`, `objects` |
| Komentar | `comment` | `text` |
| Sicer | `else_action` | — |
| Konec bloka | `end_block` | — |
| Izvedi kodo | `execute_code` | `code` |
| Izvedi skripto | `execute_script` | `script`, `arg0`, `arg1`, `arg2`, `arg3`, `arg4` |
| Zapusti dogodek | `exit_event` | — |
| Če je mogoče potisniti | `if_can_push` | `direction`, `object_type`, `then_action`, `else_action` |
| Če trk | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Če predmet obstaja | `if_object_exists` | `object`, `not_flag` |
| Začetek bloka | `start_block` | — |
| Preveri verjetnost | `test_chance` | `sides` |
| Postavi vprašanje | `test_question` | `question` |
| Preveri spremenljivko | `test_variable` | `variable`, `value`, `scope`, `operation` |

### Pogledi

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Omogoči poglede | `enable_views` | `enable` |
| Nastavi pogled | `set_view` | `view`, `visible`, `view_x`, `view_y`, `view_w`, `view_h`, `port_x`, `port_y`, `port_w`, `port_h`, `follow`, `hborder`, `vborder`, `hspeed`, `vspeed` |

### Pogled 3D

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Nariši HUD DOOM | `draw_doom_hud` | `x`, `y`, `width`, `height`, `back_color`, `divider_color`, `text_color`, `health_label`, `health_bar_width`, `health_bar_height`, `bar_color`, `face_sprite`, `face_frames`, `score_label`, `lives_sprite`, `lives_scale`, `objective_value`, `objective_label` |
| Nariši mini zemljevid | `draw_minimap` | `x`, `y`, `size`, `back_color`, `wall_color`, `player_color` |
| Omogoči pogled Raycast | `enable_raycast_view` | `enable`, `camera_object`, `fov`, `render_distance`, `cell_size`, `columns`, `wall_color`, `floor_color`, `ceiling_color`, `wall_texture`, `sky_texture`, `floor_texture`, `ceiling_texture`, `wall_textured`, `floor_cast_res`, `viewport_height` |
| Nastavi kot pogleda | `set_facing_angle` | `angle`, `relative` |

---

## Glej Tudi

- [Vodnik po Prednastavitvah](Preset-Guide_sl) — kaj so preseti in kako jih spremeniti
- [Referenca Dogodkov](Event-Reference_sl) — popoln opis vsakega dogodka
- [Popolna Referenca Dejanj](Full-Action-Reference_sl) — popolni podatki parametrov za vsako dejanje
- [Preset za Začetnike](Beginner-Preset_sl) — stopnja pod to
