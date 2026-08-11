# Dogodki Trkov

*[Domov](Home_sl) | [Referenca Dogodkov](Event-Reference_sl) | [Popolna referenca dejanj](Full-Action-Reference_sl)*

### Trk
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `collision` |
| **Ikona** | 💥 |
| **Kategorija** | Trk |
| **Preset** | Začetnik |

**Opis:** Sproži se, ko se ta instanca prekriva z drugo vrsto objekta.

**Konfiguracija:** Izberite, katera vrsta objekta sproži ta trk.

**Posebna spremenljivka:** `other` - Referenca na trkajočo instanco.

**Kdaj se sproži:** Vsak okvir, ko se instance prekrivajo.

**Pogoste uporabe:**
- Zbiranje predmetov
- Prejemanje poškodbe
- Zadevanje sten
- Sprožitev dogodkov

**Primeri dogodkov trkov:**
- `collision_with_obj_coin` - Igralec se dotakne kovanca
- `collision_with_obj_enemy` - Igralec se dotakne sovražnika
- `collision_with_obj_wall` - Instanca zadene steno

---

## Druge Kategorije Dogodkov

- [Dogodki Objekta](Event-Reference-Object_sl) - Create, Step, Destroy
- [Dogodki Vnosa](Event-Reference-Input_sl) - Tipkovnica, Miška
- [Časovni Dogodki](Event-Reference-Timing_sl) - Alarmi, Variante Step
- [Dogodki Risanja](Event-Reference-Drawing_sl) - Prilagojeno izrisovanje
- [Dogodki Sobe](Event-Reference-Room_sl) - Prehodi med sobami
- [Dogodki Igre](Event-Reference-Game_sl) - Začetek/Konec igre
- [Drugi Dogodki](Event-Reference-Other_sl) - Meje, Življenja, Zdravje

[← Nazaj na Referenco Dogodkov](Event-Reference_sl)
