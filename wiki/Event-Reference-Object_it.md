# Eventi Oggetto

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Create
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `create` |
| **Icona** | 🎯 |
| **Categoria** | Oggetto |
| **Preset** | Principiante |

**Descrizione:** Eseguito una volta quando un'istanza viene creata per la prima volta.

**Quando si attiva:**
- Quando un'istanza viene posizionata in una stanza all'avvio del gioco
- Quando creata tramite l'azione "Crea Istanza"
- Dopo le transizioni di stanza per le nuove istanze

**Usi comuni:**
- Inizializzare variabili
- Impostare valori iniziali
- Configurare lo stato iniziale

---

### Step
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `step` |
| **Icona** | ⭐ |
| **Categoria** | Oggetto |
| **Preset** | Principiante |

**Descrizione:** Eseguito ogni frame (tipicamente 60 volte al secondo).

**Quando si attiva:** Continuamente, ogni frame di gioco.

**Usi comuni:**
- Movimento continuo
- Verifica delle condizioni
- Aggiornamento delle posizioni
- Logica di gioco

**Nota:** Attenzione alle prestazioni - il codice qui viene eseguito costantemente.

---

### Destroy
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `destroy` |
| **Icona** | 💥 |
| **Categoria** | Oggetto |
| **Preset** | Intermedio |

**Descrizione:** Eseguito quando un'istanza viene distrutta.

**Quando si attiva:** Appena prima che l'istanza venga rimossa dal gioco.

**Usi comuni:**
- Generare effetti (esplosioni, particelle)
- Rilasciare oggetti
- Aggiornare i punteggi
- Riprodurre suoni

---

## Altre Categorie di Eventi

- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

[← Torna al Riferimento Eventi](Event-Reference_it)
