# Drugi Dogodki

*[Domov](Home_sl) | [Referenca Dogodkov](Event-Reference_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

### Outside Room
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `outside_room` |
| **Ikona** | 🚫 |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko je instanca popolnoma zunaj meja sobe.

**Pogoste uporabe:**
- Uničenje izstrelkov zunaj zaslona
- Ovijanje na drugo stran
- Sprožitev konca igre

---

### Intersect Boundary
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `intersect_boundary` |
| **Ikona** | ⚠️ |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko instanca dotakne mejo sobe.

**Pogoste uporabe:**
- Ohranitev igralca znotraj meja
- Odboj od robov

---

### No More Lives
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `no_more_lives` |
| **Ikona** | 💀 |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko življenja padejo na 0 ali manj.

**Pogoste uporabe:**
- Zaslon konca igre
- Ponovni zagon igre
- Prikaz končnega rezultata

---

### No More Health
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `no_more_health` |
| **Ikona** | 💔 |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko zdravje pade na 0 ali manj.

**Pogoste uporabe:**
- Izguba življenja
- Ponovno pojavitev igralca
- Sprožitev animacije smrti

---

### Animation End
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `animation_end` |
| **Ikona** | 🎞️ |
| **Kategorija** | Drugo |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko animacija spritea instance dokonča celoten cikel (se vrne z zadnje sličice na prvo).

**Pogoste uporabe:**
- Uničenje enkratnega učinka (eksplozija) po enkratnem predvajanju
- Preklop na drugo animacijo, ko se trenutna konča
- Napredovanje stanjskega avtomata ob koncu animacije

---

## Druge Kategorije Dogodkov

- [Dogodki Objekta](Event-Reference-Object_sl) - Create, Step, Destroy
- [Dogodki Vnosa](Event-Reference-Input_sl) - Tipkovnica, Miška
- [Dogodki Trkov](Event-Reference-Collision_sl) - Trki objektov
- [Časovni Dogodki](Event-Reference-Timing_sl) - Alarmi, Variante Step
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre

[← Nazaj na Referenco Dogodkov](Event-Reference_sl)
