# Časovni Dogodki

*[Domov](Home_sl) | [Referenca Dogodkov](Event-Reference_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

### Budilka
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `alarm` |
| **Ikona** | ⏰ |
| **Kategorija** | Časovni |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko odštevanje alarma doseže nic.

**Razpoložljivi alarmi:** 12 neodvisnih alarmov (alarm[0] do alarm[11])

**Nastavitev alarmov:** Uporabite akcijo "Nastavi Alarm" s koraki (60 korakov ≈ 1 sekunda pri 60 FPS)

**Pogoste uporabe:**
- Časovno generiranje
- Časi ohlajanja
- Zakasneli učinki
- Ponavljajoče akcije (ponovno nastavite alarm v dogodku alarma)

---

### Začetek koraka
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `begin_step` |
| **Ikona** | ▶️ |
| **Kategorija** | Korak |
| **Preset** | Začetnik |

**Opis:** Sproži se na začetku vsakega okvirja, pred rednimi dogodki Step.

**Vrstni red izvajanja:** Začetek koraka → Step → Konec koraka

**Pogoste uporabe:**
- Obdelava vnosa
- Pred-gibalni izračuni

---

### Konec koraka
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `end_step` |
| **Ikona** | ⏹️ |
| **Kategorija** | Korak |
| **Preset** | Začetnik |

**Opis:** Sproži se na koncu vsakega okvirja, po trkih.

**Pogoste uporabe:**
- Končne prilagoditve položaja
- Operacije čiščenja
- Posodobitve stanja po trkih

---

## Druge Kategorije Dogodkov

- [Dogodki Objekta](Event-Reference-Object_sl) - Create, Step, Destroy
- [Dogodki Vnosa](Event-Reference-Input_sl) - Tipkovnica, Miška
- [Dogodki Trkov](Event-Reference-Collision_sl) - Trki objektov
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre
- [Drugi Dogodki](Event-Reference-Other_sl) - Meje, Življenja, Zdravje

[← Nazaj na Referenco Dogodkov](Event-Reference_sl)
