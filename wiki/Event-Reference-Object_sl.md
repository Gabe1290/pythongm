# Dogodki Objekta

*[Domov](Home_sl) | [Referenca Dogodkov](Event-Reference_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

### Create
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `create` |
| **Ikona** | 🎯 |
| **Kategorija** | Objekt |
| **Preset** | Začetnik |

**Opis:** Izvršeno enkrat, ko je instanca prvič ustvarjena.

**Kdaj se sproži:**
- Ko je instanca postavljena v sobo ob zagonu igre
- Ko je ustvarjena preko akcije "Ustvari Instanco"
- Po prehodih sobe za nove instance

**Pogoste uporabe:**
- Inicializacija spremenljivk
- Nastavitev začetnih vrednosti
- Konfiguracija začetnega stanja

---

### Step
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `step` |
| **Ikona** | ⭐ |
| **Kategorija** | Objekt |
| **Preset** | Začetnik |

**Opis:** Izvršeno vsak okvir (tipično 60-krat na sekundo).

**Kdaj se sproži:** Neprekinjeno, vsak okvir igre.

**Pogoste uporabe:**
- Neprekinjeno gibanje
- Preverjanje pogojev
- Posodabljanje položajev
- Logika igre

**Opomba:** Bodite previdni z zmogljivostjo - koda tu teče nenehno.

---

### Destroy
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `destroy` |
| **Ikona** | 💥 |
| **Kategorija** | Objekt |
| **Preset** | Srednji |

**Opis:** Izvršeno, ko je instanca uničena.

**Kdaj se sproži:** Tik preden je instanca odstranjena iz igre.

**Pogoste uporabe:**
- Generiranje učinkov (eksplozije, delci)
- Spuščanje predmetov
- Posodabljanje rezultatov
- Predvajanje zvokov

---

## Druge Kategorije Dogodkov

- [Dogodki Vnosa](Event-Reference-Input_sl) - Tipkovnica, Miška
- [Dogodki Trkov](Event-Reference-Collision_sl) - Trki objektov
- [Časovni Dogodki](Event-Reference-Timing_sl) - Alarmi, Variante Step
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre
- [Drugi Dogodki](Event-Reference-Other_sl) - Meje, Življenja, Zdravje

[← Nazaj na Referenco Dogodkov](Event-Reference_sl)
