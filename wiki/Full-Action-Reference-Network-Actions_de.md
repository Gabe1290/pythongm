# Netzwerk

*[Startseite](Home_de) | [Voreinstellungs-Leitfaden](Preset-Guide_de) | [Ereignisreferenz](Event-Reference_de)*

> **Automatisch generiert** aus der Aktionsregistrierung der IDE durch `tools/gen_action_reference.py` — nicht von Hand bearbeiten; führen Sie den Generator nach Änderungen an Aktionen erneut aus. Die Übersetzungen stammen aus `tools/action_ref_i18n.py`.

### Netzwerktaste zuweisen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `bind_network_input` |
| **Symbol** | ⌨️ |
| **Kategorie** | Netzwerk |

Verknüpft eine lokale Taste mit einer „benannten Eingabe“, die an den Host gemeldet wird. Der Host prüft sie dann mit „Wenn der Spieler drückt“. Die Pfeiltasten und die Leertaste sind bereits verknüpft ("left", "right", "up", "down", "space")

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Text | — | A key name: "space", "left", "a", "5", "lshift"... |

### Netzwerkobjekt erzeugen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `network_spawn` |
| **Symbol** | ✨ |
| **Kategorie** | Netzwerk |

Nur beim Host: erzeugt eine Instanz, die auf allen Clients automatisch als geglätteter „Geist“ erscheint. Auf einem Client ohne Wirkung. Der Host steuert die erzeugte Instanz – ihre Spiellogik mit global.is_host == 1 absichern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `object` | Objekt | — | The type of object to create |
| `x` | Text | `0` |  |
| `y` | Text | `0` |  |
| `owner` | Text | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; optional |
| `relative` | Ja/Nein | Nein | Position relative to the object running the action; optional |

### Spiel hosten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `host_game` |
| **Symbol** | 🌐 |
| **Kategorie** | Netzwerk |

Wird zum Host einer LAN-Mehrspielerpartie: die anderen Spieler verbinden sich mit dieser Maschine. Nur einmal aufrufen (zum Beispiel im Erstellen-Ereignis des Raum-Controllers). Setzt global.player_id = 0 und global.network_role = "host"

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `game_name` | Text | `PyGameMaker` | Name shown in the server list (network discovery); optional |
| `max_players` | Zahl | `8` | Largest number of players, host included (2 to 16); optional |
| `port` | Zahl | `45782` | TCP port -- must be the same on the host and every client; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |
| `show_lobby` | Ja/Nein | Nein | Show a "Waiting for players..." screen with a Start button before the game begins; optional |

### Wenn ich diese Instanz steuere

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `is_instance_owner` |
| **Symbol** | ❓ |
| **Kategorie** | Netzwerk |

Eine Bedingung: wahr, wenn DIESE Maschine die synchronisierte Instanz besitzt. Vor einen Block setzen, damit die Steuerungslogik nur auf der Maschine des richtigen Spielers läuft

*Parameter:* keine

### Wenn der Spieler drückt

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `remote_input` |
| **Symbol** | ❓ |
| **Kategorie** | Netzwerk |

Eine Bedingung beim Host: wahr, solange der genannte Spieler die genannte Eingabe hält. So kann der Host auf die Tasten eines Clients reagieren, ohne dessen Figur zu besitzen

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host) |
| `name` | Text | — | The named input to test (e.g. "jump") |

### Spiel beitreten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `join_game` |
| **Symbol** | 🔌 |
| **Kategorie** | Netzwerk |

Verbindet sich mit einer LAN-Mehrspielerpartie, die eine andere Maschine hostet. Der Host setzt global.player_id (1, 2, ...). Ist der Host nicht erreichbar, läuft das Spiel als Einzelspieler weiter

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `host` | Text | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); optional |
| `port` | Zahl | `45782` | TCP port -- must match the host's; optional |
| `player_name` | Text | — | This player's name (empty = global.player_name, or "Player"); optional |

### Spiel verlassen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `leave_game` |
| **Symbol** | 🚪 |
| **Kategorie** | Netzwerk |

Trennt die Verbindung (oder beendet das Hosten) und löscht die globalen Netzwerkvariablen

*Parameter:* keine

### Geteilte Variable lesen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `get_shared_var` |
| **Symbol** | 📥 |
| **Kategorie** | Netzwerk |

Kopiert eine geteilte Variable in eine globale Variable, um sie in einer Berechnung zu verwenden. Entspricht dem direkten Lesen von global.<name>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | Name of the shared variable to read |
| `into` | Text | — | Name of the global variable to write the value into |

### Netzwerknachricht senden

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `send_network_message` |
| **Symbol** | ✉️ |
| **Kategorie** | Netzwerk |

Sendet eine eigene Nachricht an alle. Löst auf den betroffenen Maschinen das Ereignis „Netzwerknachricht“ aus, mit global.network_event / global.network_data / global.network_sender

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `event` | Text | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Text | — | A number, text, true/false, or a short list; optional |
| `target` | Auswahl | `all` | all = everyone; host = the host only; Auswahl: `all`, `host` |

### Netzwerkmodus festlegen (v1)

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_network_mode` |
| **Symbol** | 🌐 |
| **Kategorie** | Netzwerk |

Eine ältere Low-Level-Aktion: startet den Raum im Host- oder Client-Modus (nur Zuschauer – die Eingabe eines Clients hat keine Wirkung). Besser „Spiel hosten“ / „Spiel beitreten“ verwenden. Für bestehende Projekte und die Schalter --net-host / --net-client erhalten

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `mode` | Auswahl | `host` | Host = others connect to you; Client = you connect to a host; Auswahl: `host`, `client` |
| `host` | Text | `127.0.0.1` | The host's LAN IP address (Client mode only); optional |
| `port` | Zahl | `45782` | TCP port -- must be the same on the host and the client; optional |

### Geteilte Variable setzen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_shared_var` |
| **Symbol** | 📤 |
| **Kategorie** | Netzwerk |

Schreibt eine Variable, die alle Maschinen teilen. Beim Host wird sie sofort übernommen; auf einem Client ist es eine Anfrage an den Host. Überall lesbar als global.<name>

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `name` | Text | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Text | `0` | A number, text or true/false (complex objects are refused) |

### Besitzer der Instanz festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_instance_owner` |
| **Symbol** | 🎮 |
| **Kategorie** | Netzwerk |

Legt fest, welcher Spieler diese synchronisierte Instanz steuert (0 = Host, 1, 2, ... = Clients). Auf der Maschine dieses Spielers läuft die Instanz lokal und reagiert flüssig, und ihr Zustand wird an den Host zurückgemeldet; überall sonst ist sie ein geglätteter Geist. Beim Host aufrufen, abgesichert mit global.is_host == 1

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `player` | Text | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Synchronisationsrate festlegen

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `set_sync_rate` |
| **Symbol** | ⏱️ |
| **Kategorie** | Netzwerk |

Stellt ein, wie oft der Host Momentaufnahmen sendet und wie weit dahinter die Clients sie zeichnen. Einmal beim Host aufrufen, und für die Verzögerung auch bei den Clients

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `hz` | Zahl | `20` | 10-30 works well on a local network (default 20); optional |
| `interp_ms` | Zahl | `100` | How far behind ghosts are drawn, in milliseconds (default 100); optional |

### Netzwerkspiel starten

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `start_networked_game` |
| **Symbol** | 🚦 |
| **Kategorie** | Netzwerk |

Nur beim Host: holt alle aus dem Warteraum und startet die Partie. Löst auf jeder Maschine das Ereignis „Netzwerkspiel gestartet“ aus

*Parameter:* keine

### Diese Instanz synchronisieren

| Eigenschaft | Wert |
|----------|-------|
| **Name** | `sync_instance` |
| **Symbol** | 🔗 |
| **Kategorie** | Netzwerk |

Markiert die Instanz, die diese Aktion ausführt, als synchronisiert: ihre Position, ihre Drehung, ihr Bild und ihre Sichtbarkeit werden auf alle Maschinen kopiert. Im Erstellen-Ereignis aufrufen. Standardmäßig gehört sie dem Host; mit „Besitzer der Instanz festlegen“ kann ein Client sie steuern

| Parameter | Typ | Standard | Hinweise |
|-----------|------|---------|-------|
| `vars` | Text | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); optional |

---

## Weitere Kategorien

- [Bewegung](Full-Action-Reference-Movement_de) (20)
- [Instanz](Full-Action-Reference-Instance_de) (12)
- [Punkte](Full-Action-Reference-Score_de) (11)
- [Raum](Full-Action-Reference-Room_de) (13)
- [Zeitsteuerung](Full-Action-Reference-Timing_de) (8)
- [Audio](Full-Action-Reference-Audio_de) (6)
- [Spiel](Full-Action-Reference-Game_de) (25)
- [Steuerung](Full-Action-Reference-Control_de) (19)
- [Gitter](Full-Action-Reference-Grid_de) (4)
- [Ansichten](Full-Action-Reference-Views_de) (2)
- [3D-Ansicht](Full-Action-Reference-3D-View-Actions_de) (16)
- [Partikel](Full-Action-Reference-Particles_de) (8)

[← Zurück zur Vollständigen Aktionsreferenz](Full-Action-Reference_de)
