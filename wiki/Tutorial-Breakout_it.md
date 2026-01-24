# Tutorial: Creare un Gioco Breakout

*[Home](Home_it) | [Beginner Preset](Beginner-Preset_it) | [English](Tutorial-Breakout) | [Italiano](Tutorial-Breakout_it)*

Questo tutorial ti guidera nella creazione di un classico gioco Breakout. E' un primo progetto perfetto per imparare PyGameMaker!

![Breakout Game Concept](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Breakout2600.svg/220px-Breakout2600.svg.png)

---

## Cosa Imparerai

- Creare e usare gli sprite
- Configurare oggetti di gioco con eventi e azioni
- Controlli da tastiera per il movimento del giocatore
- Rilevamento delle collisioni e rimbalzi
- Distruggere oggetti alla collisione
- Costruire una stanza di gioco

---

## Passo 1: Creare gli Sprite

Prima di tutto, dobbiamo creare gli elementi visivi per il nostro gioco.

### 1.1 Creare lo Sprite del Paddle
1. Nel pannello **Assets**, clic destro su **Sprites** -> **Create Sprite**
2. Chiamalo `spr_paddle`
3. Disegna un rettangolo orizzontale (circa 64x16 pixel)
4. **Importante:** Clicca su **Center** per impostare l'origine al centro

### 1.2 Creare lo Sprite della Palla
1. Crea un altro sprite chiamato `spr_ball`
2. Disegna un piccolo cerchio (circa 16x16 pixel)
3. Clicca su **Center** per impostare l'origine

### 1.3 Creare lo Sprite del Mattone
1. Crea uno sprite chiamato `spr_brick`
2. Disegna un rettangolo (circa 48x24 pixel)
3. Clicca su **Center** per impostare l'origine

### 1.4 Creare lo Sprite del Muro
1. Crea uno sprite chiamato `spr_wall`
2. Disegna un quadrato (circa 32x32 pixel) - questo sara' il confine
3. Clicca su **Center** per impostare l'origine

### 1.5 Creare uno Sfondo (Opzionale)
1. Clic destro su **Backgrounds** -> **Create Background**
2. Chiamalo `bg_game`
3. Disegna o carica un'immagine di sfondo

---

## Passo 2: Creare l'Oggetto Paddle

Ora programmiamo il paddle che il giocatore controlla.

### 2.1 Creare l'Oggetto
1. Clic destro su **Objects** -> **Create Object**
2. Chiamalo `obj_paddle`
3. Imposta lo **Sprite** su `spr_paddle`
4. Spunta la casella **Solid**

### 2.2 Aggiungere il Movimento con Freccia Destra
1. Clicca su **Add Event** -> **Keyboard** -> seleziona **Right Arrow**
2. Aggiungi l'azione **Set Horizontal Speed**
3. Imposta **value** su `5` (o qualsiasi velocita' tu preferisca)

### 2.3 Aggiungere il Movimento con Freccia Sinistra
1. Clicca su **Add Event** -> **Keyboard** -> seleziona **Left Arrow**
2. Aggiungi l'azione **Set Horizontal Speed**
3. Imposta **value** su `-5`

### 2.4 Fermarsi Quando i Tasti Vengono Rilasciati
Il paddle continua a muoversi anche dopo aver rilasciato il tasto! Risolviamo questo problema.

1. Clicca su **Add Event** -> **Keyboard Release** -> seleziona **Right Arrow**
2. Aggiungi l'azione **Set Horizontal Speed**
3. Imposta **value** su `0`

4. Clicca su **Add Event** -> **Keyboard Release** -> seleziona **Left Arrow**
5. Aggiungi l'azione **Set Horizontal Speed**
6. Imposta **value** su `0`

Ora il paddle si ferma quando rilasci i tasti freccia.

---

## Passo 3: Creare l'Oggetto Palla

### 3.1 Creare l'Oggetto
1. Crea un nuovo oggetto chiamato `obj_ball`
2. Imposta lo **Sprite** su `spr_ball`
3. Spunta la casella **Solid**

### 3.2 Impostare il Movimento Iniziale
1. Clicca su **Add Event** -> **Create**
2. Aggiungi l'azione **Move in Direction** (o **Set Horizontal/Vertical Speed**)
3. Imposta una direzione diagonale con velocita' `5`
   - Per esempio: **hspeed** = `4`, **vspeed** = `-4`

Questo fa partire la palla quando il gioco inizia.

### 3.3 Rimbalzare sul Paddle
1. Clicca su **Add Event** -> **Collision** -> seleziona `obj_paddle`
2. Aggiungi l'azione **Reverse Vertical** (per rimbalzare)

### 3.4 Rimbalzare sui Muri
1. Clicca su **Add Event** -> **Collision** -> seleziona `obj_wall`
2. Aggiungi l'azione **Reverse Horizontal** o **Reverse Vertical** secondo necessita'
   - Oppure usa entrambe per gestire i rimbalzi negli angoli

---

## Passo 4: Creare l'Oggetto Mattone

### 4.1 Creare l'Oggetto
1. Crea un nuovo oggetto chiamato `obj_brick`
2. Imposta lo **Sprite** su `spr_brick`
3. Spunta la casella **Solid**

### 4.2 Distruggere alla Collisione con la Palla
1. Clicca su **Add Event** -> **Collision** -> seleziona `obj_ball`
2. Aggiungi l'azione **Destroy Instance** con obiettivo **self**

Questo distrugge il mattone quando la palla lo colpisce!

### 4.3 Far Rimbalzare la Palla
Nello stesso evento di collisione, aggiungi anche:
1. Aggiungi l'azione **Reverse Vertical** (applicata a **other** - la palla)

Oppure torna a `obj_ball` e aggiungi:
1. **Add Event** -> **Collision** -> seleziona `obj_brick`
2. Aggiungi l'azione **Reverse Vertical**

---

## Passo 5: Creare l'Oggetto Muro

### 5.1 Creare l'Oggetto
1. Crea un nuovo oggetto chiamato `obj_wall`
2. Imposta lo **Sprite** su `spr_wall`
3. Spunta la casella **Solid**

Questo e' tutto - il muro deve solo essere solido perche' la palla rimbalzi.

---

## Passo 6: Creare la Stanza di Gioco

### 6.1 Creare la Stanza
1. Clic destro su **Rooms** -> **Create Room**
2. Chiamala `room_game`

### 6.2 Impostare lo Sfondo (Opzionale)
1. Nelle impostazioni della stanza, trova **Background**
2. Seleziona il tuo sfondo `bg_game`
3. Spunta **Stretch** se vuoi che riempia la stanza

### 6.3 Posizionare gli Oggetti

Ora posiziona i tuoi oggetti nella stanza:

1. **Posiziona il Paddle:** Metti `obj_paddle` al centro in basso della stanza

2. **Posiziona i Muri:** Metti istanze di `obj_wall` intorno ai bordi:
   - Lungo la parte superiore
   - Lungo il lato sinistro
   - Lungo il lato destro
   - Lascia la parte inferiore aperta (e' da qui che la palla puo' scappare!)

3. **Posiziona la Palla:** Metti `obj_ball` da qualche parte al centro

4. **Posiziona i Mattoni:** Disponi istanze di `obj_brick` in righe nella parte superiore della stanza

---

## Passo 7: Testa il Tuo Gioco!

1. Clicca sul pulsante **Play** (freccia verde)
2. Usa i tasti freccia **Sinistra** e **Destra** per muovere il paddle
3. Cerca di far rimbalzare la palla per distruggere tutti i mattoni!
4. Premi **Escape** per uscire

---

## Cosa Viene Dopo?

Il tuo gioco Breakout di base e' completo! Ecco alcuni miglioramenti da provare:

### Aggiungere un Sistema di Vite
- Aggiungi un evento **No More Lives** per mostrare "Game Over"
- Perdi una vita quando la palla esce dal basso

### Aggiungere il Punteggio
- Usa l'azione **Add Score** quando distruggi i mattoni
- Mostra il punteggio con **Draw Score**

### Aggiungere Livelli Multipli
- Crea piu' stanze con diverse disposizioni di mattoni
- Usa **Next Room** quando tutti i mattoni sono distrutti

### Aggiungere Effetti Sonori
- Aggiungi suoni per rimbalzi e distruzione dei mattoni
- Usa l'azione **Play Sound**

---

## Riepilogo degli Oggetti

| Oggetto | Sprite | Solid | Eventi |
|---------|--------|-------|--------|
| `obj_paddle` | `spr_paddle` | Si | Keyboard (Left/Right), Keyboard Release |
| `obj_ball` | `spr_ball` | Si | Create, Collision (paddle, wall, brick) |
| `obj_brick` | `spr_brick` | Si | Collision (ball) - Destroy self |
| `obj_wall` | `spr_wall` | Si | Nessuno necessario |

---

## Vedi Anche

- [Beginner Preset](Beginner-Preset_it) - Eventi e azioni usati in questo tutorial
- [Event Reference](Event-Reference_it) - Tutti gli eventi disponibili
- [Full Action Reference](Full-Action-Reference_it) - Tutte le azioni disponibili
