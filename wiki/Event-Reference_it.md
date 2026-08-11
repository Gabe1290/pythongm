# Riferimento Eventi

*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

Questa pagina documenta tutti gli eventi disponibili in PyGameMaker. Gli eventi sono trigger che eseguono azioni quando si verificano condizioni specifiche nel tuo gioco.

## Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

---

## Ordine di Esecuzione degli Eventi

Capire quando gli eventi si attivano aiuta a creare un comportamento di
gioco prevedibile (verificato contro il ciclo principale in
`runtime/game_runner.py`):

1. **Begin Step** — Inizio del frame
2. **Alarm** — Tutti gli allarmi attivati contano alla rovescia e si attivano
3. **Step** (e **Keyboard (tenuto premuto)**) — Logica principale di gioco,
   poi i controlli continui dei tasti tenuti premuti per la stessa istanza
4. **Keyboard Press/Release, Mouse** — Gli eventi di input accumulati per
   questo frame vengono elaborati (questo avviene *dopo* Step, non prima —
   il codice in Step reagisce ai tasti già premuti all'*inizio* del frame,
   non a quelli premuti durante il frame stesso)
5. **Movimento, poi Collisione** — La fisica (gravità/attrito/hspeed/
   vspeed) viene applicata, poi le collisioni vengono rilevate e i loro
   eventi si attivano
6. **End Step** (e **Destroy**) — Dopo le collisioni
7. **Draw** — Fase di rendering

---

## Eventi per Preset

Verificato contro `events.event_types.get_available_events()` alimentato
con ciascun preset reale da `config/blockly_config.py` — vedi la
[Guida ai Preset](Preset-Guide_it) per quello che un "preset" restringe
davvero (sia il selettore Blockly sia il pannello strutturato Events/
Actions) e come si imposta il preset di un progetto.

| Preset | Eventi Inclusi |
|--------|----------------|
| **Principiante** (19 eventi) | Create, Step, Keyboard (tenuto premuto), Keyboard \<Nessun Tasto\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermedio** (21 eventi) | + Destroy, Keyboard Press |
| **Completo** (solo Edizione Sviluppo, 23 eventi) | + Keyboard Release, Mouse |

---

## Vedi Anche

- [Riferimento Completo delle Azioni](Full-Action-Reference_it) - Lista completa delle azioni
- [Preset Principiante](Beginner-Preset_it) - Eventi essenziali per principianti
- [Preset Intermedio](Intermediate-Preset_it) - Eventi aggiuntivi
- [Eventi e Azioni](Eventi_e_Azioni_it) - Panoramica dei concetti base
