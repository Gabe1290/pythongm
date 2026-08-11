# Eventi di Temporizzazione

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Allarme
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `alarm` |
| **Icona** | ⏰ |
| **Categoria** | Temporizzazione |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando un conto alla rovescia dell'allarme raggiunge lo zero.

**Allarmi disponibili:** 12 allarmi indipendenti (alarm[0] fino a alarm[11])

**Impostare gli allarmi:** Usa l'azione "Imposta Allarme" con step (60 step ≈ 1 secondo a 60 FPS)

**Usi comuni:**
- Generazione temporizzata
- Tempi di ricarica
- Effetti ritardati
- Azioni ripetitive (reimpostare l'allarme nell'evento allarme)

---

### Begin Step
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `begin_step` |
| **Icona** | ▶️ |
| **Categoria** | Step |
| **Preset** | Principiante |

**Descrizione:** Si attiva all'inizio di ogni frame, prima degli eventi Step regolari.

**Ordine di esecuzione:** Begin Step → Step → End Step

**Usi comuni:**
- Elaborazione dell'input
- Calcoli pre-movimento

---

### End Step
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `end_step` |
| **Icona** | ⏹️ |
| **Categoria** | Step |
| **Preset** | Principiante |

**Descrizione:** Si attiva alla fine di ogni frame, dopo le collisioni.

**Usi comuni:**
- Aggiustamenti finali della posizione
- Operazioni di pulizia
- Aggiornamenti di stato dopo le collisioni

---

## Altre Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

[← Torna al Riferimento Eventi](Event-Reference_it)
