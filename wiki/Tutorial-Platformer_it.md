# Tutorial: Creare un Gioco Platform

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Tutorial-Platformer) | [Français](Tutorial-Platformer_fr) | [Deutsch](Tutorial-Platformer_de) | [Italiano](Tutorial-Platformer_it) | [Español](Tutorial-Platformer_es) | [Português](Tutorial-Platformer_pt) | [Slovenščina](Tutorial-Platformer_sl) | [Українська](Tutorial-Platformer_uk) | [Русский](Tutorial-Platformer_ru)

---

## Introduzione

In questo tutorial, creerai un **Gioco Platform** - un gioco d'azione a scorrimento laterale dove il giocatore corre, salta e naviga sulle piattaforme evitando pericoli e raccogliendo monete. Questo genere classico è perfetto per imparare la gravità, le meccaniche di salto e la collisione con le piattaforme.

**Cosa imparerai:**
- Gravità e fisica della caduta
- Meccaniche di salto con rilevamento del terreno
- Collisione con le piattaforme (atterrare sopra)
- Movimento sinistra/destra
- Collezionabili e pericoli

**Difficoltà:** Principiante
**Preset:** Preset Principiante

---

## Passo 1: Capire il Gioco

### Meccaniche di Gioco
1. Il giocatore è influenzato dalla gravità e cade
2. Il giocatore può muoversi a sinistra e destra
3. Il giocatore può saltare quando è a terra
4. Le piattaforme impediscono al giocatore di cadere attraverso
5. Raccogli monete per punti
6. Raggiungi la bandiera per completare il livello

### Quello che ci serve

| Elemento | Scopo |
|----------|-------|
| **Giocatore** | Il personaggio che controlli |
| **Terreno/Piattaforma** | Superfici solide su cui stare |
| **Moneta** | Oggetti collezionabili per il punteggio |
| **Spuntone** | Pericolo che ferisce il giocatore |
| **Bandiera** | Obiettivo che termina il livello |

---

## Passo 2: Creare gli Sprite

### 2.1 Sprite del Giocatore
- Nome: `spr_player`
- Disegna un personaggio semplice
- Dimensione: 32x48 pixel

### 2.2 Sprite del Terreno
- Nome: `spr_ground`
- Disegna una mattonella erba/terra
- Dimensione: 32x32 pixel

### 2.3 Sprite della Piattaforma
- Nome: `spr_platform`
- Disegna una piattaforma fluttuante
- Dimensione: 64x16 pixel

### 2.4 Sprite della Moneta
- Nome: `spr_coin`
- Piccolo cerchio giallo/dorato
- Dimensione: 16x16 pixel

### 2.5 Sprite dello Spuntone
- Nome: `spr_spike`
- Triangoli che puntano verso l'alto
- Dimensione: 32x32 pixel

### 2.6 Sprite della Bandiera
- Nome: `spr_flag`
- Bandiera su un palo
- Dimensione: 32x64 pixel

---

## Passo 3: Creare l'Oggetto Terreno

Il terreno è una piattaforma solida che impedisce al giocatore di cadere.

1. Fai clic destro su **Objects** e seleziona **Create Object**
2. Nominalo `obj_ground`
3. Imposta lo sprite su `spr_ground`
4. **Seleziona la casella "Solid"**
5. Non servono eventi

---

## Passo 4: Creare l'Oggetto Piattaforma

Le piattaforme funzionano come il terreno ma possono essere posizionate in aria.

1. Crea un nuovo oggetto chiamato `obj_platform`
2. Imposta lo sprite su `spr_platform`
3. **Seleziona la casella "Solid"**

---

## Passo 5: Creare l'Oggetto Giocatore

Il giocatore è l'oggetto più complesso, con gravità, salto e movimento.

1. Crea un nuovo oggetto chiamato `obj_player`
2. Imposta lo sprite su `spr_player`

### 5.1 Gravità

**Event: Create** — Add Action: **Move** → **Set Gravity**
(Direction: `270`, Gravity: `0.5`) — 270° significa dritto verso il
basso; il valore viene aggiunto alla velocità verticale del giocatore ad
ogni frame, quindi il giocatore accelera verso il basso da solo a
partire da qui.

### 5.2 Movimento, Salto e Collisione col Terreno

Aggiungi questi eventi, seguendo lo stesso schema già usato dai tutorial
precedenti di questo wiki:

| Evento | Azione |
|---|---|
| Keyboard (held) → Left Arrow | Set Horizontal Speed a `-4` |
| Keyboard (held) → Right Arrow | Set Horizontal Speed a `4` |
| Keyboard: No Key | Set Horizontal Speed a `0` |
| Key Press → Up Arrow | Set Vertical Speed a `-10` |
| Collision with obj_ground | Stop Movement |

Due dettagli che rendono tutto naturale:

- **No Key imposta SOLO la velocità orizzontale a 0** — non usare mai
  Stop Movement qui, perché Stop Movement azzera anche la velocità
  verticale, il che annullerebbe la gravità ogni volta che il giocatore
  rilascia un tasto direzionale.
- **Key Press (non held)** è ciò che rende Up un singolo impulso di
  salto, invece di spingere il giocatore verso l'alto ad ogni frame in
  cui è tenuto premuto. **Stop Movement** all'atterraggio annulla poi
  quell'impulso, così il giocatore non continua a salire dopo essere
  atterrato — la collisione solida integrata del motore (il Passo 3 ha
  già reso `obj_ground` Solid) impedisce già che il giocatore sprofondi
  nel terreno; l'evento qui si limita ad azzerare la velocità di caduta
  residua.

---

## Passo 6-8: Collezionabili e Pericoli

**obj_coin** - Collisione con obj_player: Punteggio +10, distruggi Self

**obj_spike** - Collisione con obj_player: Mostra messaggio, riavvia la stanza

**obj_flag** - Collisione con obj_player: Mostra messaggio, stanza successiva

---

## Passo 9: Progetta il Tuo Livello

1. Crea `room_level1` (800x480)
2. Abilita lo snap alla griglia (32x32)
3. Posiziona il terreno in basso, le piattaforme in aria
4. Aggiungi monete, spuntoni
5. Metti la bandiera alla fine, il giocatore all'inizio

---

## Cosa Hai Imparato

- **Fisica della gravità** - Set Gravity applica una forza costante verso il basso ad ogni frame
- **Meccaniche di salto** - Un evento Key Press (non held) dà un singolo impulso di velocità verso l'alto
- **Collisione solida integrata** - Il terreno blocca il giocatore automaticamente una volta marcato Solid, senza codice manuale di controllo posizione

---

## Vedi Anche

- [Tutorials](Tutorials_it) - Altri tutorial di giochi
- [Tutorial: Labirinto](Tutorial-Maze_it) - Creare un gioco del labirinto
