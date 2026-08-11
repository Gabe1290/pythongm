# Griglia

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Se sulla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `if_on_grid` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Verifica se l'oggetto è allineato alla griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |
| `then_actions` | Elenco azioni | — | Azioni se sulla griglia |
| `else_actions` | Elenco azioni | — | Azioni se non sulla griglia |

### Allinea alla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `snap_to_grid` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Allinea la posizione dell'istanza alla griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Ferma se nessun tasto premuto

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_if_no_keys` |
| **Icona** | ▦ |
| **Categoria** | Griglia |

Ferma il movimento sulla griglia quando non è premuto alcun tasto di movimento (perfetto per un allineamento fluido alla griglia)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `grid_size` | Numero | `32` | Dimensione della cella della griglia in pixel |

### Verifica allineamento alla griglia

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_alignment` |
| **Icona** | ❓▦ |
| **Categoria** | Griglia |

Condizione: vero se l'istanza è allineata a una griglia

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `hsnap` | Numero | `32` | Spaziatura orizzontale della griglia in pixel |
| `vsnap` | Numero | `32` | Spaziatura verticale della griglia in pixel |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (2)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
