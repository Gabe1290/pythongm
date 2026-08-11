# Eventi di Input

*[Home](Home_it) | [Riferimento Eventi](Event-Reference_it) | [Riferimento completo delle azioni](Full-Action-Reference_it)*

### Tastiera (Continuo)
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `keyboard` |
| **Icona** | ⌨️ |
| **Categoria** | Input |
| **Preset** | Principiante |

**Descrizione:** Si attiva continuamente mentre un tasto è tenuto premuto.

**Ideale per:** Movimento fluido e continuo

**Tasti Supportati:**
- Tasti freccia (su, giu, sinistra, destra)
- Lettere (A-Z)
- Numeri (0-9)
- Spazio, Invio, Escape
- Tasti funzione (F1-F12)
- Tasti modificatori (Shift, Ctrl, Alt)

---

### Pressione Tastiera
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `keyboard_press` |
| **Icona** | 🔘 |
| **Categoria** | Input |
| **Preset** | Intermedio |

**Descrizione:** Si attiva una volta quando un tasto viene premuto per la prima volta.

**Ideale per:** Azioni singole (saltare, sparare, selezionare nel menu)

**Differenza da Tastiera:** Si attiva solo una volta per pressione, non mentre è tenuto premuto.

---

### Rilascio Tastiera
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `keyboard_release` |
| **Icona** | ⬆️ |
| **Categoria** | Input |
| **Preset** | Completo (Edizione Sviluppo) |

**Descrizione:** Si attiva una volta quando un tasto viene rilasciato.

**Usi comuni:**
- Fermare il movimento quando il tasto viene rilasciato
- Terminare attacchi caricati
- Alternare stati

---

### Tastiera (Nessun tasto)
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `keyboard_no_key` |
| **Icona** | ⌨️ |
| **Categoria** | Input |
| **Preset** | Principiante |

**Descrizione:** Si attiva a ogni fotogramma mentre **nessun** tasto è premuto.

**Quando si attiva:** A ogni fotogramma in cui la tastiera è inattiva, *prima* dell'evento Step.

**Usi comuni:**
- Fermare il movimento quando il giocatore rilascia tutti i tasti (giochi a griglia/labirinti)
- Animazioni di riposo

---

### Mouse
| Proprietà | Valore |
|-----------|--------|
| **Nome** | `mouse` |
| **Icona** | 🖱️ |
| **Categoria** | Input |
| **Preset** | Completo (Edizione Sviluppo) |

**Descrizione:** Eventi di pulsanti del mouse e movimento.

**Tipi di Eventi:**

| Tipo | Descrizione |
|------|-------------|
| Pulsante Sinistro | Clic con il pulsante sinistro del mouse |
| Pulsante Destro | Clic con il pulsante destro del mouse |
| Pulsante Centrale | Clic con il pulsante centrale/rotella |
| Entrata Mouse | Il cursore entra nei confini dell'istanza |
| Uscita Mouse | Il cursore esce dai confini dell'istanza |
| Pulsante Sinistro Globale | Clic sinistro ovunque |
| Pulsante Destro Globale | Clic destro ovunque |

---

## Altre Categorie di Eventi

- [Eventi Oggetto](Event-Reference-Object_it) - Create, Step, Destroy
- [Eventi di Collisione](Event-Reference-Collision_it) - Collisioni tra oggetti
- [Eventi di Temporizzazione](Event-Reference-Timing_it) - Allarmi, Varianti di Step
- [Eventi di Disegno](Event-Reference-Drawing_it) - Rendering personalizzato
- [Eventi di Stanza](Event-Reference-Room_it) - Transizioni di stanza
- [Eventi di Gioco](Event-Reference-Game_it) - Inizio/Fine gioco
- [Altri Eventi](Event-Reference-Other_it) - Confini, Vite, Salute

[← Torna al Riferimento Eventi](Event-Reference_it)
