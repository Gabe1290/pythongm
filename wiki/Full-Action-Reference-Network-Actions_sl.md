# Network

*[Domov](Home_sl) | [Vodnik po prednastavitvah](Preset-Guide_sl) | [Referenca dogodkov](Event-Reference_sl)*

> **Samodejno ustvarjeno** iz registra dejanj IDE z `tools/gen_action_reference.py` — ne urejajte ročno; po spremembi dejanj znova zaženite generator. Prevodi so iz `tools/action_ref_i18n.py`.

### Dodeli omrežno tipko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `bind_network_input` |
| **Ikona** | ⌨️ |
| **Kategorija** | Network |

Poveže krajevno tipko z »imenovanim vnosom«, o katerem se poroča gostitelju. Gostitelj ga nato preveri z »Če igralec pritisne«. Puščice in preslednica so že povezane ("left", "right", "up", "down", "space")

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Besedilo | — | A key name: "space", "left", "a", "5", "lshift"... |

### Ustvari omrežni predmet

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `network_spawn` |
| **Ikona** | ✨ |
| **Kategorija** | Network |

Samo pri gostitelju: ustvari primerek, ki se samodejno pojavi pri vseh odjemalcih kot zglajen »duh«. Pri odjemalcu ne naredi ničesar. Ustvarjeni primerek vodi gostitelj – njegovo igralno logiko zavaruj z global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `object` | Predmet | — | The type of object to create |
| `x` | Besedilo | `0` |  |
| `y` | Besedilo | `0` |  |
| `owner` | Besedilo | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; neobvezno |
| `relative` | Da/Ne | Ne | Position relative to the object running the action; neobvezno |

### Gosti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `host_game` |
| **Ikona** | 🌐 |
| **Kategorija** | Network |

Ta računalnik postane gostitelj večigralske igre v krajevnem omrežju: drugi igralci se povežejo nanj. Pokliči enkrat (na primer v dogodku Ustvari pri krmilniku sobe). Nastavi global.player_id = 0 in global.network_role = "host"

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `game_name` | Besedilo | `PyGameMaker` | Name shown in the server list (network discovery); neobvezno |
| `max_players` | Število | `8` | Largest number of players, host included (2 to 16); neobvezno |
| `port` | Število | `45782` | TCP port -- must be the same on the host and every client; neobvezno |
| `player_name` | Besedilo | — | This player's name (empty = global.player_name, or "Player"); neobvezno |
| `show_lobby` | Da/Ne | Ne | Show a "Waiting for players..." screen with a Start button before the game begins; neobvezno |

### Če upravljam ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `is_instance_owner` |
| **Ikona** | ❓ |
| **Kategorija** | Network |

Pogoj: resničen, kadar je TA računalnik lastnik sinhroniziranega primerka. Postavi ga pred blok, da se krmilna logika izvaja le na računalniku pravega igralca

*Parametri:* brez

### Če igralec pritisne

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `remote_input` |
| **Ikona** | ❓ |
| **Kategorija** | Network |

Pogoj pri gostitelju: resničen, dokler navedeni igralec drži navedeni vnos. Gostitelju omogoča, da se odziva na tipke odjemalca, ne da bi bil lastnik njegovega lika

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Player number (0 = host) |
| `name` | Besedilo | — | The named input to test (e.g. "jump") |

### Pridruži se igri

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `join_game` |
| **Ikona** | 🔌 |
| **Kategorija** | Network |

Poveže se z večigralsko igro v krajevnem omrežju, ki jo gosti drug računalnik. Gostitelj nastavi global.player_id (1, 2, ...). Če gostitelj ni dosegljiv, se igra nadaljuje kot enoigralska

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `host` | Besedilo | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); neobvezno |
| `port` | Število | `45782` | TCP port -- must match the host's; neobvezno |
| `player_name` | Besedilo | — | This player's name (empty = global.player_name, or "Player"); neobvezno |

### Zapusti igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `leave_game` |
| **Ikona** | 🚪 |
| **Kategorija** | Network |

Prekine povezavo (ali preneha gostiti) in počisti globalne omrežne spremenljivke

*Parametri:* brez

### Preberi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `get_shared_var` |
| **Ikona** | 📥 |
| **Kategorija** | Network |

Skupno spremenljivko prepiše v globalno, da jo lahko uporabiš v izračunu. Enako kot neposredno branje global.<ime>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | Name of the shared variable to read |
| `into` | Besedilo | — | Name of the global variable to write the value into |

### Pošlji omrežno sporočilo

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `send_network_message` |
| **Ikona** | ✉️ |
| **Kategorija** | Network |

Razpošlje sporočilo po tvoji izbiri. Na zadevnih računalnikih sproži dogodek »Omrežno sporočilo«, z global.network_event / global.network_data / global.network_sender

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `event` | Besedilo | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Besedilo | — | A number, text, true/false, or a short list; neobvezno |
| `target` | Izbira | `all` | all = everyone; host = the host only; Izbire: `all`, `host` |

### Nastavi omrežni način (v1)

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_network_mode` |
| **Ikona** | 🌐 |
| **Kategorija** | Network |

Starejše nizkonivojsko dejanje: sobo zažene v načinu gostitelja ali odjemalca (samo opazovanje – vnos odjemalca nima učinka). Raje uporabi »Gosti igro« / »Pridruži se igri«. Ohranjeno za obstoječe projekte in za zastavici --net-host / --net-client

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `mode` | Izbira | `host` | Host = others connect to you; Client = you connect to a host; Izbire: `host`, `client` |
| `host` | Besedilo | `127.0.0.1` | The host's LAN IP address (Client mode only); neobvezno |
| `port` | Število | `45782` | TCP port -- must be the same on the host and the client; neobvezno |

### Nastavi skupno spremenljivko

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_shared_var` |
| **Ikona** | 📤 |
| **Kategorija** | Network |

Zapiše spremenljivko, ki si jo delijo vsi računalniki. Pri gostitelju se uveljavi takoj; pri odjemalcu je to zahteva, poslana gostitelju. Povsod berljiva kot global.<ime>

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `name` | Besedilo | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Besedilo | `0` | A number, text or true/false (complex objects are refused) |

### Nastavi lastnika primerka

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_instance_owner` |
| **Ikona** | 🎮 |
| **Kategorija** | Network |

Določi, kateri igralec vodi ta sinhronizirani primerek (0 = gostitelj; 1, 2, ... = odjemalci). Na računalniku tega igralca se primerek računa krajevno in se odziva gladko, njegovo stanje pa se sporoča gostitelju; drugje je zglajen duh. Pokliči pri gostitelju, zavarovano z global.is_host == 1

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `player` | Besedilo | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Nastavi hitrost sinhronizacije

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `set_sync_rate` |
| **Ikona** | ⏱️ |
| **Kategorija** | Network |

Nastavi, kako pogosto gostitelj pošilja posnetke stanja in koliko za njimi jih odjemalci rišejo. Pokliči enkrat pri gostitelju, za zakasnitev pa tudi pri odjemalcih

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `hz` | Število | `20` | 10-30 works well on a local network (default 20); neobvezno |
| `interp_ms` | Število | `100` | How far behind ghosts are drawn, in milliseconds (default 100); neobvezno |

### Začni omrežno igro

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `start_networked_game` |
| **Ikona** | 🚦 |
| **Kategorija** | Network |

Samo pri gostitelju: vse pospremi iz čakalnice in začne igro. Na vsakem računalniku sproži dogodek »Omrežna igra se je začela«

*Parametri:* brez

### Sinhroniziraj ta primerek

| Lastnost | Vrednost |
|----------|-------|
| **Ime** | `sync_instance` |
| **Ikona** | 🔗 |
| **Kategorija** | Network |

Primerek, ki izvaja to dejanje, označi kot sinhroniziran: njegov položaj, zasuk, slika in vidnost se prepišejo na vse računalnike. Pokliči v dogodku Ustvari. Privzeto je last gostitelja; z »Nastavi lastnika primerka« ga lahko vodi odjemalec

| Parameter | Vrsta | Privzeto | Opombe |
|-----------|------|---------|-------|
| `vars` | Besedilo | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); neobvezno |

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
- [Pogled 3D](Full-Action-Reference-3D-View-Actions_sl) (16)
- [Particles](Full-Action-Reference-Particles_sl) (8)

[← Nazaj na Popolno Referenco Dejanj](Full-Action-Reference_sl)
