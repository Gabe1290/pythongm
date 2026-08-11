# Istanza

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Cambia istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `change_instance` |
| **Icona** | 🔄 |
| **Categoria** | Istanza |
| **Si applica a** | self / other / object |

Trasforma in un altro tipo di oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Nuovo tipo di oggetto |
| `perform_events` | Sì/No | Sì | Esegui gli eventi distruzione/creazione |

### Crea istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_instance` |
| **Icona** | ✨ |
| **Categoria** | Istanza |

Crea una nuova istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da creare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `relative` | Sì/No | No | Posizione relativa all'istanza corrente |

### Crea istanza in movimento

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_moving_instance` |
| **Icona** | ✨➡️ |
| **Categoria** | Istanza |

Crea un'istanza e avviala in una direzione

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da creare |
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `speed` | Numero | `0` | Intensità della velocità iniziale |
| `direction` | Numero | `0` | Direzione iniziale in gradi |

### Crea istanza casuale

| Proprietà | Valore |
|----------|-------|
| **Nome** | `create_random_instance` |
| **Icona** | 🎲 |
| **Categoria** | Istanza |

Crea uno di diversi tipi di oggetto scelto a caso

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Posizione X |
| `y` | Numero | `0` | Posizione Y |
| `object1` | Oggetto | — | Primo oggetto candidato; facoltativo |
| `object2` | Oggetto | — | Secondo oggetto candidato; facoltativo |
| `object3` | Oggetto | — | Terzo oggetto candidato; facoltativo |
| `object4` | Oggetto | — | Quarto oggetto candidato; facoltativo |

### Distruggi istanza

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_instance` |
| **Icona** | 💥 |
| **Categoria** | Istanza |
| **Si applica a** | self / other / object |

Distruggi un'istanza

*Parametri:* nessuno

### Distruggi in posizione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `destroy_at_position` |
| **Icona** | 💣 |
| **Categoria** | Istanza |

Distruggi le istanze entro un raggio da (x, y)

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | `all` | Quale tipo di oggetto distruggere. «all» distrugge ogni istanza nel raggio; «solid» solo quelle solide (es. muri); «non-solid» tutto tranne i solidi.; Scelte: `all`, `solid`, `non-solid` |
| `x` | Testo | `self.x` | Posizione X (espressione consentita, es. self.x) |
| `y` | Testo | `self.y` | Posizione Y (espressione consentita, es. self.y) |
| `relative` | Sì/No | No | Tratta X/Y come scostamenti dalla posizione di questa istanza invece che come coordinate assolute; facoltativo |
| `radius` | Numero | `32` | Raggio in pixel attorno a (x, y). Predefinito 32 = ~una cella della griglia. |

### Imposta indice immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_image_index` |
| **Icona** | 🖼️ |
| **Categoria** | Istanza |

Imposta il fotogramma di animazione corrente dello sprite dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `frame` | Numero | `0` | Indice del fotogramma |

### Imposta velocità immagine

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_image_speed` |
| **Icona** | ⏩ |
| **Categoria** | Istanza |

Imposta la velocità di riproduzione dell'animazione dello sprite dell'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `1.0` | Fotogrammi avanzati per passo (0 = in pausa) |

### Imposta sprite

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_sprite` |
| **Icona** | 🖼️ |
| **Categoria** | Istanza |

Cambia lo sprite e/o il fotogramma/la velocità di animazione di un'istanza

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `sprite` | Sprite | `<self>` | Sprite da usare (o «<self>» per mantenere quello corrente) |
| `subimage` | Numero | `-1` | Indice del fotogramma da impostare; -1 lascia invariato |
| `speed` | Numero | `-1` | Velocità di animazione; -1 lascia invariato |

### Avvia animazione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `start_animation` |
| **Icona** | ▶️ |
| **Categoria** | Istanza |

Riprendi l'animazione dello sprite dell'istanza (image_speed = 1)

*Parametri:* nessuno

### Ferma animazione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `stop_animation` |
| **Icona** | ⏸️ |
| **Categoria** | Istanza |

Metti in pausa l'animazione dello sprite dell'istanza (image_speed = 0)

*Parametri:* nessuno

### Verifica numero di istanze

| Proprietà | Valore |
|----------|-------|
| **Nome** | `test_instance_count` |
| **Icona** | ❓🔢 |
| **Categoria** | Istanza |

Condizione: confronta il numero di istanze di un oggetto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `object` | Oggetto | — | Oggetto da contare |
| `number` | Numero | `0` | Valore di confronto |
| `operation` | Scelta | `equal` | Operatore di confronto; Scelte: `equal`, `less`, `greater`, `less_equal`, `greater_equal`, `not_equal` |

---

## Altre Categorie

- [Movimento](Full-Action-Reference-Movement_it) (20)
- [Punteggio](Full-Action-Reference-Score_it) (11)
- [Stanza](Full-Action-Reference-Room_it) (13)
- [Tempo](Full-Action-Reference-Timing_it) (2)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (20)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_it) (4)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
