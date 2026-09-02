# Viste

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Abilita viste

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_views` |
| **Icona** | 🎥 |
| **Categoria** | Viste |

Attiva o disattiva il sistema di camera/vista della stanza (consente a un livello di scorrere quando è più grande della finestra)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = viste camera; disattivo = disegna l'intera stanza in una volta |

### Imposta vista

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_view` |
| **Icona** | 🎥 |
| **Categoria** | Viste |

Configura una vista di camera: quale parte della stanza mostra, dove si disegna sullo schermo e un oggetto da seguire

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `view` | Scelta | `0` | Quale delle 8 viste configurare; Scelte: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` |
| `visible` | Sì/No | Sì | Disegna questa vista |
| `view_x` | Numero | `0` | Bordo sinistro della regione della stanza mostrata |
| `view_y` | Numero | `0` | Bordo superiore della regione della stanza mostrata |
| `view_w` | Numero | `800` | Larghezza della regione della stanza mostrata |
| `view_h` | Numero | `600` | Altezza della regione della stanza mostrata |
| `port_x` | Numero | `0` | Bordo sinistro sullo schermo |
| `port_y` | Numero | `0` | Bordo superiore sullo schermo |
| `port_w` | Numero | `800` | Larghezza disegnata sullo schermo |
| `port_h` | Numero | `600` | Altezza disegnata sullo schermo |
| `follow` | Oggetto | — | Oggetto seguito dalla camera (vuoto = vista fissa); facoltativo |
| `hborder` | Numero | `32` | Bordo orizzontale prima che la camera scorra |
| `vborder` | Numero | `32` | Bordo verticale prima che la camera scorra |
| `hspeed` | Numero | `-1` | Velocità di scorrimento orizzontale massima (-1 = istantanea) |
| `vspeed` | Numero | `-1` | Velocità di scorrimento verticale massima (-1 = istantanea) |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Istanza](Full-Action-Reference-Instance_it) (12)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (16)
- [Particles](Full-Action-Reference-Particles_it) (8)
- [Réseau](Full-Action-Reference-Network-Actions_it) (15)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
