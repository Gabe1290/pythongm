# Iniziare

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Torna alla Home](Home_it)

Questa guida ti aiuterà a mettere in funzione PyGameMaker sul tuo sistema.

---

## Requisiti di Sistema

- **Python** 3.10 o superiore
- **Sistema Operativo:** Windows, Linux o macOS
- **Spazio su Disco:** ~500 MB per l'installazione
- **RAM:** minimo 4 GB, 8 GB consigliati

---

## Installazione

### Passo 1: Installare Python

Scarica Python 3.10+ da [python.org](https://www.python.org/downloads/) e installalo. Assicurati di selezionare "Add Python to PATH" durante l'installazione su Windows.

### Passo 2: Clonare il Repository

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Oppure scarica il file ZIP dalla [pagina Releases](https://github.com/Gabe1290/pythongm/releases).

### Passo 3: Creare un Ambiente Virtuale

Creare un ambiente virtuale mantiene isolate le dipendenze di PyGameMaker:

```bash
python -m venv venv
```

Attiva l'ambiente virtuale:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Passo 4: Installare le Dipendenze

```bash
pip install -r requirements.txt
```

### Passo 5: Avviare PyGameMaker

```bash
python main.py
```

---

## Primo Avvio

Al primo avvio di PyGameMaker, vedrai:

1. **Barra dei Menu** — i menu File, Edit, Assets, Build, Tools e Help
2. **Albero delle Risorse** — pannello sinistro con gli asset del progetto (Sprite, Suoni, Sfondi, Oggetti, Stanze)
3. **Area di Lavoro** — area centrale per modificare gli asset
4. **Pannello Proprietà** — pannello destro per le proprietà degli asset

---

## Creare il Tuo Primo Progetto

1. Vai su **File > New Project**
2. Scegli una posizione e un nome per il tuo progetto
3. Verrà creata una nuova cartella di progetto con la struttura standard

---

## Struttura del Progetto

Ogni progetto PyGameMaker contiene:

```
mio_progetto/
├── project.json      # Impostazioni del progetto
├── sprites/          # Immagini sprite
├── sounds/           # File audio
├── backgrounds/      # Immagini di sfondo
├── objects/          # Definizioni degli oggetti di gioco
├── rooms/            # Layout dei livelli
├── fonts/            # File dei font
├── scripts/          # Script personalizzati
└── data/             # File di dati personalizzati
```

---

## Cambiare Lingua

PyGameMaker supporta più lingue:

1. Vai su **Tools > Language**
2. Seleziona la lingua preferita dal menu
3. Riavvia PyGameMaker per applicare la modifica

Lingue disponibili: Inglese, Francese, Tedesco, Italiano, Spagnolo, Portoghese, Sloveno, Ucraino, Russo

---

## Prossimi Passi

- [[Primo_Gioco_it]] - Costruisci un semplice gioco passo dopo passo
- [[Editor_Oggetti_it]] - Impara a creare oggetti di gioco
- [[Editor_Stanze_it]] - Progetta i tuoi livelli di gioco
- [[Eventi_e_Azioni_it]] - Comprendi la logica di gioco

---

## Risoluzione dei Problemi

### Python non trovato
Assicurati che Python sia installato e aggiunto al PATH. Prova a eseguire `python --version` per verificare.

### Dipendenze mancanti
Se ricevi errori di importazione, prova a reinstallare le dipendenze:
```bash
pip install -r requirements.txt --force-reinstall
```

### Problemi di visualizzazione
Su Linux, Qt (il framework GUI su cui è basato PyGameMaker) richiede
alcune librerie di sistema non incluse da `pip`:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Ottenere Aiuto

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Segnala bug o richiedi funzionalità
- [[FAQ_it]] - Domande e risposte comuni
