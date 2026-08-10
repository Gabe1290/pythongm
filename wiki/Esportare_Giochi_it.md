# Esportare Giochi

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Torna alla Home](Home_it)

PyGameMaker può esportare il tuo gioco verso più piattaforme. Questa guida copre ogni opzione di esportazione e come usarla.

---

## Panoramica dell'esportazione

| Piattaforma | Formato | Requisiti |
|-------------|---------|-----------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (su un Mac) |
| **HTML5** | .html | Browser moderno |
| **Linux** | Binario | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Sorgente / .apk | Buildozer |
| **Progetto (.zip)** | .zip | — (condividere il progetto modificabile) |

> **Nulla viene scartato silenziosamente.** Se il tuo gioco usa un'azione che un
> target non può riprodurre (per esempio, alcune azioni non sono supportate
> dall'esportazione Kivy/Android), l'esportazione riesce comunque ma ti indica
> esattamente quali azioni sono state **saltate**, così puoi correggere. Se il tuo
> progetto usa un'[estensione](Extensions_it) disattivata (ad es. la Vista 3D), l'IDE
> ti avvisa al caricamento.

---

## Esportazione Windows EXE

Crea un eseguibile Windows standalone che funziona senza Python installato.

### Come esportare

1. Apri **File → Esporta progetto…** (Ctrl+E) e scegli **Windows**
2. Scegli una cartella di output
3. Attendi il completamento del processo di build
4. Trova il file .exe nella cartella di output

### Cosa viene creato

```
cartella_output/
├── MioGioco.exe      # Eseguibile principale
├── _internal/        # Librerie necessarie
└── assets/           # Risorse del gioco
```

### Requisiti

- PyInstaller (installato tramite `pip install pyinstaller`)
- Sistema Windows per la build (la cross-compilation non è supportata)

### Distribuzione

Per condividere il gioco:
1. Comprimi in zip l'intera cartella di output
2. Distribuisci il file zip
3. Gli utenti estraggono ed eseguono il .exe

### Risoluzione problemi

**DLL mancanti:** Assicurati che tutte le dipendenze siano incluse. Controlla l'output di PyInstaller per gli avvisi.

**Segnalazioni antivirus:** Alcuni antivirus segnalano gli eseguibili PyInstaller. È un falso positivo. Potresti dover firmare il tuo eseguibile.

---

## Esportazione app macOS

Crea un bundle `.app` nativo per macOS con PyInstaller.

### Come esportare

1. Apri **File → Esporta progetto…** (Ctrl+E) e scegli **macOS**
2. Scegli una cartella di output
3. Attendi il completamento della build
4. Trova `MioGioco.app` nella cartella di output

### Requisiti

- Un **Mac** per la build (la cross-compilation da Windows/Linux non è supportata)
- PyInstaller e Kivy installati nel Python di build

### Distribuzione

Comprimi in zip il bundle `.app` per condividerlo. Le app non firmate attivano
Gatekeeper su altri Mac — gli utenti fanno clic destro → **Apri** la prima volta,
oppure firmi/notarizzi l'app con un account Apple Developer.

---

## Esportazione HTML5

Crea un singolo file HTML che funziona nei browser web.

### Come esportare

1. Vai su **File → Esporta come HTML5…**
2. Scegli una posizione di output
3. Seleziona le opzioni (compressione, ecc.)
4. Clicca su Esporta

### Cosa viene creato

```
cartella_output/
└── MioGioco.html     # Gioco a file singolo
```

### Caratteristiche

- Funziona in qualsiasi browser moderno (Chrome, Firefox, Edge, Safari)
- Nessuna installazione richiesta
- Compresso con gzip per un caricamento veloce
- Compatibile con i dispositivi mobili con controlli touch

### Hosting del tuo gioco

Carica il file HTML su:
- Il tuo server web
- GitHub Pages (gratuito)
- itch.io (hosting orientato ai giochi)
- Qualsiasi hosting di file statici

### Compatibilità browser

| Browser | Supporto |
|---------|----------|
| Chrome 80+ | Completo |
| Firefox 75+ | Completo |
| Edge 80+ | Completo |
| Safari 13+ | Completo |
| Chrome mobile | Completo |
| Safari mobile | Completo |

### Limitazioni

- Alcune funzioni potrebbero non funzionare (accesso al file system, ecc.)
- L'audio potrebbe richiedere un'interazione dell'utente per avviarsi
- Le prestazioni dipendono dal dispositivo/browser

---

## Esportazione Linux

Crea un eseguibile Linux nativo.

### Come esportare

1. Apri **File → Esporta progetto…** (Ctrl+E) e scegli **Linux**
2. Scegli una cartella di output
3. Attendi il processo di build

### Requisiti

- Sistema Linux per la build
- Python 3.10+
- PyInstaller

### Distribuzione

```bash
# Rendere il file eseguibile
chmod +x MioGioco

# Avviare il gioco
./MioGioco
```

Distribuisci come archivio .tar.gz:
```bash
tar -czvf MioGioco-linux.tar.gz MioGioco/
```

---

## Esportazione Kivy (mobile)

Crea app mobili per iOS e Android usando il framework Kivy.

### Come esportare

1. Vai su **File → Esporta in Kivy…**
2. Scegli una cartella di output
3. Configura le impostazioni mobili
4. Esporta il progetto Kivy

### Build per Android

Il progetto Kivy esportato usa Buildozer per creare gli APK:

```bash
cd progetto_esportato
pip install buildozer
buildozer init
buildozer android debug
```

### Build per iOS

Richiede un Mac con Xcode:

```bash
cd progetto_esportato
pip install kivy-ios
toolchain build python3 kivy
toolchain create MioGioco ~/progetto_ios
```

### Considerazioni mobili

- I controlli touch vengono mappati automaticamente
- Il ridimensionamento dello schermo è gestito automaticamente
- Testa su più dimensioni di schermo
- Ottimizza le dimensioni delle risorse per il mobile

---

## Esportazione del progetto (.zip)

Condividi il **progetto modificabile** stesso (non un gioco compilato): usa
**File → Esporta progetto…** (Ctrl+E) per creare un archivio `.zip` che qualcun
altro può riaprire in PyGameMaker. Ideale per la collaborazione, i backup o la
consegna di compiti scolastici.

---

## Impostazioni di esportazione

### Impostazioni generali

| Impostazione | Descrizione |
|--------------|-------------|
| **Nome gioco** | Nome mostrato nella barra del titolo/app |
| **Icona** | Icona dell'applicazione (Windows/mobile) |
| **Versione** | Numero di versione (1.0.0) |
| **Autore** | Nome dello sviluppatore |

### Impostazioni Windows

| Impostazione | Descrizione |
|--------------|-------------|
| **Console** | Mostra la finestra della console (per il debug) |
| **File singolo** | Un solo .exe vs. cartella con _internal |
| **UPX** | Comprimi con UPX (dimensione ridotta) |

### Impostazioni HTML5

| Impostazione | Descrizione |
|--------------|-------------|
| **Compressione** | Abilita la compressione gzip |
| **Schermo intero** | Avvia in modalità schermo intero |
| **Controlli touch** | Mostra i controlli a schermo |

---

## Lista di controllo prima dell'esportazione

Prima di esportare, verifica:

- [ ] Tutte le risorse sono incluse nel progetto
- [ ] Il gioco funziona correttamente nell'IDE
- [ ] Nessun messaggio di debug o codice di test
- [ ] L'ordine delle stanze è corretto (stanza iniziale per prima)
- [ ] I file audio sono in formati supportati
- [ ] Gli sprite sono ottimizzati per la dimensione del file

---

## Ottimizzare la dimensione dei file

### Sprite
- Usa dimensioni appropriate (non sovradimensionate)
- Comprimi i file PNG
- Considera il JPEG per immagini senza trasparenza

### Audio
- Usa OGG/MP3 per la musica (non WAV)
- Mantieni brevi gli effetti sonori
- Frequenze di campionamento più basse per suoni semplici

### Generale
- Rimuovi le risorse inutilizzate
- Minimizza le dimensioni delle stanze
- Testa sulle piattaforme target

---

## Testare le esportazioni

Testa sempre il tuo gioco esportato:

1. **Windows:** Testa su un PC pulito senza Python
2. **HTML5:** Testa in più browser
3. **Linux:** Se possibile, testa su diverse distribuzioni
4. **Mobile:** Testa su dispositivi reali, non solo sugli emulatori

---

## Piattaforme di distribuzione

### itch.io
- Hosting gratuito per giochi indie
- Supporta HTML5, Windows, Linux, Mac
- Sistema di pagamento integrato

### Steam
- Richiede l'integrazione dello Steamworks SDK
- Usa PyInstaller con l'API Steam
- Quota di pubblicazione a pagamento

### Google Play (Android)
- Richiede un account sviluppatore (25 $)
- Crea un APK firmato con Buildozer
- Segui le linee guida sui contenuti

### App Store (iOS)
- Richiede un account Apple Developer (99 $/anno)
- Crea con kivy-ios
- Invia tramite App Store Connect

---

## Passaggi successivi

- [[Iniziare_it]] - Rivedere le basi
- [[Troubleshooting_it|Risoluzione dei Problemi]] - Errori di dipendenza mancante e altri problemi di export
- [[FAQ_it]] - Domande comuni sull'esportazione
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Segnalare problemi di esportazione
