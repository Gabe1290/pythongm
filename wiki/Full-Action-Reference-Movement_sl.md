# Gibanje

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

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

## Druge Kategorije

- [Instanca](Full-Action-Reference-Instance_sl) (12)
- [Rezultat](Full-Action-Reference-Score_sl) (11)
- [Soba](Full-Action-Reference-Room_sl) (13)
- [Čas](Full-Action-Reference-Timing_sl) (8)
- [Zvok](Full-Action-Reference-Audio_sl) (6)
- [Igra](Full-Action-Reference-Game_sl) (25)
- [Nadzor](Full-Action-Reference-Control_sl) (19)
- [Mreža](Full-Action-Reference-Grid_sl) (4)
- [Pogledi](Full-Action-Reference-Views_sl) (2)
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)
- [Réseau](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
