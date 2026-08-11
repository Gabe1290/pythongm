# Eventi di Collisione

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Collisione
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `collision` |
| **Icona** | 💥 |
| **Categoria** | Collisione |
| **Preset** | Principiante |

**Descrizione:** Si attiva quando questa istanza si sovrappone con un altro tipo di oggetto.

**Configurazione:** Seleziona quale tipo di oggetto attiva questa collisione.

**Variabile speciale:** `other` - Riferimento all'istanza in collisione.

**Quando si attiva:** Ogni frame in cui le istanze si sovrappongono.

**Usi comuni:**
- Raccogliere oggetti
- Subire danni
- Colpire muri
- Attivare eventi

**Esempi di eventi di collisione:**
- `collision_with_obj_coin` - Il giocatore tocca una moneta
- `collision_with_obj_enemy` - Il giocatore tocca un nemico
- `collision_with_obj_wall` - L'istanza colpisce un muro

---

## Altre Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

[← Torna al Riferimento Eventi](Event-Reference_it)
