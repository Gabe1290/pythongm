# Eventi di Disegno

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Draw
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw` |
| **Icona** | 🎨 |
| **Categoria** | Disegno |
| **Preset** | Principiante |

**Descrizione:** Si attiva durante la fase di rendering.

**Importante:** Aggiungere un evento Draw disabilita il disegno automatico dello sprite. Devi disegnare lo sprite manualmente se vuoi che sia visibile.

**Usi comuni:**
- Rendering personalizzato
- Disegnare forme
- Visualizzare testo
- Barre della salute
- Elementi HUD

**Azioni di disegno disponibili:**
- Disegna Sprite
- Disegna Testo
- Disegna Rettangolo
- Disegna Cerchio
- Disegna Linea
- Disegna Barra della Salute

---

### Draw GUI
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `draw_gui` |
| **Icona** | 🖥️ |
| **Categoria** | Disegno |
| **Preset** | Principiante |

**Descrizione:** Disegna nello **spazio schermo (GUI)**, sopra la stanza e non influenzato dallo scorrimento delle viste/camera.

**Differenza da Draw:** l'evento Draw normale è in coordinate della stanza (scorre con la vista); Draw GUI resta fisso allo schermo — usalo per HUD, punteggi e menu.

---

## Altre Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Input](Event-Reference-Input_it) - Tastiera, Mouse
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

[← Torna al Riferimento Eventi](Event-Reference_it)
