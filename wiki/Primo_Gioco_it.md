# Creare il tuo primo gioco

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Torna alla Home](Home_it)

In questo tutorial, creeremo un semplice gioco "Cattura le Stelle" in cui il giocatore si muove per raccogliere stelle che cadono.

---

## Cosa Imparerai

- Creare sprite
- Creare oggetti con eventi e azioni
- Usare l'editor delle stanze
- Eseguire e testare il tuo gioco

---

## Passo 1: Creare un Nuovo Progetto

1. Avvia PyGameMaker
2. Vai su **File > New Project**
3. Chiama il tuo progetto "CatchTheStars"
4. Clicca su **Create**

---

## Passo 2: Creare lo Sprite del Giocatore

1. Fai clic destro su **Sprites** nell'albero delle risorse
2. Seleziona **Create Sprite**
3. Chiamalo `spr_player`
4. Clicca su **Edit Sprite** per aprire l'editor sprite
5. Disegna un semplice personaggio (o usa un rettangolo colorato 32x32)
6. Clicca su **Save**

---

## Passo 3: Creare lo Sprite della Stella

1. Fai clic destro su **Sprites** > **Create Sprite**
2. Chiamalo `spr_star`
3. Disegna una forma a stella (o usa un cerchio giallo)
4. Clicca su **Save**

---

## Passo 4: Creare l'Oggetto Giocatore

1. Fai clic destro su **Objects** nell'albero delle risorse
2. Seleziona **Create Object**
3. Chiamalo `obj_player`
4. Imposta lo **Sprite** su `spr_player`

### Aggiungere gli Eventi Tastiera

**Freccia Sinistra:**
1. Clicca su **Add Event** > **Keyboard** > **Left**
2. Aggiungi l'azione: **Set Horizontal Speed** con valore `-4`

**Freccia Destra:**
1. Clicca su **Add Event** > **Keyboard** > **Right**
2. Aggiungi l'azione: **Set Horizontal Speed** con valore `4`

**Nessun Tasto Premuto:**
1. Clicca su **Add Event** > **Keyboard** > **No Key**
2. Aggiungi l'azione: **Set Horizontal Speed** con valore `0`

---

## Passo 5: Creare l'Oggetto Stella

1. Fai clic destro su **Objects** > **Create Object**
2. Chiamalo `obj_star`
3. Imposta lo **Sprite** su `spr_star`

### Aggiungere l'Evento Create
1. Clicca su **Add Event** > **Create**
2. Aggiungi l'azione: **Set Vertical Speed** con valore `3`
3. Aggiungi l'azione: **Jump To Position** con X `irandom(600)`, Y `20` —
   `irandom(n)` sceglie un numero intero casuale da 0 a `n`, quindi
   sparge la stella in un punto casuale vicino al bordo superiore di una
   stanza larga 640 pixel ogni volta che (ri)appare

### Aggiungere l'Evento Outside Room
1. Clicca su **Add Event** > **Other** > **Outside Room**
2. Aggiungi l'azione: **Jump to Start Position**
3. Aggiungi l'azione: **Set Score** con valore `1` e **Relative** selezionato

### Aggiungere la Collisione con il Giocatore
1. Clicca su **Add Event** > **Collision** > seleziona `obj_player`
2. Aggiungi l'azione: **Set Score** con valore `10` e **Relative** selezionato
3. Aggiungi l'azione: **Play Sound** (opzionale, se hai un suono)
4. Aggiungi l'azione: **Jump to Random Position**

---

## Passo 6: Creare la Stanza

1. Fai clic destro su **Rooms** nell'albero delle risorse
2. Seleziona **Create Room**
3. Chiamala `room_game`
4. Imposta la dimensione della stanza a **640 x 480**

### Posizionare gli Oggetti
1. Seleziona la scheda **Objects** nell'editor della stanza
2. Clicca su `obj_player` e posizionalo in basso al centro della stanza
3. Clicca su `obj_star` e posiziona 5-10 stelle sparse in alto

---

## Passo 7: Visualizzare il Punteggio

1. Apri `obj_player`
2. Clicca su **Add Event** > **Draw**
3. Aggiungi l'azione: **Draw Score** in posizione (10, 10)

---

## Passo 8: Avvia il Tuo Gioco!

1. Premi **F5** o vai su **Build > Test Game**
2. Usa i tasti freccia sinistra e destra per muoverti
3. Cattura le stelle che cadono per aumentare il tuo punteggio!

---

## Miglioramenti da Provare

### Aggiungere Vite
1. Crea un oggetto "game over" che appare quando le vite raggiungono 0
2. Aggiungi un evento di collisione con un oggetto "cattivo" che riduce le vite

### Aggiungere Livelli
1. Crea più stanze
2. Usa l'azione **Next Room** quando il punteggio raggiunge una soglia

### Aggiungere Suoni
1. Importa i file audio nella risorsa Sounds
2. Aggiungi azioni **Play Sound** agli eventi

### Usare la Programmazione Visuale
1. Apri un oggetto
2. Clicca sulla scheda **Blockly** per la programmazione drag-and-drop
3. Costruisci la stessa logica visivamente con i blocchi

---

## Struttura del Progetto Completo

Dopo aver completato questo tutorial, il tuo progetto dovrebbe avere:

- **Sprite:** spr_player, spr_star
- **Oggetti:** obj_player, obj_star
- **Stanze:** room_game

---

## Prossimi Passi

- [[Editor_Oggetti_it]] - Scopri di più sulle proprietà degli oggetti
- [[Eventi_e_Azioni_it]] - Esplora tutti gli eventi e le azioni disponibili
- [[Programmazione_Visuale_it]] - Prova a costruire con i blocchi Blockly
- [[Esportare_Giochi_it]] - Condividi il tuo gioco con altri
