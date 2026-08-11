# Vista 3D

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Disegna HUD DOOM

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_doom_hud` |
| **Icona** | 🎯 |
| **Categoria** | Vista 3D |

Disegna una barra di stato inferiore in stile DOOM (barra della salute + numero, punteggio, vite, un contatore di obiettivo e un'icona del volto reattiva alla salute) sopra la vista raycast

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della barra, in pixel schermo |
| `y` | Numero | `-1` | Bordo superiore della barra; un valore negativo la allinea automaticamente in fondo alla finestra, sotto la vista ridotta; facoltativo |
| `width` | Numero | `0` | Larghezza della barra (0 = larghezza piena della finestra); facoltativo |
| `height` | Numero | `42` | Altezza della barra; mantienila coerente con la fascia viewport_height riservata in enable_raycast_view; facoltativo |
| `back_color` | Colore | `#101010` | Pannello di sfondo della barra; facoltativo |
| `divider_color` | Colore | `#505050` | Bordo superiore e sfondo della barra della salute; facoltativo |
| `text_color` | Colore | `#ffffff` | Colore di tutto il testo della barra; facoltativo |
| `health_label` | Testo | `Health` | facoltativo |
| `health_bar_width` | Numero | `90` | facoltativo |
| `health_bar_height` | Numero | `14` | facoltativo |
| `bar_color` | Colore | `#20c020` | Colore di riempimento della barra della salute; facoltativo |
| `face_sprite` | Sprite | — | Striscia orizzontale di fotogrammi del volto, il più sano per primo (vuoto = nessuna icona del volto); facoltativo |
| `face_frames` | Numero | `4` | Quanti fotogrammi ha la striscia del volto; la salute è distribuita uniformemente tra essi; facoltativo |
| `score_label` | Testo | `Score: ` | facoltativo |
| `lives_sprite` | Sprite | — | Sprite disegnato una volta per ogni vita rimanente; facoltativo |
| `lives_scale` | Numero | `1.0` | facoltativo |
| `objective_value` | Testo | `0` | Espressione mostrata dopo l'etichetta dell'obiettivo (associa la tua variabile chiave/missione); facoltativo |
| `objective_label` | Testo | `Keys: ` | facoltativo |

### Disegna minimappa

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_minimap` |
| **Icona** | 🗺️ |
| **Categoria** | Vista 3D |

Disegna una minimappa orientata a nord dei muri della stanza raycast, con un indicatore che mostra dove si trova la camera e in quale direzione guarda

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `x` | Numero | `0` | Bordo sinistro della minimappa, in pixel schermo |
| `y` | Numero | `0` | Bordo superiore della minimappa, in pixel schermo |
| `size` | Numero | `120` | Larghezza e altezza del quadrato della minimappa, in pixel; facoltativo |
| `back_color` | Colore | `#101018` | Colore del pannello dietro la mappa; facoltativo |
| `wall_color` | Colore | `#8080a0` | Colore delle linee dei muri; facoltativo |
| `player_color` | Colore | `#ffd040` | Colore dell'indicatore della camera e della sua linea di direzione; facoltativo |

### Abilita vista Raycast

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_raycast_view` |
| **Icona** | 🕹️ |
| **Categoria** | Vista 3D |

Renderizza la stanza come vista 3D in prima persona in stile Doom/Wolfenstein (muri, cielo, pavimento) invece della vista dall'alto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = vista raycast in prima persona; disattivo = normale vista dall'alto |
| `camera_object` | Oggetto | — | Oggetto la cui posizione + angolo di sguardo è la camera (vuoto = l'oggetto che esegue questa azione); facoltativo |
| `fov` | Numero | `66` | Campo visivo orizzontale in gradi; facoltativo |
| `render_distance` | Numero | `20` | Lunghezza massima del raggio in celle della griglia; facoltativo |
| `cell_size` | Numero | `32` | Dimensione della cella della griglia in pixel (corrisponde alla griglia di posizionamento dei muri); facoltativo |
| `columns` | Numero | `320` | Colonne dello schermo per il raycast (meno = più veloce/più grezzo); facoltativo |
| `wall_color` | Colore | `#993333` | Colore uniforme dei muri quando non è impostata una texture di muro; facoltativo |
| `floor_color` | Colore | `#464632` | Colore uniforme del pavimento quando non è impostata una texture di pavimento; facoltativo |
| `ceiling_color` | Colore | `#87CEEB` | Colore uniforme del soffitto quando non è impostata una texture di cielo/soffitto; facoltativo |
| `wall_texture` | Sprite | — | Sprite per texturizzare ogni muro (vuoto = colore uniforme); facoltativo |
| `sky_texture` | Sprite | — | Sprite per un cielo panoramico sopra il soffitto (vuoto = uniforme); facoltativo |
| `floor_texture` | Sprite | — | Sprite proiettato sul pavimento (vuoto = colore uniforme); facoltativo |
| `ceiling_texture` | Sprite | — | Sprite proiettato sul soffitto quando non è impostato un cielo; facoltativo |
| `wall_textured` | Sì/No | Sì | Disattivo forza colori uniformi dei muri anche quando è impostata una texture; facoltativo |
| `floor_cast_res` | Numero | `4` | Sottocampionamento del pavimento proiettato (più alto = più veloce + più grezzo); facoltativo |
| `viewport_height` | Numero | `0` | Riduci la vista 3D a questa altezza in pixel (letterbox), riservando la fascia sottostante per una barra di stato in stile DOOM (0 = altezza piena della finestra, invariato); facoltativo |

### Imposta angolo di sguardo

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_facing_angle` |
| **Icona** | 🧭 |
| **Categoria** | Vista 3D |

Imposta la direzione dello sguardo dell'istanza per una camera raycast (in prima persona) — indipendente dalla velocità di movimento

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `angle` | Numero | `0` | Gradi (0=destra, 90=su, 180=sinistra, 270=giù) |
| `relative` | Sì/No | No | Aggiungi all'angolo di sguardo attuale invece di sostituirlo; facoltativo |

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
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
