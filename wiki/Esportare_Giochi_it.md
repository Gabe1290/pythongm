# Esportare Giochi

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

[Torna alla Home](Home_it)

Scopri come esportare i tuoi giochi pyGM per diverse piattaforme.

## Panoramica

pyGM permette l'esportazione per:
- Windows (EXE)
- macOS (APP)
- Linux
- Web (HTML5)

## Preparazione all'esportazione

### Prima di esportare, verifica
1. **Tutte le risorse presenti**: Sprite, suoni, ecc.
2. **Gioco testato**: Nessun errore critico
3. **Impostazioni ottimizzate**: Risoluzione, schermo intero

### Impostazioni del progetto
- **Nome gioco**: Nome visualizzato
- **Versione**: Numero di versione
- **Icona**: Icona dell'applicazione
- **Schermata iniziale**: Splash Screen

## Esportazione Windows

### Prerequisiti
- pyinstaller installato
- Sistema Windows o cross-compilation

### Passaggi
1. Vai su File > Esporta
2. Seleziona "Windows Executable"
3. Configura le opzioni:
   - File icona
   - Nascondi finestra console
   - File EXE singolo
4. Clicca su "Esporta"

### Output
- File EXE singolo
- Oppure cartella con dipendenze

## Esportazione macOS

### Prerequisiti
- Sistema macOS consigliato
- py2app o pyinstaller

### Passaggi
1. File > Esporta > macOS
2. Inserisci nome App Bundle
3. Scegli icona (formato ICNS)
4. Esporta

## Esportazione Linux

### Opzioni
- AppImage (consigliato)
- Pacchetto Debian
- File eseguibile

### Passaggi
1. File > Esporta > Linux
2. Scegli formato
3. Esporta

## Esportazione Web (HTML5)

### Vantaggi
- Funziona nel browser
- Facile da condividere
- Nessuna installazione necessaria

### Passaggi
1. File > Esporta > Web
2. Configura:
   - Dimensione canvas
   - Schermata di caricamento
   - Compressione
3. Esporta

### Output
- File HTML
- File JavaScript
- Cartella risorse

### Hosting
- Carica su server web
- Usa itch.io
- Usa GitHub Pages

## Opzioni di esportazione

### Generali
- **Compressione**: Riduci dimensione file
- **Modalita debug**: Mantieni per test
- **Incorpora risorse**: Tutto in un file

### Specifiche per piattaforma
- **Windows**: Manifesto UAC
- **macOS**: Firma del codice
- **Web**: Versione WebGL

## Risoluzione problemi

### Problemi comuni

**Esportazione fallisce**
- Controlla messaggi di errore
- Aggiorna pyinstaller

**Risorse mancanti**
- Verifica i percorsi
- Reintegra le risorse

**Il gioco non si avvia**
- Testa in modalita debug
- Verifica le dipendenze

## Ottimizzazione

1. **Ottimizza dimensioni immagini**: Comprimi sprite
2. **Comprimi audio**: MP3 invece di WAV
3. **Rimuovi risorse inutilizzate**
4. **Ottimizza il codice**: Migliora efficienza

## Vedi anche

- [FAQ](FAQ_it)
- [Creare il tuo primo gioco](Primo_Gioco_it)
- [Iniziare](Iniziare_it)
