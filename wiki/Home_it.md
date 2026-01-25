# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Un ambiente di sviluppo giochi visuale ispirato a GameMaker 7.0**

PyGameMaker è un IDE open-source che rende accessibile la creazione di giochi 2D attraverso la programmazione visuale a blocchi (Google Blockly) e un sistema eventi-azioni. Crea giochi senza conoscenze approfondite di programmazione, poi esportali su Windows, Linux, HTML5 o piattaforme mobili.

---

## Scegli il Tuo Livello

PyGameMaker usa **preset** per controllare quali eventi e azioni sono disponibili. Questo aiuta i principianti a concentrarsi sulle funzionalità essenziali permettendo agli utenti esperti di accedere al set completo di strumenti.

| Preset | Ideale Per | Funzionalità |
|--------|------------|--------------|
| [**Principiante**](Beginner-Preset_it) | Nuovi allo sviluppo giochi | 4 eventi, 17 azioni - Movimento, collisioni, punteggio, stanze |
| [**Intermedio**](Intermediate-Preset_it) | Qualche esperienza | +4 eventi, +12 azioni - Vite, salute, suono, allarmi, disegno |
| **Avanzato** | Utenti esperti | Tutti i 40+ eventi e azioni disponibili |

**Nuovi utenti:** Inizia con il [Preset Principiante](Beginner-Preset_it) per imparare i fondamentali senza essere sopraffatto.

Vedi la [Guida ai Preset](Preset-Guide_it) per una panoramica completa del sistema di preset.

---

## Funzionalità in Breve

| Funzionalità | Descrizione |
|--------------|-------------|
| **Programmazione Visuale** | Codifica drag-and-drop con Google Blockly 12.x |
| **Sistema Eventi-Azioni** | Logica event-driven compatibile con GameMaker 7.0 |
| **Preset per Livello** | Set di funzionalità Principiante, Intermedio e Avanzato |
| **Esportazione Multi-Piattaforma** | Windows EXE, HTML5, Linux, Kivy (mobile/desktop) |
| **Gestione Asset** | Sprite, suoni, sfondi, font e stanze |
| **UI Multilingue** | Inglese, Francese, Tedesco, Italiano, Spagnolo, Portoghese, Sloveno, Ucraino, Russo |
| **Estensibile** | Sistema plugin per eventi e azioni personalizzati |

---

## Per Iniziare

### Requisiti di Sistema

- **Python** 3.10 o superiore
- **Sistema Operativo:** Windows, Linux o macOS

### Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Crea un ambiente virtuale (raccomandato):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # oppure
   venv\Scripts\activate     # Windows
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Avvia PyGameMaker:
   ```bash
   python main.py
   ```

---

## Concetti Fondamentali

### Oggetti
Entità di gioco con sprite, proprietà e comportamenti. Ogni oggetto può avere più eventi con azioni associate.

### Eventi
Trigger che eseguono azioni quando si verificano condizioni specifiche:
- **Create** - Quando un'istanza viene creata
- **Step** - Ogni frame (tipicamente 60 FPS)
- **Draw** - Fase di rendering personalizzato
- **Destroy** - Quando un'istanza viene distrutta
- **Keyboard** - Tasto premuto, rilasciato o tenuto
- **Mouse** - Click, movimento, entrata/uscita
- **Collision** - Quando le istanze si toccano
- **Alarm** - Timer countdown (12 disponibili)

Vedi il [Riferimento Eventi](Event-Reference_it) per la documentazione completa.

### Azioni
Operazioni eseguite quando gli eventi si attivano. 40+ azioni integrate per:
- Movimento e fisica
- Disegno e sprite
- Punteggio, vite e salute
- Suono e musica
- Gestione istanze e stanze

Vedi il [Riferimento Completo Azioni](Full-Action-Reference_it) per la documentazione completa.

### Stanze
Livelli di gioco dove posizioni le istanze degli oggetti, imposti gli sfondi e definisci l'area di gioco.

---

## Programmazione Visuale con Blockly

PyGameMaker integra Google Blockly per la programmazione visuale. I blocchi sono organizzati in categorie:

- **Eventi** - Create, Step, Draw, Keyboard, Mouse
- **Movimento** - Velocità, direzione, posizione, gravità
- **Temporizzazione** - Allarmi e ritardi
- **Disegno** - Forme, testo, sprite
- **Punteggio/Vite/Salute** - Tracciamento stato gioco
- **Istanza** - Creare e distruggere oggetti
- **Stanza** - Navigazione e gestione
- **Valori** - Variabili ed espressioni
- **Suono** - Riproduzione audio
- **Output** - Debug e visualizzazione

---

## Opzioni di Esportazione

### Windows EXE
Eseguibili Windows standalone usando PyInstaller. Nessun Python richiesto sulla macchina target.

### HTML5
Giochi web a file singolo che funzionano in qualsiasi browser moderno. Compressi con gzip per caricamento veloce.

### Linux
Eseguibili Linux nativi per ambienti Python 3.10+.

### Kivy
App cross-platform per mobile (iOS/Android) e desktop via Buildozer.

---

## Struttura del Progetto

```
nome_progetto/
├── project.json      # Configurazione progetto
├── backgrounds/      # Immagini sfondo e metadati
├── data/             # File dati personalizzati
├── fonts/            # Definizioni font
├── objects/          # Definizioni oggetti (JSON)
├── rooms/            # Layout stanze (JSON)
├── scripts/          # Script personalizzati
├── sounds/           # File audio e metadati
├── sprites/          # Immagini sprite e metadati
└── thumbnails/       # Miniature asset generate
```

---

## Contenuto Wiki

### Preset e Riferimento
- [Guida ai Preset](Preset-Guide_it) - Panoramica del sistema di preset
- [Preset Principiante](Beginner-Preset_it) - Funzionalità essenziali per nuovi utenti
- [Preset Intermedio](Intermediate-Preset_it) - Funzionalità aggiuntive
- [Riferimento Eventi](Event-Reference_it) - Documentazione completa eventi
- [Riferimento Azioni](Full-Action-Reference_it) - Documentazione completa azioni

### Tutorial e Guide
- [**Tutorial**](Tutorials_it) - Tutti i tutorial in un unico posto
- [Per Iniziare](Per_Iniziare_it) - Primi passi con PyGameMaker
- [Crea il Tuo Primo Gioco](Primo_Gioco_it) - Tutorial passo-passo
- [Tutorial Pong](Tutorial-Pong_it) - Crea un classico gioco Pong a due giocatori
- [Tutorial Breakout](Tutorial-Breakout_it) - Crea un classico gioco Breakout
- [Introduzione alla Creazione di Giochi](Getting-Started-Breakout_it) - Tutorial completo per principianti
- [Editor Oggetti](Editor_Oggetti_it) - Lavorare con oggetti di gioco
- [Editor Stanze](Editor_Stanze_it) - Progettare livelli
- [Eventi e Azioni](Eventi_e_Azioni_it) - Riferimento logica di gioco
- [Programmazione Visuale](Programmazione_Visuale_it) - Usare i blocchi Blockly
- [Esportare Giochi](Esportare_Giochi_it) - Compilare per diverse piattaforme
- [FAQ](FAQ_it) - Domande frequenti

---

## Contribuire

I contributi sono benvenuti! Vedi le nostre linee guida per:
- Segnalazioni bug e richieste funzionalità
- Contributi al codice
- Traduzioni
- Miglioramenti alla documentazione

---

## Licenza

PyGameMaker è rilasciato sotto **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Link

- [Repository GitHub](https://github.com/Gabe1290/pythongm)
- [Issue Tracker](https://github.com/Gabe1290/pythongm/issues)
- [Release](https://github.com/Gabe1290/pythongm/releases)
