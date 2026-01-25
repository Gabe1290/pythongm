# Tutorial: Crea un Classico Gioco Pong

> **Seleziona la tua lingua / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Pong) | [Français](Tutorial-Pong_fr) | [Deutsch](Tutorial-Pong_de) | [Italiano](Tutorial-Pong_it) | [Español](Tutorial-Pong_es) | [Português](Tutorial-Pong_pt) | [Slovenščina](Tutorial-Pong_sl) | [Українська](Tutorial-Pong_uk) | [Русский](Tutorial-Pong_ru)

---

## Introduzione

In questo tutorial, creerai un classico gioco **Pong** - uno dei primi videogiochi mai creati! Pong è un gioco per due giocatori dove ogni giocatore controlla una racchetta e cerca di colpire la palla oltre la racchetta dell'avversario per segnare punti.

**Cosa imparerai:**
- Creare sprite per racchette, palla e muri
- Gestire l'input da tastiera per due giocatori
- Far rimbalzare gli oggetti l'uno contro l'altro
- Tracciare e visualizzare i punteggi di entrambi i giocatori
- Usare le variabili globali

**Difficoltà:** Principiante
**Preset:** Beginner Preset

---

## Passo 1: Pianifica il Tuo Gioco

Prima di iniziare, comprendiamo di cosa abbiamo bisogno:

| Elemento | Scopo |
|---------|---------|
| **Palla** | Rimbalza tra i giocatori |
| **Racchetta Sinistra** | Giocatore 1 controlla con i tasti W/S |
| **Racchetta Destra** | Giocatore 2 controlla con le frecce Su/Giù |
| **Muri** | Confini superiori e inferiori |
| **Goal** | Aree invisibili dietro ogni racchetta per rilevare i gol |
| **Visualizzazione del Punteggio** | Mostra i punteggi di entrambi i giocatori |

---

## Passo 2: Crea gli Sprite

### 2.1 Sprite della Palla

1. Nell'**Albero delle Risorse**, fai clic destro su **Sprites** e seleziona **Crea Sprite**
2. Denominalo `spr_ball`
3. Fai clic su **Modifica Sprite** per aprire l'editor sprite
4. Disegna un piccolo cerchio bianco (circa 16x16 pixel)
5. Fai clic su **OK** per salvare

### 2.2 Sprite delle Racchette

Creeremo due racchette - una per ogni giocatore:

**Racchetta Sinistra (Giocatore 1):**
1. Crea un nuovo sprite denominato `spr_paddle_left`
2. Disegna un rettangolo alto e sottile a forma di parentesi ")" - si consiglia il colore blu
3. Dimensioni: approssimativamente 16x64 pixel

**Racchetta Destra (Giocatore 2):**
1. Crea un nuovo sprite denominato `spr_paddle_right`
2. Disegna un rettangolo alto e sottile a forma di parentesi "(" - si consiglia il colore rosso
3. Dimensioni: approssimativamente 16x64 pixel

### 2.3 Sprite del Muro

1. Crea un nuovo sprite denominato `spr_wall`
2. Disegna un rettangolo solido (grigio o bianco)
3. Dimensioni: 32x32 pixel (lo allungheremo nella stanza)

### 2.4 Sprite del Goal (Invisibile)

1. Crea un nuovo sprite denominato `spr_goal`
2. Rendilo 32x32 pixel
3. Lascialo trasparente o rendilo di un colore solido (sarà invisibile nel gioco)

---

## Passo 3: Crea l'Oggetto Muro

L'oggetto muro crea confini nella parte superiore e inferiore dell'area di gioco.

1. Fai clic destro su **Oggetti** e seleziona **Crea Oggetto**
2. Denominalo `obj_wall`
3. Imposta lo sprite su `spr_wall`
4. **Spunta la casella "Solido"** - questo è importante per il rimbalzo!
5. Non sono necessari eventi - il muro rimane semplicemente lì

---

## Passo 4: Crea gli Oggetti Racchetta

### 4.1 Racchetta Sinistra (Giocatore 1)

1. Crea un nuovo oggetto denominato `obj_paddle_left`
2. Imposta lo sprite su `spr_paddle_left`
3. **Spunta la casella "Solido"**

**Aggiungi gli Eventi da Tastiera per il Movimento:**

**Evento: Pressione del Tasto W**
1. Aggiungi Evento → Tastiera → Pressione W
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `-8` (si muove verso l'alto)

**Evento: Rilascio del Tasto W**
1. Aggiungi Evento → Tastiera → Rilascio W
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `0` (smette di muoversi)

**Evento: Pressione del Tasto S**
1. Aggiungi Evento → Tastiera → Pressione S
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `8` (si muove verso il basso)

**Evento: Rilascio del Tasto S**
1. Aggiungi Evento → Tastiera → Rilascio S
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `0` (smette di muoversi)

**Evento: Collisione con obj_wall**
1. Aggiungi Evento → Collisione → obj_wall
2. Aggiungi Azione: **Movimento** → **Rimbalza Contro Oggetti**
3. Seleziona "Contro oggetti solidi"

### 4.2 Racchetta Destra (Giocatore 2)

1. Crea un nuovo oggetto denominato `obj_paddle_right`
2. Imposta lo sprite su `spr_paddle_right`
3. **Spunta la casella "Solido"**

**Aggiungi gli Eventi da Tastiera per il Movimento:**

**Evento: Pressione della Freccia Su**
1. Aggiungi Evento → Tastiera → Pressione Su
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `-8`

**Evento: Rilascio della Freccia Su**
1. Aggiungi Evento → Tastiera → Rilascio Su
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `0`

**Evento: Pressione della Freccia Giù**
1. Aggiungi Evento → Tastiera → Pressione Giù
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `8`

**Evento: Rilascio della Freccia Giù**
1. Aggiungi Evento → Tastiera → Rilascio Giù
2. Aggiungi Azione: **Movimento** → **Imposta Velocità Verticale**
3. Imposta la velocità verticale su `0`

**Evento: Collisione con obj_wall**
1. Aggiungi Evento → Collisione → obj_wall
2. Aggiungi Azione: **Movimento** → **Rimbalza Contro Oggetti**
3. Seleziona "Contro oggetti solidi"

---

## Passo 5: Crea l'Oggetto Palla

1. Crea un nuovo oggetto denominato `obj_ball`
2. Imposta lo sprite su `spr_ball`

**Evento: Creazione**
1. Aggiungi Evento → Creazione
2. Aggiungi Azione: **Movimento** → **Inizia a Muoverti in Direzione**
3. Scegli una direzione diagonale (non dritta verso l'alto o il basso)
4. Imposta la velocità su `6`

**Evento: Collisione con obj_paddle_left**
1. Aggiungi Evento → Collisione → obj_paddle_left
2. Aggiungi Azione: **Movimento** → **Rimbalza Contro Oggetti**
3. Seleziona "Contro oggetti solidi"

**Evento: Collisione con obj_paddle_right**
1. Aggiungi Evento → Collisione → obj_paddle_right
2. Aggiungi Azione: **Movimento** → **Rimbalza Contro Oggetti**
3. Seleziona "Contro oggetti solidi"

**Evento: Collisione con obj_wall**
1. Aggiungi Evento → Collisione → obj_wall
2. Aggiungi Azione: **Movimento** → **Rimbalza Contro Oggetti**
3. Seleziona "Contro oggetti solidi"

---

## Passo 6: Crea gli Oggetti Goal

I goal sono aree invisibili dietro ogni racchetta. Quando la palla entra in un goal, il giocatore avversario segna.

### 6.1 Goal Sinistro

1. Crea un nuovo oggetto denominato `obj_goal_left`
2. Imposta lo sprite su `spr_goal`
3. **Deseleziona "Visibile"** - il goal dovrebbe essere invisibile
4. **Spunta "Solido"**

### 6.2 Goal Destro

1. Crea un nuovo oggetto denominato `obj_goal_right`
2. Imposta lo sprite su `spr_goal`
3. **Deseleziona "Visibile"**
4. **Spunta "Solido"**

### 6.3 Aggiungi gli Eventi di Collisione Goal alla Palla

Torna a `obj_ball` e aggiungi questi eventi:

**Evento: Collisione con obj_goal_left**
1. Aggiungi Evento → Collisione → obj_goal_left
2. Aggiungi Azione: **Movimento** → **Salta alla Posizione di Inizio** (ripristina la palla)
3. Aggiungi Azione: **Punteggio** → **Imposta Punteggio**
   - Variabile: `global.p2score`
   - Valore: `1`
   - Spunta "Relativo" (aggiunge 1 al punteggio attuale)

**Evento: Collisione con obj_goal_right**
1. Aggiungi Evento → Collisione → obj_goal_right
2. Aggiungi Azione: **Movimento** → **Salta alla Posizione di Inizio**
3. Aggiungi Azione: **Punteggio** → **Imposta Punteggio**
   - Variabile: `global.p1score`
   - Valore: `1`
   - Spunta "Relativo"

---

## Passo 7: Crea l'Oggetto Visualizzazione del Punteggio

1. Crea un nuovo oggetto denominato `obj_score`
2. Nessuno sprite necessario

**Evento: Creazione**
1. Aggiungi Evento → Creazione
2. Aggiungi Azione: **Punteggio** → **Imposta Punteggio**
   - Variabile: `global.p1score`
   - Valore: `0`
3. Aggiungi Azione: **Punteggio** → **Imposta Punteggio**
   - Variabile: `global.p2score`
   - Valore: `0`

**Evento: Disegna**
1. Aggiungi Evento → Disegna
2. Aggiungi Azione: **Disegna** → **Disegna Testo**
   - Testo: `Giocatore 1:`
   - X: `10`
   - Y: `10`
3. Aggiungi Azione: **Disegna** → **Disegna Variabile**
   - Variabile: `global.p1score`
   - X: `100`
   - Y: `10`
4. Aggiungi Azione: **Disegna** → **Disegna Testo**
   - Testo: `Giocatore 2:`
   - X: `10`
   - Y: `30`
5. Aggiungi Azione: **Disegna** → **Disegna Variabile**
   - Variabile: `global.p2score`
   - X: `100`
   - Y: `30`

---

## Passo 8: Progetta la Stanza

1. Fai clic destro su **Stanze** e seleziona **Crea Stanza**
2. Denominala `room_pong`
3. Imposta la dimensione della stanza (ad es., 640x480)

**Posiziona gli oggetti:**

1. **Muri**: Posiziona istanze di `obj_wall` lungo i bordi superiore e inferiore della stanza
2. **Racchetta Sinistra**: Posiziona `obj_paddle_left` vicino al bordo sinistro, centrata verticalmente
3. **Racchetta Destra**: Posiziona `obj_paddle_right` vicino al bordo destro, centrata verticalmente
4. **Palla**: Posiziona `obj_ball` al centro della stanza
5. **Goal**:
   - Posiziona istanze di `obj_goal_left` lungo il bordo sinistro (dietro dove si trova la racchetta)
   - Posiziona istanze di `obj_goal_right` lungo il bordo destro
6. **Visualizzazione del Punteggio**: Posiziona `obj_score` in qualsiasi punto (non ha uno sprite, disegna semplicemente il testo)

**Esempio di Layout della Stanza:**
```
[MURO MURO MURO MURO MURO MURO MURO MURO MURO MURO]
[GOAL]  [RACCHETTA_S]            [PALLA]            [RACCHETTA_D]  [GOAL]
[GOAL]  [RACCHETTA_S]                              [RACCHETTA_D]  [GOAL]
[GOAL]                                                      [GOAL]
[MURO MURO MURO MURO MURO MURO MURO MURO MURO MURO]
```

---

## Passo 9: Prova il Tuo Gioco!

1. Fai clic su **Esegui** o premi **F5** per testare il tuo gioco
2. Giocatore 1 usa **W** (su) e **S** (giù)
3. Giocatore 2 usa **Freccia Su** e **Freccia Giù**
4. Prova a colpire la palla oltre la racchetta del tuo avversario!

---

## Miglioramenti (Opzionali)

### Aumento della Velocità
Rendi la palla più veloce ogni volta che colpisce una racchetta aggiungendo agli eventi di collisione:
- Dopo l'azione di rimbalzo, aggiungi **Movimento** → **Imposta Velocità**
- Imposta la velocità su `speed + 0.5` con "Relativo" spuntato

### Effetti Sonori
Aggiungi suoni quando:
- La palla colpisce una racchetta
- La palla colpisce un muro
- Un giocatore segna

### Condizione di Vittoria
Aggiungi un controllo nell'evento Disegna:
- Se `global.p1score >= 10`, visualizza "Il Giocatore 1 Vince!"
- Se `global.p2score >= 10`, visualizza "Il Giocatore 2 Vince!"

---

## Risoluzione dei Problemi

| Problema | Soluzione |
|---------|----------|
| La palla passa attraverso la racchetta | Assicurati che le racchette abbiano "Solido" spuntato |
| La racchetta non si ferma ai muri | Aggiungi evento di collisione con obj_wall |
| Il punteggio non si aggiorna | Controlla che i nomi delle variabili corrispondano esattamente (global.p1score, global.p2score) |
| La palla non si muove | Controlla che l'evento Creazione abbia l'azione di movimento |

---

## Cosa Hai Imparato

Complimenti! Hai creato un gioco Pong completo per due giocatori! Hai imparato:

- Come gestire l'input da tastiera per due giocatori diversi
- Come usare gli eventi Rilascio del Tasto per fermare il movimento
- Come fare rimbalzare gli oggetti l'uno contro l'altro
- Come usare le variabili globali per tracciare i punteggi
- Come visualizzare testo e variabili sullo schermo

---

## Vedi Anche

- [Beginner Preset](Beginner-Preset) - Panoramica delle funzionalità per principianti
- [Tutorial: Breakout](Tutorial-Breakout_it) - Crea un gioco brick breaker
- [Event Reference](Event-Reference_it) - Documentazione completa degli eventi
- [Full Action Reference](Full-Action-Reference_it) - Tutte le azioni disponibili
