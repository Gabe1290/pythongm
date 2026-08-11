# Dogodki Vnosa

*[Domov](Home_sl) | [Referenca Dogodkov](Event-Reference_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

### Tipkovnica (Neprekinjena)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard` |
| **Ikona** | ⌨️ |
| **Kategorija** | Vnos |
| **Preset** | Začetnik |

**Opis:** Sproži se neprekinjeno, medtem ko je tipka pritisnjena.

**Najboljše za:** Gladko, neprekinjeno gibanje

**Podprte Tipke:**
- Puščične tipke (gor, dol, levo, desno)
- Črke (A-Z)
- Številke (0-9)
- Presledek, Enter, Escape
- Funkcijske tipke (F1-F12)
- Modifikacijske tipke (Shift, Ctrl, Alt)

---

### Pritisk Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_press` |
| **Ikona** | 🔘 |
| **Kategorija** | Vnos |
| **Preset** | Srednji |

**Opis:** Sproži se enkrat, ko je tipka prvič pritisnjena.

**Najboljše za:** Posamezne akcije (skok, strel, izbira v meniju)

**Razlika od Tipkovnice:** Sproži se samo enkrat na pritisk, ne med držanjem.

---

### Sprostitev Tipkovnice
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_release` |
| **Ikona** | ⬆️ |
| **Kategorija** | Vnos |
| **Preset** | Popoln (Razvojna izdaja) |

**Opis:** Sproži se enkrat, ko je tipka sproščena.

**Pogoste uporabe:**
- Ustavitev gibanja ob sprostitvi tipke
- Zaključek polnilnih napadov
- Preklop stanj

---

### Tipkovnica (Nobene tipke)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `keyboard_no_key` |
| **Ikona** | ⌨️ |
| **Kategorija** | Vnos |
| **Preset** | Začetnik |

**Opis:** Sproži se ob vsakem sličici, medtem ko **nobena** tipka ni pritisnjena.

**Kdaj se sproži:** Ob vsaki sličici, ko je tipkovnica nedejavna, *pred* dogodkom Step.

**Pogoste uporabe:**
- Ustavitev gibanja, ko igralec sprosti vse tipke (igre na mreži/labirinti)
- Animacije mirovanja

---

### Miška
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `mouse` |
| **Ikona** | 🖱️ |
| **Kategorija** | Vnos |
| **Preset** | Popoln (Razvojna izdaja) |

**Opis:** Dogodki gumbov miške in gibanja.

**Vrste Dogodkov:**

| Vrsta | Opis |
|-------|------|
| Levi Gumb | Klik z levim gumbom miške |
| Desni Gumb | Klik z desnim gumbom miške |
| Srednji Gumb | Klik s srednjim/koleščkom |
| Vstop Miške | Kazalec vstopi v meje instance |
| Izstop Miške | Kazalec izstopi iz mej instance |
| Globalni Levi Gumb | Levi klik kjerkoli |
| Globalni Desni Gumb | Desni klik kjerkoli |

---

## Druge Kategorije Dogodkov

- [Dogodki Objekta](Event-Reference-Object_sl) - Create, Step, Destroy
- [Dogodki Trkov](Event-Reference-Collision_sl) - Trki objektov
- [Časovni Dogodki](Event-Reference-Timing_sl) - Alarmi, Variante Step
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre
- [Drugi Dogodki](Event-Reference-Other_sl) - Meje, Življenja, Zdravje

[← Nazaj na Referenco Dogodkov](Event-Reference_sl)
