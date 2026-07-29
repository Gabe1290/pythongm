# Popolna referenca dejanj

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

Ta stran navaja vseh **109** dejanj, ki so na voljo v PyGameMaker, natanko tako, kot so prikazana v izbirniku dejanj IDE (vključno z vtičnikom Audio in razširitvijo Pogled 3D). Dejanja so ukazi, ki se izvedejo, ko se sproži dogodek.

## Kategorije

- [Gibanje](#movement) (20)
- [Instanca](#instance) (12)
- [Rezultat](#score) (11)
- [Soba](#room) (9)
- [Čas](#timing) (2)
- [Zvok](#audio) (6)
- [Igra](#game) (20)
- [Nadzor](#control) (19)
- [Mreža](#grid) (4)
- [Pogledi](#views) (2)
- [Pogled 3D](#3d-view) (4)

---

<a id="movement"></a>
## Gibanje

### Odbij se

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `bounce` |
| **Kategorija** | Gibanje |

Odbij se od trdnih predmetov

*Parametri:* brez

### Skoči na položaj

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `jump_to_position` |
| **Ikona** | 📍 |
| **Kategorija** | Gibanje |

Takoj premakni na položaj

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `relative` | Da/Ne | Ne | Prištej trenutnemu položaju namesto nastavitve absolutnega |

### Skoči na naključni položaj

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `jump_to_random` |
| **Ikona** | 🎲↪️ |
| **Kategorija** | Gibanje |

Teleportiraj na naključni položaj (izbirno pripet na mrežo)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `snap_h` | Število | `1` | Vodoravno pripenjanje na mrežo (1 = brez pripenjanja) |
| `snap_v` | Število | `1` | Navpično pripenjanje na mrežo (1 = brez pripenjanja) |

### Skoči na začetni položaj

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `jump_to_start` |
| **Ikona** | ↩️ |
| **Kategorija** | Gibanje |

Vrni instanco na njen položaj ustvarjanja

*Parametri:* brez

### Prosto gibanje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_free` |
| **Ikona** | 🧭 |
| **Kategorija** | Gibanje |

Premakni v natančni smeri (0-360 stopinj)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Število | `0` | Smer v stopinjah (0=desno, 90=gor, v nasprotni smeri urinega kazalca) |
| `speed` | Število | `4.0` | Hitrost gibanja |

### Premakni po mreži

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_grid` |
| **Ikona** | ▦ |
| **Kategorija** | Gibanje |

Premakni za eno celico mreže v navedeni smeri

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Izbira | `right` | Smer gibanja; Izbire: `left`, `right`, `up`, `down` |
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |

### Premakni proti točki

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_towards_point` |
| **Ikona** | 🎯 |
| **Kategorija** | Gibanje |

Premakni proti točki z dano hitrostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Ciljni X |
| `y` | Število | `0` | Ciljni Y |
| `speed` | Število | `4.0` | Hitrost gibanja |

### Premakni do stika

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `move_to_contact` |
| **Ikona** | 🎯 |
| **Kategorija** | Gibanje |

Premakni v smeri, dokler se ne dotakne predmeta (ali največje razdalje)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Besedilo | `direction` | Smer v stopinjah (0=desno, 90=gor, 180=levo, 270=dol) ali izraz. Privzeto »direction« = trenutna usmerjenost instance (pripenjanje ob trku). |
| `max_distance` | Število | `1000` | Največja razdalja gibanja, v pikslih |
| `object` | Predmet | `all` | Ustavi se ob stiku z: »all« vsemi instancami, »solid« samo trdnimi predmeti ali določenim imenom predmeta.; Izbire: `all`, `solid`; neobvezno |

### Obrni vodoravno

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `reverse_horizontal` |
| **Ikona** | ↔️ |
| **Kategorija** | Gibanje |

Obrni smer vodoravnega gibanja

*Parametri:* brez

### Obrni navpično

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `reverse_vertical` |
| **Ikona** | ↕️ |
| **Kategorija** | Gibanje |

Obrni smer navpičnega gibanja

*Parametri:* brez

### Nastavi smer

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_direction` |
| **Ikona** | 🧭 |
| **Kategorija** | Gibanje |

Nastavi smer gibanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Število | `0` | Smer v stopinjah (0=desno, 90=gor) |

### Nastavi smer in hitrost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_direction_speed` |
| **Ikona** | 🧭 |
| **Kategorija** | Gibanje |

Nastavi smer (v stopinjah) in velikost hitrosti instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Število | `0` | Smer v stopinjah (0=desno, 90=gor) |
| `speed` | Število | `4.0` | Hitrost v pikslih na sličico |

### Nastavi trenje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_friction` |
| **Ikona** | 🛑 |
| **Kategorija** | Gibanje |

Nastavi trenje (upočasnitev)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `friction` | Število | `0.1` | Količina trenja (odšteta od hitrosti ob vsakem koraku) |

### Nastavi gravitacijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_gravity` |
| **Ikona** | ⬇️ |
| **Kategorija** | Gibanje |

Nastavi smer in jakost gravitacije

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Število | `270` | Smer gravitacije v stopinjah (270=dol) |
| `gravity` | Število | `0.5` | Jakost gravitacije (dodana ob vsakem koraku) |

### Nastavi vodoravno hitrost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_hspeed` |
| **Ikona** | ↔️ |
| **Kategorija** | Gibanje |

Nastavi vodoravno hitrost gibanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `0` | Hitrost v pikslih na sličico |

### Nastavi hitrost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_speed` |
| **Ikona** | ⚡ |
| **Kategorija** | Gibanje |

Nastavi hitrost gibanja (velikost)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `0` | Hitrost gibanja |

### Nastavi navpično hitrost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_vspeed` |
| **Ikona** | ↕️ |
| **Kategorija** | Gibanje |

Nastavi navpično hitrost gibanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `0` | Hitrost v pikslih na sličico |

### Začni se premikati (smer)

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_moving_direction` |
| **Ikona** | ➡️ |
| **Kategorija** | Gibanje |

Začni se premikati v smeri z dano hitrostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `directions` | Večkratna izbira | right | Smer(i) gibanja — izberite eno ali več, da vsak korak izberete naključno. Sredinska celica je ustavitev.; Izbire: `up-left`, `up`, `up-right`, `left`, `stop`, `right`, `down-left`, `down`, `down-right` |
| `direction_expr` | Besedilo | — | Alternativa: prosti izraz, ovrednoten kot stopinje; neobvezno |
| `speed` | Število | `4.0` | Hitrost v pikslih na sličico |

### Ustavi gibanje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_movement` |
| **Ikona** | 🛑 |
| **Kategorija** | Gibanje |

Ponastavi obe hitrosti na nič

*Parametri:* brez

### Ovij okoli sobe

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `wrap_around_room` |
| **Ikona** | 🔄 |
| **Kategorija** | Gibanje |

Znova se pojavi na nasprotni strani sobe

*Parametri:* brez

---

<a id="instance"></a>
## Instanca

### Spremeni instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `change_instance` |
| **Ikona** | 🔄 |
| **Kategorija** | Instanca |
| **Velja za** | self / other / object |

Preoblikuj v drugo vrsto predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Nova vrsta predmeta |
| `perform_events` | Da/Ne | Da | Izvedi dogodke uniči/ustvari |

### Ustvari instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_instance` |
| **Ikona** | ✨ |
| **Kategorija** | Instanca |

Ustvari novo instanco

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za ustvarjanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `relative` | Da/Ne | Ne | Položaj glede na trenutno instanco |

### Ustvari premikajočo se instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_moving_instance` |
| **Ikona** | ✨➡️ |
| **Kategorija** | Instanca |

Ustvari instanco in jo zaženi v smeri

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za ustvarjanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `speed` | Število | `0` | Začetna velikost hitrosti |
| `direction` | Število | `0` | Začetna smer v stopinjah |

### Ustvari naključno instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_random_instance` |
| **Ikona** | 🎲 |
| **Kategorija** | Instanca |

Ustvari eno od več vrst predmetov, izbrano naključno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `object1` | Predmet | — | Prvi kandidatni predmet; neobvezno |
| `object2` | Predmet | — | Drugi kandidatni predmet; neobvezno |
| `object3` | Predmet | — | Tretji kandidatni predmet; neobvezno |
| `object4` | Predmet | — | Četrti kandidatni predmet; neobvezno |

### Uniči instanco

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_instance` |
| **Ikona** | 💥 |
| **Kategorija** | Instanca |
| **Velja za** | self / other / object |

Uniči instanco

*Parametri:* brez

### Uniči na položaju

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_at_position` |
| **Ikona** | 💣 |
| **Kategorija** | Instanca |

Uniči instance znotraj polmera od (x, y)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | `all` | Katero vrsto predmeta uničiti. »all« uniči vsako instanco v dosegu; »solid« samo trdne (npr. stene); »non-solid« vse razen trdnih.; Izbire: `all`, `solid`, `non-solid` |
| `x` | Besedilo | `self.x` | Položaj X (izraz dovoljen, npr. self.x) |
| `y` | Besedilo | `self.y` | Položaj Y (izraz dovoljen, npr. self.y) |
| `relative` | Da/Ne | Ne | Obravnavaj X/Y kot odmike od položaja te instance namesto absolutnih koordinat; neobvezno |
| `radius` | Število | `32` | Polmer v pikslih okoli (x, y). Privzeto 32 = ~ena celica mreže. |

### Nastavi indeks slike

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_image_index` |
| **Ikona** | 🖼️ |
| **Kategorija** | Instanca |

Nastavi trenutno sličico animacije spritea instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `frame` | Število | `0` | Indeks sličice |

### Nastavi hitrost slike

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_image_speed` |
| **Ikona** | ⏩ |
| **Kategorija** | Instanca |

Nastavi hitrost predvajanja animacije spritea instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `speed` | Število | `1.0` | Sličice, napredovane na korak (0 = zaustavljeno) |

### Nastavi sprite

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sprite` |
| **Ikona** | 🖼️ |
| **Kategorija** | Instanca |

Spremeni sprite in/ali sličico/hitrost animacije instance

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite za uporabo (ali »<self>« za ohranitev trenutnega) |
| `subimage` | Število | `-1` | Indeks sličice za nastavitev; -1 pusti nespremenjeno |
| `speed` | Število | `-1` | Hitrost animacije; -1 pusti nespremenjeno |

### Zaženi animacijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_animation` |
| **Ikona** | ▶️ |
| **Kategorija** | Instanca |

Nadaljuj animacijo spritea instance (image_speed = 1)

*Parametri:* brez

### Ustavi animacijo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_animation` |
| **Ikona** | ⏸️ |
| **Kategorija** | Instanca |

Zaustavi animacijo spritea instance (image_speed = 0)

*Parametri:* brez

### Preveri število instanc

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_instance_count` |
| **Ikona** | ❓🔢 |
| **Kategorija** | Instanca |

Pogoj: primerjaj število instanc predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Predmet za štetje |
| `number` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="score"></a>
## Rezultat

### Počisti tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `clear_highscore` |
| **Ikona** | 🗑️🏆 |
| **Kategorija** | Rezultat |

Počisti vse vnose tabele rekordov

*Parametri:* brez

### Nariši vrstico zdravja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_health_bar` |
| **Ikona** | 🩺 |
| **Kategorija** | Rezultat |

Nariši trenutno zdravje kot dvobarvno vrstico

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `20` | Y spodaj |
| `back_color` | Barva | `#FF0000` | Barva ozadja (prazno) |
| `bar_color` | Barva | `#00FF00` | Barva polnila (zdravje) |

### Nariši življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_lives` |
| **Ikona** | 🖍️❤️ |
| **Kategorija** | Rezultat |

Nariši trenutno število življenj kot ponovljene slike spritea

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `sprite` | Sprite | — | Sprite, narisan enkrat na vsako preostalo življenje; neobvezno |
| `scale` | Število | `1.0` | Enakomeren faktor merila za ikono življenja (1.0 = izvirna velikost); neobvezno |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nariši rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_score` |
| **Ikona** | 🖍️🏆 |
| **Kategorija** | Rezultat |

Nariši trenutni rezultat na zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `caption` | Besedilo | `Score: ` | Besedilo, prikazano pred vrednostjo rezultata; neobvezno |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nastavi zdravje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_health` |
| **Ikona** | 💚 |
| **Kategorija** | Rezultat |

Nastavi zdravje ali mu prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `100` | Vrednost zdravja (0-100) |
| `relative` | Da/Ne | Ne | Prištej trenutnemu zdravju namesto zamenjave |

### Nastavi življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_lives` |
| **Ikona** | ❤️ |
| **Kategorija** | Rezultat |

Nastavi življenja ali jim prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `3` | Število življenj |
| `relative` | Da/Ne | Ne | Prištej trenutnim življenjem namesto zamenjave |

### Nastavi rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_score` |
| **Ikona** | 🏆 |
| **Kategorija** | Rezultat |

Nastavi rezultat ali mu prištej z »Relativno«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost rezultata za nastavitev |
| `relative` | Da/Ne | Ne | Prištej trenutnemu rezultatu namesto zamenjave |

### Prikaži tabelo rekordov

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_highscore` |
| **Ikona** | 🏆 |
| **Kategorija** | Rezultat |

Prikaži pogovorno okno tabele rekordov

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Barva | `#FFFFDD` | Barva ozadja pogovornega okna; neobvezno |
| `new_color` | Barva | `#FF0000` | Barva za nov (kvalificiran) vnos; neobvezno |
| `other_color` | Barva | `#000000` | Barva za druge vnose; neobvezno |
| `allow_new_entry` | Da/Ne | Da | Vprašaj za ime, če se trenutni rezultat kvalificira |

### Preveri zdravje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_health` |
| **Ikona** | ❓💚 |
| **Kategorija** | Rezultat |

Pogoj: primerjaj trenutno zdravje z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |
| `value` | Število | `0` | Vrednost za primerjavo |

### Preveri življenja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_lives` |
| **Ikona** | ❓❤️ |
| **Kategorija** | Rezultat |

Pogoj: primerjaj število življenj z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

### Preveri rezultat

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_score` |
| **Ikona** | ❓🏆 |
| **Kategorija** | Rezultat |

Pogoj: primerjaj rezultat z vrednostjo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `value` | Število | `0` | Vrednost za primerjavo |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="room"></a>
## Soba

### Preveri sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_room` |
| **Ikona** | ❓🚪 |
| **Kategorija** | Soba |

Pogoj: resnično, če se trenutna soba ujema

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `room` | Soba | — | Soba za primerjavo |
| `not_flag` | Da/Ne | Ne | Obrni rezultat; neobvezno |

### Končaj igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `game_end` |
| **Ikona** | 🛑🎮 |
| **Kategorija** | Soba |

Končaj igro

*Parametri:* brez

### Pojdi v sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `goto_room` |
| **Ikona** | 🚪 |
| **Kategorija** | Soba |

Preklopi na določeno sobo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `room` | Soba | — | Ime ciljne sobe |
| `transition` | Izbira | `none` | Učinek prehoda (trenutno sprejet, a ne izrisan); Izbire: `none`; neobvezno |

### Če obstaja naslednja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_next_room_exists` |
| **Ikona** | ❓➡️ |
| **Kategorija** | Soba |

Preveri, ali obstaja naslednja soba za trenutno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `then_actions` | Seznam dejanj | — | Dejanja, če obstaja naslednja soba |
| `else_actions` | Seznam dejanj | — | Dejanja, če naslednja soba ne obstaja |

### Če obstaja prejšnja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_previous_room_exists` |
| **Ikona** | ❓⬅️ |
| **Kategorija** | Soba |

Preveri, ali obstaja prejšnja soba pred trenutno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `then_actions` | Seznam dejanj | — | Dejanja, če obstaja prejšnja soba |
| `else_actions` | Seznam dejanj | — | Dejanja, če prejšnja soba ne obstaja |

### Naslednja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `next_room` |
| **Ikona** | ➡️ |
| **Kategorija** | Soba |

Pojdi v naslednjo sobo

*Parametri:* brez

### Prejšnja soba

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `previous_room` |
| **Ikona** | ⬅️ |
| **Kategorija** | Soba |

Pojdi v prejšnjo sobo

*Parametri:* brez

### Znova zaženi sobo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `restart_room` |
| **Ikona** | 🔄 |
| **Kategorija** | Soba |

Znova zaženi trenutno sobo

*Parametri:* brez

### Nastavi naslov sobe

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_room_caption` |
| **Ikona** | 🏷️ |
| **Kategorija** | Soba |

Nastavi naslov okna igre

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `caption` | Besedilo | — | Besedilo naslova okna |

---

<a id="timing"></a>
## Čas

### Nastavi budilko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_alarm` |
| **Ikona** | ⏰ |
| **Kategorija** | Čas |

Nastavi budilko

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `alarm_number` | Število | `0` | Katera budilka (0-11) |
| `steps` | Število | `30` | Število korakov do sprožitve budilke (30 = 0,5 s pri 60 FPS) |

### Premor

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sleep` |
| **Ikona** | 💤 |
| **Kategorija** | Čas |

Zaustavi igro za določeno število milisekund, nato nadaljuj. Zvoki se med premorom še naprej predvajajo (na primer, da se zvok konča pred menjavo sobe). Opomba: izrisovanje in vnos sta med premorom zamrznjena, zato ohranjaj kratke dolžine

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `milliseconds` | Število | `1000` | Trajanje premora, v milisekundah (1000 = 1 sekunda) |

---

<a id="audio"></a>
## Zvok

### Preveri predvajanje zvoka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_sound` |
| **Ikona** | ❓🔊 |
| **Kategorija** | Zvok |

Pogoj: resnično, če se navedeni zvok trenutno predvaja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za preverjanje |
| `not_flag` | Da/Ne | Ne | Obrni rezultat; neobvezno |

### Predvajaj glasbo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `play_music` |
| **Ikona** | 🎵 |
| **Kategorija** | Zvok |

Predvajaj glasbo v ozadju (v zanki)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `music` | Zvok | — | Glasbena datoteka za predvajanje |
| `loop` | Da/Ne | Da | Predvajaj glasbo v zanki |
| `volume` | Število | `0.7` | Glasnost (od 0.0 do 1.0) |

### Predvajaj zvok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `play_sound` |
| **Ikona** | 🔊 |
| **Kategorija** | Zvok |

Predvajaj zvočni učinek enkrat

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za predvajanje |
| `volume` | Število | `1.0` | Glasnost (od 0.0 do 1.0) |

### Nastavi glasnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_volume` |
| **Ikona** | 🔉 |
| **Kategorija** | Zvok |

Nastavi splošno glasnost zvoka/glasbe

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `volume` | Število | `1.0` | Glasnost (od 0.0 do 1.0) |

### Ustavi glasbo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_music` |
| **Ikona** | 🔇 |
| **Kategorija** | Zvok |

Ustavi glasbo v ozadju

*Parametri:* brez

### Ustavi zvok

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_sound` |
| **Ikona** | 🔇 |
| **Kategorija** | Zvok |

Ustavi predvajani zvok

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sound` | Zvok | — | Zvok za ustavitev |

---

<a id="game"></a>
## Igra

### Nariši puščico

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_arrow` |
| **Ikona** | ➡️ |
| **Kategorija** | Igra |

Nariši puščico od ene točke do druge

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | Začetni X |
| `y1` | Število | `0` | Začetni Y |
| `x2` | Število | `100` | X konice |
| `y2` | Število | `100` | Y konice |
| `tip_size` | Število | `10` | Velikost konice puščice v pikslih |

### Nariši ozadje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_background` |
| **Ikona** | 🌄 |
| **Kategorija** | Igra |

Nariši sliko ozadja, izbirno tlakovano po vsem zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `background` | Besedilo | — | Ime sredstva ozadja |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `tiled` | Da/Ne | Ne | Tlakuj po vsem zaslonu; neobvezno |

### Nariši krog

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_circle` |
| **Ikona** | ⭕ |
| **Kategorija** | Igra |

Nariši zapolnjen ali obrisan krog

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | X središče |
| `y` | Število | `0` | Y središče |
| `radius` | Število | `50` | Polmer kroga |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši elipso

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_ellipse` |
| **Ikona** | 🥚 |
| **Kategorija** | Igra |

Nariši zapolnjeno ali obrisano elipso znotraj okvirja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `100` | Y spodaj |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši črto

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_line` |
| **Ikona** | 📏 |
| **Kategorija** | Igra |

Nariši črto med dvema točkama

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | Začetni X |
| `y1` | Število | `0` | Začetni Y |
| `x2` | Število | `100` | Končni X |
| `y2` | Število | `100` | Končni Y |

### Nariši pravokotnik

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_rectangle` |
| **Ikona** | 🟥 |
| **Kategorija** | Igra |

Nariši zapolnjen ali obrisan pravokotnik

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x1` | Število | `0` | X levo |
| `y1` | Število | `0` | Y zgoraj |
| `x2` | Število | `100` | X desno |
| `y2` | Število | `100` | Y spodaj |
| `filled` | Da/Ne | Da | Zapolnjeno ali samo obris; neobvezno |

### Nariši povečano besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_scaled_text` |
| **Ikona** | 🖍️ |
| **Kategorija** | Igra |

Nariši besedilo v poljubnem merilu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Besedilo za risanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `xscale` | Število | `1.0` | Faktor vodoravnega merila |
| `yscale` | Število | `1.0` | Faktor navpičnega merila |

### Nariši sprite

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_sprite` |
| **Ikona** | 🖼️ |
| **Kategorija** | Igra |

Nariši sličico spritea na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sprite za risanje |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `subimage` | Število | `0` | Indeks sličice za risanje |

### Nariši besedilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_text` |
| **Ikona** | 🖍️ |
| **Kategorija** | Igra |

Nariši besedilni niz na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Besedilo za risanje (podpira izraze) |
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `relative` | Da/Ne | Ne | Nariši glede na položaj te instance namesto absolutnih zaslonskih koordinat; neobvezno |

### Nariši spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `draw_variable` |
| **Ikona** | 🔢 |
| **Kategorija** | Igra |

Nariši vrednost spremenljivke na zaslonu

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Položaj X |
| `y` | Število | `0` | Položaj Y |
| `variable` | Besedilo | — | Ime spremenljivke (self.var, global.var ali preprosto ime) |

### Zapolni zaslon z barvo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `fill_color` |
| **Ikona** | 🪣 |
| **Kategorija** | Igra |

Zapolni celotno območje prikaza z enotno barvo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Odpri spletno stran

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `open_webpage` |
| **Ikona** | 🌐 |
| **Kategorija** | Igra |

Odpri URL v privzetem brskalniku

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `url` | Besedilo | — | Spletni naslov za odprtje |

### Znova zaženi igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `restart_game` |
| **Ikona** | 🔁🎮 |
| **Kategorija** | Igra |

Znova zaženi igro iz začetne sobe

*Parametri:* brez

### Nastavi prosojnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_alpha` |
| **Ikona** | 🌫️ |
| **Kategorija** | Igra |

Nastavi prosojnost risanja za naslednja risanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `alpha` | Število | `1.0` | Prosojnost od 0.0 (prozorno) do 1.0 (neprozorno) |

### Nastavi barvo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Igra |

Nastavi barvo in prosojnost risanja za naslednja risanja

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#FFFFFF` | Šestnajstiška barva RGB |
| `alpha` | Število | `1.0` | Prosojnost 0.0–1.0; neobvezno |

### Nastavi barvo risanja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_draw_color` |
| **Ikona** | 🎨 |
| **Kategorija** | Igra |

Nastavi barvo, ki jo uporabljajo naslednja dejanja draw_*

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `color` | Barva | `#000000` | Šestnajstiška barva RGB |

### Nastavi pisavo risanja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_draw_font` |
| **Ikona** | 🔤 |
| **Kategorija** | Igra |

Nastavi pisavo in poravnavo za naslednje risanje besedila

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `font` | Besedilo | — | Ime sredstva pisave (prazno = privzeta pisava); neobvezno |
| `halign` | Izbira | `left` | Vodoravna poravnava besedila; Izbire: `left`, `center`, `right` |
| `valign` | Izbira | `top` | Navpična poravnava besedila; Izbire: `top`, `middle`, `bottom` |

### Nastavi naslov okna

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_window_caption` |
| **Ikona** | 🪟 |
| **Kategorija** | Igra |

Konfiguriraj prikaz rezultata/življenj/zdravja v naslovu okna

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `show_score` | Da/Ne | Da | Dodaj trenutni rezultat naslovu okna |
| `show_lives` | Da/Ne | Da | Dodaj trenutno število življenj naslovu okna |
| `show_health` | Da/Ne | Ne | Dodaj trenutno vrednost zdravja naslovu okna |
| `caption` | Besedilo | — | Neobvezna predpona naslova, prikazana pred števci; neobvezno |

### Prikaži informacije o igri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_info` |
| **Ikona** | ℹ️ |
| **Kategorija** | Igra |

Prikaži zaslon z informacijami o igri

*Parametri:* brez

### Prikaži sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `show_message` |
| **Ikona** | 💬 |
| **Kategorija** | Igra |

Prikaži sporočilo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `message` | Besedilo | `Hello!` | Besedilo sporočila |

---

<a id="control"></a>
## Nadzor

### Preveri, ali je prazno

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `check_empty` |
| **Ikona** | 🔍 |
| **Kategorija** | Nadzor |

Resnično, ko je (x, y) brez trkov. Uporabi s start_block/end_block za pogojevanje naslednjega dejanja/dejanj, v slogu GM

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `self.x` | Položaj X za preverjanje (izraz dovoljen, npr. self.x + 32) |
| `y` | Besedilo | `self.y` | Položaj Y za preverjanje (izraz dovoljen, npr. self.y + 32) |
| `relative` | Da/Ne | Ne | Obravnavaj X/Y kot odmike od položaja te instance namesto absolutnih koordinat; neobvezno |
| `objects` | Izbira | `solid` | Katere instance štejejo kot zasedajoče položaj; Izbire: `solid`, `all` |

### Komentar

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `comment` |
| **Ikona** | ⚠️ |
| **Kategorija** | Nadzor |

Komentar na seznamu dejanj (brez učinka med izvajanjem)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `text` | Besedilo | — | Prosto oblikovano besedilo komentarja; neobvezno |

### Sicer

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `else_action` |
| **Ikona** | ⚡ |
| **Kategorija** | Nadzor |

Označuje vejo »sicer« pogoja

*Parametri:* brez

### Konec bloka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `end_block` |
| **Ikona** | 📁 |
| **Kategorija** | Nadzor |

Končaj blok dejanj

*Parametri:* brez

### Izvedi kodo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `execute_code` |
| **Ikona** | 📜 |
| **Kategorija** | Nadzor |

Izvedi vgrajeni blok kode Python

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `code` | Koda | — | Koda Python za ovrednotenje glede na instanco |

### Izvedi skripto

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `execute_script` |
| **Ikona** | 📜 |
| **Kategorija** | Nadzor |

Izvedi eno od skript projekta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `script` | Skripta | — | Ime skripte projekta za zagon |
| `arg0` | Besedilo | — | Na voljo v skripti kot argument0; neobvezno |
| `arg1` | Besedilo | — | Na voljo v skripti kot argument1; neobvezno |
| `arg2` | Besedilo | — | Na voljo v skripti kot argument2; neobvezno |
| `arg3` | Besedilo | — | Na voljo v skripti kot argument3; neobvezno |
| `arg4` | Besedilo | — | Na voljo v skripti kot argument4; neobvezno |

### Zapusti dogodek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `exit_event` |
| **Ikona** | 🚪 |
| **Kategorija** | Nadzor |

Ustavi izvajanje preostalih dejanj v tem dogodku

*Parametri:* brez

### Če je mogoče potisniti

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_can_push` |
| **Ikona** | 📦 |
| **Kategorija** | Nadzor |

Preveri, ali je mogoče potisniti škatlo/predmet v trenutni smeri (v slogu Sokoban)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `direction` | Izbira | `facing` | Smer za preverjanje potiska; Izbire: `facing` |
| `object_type` | Besedilo | `box` | Vrsta potisnjenega predmeta |
| `then_action` | Izbira | `push_and_move` | Dejanje, če je potisk mogoč; Izbire: `push_and_move`, `none` |
| `else_action` | Izbira | `stop_movement` | Dejanje, če je potisk blokiran; Izbire: `stop_movement`, `none` |

### Če trk

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_collision` |
| **Ikona** | ❓💥 |
| **Kategorija** | Nadzor |

Pogoj: resnično, če bi instanca trčila pri odmiku (x, y)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | Vodoravni odmik za preverjanje |
| `y` | Število | `0` | Navpični odmik za preverjanje |
| `object` | Besedilo | `any` | »any«, »solid« ali ime predmeta; Izbire: `any`, `solid`; neobvezno |
| `not_flag` | Da/Ne | Ne | Zanikaj rezultat; neobvezno |

### Če trk pri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_collision_at` |
| **Ikona** | 🎯 |
| **Kategorija** | Nadzor |

Preveri trk na položaju

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Besedilo | `self.x + 32` | Izraz položaja X |
| `y` | Besedilo | `self.y` | Izraz položaja Y |
| `object_type` | Izbira | `any` | Vrsta predmeta za preverjanje; Izbire: `any`, `solid` |
| `then_actions` | Seznam dejanj | — | Dejanja, če je najden trk |
| `else_actions` | Seznam dejanj | — | Dejanja, če ni trka |

### Če pogoj

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_condition` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Pogojno preverjanje z dejanji potem/sicer

*Parametri:* brez

### Če predmet obstaja

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_object_exists` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Pogoj: resnično, če obstaja vsaj ena instanca predmeta

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Vrsta predmeta za preverjanje |
| `not_flag` | Da/Ne | Ne | Zanikaj rezultat (ukrepaj, ko predmet NE obstaja); neobvezno |

### Ponovi

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `repeat` |
| **Ikona** | 🔁 |
| **Kategorija** | Nadzor |

Ponovi naslednje dejanje/blok N-krat

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `times` | Število | `10` | Število ponovitev |
| `actions` | Seznam dejanj | — | Dejanja za ponovitev |

### Nastavi spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_variable` |
| **Ikona** | 📝 |
| **Kategorija** | Nadzor |

Nastavi spremenljivko instance ali globalno

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `variable` | Besedilo | — | Ime spremenljivke |
| `value` | Besedilo | `0` | Vrednost (število, niz ali izraz) |
| `scope` | Izbira | `self` | Obseg spremenljivke; Izbire: `self`, `other`, `global` |
| `relative` | Da/Ne | Ne | Prištej trenutni vrednosti namesto zamenjave |

### Začetek bloka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_block` |
| **Ikona** | 📂 |
| **Kategorija** | Nadzor |

Začni blok dejanj (za združevanje)

*Parametri:* brez

### Preveri verjetnost

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_chance` |
| **Ikona** | 🎲❓ |
| **Kategorija** | Nadzor |

Pogoj: resnično z verjetnostjo 1 od »sides«

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sides` | Število | `6` | Verjetnost 1 od N, da je resnično |

### Preveri izraz

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_expression` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Preveri, ali je izraz resničen

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `expression` | Besedilo | — | Izraz za ovrednotenje (resnično, če >= 0.5) |
| `then_actions` | Seznam dejanj | — | Dejanja, če resnično |
| `else_actions` | Seznam dejanj | — | Dejanja, če neresnično |

### Postavi vprašanje

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_question` |
| **Ikona** | ❓💬 |
| **Kategorija** | Nadzor |

Pogoj: prikaži pogovorno okno da/ne; resnično, če uporabnik odgovori z da

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `question` | Besedilo | `Continue?` | Vprašanje, prikazano igralcu |

### Preveri spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_variable` |
| **Ikona** | ❓ |
| **Kategorija** | Nadzor |

Preveri vrednost spremenljivke instance ali globalne

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `variable` | Besedilo | — | Ime spremenljivke |
| `value` | Besedilo | `0` | Vrednost za primerjavo |
| `scope` | Izbira | `self` | Obseg spremenljivke; Izbire: `self`, `other`, `global` |
| `operation` | Izbira | `equal` | Primerjalni operator; Izbire: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

<a id="grid"></a>
## Mreža

### Če na mreži

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `if_on_grid` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Preveri, ali je predmet poravnan na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |
| `then_actions` | Seznam dejanj | — | Dejanja, če na mreži |
| `else_actions` | Seznam dejanj | — | Dejanja, če ne na mreži |

### Pripni na mrežo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `snap_to_grid` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Poravnaj položaj instance na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |

### Ustavi, če ni pritisnjenih tipk

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stop_if_no_keys` |
| **Ikona** | ▦ |
| **Kategorija** | Mreža |

Ustavi gibanje po mreži, ko ni pritisnjena nobena tipka za gibanje (odlično za gladko pripenjanje na mrežo)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `grid_size` | Število | `32` | Velikost celice mreže v pikslih |

### Preveri poravnavo na mrežo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `test_alignment` |
| **Ikona** | ❓▦ |
| **Kategorija** | Mreža |

Pogoj: resnično, če je instanca poravnana na mrežo

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hsnap` | Število | `32` | Vodoravni razmik mreže v pikslih |
| `vsnap` | Število | `32` | Navpični razmik mreže v pikslih |

---

<a id="views"></a>
## Pogledi

### Omogoči poglede

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `enable_views` |
| **Ikona** | 🎥 |
| **Kategorija** | Pogledi |

Vklopi ali izklopi sistem kamere/pogleda sobe (omogoča drsenje ravni, ko je večja od okna)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `enable` | Da/Ne | Da | Vklop = pogledi kamere; izklop = nariši celotno sobo naenkrat |

### Nastavi pogled

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_view` |
| **Ikona** | 🎥 |
| **Kategorija** | Pogledi |

Konfiguriraj pogled kamere: kateri del sobe prikazuje, kje se izriše na zaslonu in predmet za sledenje

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `view` | Izbira | `0` | Katerega od 8 pogledov konfigurirati; Izbire: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Da/Ne | Da | Nariši ta pogled |
| `view_x` | Število | `0` | Levi rob prikazanega območja sobe |
| `view_y` | Število | `0` | Zgornji rob prikazanega območja sobe |
| `view_w` | Število | `800` | Širina prikazanega območja sobe |
| `view_h` | Število | `600` | Višina prikazanega območja sobe |
| `port_x` | Število | `0` | Levi rob na zaslonu |
| `port_y` | Število | `0` | Zgornji rob na zaslonu |
| `port_w` | Število | `800` | Širina, narisana na zaslonu |
| `port_h` | Število | `600` | Višina, narisana na zaslonu |
| `follow` | Predmet | — | Predmet, ki mu kamera sledi (prazno = fiksni pogled); neobvezno |
| `hborder` | Število | `32` | Vodoravni rob, preden se kamera pomakne |
| `vborder` | Število | `32` | Navpični rob, preden se kamera pomakne |
| `hspeed` | Število | `-1` | Največja vodoravna hitrost drsenja (-1 = takoj) |
| `vspeed` | Število | `-1` | Največja navpična hitrost drsenja (-1 = takoj) |

---

<a id="3d-view"></a>
## Pogled 3D

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

## Glejte tudi

- [Referenca dogodkov](Event-Reference_sl) — dogodki, ki sprožijo dejanja
- [Vodnik po prednastavitvah](Preset-Guide_sl) — katera dejanja izpostavlja vsaka prednastavitev/izdaja
- [Pogled 3D](3D-View_sl) — dejanja pogleda iz prve osebe (raycast)
- [Razširitve](Extensions_sl) — kako so zagotovljena dejanja Pogleda 3D
