# Guida ai Preset

*[Italiano](Preset-Guide_it) | [Torna alla Home](Home_it)*

PyGameMaker offre diversi preset che controllano quali eventi e azioni sono disponibili. Questo aiuta i principianti a concentrarsi sulle funzionalità essenziali permettendo agli utenti esperti di accedere al set completo di strumenti.

## Scegli il Tuo Livello

| Preset | Ideale Per | Funzionalità |
|--------|------------|--------------|
| [**Principiante**](Beginner-Preset_it) | Nuovi allo sviluppo giochi | 4 eventi, 17 azioni - Movimento, collisioni, punteggio, stanze |
| [**Intermedio**](Intermediate-Preset_it) | Qualche esperienza | +4 eventi, +12 azioni - Vite, salute, suono, allarmi, disegno |
| **Avanzato** | Utenti esperti | Tutti i 40+ eventi e azioni disponibili |

---

## Documentazione Preset

### Preset
| Pagina | Descrizione |
|--------|-------------|
| [Preset Principiante](Beginner-Preset_it) | 4 eventi, 17 azioni - Funzionalità essenziali |
| [Preset Intermedio](Intermediate-Preset_it) | +4 eventi, +12 azioni - Vite, salute, suono |

### Riferimento
| Pagina | Descrizione |
|--------|-------------|
| [Riferimento Eventi](Event-Reference_it) | Lista completa di tutti gli eventi |
| [Riferimento Azioni](Full-Action-Reference_it) | Lista completa di tutte le azioni |

---

## Esempio di Avvio Rapido

Ecco un semplice gioco di raccolta monete usando solo funzionalità Principiante:

### 1. Creare Oggetti
- `obj_player` - Il personaggio controllabile
- `obj_coin` - Oggetti collezionabili
- `obj_wall` - Ostacoli solidi

### 2. Aggiungere Eventi al Giocatore

**Tastiera (Tasti Freccia):**
```
Freccia Sinistra  → Imposta Velocità Orizzontale: -4
Freccia Destra    → Imposta Velocità Orizzontale: 4
Freccia Su        → Imposta Velocità Verticale: -4
Freccia Giù       → Imposta Velocità Verticale: 4
```

**Collisione con obj_coin:**
```
Aggiungi Punteggio: 10
Distruggi Istanza: other
```

**Collisione con obj_wall:**
```
Ferma Movimento
```

### 3. Creare una Stanza
- Posiziona il giocatore
- Aggiungi alcune monete
- Aggiungi muri attorno ai bordi

### 4. Avvia il Gioco!
Premi il pulsante Play per testare il tuo gioco.

---

## Consigli per il Successo

1. **Inizia Semplice** - Usa prima il preset Principiante
2. **Testa Spesso** - Esegui il tuo gioco frequentemente per individuare problemi
3. **Una Cosa alla Volta** - Aggiungi funzionalità gradualmente
4. **Usa le Collisioni** - La maggior parte delle meccaniche di gioco coinvolge eventi di collisione
5. **Leggi la Documentazione** - Consulta le pagine di riferimento quando sei bloccato

---

## Vedi Anche

- [Home](Home_it) - Pagina principale wiki
- [Per Iniziare](Per_Iniziare_it) - Installazione e configurazione
- [Eventi e Azioni](Eventi_e_Azioni_it) - Concetti base
- [Crea il Tuo Primo Gioco](Primo_Gioco_it) - Tutorial
