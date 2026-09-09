# Delci

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Izpusti delce

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `burst_particles` |
| **Ikona** | 💥 |
| **Kategorija** | Delci |

Iz nazadnje ustvarjenega izvora izpusti enkraten izbruh delcev

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `particle_type` | Število | `0` | Oznaka vrste delca (iz »Ustvari vrsto delca«) |
| `number` | Število | `10` | Koliko delcev naj se izpusti |

### Počisti delce

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `clear_particles` |
| **Ikona** | 🧹 |
| **Kategorija** | Delci |

Odstrani vse dejavne delce, ohrani pa vrste delcev in izvore

*Parametri:* brez

### Ustvari izvor

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_emitter` |
| **Ikona** | 🌀 |
| **Kategorija** | Delci |

Ustvari območje, ki oddaja delce (vrnjena oznaka se shrani za naslednje dejanje, ki uporablja izvor)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `x` | Število | `0` | X središča izvora (koordinate sobe) |
| `y` | Število | `0` | Y središča izvora (koordinate sobe) |
| `width` | Število | `0` | Širina območja izvora |
| `height` | Število | `0` | Višina območja izvora |
| `shape` | Izbira | `rectangle` | Oblika območja izvora, v katerem nastajajo delci; Izbire: `rectangle`, `ellipse`, `diamond`, `line` |

### Ustvari sistem delcev

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_particle_system` |
| **Ikona** | ✨ |
| **Kategorija** | Delci |

Ustvari sistem delcev, pripet na ta primerek (nadomesti obstoječega)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `depth` | Število | `0` | Globina risanja sistema delcev (za vrstni red med primerki še ni v rabi) |

### Ustvari vrsto delca

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `create_particle_type` |
| **Ikona** | ⚙️ |
| **Kategorija** | Delci |

Določi nov videz oziroma vedenje delca (vrnjena oznaka vrste se shrani za naslednje dejanje, ki uporablja vrsto delca)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `sprite` | Sprite | — | Sličica, s katero se nariše vsak delec; pusti prazno za preprost obarvan krog; neobvezno |
| `size_min` | Število | `1.0` | Najmanjša velikost delca (faktor merila) |
| `size_max` | Število | `1.0` | Največja velikost delca (faktor merila) |
| `size_increase` | Število | `0.0` | Sprememba velikosti na korak (negativna manjša, najmanj 0) |
| `color` | Barva | `#FFFFFF` | Barva delca (uporabljena, kadar sličica ni nastavljena) |
| `alpha` | Število | `1.0` | Prosojnost (0 = neviden, 1 = neprosojen) |
| `speed_min` | Število | `0.0` | Najmanjša hitrost premikanja |
| `speed_max` | Število | `0.0` | Največja hitrost premikanja |
| `direction_min` | Število | `0` | Najmanjši kot smeri (0 = desno, 90 = navzgor) |
| `direction_max` | Število | `360` | Največji kot smeri |
| `life_min` | Število | `100` | Najkrajša življenjska doba, v korakih |
| `life_max` | Število | `100` | Najdaljša življenjska doba, v korakih |

### Odstrani izvor

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_emitter` |
| **Ikona** | 💥 |
| **Kategorija** | Delci |

Odstrani nazadnje ustvarjeni izvor

*Parametri:* brez

### Odstrani sistem delcev

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `destroy_particle_system` |
| **Ikona** | 💥 |
| **Kategorija** | Delci |

Odstrani sistem delcev tega primerka in z njim vse delce in izvore

*Parametri:* brez

### Neprekinjeno oddajaj delce

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `stream_particles` |
| **Ikona** | 🌊 |
| **Kategorija** | Delci |

Iz nazadnje ustvarjenega izvora v vsakem koraku neprekinjeno oddaja delce (0 za ustavitev)

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `particle_type` | Število | `0` | Oznaka vrste delca (iz »Ustvari vrsto delca«) |
| `number` | Število | `1` | Delcev na korak (0 ustavi oddajanje) |

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
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (18)
- [Omrežje](Full-Action-Reference-Network-Actions_sl) (15)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
