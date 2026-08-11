# Altri Eventi

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Outside Room
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `outside_room` |
| **Icona** | 🚫 |
| **Categoria** | Altro |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando l'istanza e completamente fuori dai confini della stanza.

**Usi comuni:**
- Distruggere proiettili fuori schermo
- Avvolgere dall'altro lato
- Attivare game over

---

### Intersect Boundary
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `intersect_boundary` |
| **Icona** | ⚠️ |
| **Categoria** | Altro |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando l'istanza tocca il confine della stanza.

**Usi comuni:**
- Mantenere il giocatore nei confini
- Rimbalzare sui bordi

---

### No More Lives
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `no_more_lives` |
| **Icona** | 💀 |
| **Categoria** | Altro |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando le vite diventano 0 o meno.

**Usi comuni:**
- Schermata di game over
- Riavviare il gioco
- Mostrare il punteggio finale

---

### No More Health
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `no_more_health` |
| **Icona** | 💔 |
| **Categoria** | Altro |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando la salute diventa 0 o meno.

**Usi comuni:**
- Perdere una vita
- Far riapparire il giocatore
- Attivare l'animazione di morte

---

### Animation End
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `animation_end` |
| **Icona** | 🎞️ |
| **Categoria** | Altro |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando l'animazione dello sprite dell'istanza completa un ciclo intero (torna dall'ultimo fotogramma al primo).

**Usi comuni:**
- Distruggere un effetto una tantum (esplosione) dopo una singola riproduzione
- Passare a un'altra animazione quando quella corrente finisce
- Far avanzare una macchina a stati al termine dell'animazione

---

## Altre Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco

[← Torna al Riferimento Eventi](Event-Reference_it)
