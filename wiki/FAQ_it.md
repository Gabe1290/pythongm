# Domande Frequenti (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Torna alla Home](Home_it)

Risposte alle domande comuni su pyGM.

## Domande generali

### Cos'e pyGM?
pyGM e un editor visuale per lo sviluppo di giochi in Python. Permette di creare giochi 2D senza conoscenze di programmazione approfondite.

### pyGM e gratuito?
Si, pyGM e open source e completamente gratuito.

### Quale linguaggio di programmazione viene usato?
pyGM e basato su Python. Puoi usare la programmazione visuale o scrivere direttamente codice Python.

### Per quali piattaforme posso sviluppare?
- Windows
- macOS
- Linux
- Web (HTML5)

## Installazione

### Come installo pyGM?
```bash
pip install pygm
```

### Quale versione di Python serve?
Python 3.8 o superiore.

### pyGM non si avvia. Cosa faccio?
1. Verifica la versione di Python
2. Reinstalla le dipendenze
3. Avvia da linea di comando per vedere gli errori

## Sviluppo

### Come creo un nuovo progetto?
Avvia pyGM e seleziona "Nuovo Progetto" o usa File > Nuovo.

### Come aggiungo sprite?
1. Click destro su "Sprite" nell'albero delle risorse
2. Seleziona "Nuovo Sprite"
3. Importa un'immagine o creane una

### Come creo animazioni?
1. Apri uno sprite
2. Aggiungi piu frame
3. Imposta la velocita dell'animazione

### Come programmo il comportamento degli oggetti?
1. Apri un oggetto
2. Aggiungi eventi (es. Create, Step)
3. Aggiungi azioni agli eventi
4. Oppure usa l'editor visuale Blockly

## Risorse

### Quali formati immagine sono supportati?
- PNG (consigliato)
- JPG
- GIF
- BMP

### Quali formati audio sono supportati?
- WAV
- MP3
- OGG

### Come ottimizzo le mie risorse?
- Usa dimensioni immagine appropriate
- Comprimi i file audio
- Rimuovi risorse inutilizzate

## Gameplay

### Come implemento il rilevamento collisioni?
1. Crea un evento collisione nell'oggetto
2. Seleziona l'altro oggetto
3. Aggiungi azioni per la reazione

### Come creo piu livelli?
1. Crea piu stanze
2. Usa l'azione "Vai alla stanza"
3. Oppure "Vai alla stanza successiva"

### Come salvo i progressi di gioco?
Usa le funzioni di salvataggio integrate:
- `save_game()`: Salva gioco
- `load_game()`: Carica gioco

## Esportazione

### Come esporto il mio gioco?
1. Vai su File > Esporta
2. Seleziona la piattaforma di destinazione
3. Configura le opzioni
4. Clicca su "Esporta"

### Perche il file esportato e cosi grande?
- Include il runtime Python
- Tutte le risorse incorporate
- Suggerimento: Ottimizza le risorse

### Posso esportare per dispositivi mobili?
Attualmente non supportato direttamente. L'esportazione web funziona sui browser mobili.

## Risoluzione problemi

### Il mio gioco e lento
- Riduci il codice negli eventi Step
- Ottimizza le dimensioni degli sprite
- Evita troppe istanze

### Gli sprite non vengono visualizzati
- Verifica il percorso dello sprite
- Assicurati che Visibile=true
- Controlla l'ordine di disegno (profondita)

### Le collisioni non funzionano
- Verifica le maschere di collisione
- Assicurati che gli oggetti siano solidi (se necessario)
- Controlla la configurazione degli eventi

## Community

### Dove trovo aiuto?
- Documentazione ufficiale
- GitHub Issues
- Forum della community

### Come posso contribuire?
- Segnala bug su GitHub
- Invia Pull Request
- Migliora la documentazione

## Vedi anche

- [Iniziare](Iniziare_it)
- [Creare il tuo primo gioco](Primo_Gioco_it)
- [Eventi e Azioni](Eventi_e_Azioni_it)
