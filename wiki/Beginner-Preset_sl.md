# Preset za Začetnike

*[Domov](Home_sl) | [Vodnik po Prednastavitvah](Preset-Guide_sl) | [Vmesni Preset](Intermediate-Preset_sl)*

> **Samodejno ustvarjeno** iz `get_beginner()` v `config/blockly_config.py` s `tools/gen_preset_docs.py` — ne urejajte ročno; po spremembi presetov znova zaženite generator.

> **Kaj ta preset dejansko omejuje:** ta preset filtrira TAKO vizualno paleto blokov Blockly KOT menija "Dodaj dogodek"/"Dodaj dejanje" v strukturirani plošči Dogodki/Dejanja — ne glede na to, kateri urejevalnik uporabljate, se prikažejo samo spodaj navedeni dogodki/dejanja. Preset *projekta* je nastavljen na dva načina: **`Nastavitve > IDE Edition`** izbere privzeto vrednost za *nove* projekte (izdaja Začetnik -> ta preset; obstoječi projekti se z zamenjavo izdaje nikoli ne spremenijo), in **`Orodja > Nastavi akcijske bloke...`** kadar koli spremeni preset *trenutno odprtega* projekta. Privzeta izdaja IDE-ja je Začetnik, zato se novi projekti sveže namestitve začnejo prav na tem seznamu.

## Pregled

Ta preset omogoča **19** vrst dogodkov in **54** vrst dejanj.

---

## Dogodki

| Dogodek | Ime Bloka | Kategorija | Opis |
|-------|------------|----------|-------------|
| Create | `create` | Objekt | Izvede se enkrat, ko je instanca prvič ustvarjena |
| Step | `step` | Objekt | Izvede se pri vsaki sličici (uporabite za neprekinjena preverjanja) |
| Keyboard (held) | `keyboard` | Vnos | Izvaja se neprekinjeno, dokler je tipka pritisnjena (za gladko gibanje) |
| Keyboard <No Key> | `keyboard_no_key` | Vnos | Izvede se, ko trenutno ni pritisnjena nobena tipka |
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
| Skoči na začetni položaj | `jump_to_start` | — |
| Premakni do stika | `move_to_contact` | `direction`, `max_distance`, `object` |
| Obrni vodoravno | `reverse_horizontal` | — |
| Obrni navpično | `reverse_vertical` | — |
| Nastavi smer in hitrost | `set_direction_speed` | `direction`, `speed` |
| Nastavi gravitacijo | `set_gravity` | `direction`, `gravity` |
| Nastavi vodoravno hitrost | `set_hspeed` | `speed` |
| Nastavi navpično hitrost | `set_vspeed` | `speed` |
| Začni se premikati (smer) | `start_moving_direction` | `directions`, `direction_expr`, `speed` |
| Ustavi gibanje | `stop_movement` | — |

### Mreža

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Preveri poravnavo na mrežo | `test_alignment` | `hsnap`, `vsnap` |

### Instanca

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Spremeni instanco | `change_instance` | `object`, `perform_events` |
| Ustvari instanco | `create_instance` | `object`, `x`, `y`, `relative` |
| Uniči instanco | `destroy_instance` | — |
| Uniči na položaju | `destroy_at_position` | `object`, `x`, `y`, `relative`, `radius` |
| Preveri število instanc | `test_instance_count` | `object`, `number`, `operation` |

### Rezultat

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Nariši življenja | `draw_lives` | `x`, `y`, `sprite`, `scale`, `relative` |
| Nariši rezultat | `draw_score` | `x`, `y`, `caption`, `relative` |
| Nastavi življenja | `set_lives` | `value`, `relative` |
| Nastavi rezultat | `set_score` | `value`, `relative` |
| Prikaži tabelo rekordov | `show_highscore` | `background`, `new_color`, `other_color`, `allow_new_entry` |

### Čas

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Nastavi budilko | `set_alarm` | `alarm_number`, `steps` |
| Premor | `sleep` | `milliseconds` |

### Soba

| Dejanje | Ime Bloka | Parametri |
|--------|------------|------------|
| Končaj igro | `game_end` | — |
| Če obstaja naslednja soba | `if_next_room_exists` | `then_actions`, `else_actions` |
| Če obstaja prejšnja soba | `if_previous_room_exists` | `then_actions`, `else_actions` |
| Znova zaženi sobo | `restart_room` | — |
| Nastavi ozadje | `set_background` | `background`, `visible`, `foreground`, `tiled_h`, `tiled_v`, `hspeed`, `vspeed` |

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
| Nariši besedilo | `draw_text` | `text`, `x`, `y`, `relative`, `color` |
| Znova zaženi igro | `restart_game` | — |
| Nastavi barvo risanja | `set_draw_color` | `color` |
| Nastavi naslov okna | `set_window_caption` | `show_score`, `show_lives`, `show_health`, `caption` |
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
| Če trk | `if_collision` | `x`, `y`, `object`, `not_flag` |
| Če predmet obstaja | `if_object_exists` | `object`, `not_flag` |
| Začetek bloka | `start_block` | — |
| Preveri verjetnost | `test_chance` | `sides` |
| Preveri izraz | `test_expression` | `expression`, `then_actions`, `else_actions` |
| Preveri spremenljivko | `test_variable` | `variable`, `value`, `scope`, `operation` |

---

## Glej Tudi

- [Vodnik po Prednastavitvah](Preset-Guide_sl) — kaj so preseti in kako jih spremeniti
- [Referenca Dogodkov](Event-Reference_sl) — popoln opis vsakega dogodka
- [Popolna Referenca Dejanj](Full-Action-Reference_sl) — popolni podatki parametrov za vsako dejanje
- [Vmesni Preset](Intermediate-Preset_sl) — naslednja stopnja
