# Guida ai Preset

*[Italiano](Preset-Guide_it) | [Torna alla Home](Home_it)*

PyGameMaker offre diversi preset che controllano quali eventi e azioni
sono disponibili — **sia** nella tavolozza di blocchi visivi Blockly sia
nel pannello strutturato Eventi/Azioni ("Add Event"/"Add Action") che
ogni tutorial di questo wiki utilizza. Questo aiuta i principianti a
concentrarsi sulle funzionalità essenziali, permettendo agli utenti
esperti di accedere al set completo di strumenti.

Il preset di un progetto si imposta in due modi: **`Preferenze > IDE
Edition`** sceglie il predefinito per i *nuovi* progetti (i progetti
esistenti non vengono mai modificati cambiando edizione), e
**`Strumenti > Configura blocchi azione...`** cambia il preset del
progetto *attualmente aperto* in qualsiasi momento. L'edizione
predefinita dell'IDE è Principiante, quindi i nuovi progetti di
un'installazione pulita partono già sul preset Principiante.

## Scegli il Tuo Livello

| IDE Edition | Ideale Per | Preset usato |
|--------|------------|--------------|
| **Principiante** (predefinita) | Nuovi utenti | [Preset Principiante](Beginner-Preset_it) — movimento base, collisioni, punteggio, stanze |
| **Avanzato** | Un po' di esperienza | [Preset Intermedio](Intermediate-Preset_it) — + vite, salute, suono, allarmi, movimento a griglia |
| **Sviluppo** | Utenti esperti | Il preset `full` — ogni evento e azione disponibile |

Nota che i nomi non corrispondono 1:1: l'edizione "Avanzato" usa il
preset `intermediate` (non esiste un preset separato "avanzato") — vedi
[Preset Principiante](Beginner-Preset_it)/[Preset Intermedio](Intermediate-Preset_it)
per i numeri esatti e sempre aggiornati di eventi e azioni di ciascuno.

---

## Documentazione Preset

### Preset
| Pagina | Descrizione |
|--------|-------------|
| [Preset Principiante](Beginner-Preset_it) | Funzionalità essenziali — numeri esatti in quella pagina |
| [Preset Intermedio](Intermediate-Preset_it) | Aggiunge vite, salute, suono, allarmi, movimento a griglia — numeri esatti in quella pagina |

### Riferimento
| Pagina | Descrizione |
|--------|-------------|
| [Riferimento Eventi](Event-Reference_it) | Lista completa di tutti gli eventi |
| [Riferimento completo delle azioni](Full-Action-Reference_it) | Lista completa di tutte le azioni |

---

## Esempio di Avvio Rapido

Ecco un semplice gioco di raccolta monete usando solo funzionalità Principiante:

### 1. Creare Oggetti
- `obj_player` - Il personaggio controllabile
- `obj_coin` - Oggetti collezionabili
- `obj_wall` - Ostacoli solidi

### 2. Aggiungere Eventi al Giocatore

**Keyboard (Arrow Keys):**
```
Left Arrow  → Set Horizontal Speed: -4
Right Arrow → Set Horizontal Speed: 4
Up Arrow    → Set Vertical Speed: -4
Down Arrow  → Set Vertical Speed: 4
```

**Collision with obj_coin:**
```
Add Score: 10
Destroy Instance: other
```

**Collision with obj_wall:**
```
Stop Movement
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
- [Iniziare](Iniziare_it) - Installazione e configurazione
- [Eventi e Azioni](Eventi_e_Azioni_it) - Concetti base
- [Crea il Tuo Primo Gioco](Primo_Gioco_it) - Tutorial
- [Tutorial Breakout](Tutorial-Breakout_it) - Crea un classico gioco Breakout
- [Introduzione alla Creazione di Giochi](Getting-Started-Breakout_it) - Tutorial completo per principianti
