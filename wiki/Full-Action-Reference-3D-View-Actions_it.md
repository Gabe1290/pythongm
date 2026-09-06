# Vista 3D

*[Home](Home_it) | [Guida ai preset](Preset-Guide_it) | [Riferimento eventi](Event-Reference_it)*

> **Generato automaticamente** dal registro delle azioni dell'IDE tramite `tools/gen_action_reference.py` — non modificare a mano; riesegui il generatore dopo aver cambiato le azioni. Le traduzioni provengono da `tools/action_ref_i18n.py`.

### Applica gravità

| Proprietà | Valore |
|----------|-------|
| **Nome** | `apply_gravity` |
| **Icona** | ⬇️ |
| **Categoria** | Vista 3D |

Fisica continua di caduta e atterraggio per la telecamera Block World: va messa nell'evento Passo (non in un evento di tasto tenuto premuto), così viene eseguita a ogni fotogramma, che ci sia o no un comando di movimento. Non fa nulla finché il parametro Gravità di «Attiva vista Block World» non è maggiore di 0

*Parametri:* nessuno

### Rompi blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `break_block` |
| **Icona** | ⛏️ |
| **Categoria** | Vista 3D |

Rimuove il blocco inquadrato dalla telecamera; lo raccoglie anche nell'inventario dell'istanza che esegue l'azione se l'inventario di «Attiva vista Block World» è attivo, e si rifiuta di rimuoverlo se il blocco è protetto («Imposta protezione blocchi») e la chiave richiesta non è nell'inventario

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `reach` | Numero | `5` | Quanto lontano arrivi in avanti, in celle della griglia; facoltativo |

### Disegna HUD Block World

| Proprietà | Valore |
|----------|-------|
| **Nome** | `draw_block_world_hud` |
| **Icona** | 🧰 |
| **Categoria** | Vista 3D |

Disegna un mirino e una barra rapida (con la casella selezionata evidenziata e un contatore su ogni casella quando l'inventario è attivo): va chiamata dall'evento Disegno dell'oggetto giocatore o telecamera stesso

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `slot_size` | Numero | `40` | Larghezza e altezza di ogni casella della barra, in pixel; facoltativo |
| `gap` | Numero | `6` | Spazio fra le caselle della barra, in pixel; facoltativo |
| `margin_bottom` | Numero | `16` | Spazio fra la barra e il bordo inferiore dello schermo; facoltativo |
| `back_color` | Colore | `#202020` | Colore di riempimento di una casella non selezionata; facoltativo |
| `selected_color` | Colore | `#ffd040` | Colore di riempimento della casella selezionata; facoltativo |
| `border_color` | Colore | `#ffffff` | Colore del contorno di tutte le caselle; facoltativo |
| `text_color` | Colore | `#ffffff` | Colore dell'etichetta del tipo di blocco su ogni casella; facoltativo |
| `crosshair_size` | Numero | `12` | Larghezza e altezza del mirino centrale, in pixel; facoltativo |
| `crosshair_color` | Colore | `#ffffff` | Colore del mirino centrale; facoltativo |

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
| `mark_object` | Oggetto | — | Segnare sulla mappa anche ogni istanza di questo oggetto (vuoto = mostrare solo muri e giocatore); facoltativo |
| `mark_color` | Colore | `#40e0ff` | Colore dei punti di «Segna oggetto»; facoltativo |
| `mark_object_2` | Oggetto | — | Un secondo oggetto da segnare, con un colore proprio; facoltativo |
| `mark_color_2` | Colore | `#ff5050` | Colore dei punti di «Segna oggetto 2»; facoltativo |

### Attiva vista Block World

| Proprietà | Valore |
|----------|-------|
| **Nome** | `enable_block_world_view` |
| **Icona** | 🧱 |
| **Categoria** | Vista 3D |

Mostra la stanza come vista voxel in prima persona (un solo livello) invece della vista dall'alto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `enable` | Sì/No | Sì | Attivo = vista dei blocchi in prima persona; disattivo = normale vista dall'alto |
| `camera_object` | Oggetto | — | Oggetto la cui posizione + angolo di sguardo è la camera (vuoto = l'oggetto che esegue questa azione); facoltativo |
| `z_layer` | Numero | `0` | Quale livello del mondo viene disegnato (la fase 2a ne disegna esattamente uno: non si guarda ancora su e giù); facoltativo |
| `fov` | Numero | `66` | Campo visivo orizzontale in gradi; facoltativo |
| `render_distance` | Numero | `20` | Lunghezza massima del raggio in celle della griglia; facoltativo |
| `cell_size` | Numero | `32` | Dimensione della cella della griglia, in pixel (da far coincidere con la griglia di posa dei blocchi); facoltativo |
| `columns` | Numero | `320` | Colonne dello schermo per il raycast (meno = più veloce/più grezzo); facoltativo |
| `wall_color` | Colore | `#8a8a8a` | Colore pieno, usato solo se i blocchi con texture sono disattivati; facoltativo |
| `floor_color` | Colore | `#3a2f1c` | Colore pieno del pavimento (la fase 2a non applica ancora texture al pavimento); facoltativo |
| `ceiling_color` | Colore | `#87CEEB` | Colore pieno del soffitto o del cielo (la fase 2a non ha ancora un cielo); facoltativo |
| `pitch` | Numero | `0` | Gradi per guardare in alto (+) o in basso (−); 0 è l'orizzontale; facoltativo |
| `wall_textured` | Sì/No | Sì | Disattivo impone colori pieni per i blocchi, anche se sono disponibili texture vere; facoltativo |
| `top_cast_res` | Numero | `4` | Dettaglio della texture delle facce superiore e inferiore: righe campionate ogni N righe di schermo (più alto = più veloce e più grezzo, 0 = colore medio pieno invece della texture); facoltativo |
| `eye_height` | Numero | `1.5` | Altezza della telecamera sopra il livello su cui poggia, in celle (1,5 = un corpo alto due blocchi, necessario per vedere la faccia superiore di un blocco del proprio livello e salirci sopra); facoltativo |
| `gravity` | Numero | `0` | Accelerazione verso il basso, in celle/passo², per l'azione «Salta» e per gravità e cadute (livello 7a). 0 (predefinito) mantiene l'appoggio istantaneo originale di «Muovi con collisione», senza salti; un valore tipico è intorno a 0,04; facoltativo |
| `inventory` | Sì/No | No | Attivo = «Rompi blocco» raccoglie ciò che rompe e «Posiziona blocco» attinge da quell'inventario (livello 7c); disattivo (predefinito) = posa illimitata in stile creativo, come prima del livello 7c; facoltativo |
| `generate` | Sì/No | No | Attivo = genera proceduralmente un terreno ondulato attorno alla telecamera man mano che esplora (livello 7e), usando il seme qui sotto; disattivo (predefinito) = esistono solo i blocchi posati a mano o caricati, come prima del livello 7e; facoltativo |
| `seed` | Numero | `0` | Seme del mondo per «Genera terreno»: lo stesso seme produce sempre lo stesso terreno su questa piattaforma. Ignorato se «Genera terreno» è disattivato; facoltativo |

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

### Salta

| Proprietà | Valore |
|----------|-------|
| **Nome** | `jump` |
| **Icona** | ⬆️ |
| **Categoria** | Vista 3D |

Dà alla telecamera Block World una velocità verso l'alto, solo quando poggia su terreno solido (niente doppio salto né salto in aria). Richiede la Gravità configurata («Attiva vista Block World») e «Applica gravità» nell'evento Passo, altrimenti nulla la riporta giù

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `speed` | Numero | `0.35` | Velocità iniziale verso l'alto, in celle per passo; facoltativo |

### Carica Block World

| Proprietà | Valore |
|----------|-------|
| **Nome** | `load_block_world` |
| **Icona** | 📂 |
| **Categoria** | Vista 3D |

Carica un mondo già pronto (blocchi posati da un generatore o scritti a mano) nella stanza corrente, sostituendo i blocchi presenti

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `data_file` | Testo | — | Percorso di un file JSON di mondo a blocchi, relativo alla cartella del progetto (per es. blocks/room1.json) |

### Guarda su / giù

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_look_pitch` |
| **Icona** | 🔭 |
| **Categoria** | Vista 3D |

Inclina la vista Block World verso l'alto o verso il basso

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `pitch` | Numero | `0` | Gradi per guardare in alto (+) o in basso (−); 0 è l'orizzontale |
| `relative` | Sì/No | No | Attivo = aggiungere all'angolo attuale, per un comando di mira da tenere premuto; disattivo = impostarlo direttamente; facoltativo |

### Muovi con collisione

| Proprietà | Valore |
|----------|-------|
| **Nome** | `move_and_collide` |
| **Icona** | 🚶 |
| **Categoria** | Vista 3D |

Muove di un passo, controllando la griglia dei blocchi, con appoggio automatico (sale di un blocco, scende di qualsiasi altezza): il z_layer della telecamera lo segue se questa è la telecamera Block World

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `dx` | Numero | `0` | Di quanto muoversi su x in questo passo, in pixel |
| `dy` | Numero | `0` | Di quanto muoversi su y in questo passo, in pixel |
| `collide` | Sì/No | Sì | Disattivo ignora del tutto la griglia dei blocchi (volo / debug); facoltativo |

### Posiziona blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `place_block` |
| **Icona** | 🧱 |
| **Categoria** | Vista 3D |

Mette un blocco nella cella vuota inquadrata dalla telecamera: senza limiti, a meno che l'inventario di «Attiva vista Block World» sia attivo, nel qual caso attinge a ciò che «Rompi blocco» ha raccolto

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block` | Scelta | `stone` | Che tipo di blocco posizionare; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `reach` | Numero | `5` | Quanto lontano puoi costruire in avanti, in celle della griglia; facoltativo |

### Scegli casella della barra

| Proprietà | Valore |
|----------|-------|
| **Nome** | `select_hotbar_slot` |
| **Icona** | 🔢 |
| **Categoria** | Vista 3D |

Sceglie quale blocco è selezionato nella barra rapida, con cui «Posiziona blocco» costruirà: per usarlo, imposta il parametro Blocco di «Posiziona blocco» sull'espressione «hotbar_block»

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `index` | Numero | `0` | Indice della casella nella barra rapida, che riparte da capo a entrambe le estremità |
| `relative` | Sì/No | No | Attivo = aggiungere alla casella corrente, per scorrere con [ ] o con la rotella; disattivo = andarci direttamente; facoltativo |

### Imposta protezione blocchi

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_block_protection` |
| **Icona** | 🔒 |
| **Categoria** | Vista 3D |

Richiede un tipo di blocco preciso nell'inventario prima che «Rompi blocco» possa rimuovere un tipo di blocco scelto: va chiamata una volta per ogni tipo protetto; richiede l'inventario di «Attiva vista Block World», altrimenti la condizione non potrà mai essere soddisfatta

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block_type` | Scelta | `diamond_block` | Quale tipo di blocco diventa protetto; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `required_key` | Scelta | `gold_block` | Quale tipo di blocco deve essere nell'inventario per poterlo rompere; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |

### Imposta ricompensa blocco

| Proprietà | Valore |
|----------|-------|
| **Nome** | `set_block_reward` |
| **Icona** | 💎 |
| **Categoria** | Vista 3D |

Assegna punti quando «Rompi blocco» rimuove con successo un tipo di blocco scelto: va chiamata una volta per ogni tipo premiato (per es. nell'evento Creazione della stanza, subito dopo «Attiva vista Block World»). Un blocco di minerale o gemma da estrarre: mettilo nel terreno, registra la sua ricompensa, e romperlo assegnerà i punti automaticamente

| Parametro | Tipo | Predef. | Note |
|-----------|------|---------|-------|
| `block_type` | Scelta | `diamond_block` | Quale tipo di blocco assegna punti quando viene rotto; Scelte: `brick`, `clay`, `coal_block`, `cobble`, `desert_sand`, `diamond_block`, `dirt`, `glass`, `gold_block`, `grass`, `gravel`, `ice`, `jungle_plank`, `leaves`, `mese_block`, `obsidian`, `pine_plank`, `sand`, `sandstone`, `snow`, `stone`, `water`, `wood_log`, `wood_plank`, `wool_black`, `wool_blue`, `wool_green`, `wool_red`, `wool_white`, `wool_yellow` |
| `points` | Numero | `10` | Punti assegnati per ogni blocco di questo tipo rotto |

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
- [Tempo](Full-Action-Reference-Timing_it) (8)
- [Audio](Full-Action-Reference-Audio_it) (6)
- [Gioco](Full-Action-Reference-Game_it) (25)
- [Controllo](Full-Action-Reference-Control_it) (19)
- [Griglia](Full-Action-Reference-Grid_it) (4)
- [Viste](Full-Action-Reference-Views_it) (2)
- [Rete](Full-Action-Reference-Network-Actions_it) (15)
- [Particelle](Full-Action-Reference-Particles_it) (8)

[← Torna al Riferimento Completo delle Azioni](Full-Action-Reference_it)
