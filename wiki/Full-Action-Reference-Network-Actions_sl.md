# Omrežje

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Dodeli omrežno tipko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `bind_network_input` |
| **Ikona** | ⌨️ |
| **Kategorija** | Omrežje |

Poveže krajevno tipko z »imenovanim vnosom«, o katerem se poroča gostitelju. Gostitelj ga nato preveri z »Če igralec pritisne«. Puščice in preslednica so že povezane ("left", "right", "up", "down", "space")

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Oznaka po tvoji izbiri (npr. "jump", "fire") |
| `key` | Besedilo | — | Ime tipke: "space", "left", "a", "5", "lshift"... |

### Ustvari omrežni predmet

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `network_spawn` |
| **Ikona** | ✨ |
| **Kategorija** | Omrežje |

Samo pri gostitelju: ustvari primerek, ki se samodejno pojavi pri vseh odjemalcih kot zglajen »duh«. Pri odjemalcu ne naredi ničesar. Ustvarjeni primerek vodi gostitelj – njegovo igralno logiko zavaruj z global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | Vrsta objekta, ki naj se ustvari |
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `owner` | Besedilo | `0` | Igralec, ki vodi ta primerek (0 = gostitelj). Pogosto global.network_sender znotraj »Igralec se je pridružil«.; neobvezno |
| `relative` | Da/Ne | Ne | Položaj glede na objekt, ki izvaja dejanje; neobvezno |

### Gosti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `host_game` |
| **Ikona** | 🌐 |
| **Kategorija** | Omrežje |

Ta računalnik postane gostitelj večigralske igre v krajevnem omrežju: drugi igralci se povežejo nanj. Pokliči enkrat (na primer v dogodku Ustvari pri krmilniku sobe). Nastavi global.player_id = 0 in global.network_role = "host"

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `game_name` | Besedilo | `PyGameMaker` | Ime, prikazano na seznamu strežnikov (odkrivanje v omrežju); neobvezno |
| `max_players` | Število | `8` | Največje število igralcev, skupaj z gostiteljem (od 2 do 16); neobvezno |
| `port` | Število | `45782` | Vrata TCP – morajo biti enaka pri gostitelju in pri vsakem odjemalcu; neobvezno |
| `player_name` | Besedilo | — | Ime tega igralca (prazno = global.player_name, sicer "Player"); neobvezno |
| `show_lobby` | Da/Ne | Ne | Pred začetkom igre pokaži zaslon »Čakanje na igralce ...« z gumbom za začetek; neobvezno |

### Če upravljam ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `is_instance_owner` |
| **Ikona** | ❓ |
| **Kategorija** | Omrežje |

Pogoj: resničen, kadar je TA računalnik lastnik sinhroniziranega primerka. Postavi ga pred blok, da se krmilna logika izvaja le na računalniku pravega igralca

*Parametri:* brez

### Če igralec pritisne

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `remote_input` |
| **Ikona** | ❓ |
| **Kategorija** | Omrežje |

Pogoj pri gostitelju: resničen, dokler navedeni igralec drži navedeni vnos. Gostitelju omogoča, da se odziva na tipke odjemalca, ne da bi bil lastnik njegovega lika

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Številka igralca (0 = gostitelj) |
| `name` | Besedilo | — | Imenovani vnos, ki se preveri (npr. "jump") |

### Pridruži se igri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `join_game` |
| **Ikona** | 🔌 |
| **Kategorija** | Omrežje |

Poveže se z večigralsko igro v krajevnem omrežju, ki jo gosti drug računalnik. Gostitelj nastavi global.player_id (1, 2, ...). Če gostitelj ni dosegljiv, se igra nadaljuje kot enoigralska

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `host` | Besedilo | `127.0.0.1` | Naslov IP gostitelja v krajevnem omrežju ("auto" odpre vgrajeni zaslon za povezovanje); neobvezno |
| `port` | Število | `45782` | Vrata TCP – morajo se ujemati z gostiteljevimi; neobvezno |
| `player_name` | Besedilo | — | Ime tega igralca (prazno = global.player_name, sicer "Player"); neobvezno |

### Zapusti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `leave_game` |
| **Ikona** | 🚪 |
| **Kategorija** | Omrežje |

Prekine povezavo (ali preneha gostiti) in počisti globalne omrežne spremenljivke

*Parametri:* brez

### Preberi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `get_shared_var` |
| **Ikona** | 📥 |
| **Kategorija** | Omrežje |

Skupno spremenljivko prepiše v globalno, da jo lahko uporabiš v izračunu. Enako kot neposredno branje global.<ime>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Ime skupne spremenljivke, ki naj se prebere |
| `into` | Besedilo | — | Ime globalne spremenljivke, v katero se zapiše vrednost |

### Pošlji omrežno sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `send_network_message` |
| **Ikona** | ✉️ |
| **Kategorija** | Omrežje |

Razpošlje sporočilo po tvoji izbiri. Na zadevnih računalnikih sproži dogodek »Omrežno sporočilo«, z global.network_event / global.network_data / global.network_sender

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `event` | Besedilo | — | Oznaka po tvoji izbiri, ki jo preverja obravnava (npr. "buzz", "answer") |
| `data` | Besedilo | — | Število, besedilo, true/false ali kratek seznam; neobvezno |
| `target` | Izbira | `all` | all = vsi; host = samo gostitelj; Izbire: `all`, `host` |

### Nastavi omrežni način (v1)

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_network_mode` |
| **Ikona** | 🌐 |
| **Kategorija** | Omrežje |

Starejše nizkonivojsko dejanje: sobo zažene v načinu gostitelja ali odjemalca (samo opazovanje – vnos odjemalca nima učinka). Raje uporabi »Gosti igro« / »Pridruži se igri«. Ohranjeno za obstoječe projekte in za zastavici --net-host / --net-client

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `mode` | Izbira | `host` | Gostitelj = drugi se povežejo s teboj; Odjemalec = ti se povežeš z gostiteljem; Izbire: `host`, `client` |
| `host` | Besedilo | `127.0.0.1` | Naslov IP gostitelja v krajevnem omrežju (samo v načinu odjemalca); neobvezno |
| `port` | Število | `45782` | Vrata TCP – morajo biti enaka pri gostitelju in pri odjemalcu; neobvezno |

### Nastavi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_shared_var` |
| **Ikona** | 📤 |
| **Kategorija** | Omrežje |

Zapiše spremenljivko, ki si jo delijo vsi računalniki. Pri gostitelju se uveljavi takoj; pri odjemalcu je to zahteva, poslana gostitelju. Povsod berljiva kot global.<ime>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Preprosto ime (črke, števke, _) – brez presledkov in operatorjev |
| `value` | Besedilo | `0` | Število, besedilo ali true/false (sestavljeni predmeti so zavrnjeni) |

### Nastavi lastnika primerka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_instance_owner` |
| **Ikona** | 🎮 |
| **Kategorija** | Omrežje |

Določi, kateri igralec vodi ta sinhronizirani primerek (0 = gostitelj; 1, 2, ... = odjemalci). Na računalniku tega igralca se primerek računa krajevno in se odziva gladko, njegovo stanje pa se sporoča gostitelju; drugje je zglajen duh. Pokliči pri gostitelju, zavarovano z global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Številka igralca (0 = gostitelj). Pogosto global.network_sender znotraj »Igralec se je pridružil«. |

### Nastavi hitrost sinhronizacije

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sync_rate` |
| **Ikona** | ⏱️ |
| **Kategorija** | Omrežje |

Nastavi, kako pogosto gostitelj pošilja posnetke stanja in koliko za njimi jih odjemalci rišejo. Pokliči enkrat pri gostitelju, za zakasnitev pa tudi pri odjemalcih

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hz` | Število | `20` | 10–30 dobro deluje v krajevnem omrežju (privzeto 20); neobvezno |
| `interp_ms` | Število | `100` | Kako daleč zadaj se rišejo duhovi, v milisekundah (privzeto 100); neobvezno |

### Začni omrežno igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_networked_game` |
| **Ikona** | 🚦 |
| **Kategorija** | Omrežje |

Samo pri gostitelju: vse pospremi iz čakalnice in začne igro. Na vsakem računalniku sproži dogodek »Omrežna igra se je začela«

*Parametri:* brez

### Sinhroniziraj ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sync_instance` |
| **Ikona** | 🔗 |
| **Kategorija** | Omrežje |

Primerek, ki izvaja to dejanje, označi kot sinhroniziran: njegov položaj, zasuk, slika in vidnost se prepišejo na vse računalnike. Pokliči v dogodku Ustvari. Privzeto je last gostitelja; z »Nastavi lastnika primerka« ga lahko vodi odjemalec

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `vars` | Besedilo | — | Imena spremenljivk primerka, ki naj se prav tako prepišejo, ločena z vejicami (npr. "hp, colour"); neobvezno |

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
- [Delci](Full-Action-Reference-Particles_sl) (8)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
