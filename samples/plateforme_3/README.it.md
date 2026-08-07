# Platform — Livello 3

Un platform a scorrimento laterale importato da GameMaker 8.x
(`samples/plateforme_3.gmk`). È di gran lunga il più grande dei tre
esempi platform: 2 oggetti (plateforme_1) → 4 oggetti (plateforme_2)
→ **15 oggetti** qui, aggiungendo mostri terrestri e volanti in
pattuglia (con uccisione a calpestio e varianti cadavere/schizzo
generate a runtime), un pericolo di morte istantanea invisibile, due
tipi di collezionabili, e un oggetto uscita che avanza alla stanza
successiva o mostra la tabella dei record e riavvia.

**Dove si colloca:** parte della famiglia `plateforme_*` — come
`plateforme_2`, usa uno **sfondo a tessere** (125 pezzi di tessere
sotto gli oggetti mattone solidi, più l'immagine sfumata
`fond_degrade`), il passo che questa famiglia aggiunge oltre
`maze_*`. Vedi
[`../README.md`](../README.md#progression-how-each-family-is-built-not-just-how-it-plays)
per la progressione completa.

**Audio e musica:** 4 file audio, genuinamente collegati: 7 punti di
chiamata `play_sound` per `son_bonus` (raccolta), `son_monstre_mort`
(uccisione a calpestio), `son_personnage_mort` (morte giocatore), e
`son_niveaufini` (livello completato).

## Come si gioca

- **Freccia sinistra/destra** — muove Pingus (`obj_pingus`) sinistra/destra.
- **Freccia su** — salto, ma solo mentre si sta su qualcosa di solido
  (controllato un pixel sotto il giocatore).
- **Obiettivo** — raccogli gli `obj_bonus` (+5 punteggio) e gli
  `obj_power` (+20 punteggio) attraversando `niveau_01` per raggiungere
  `obj_sortie`; toccarlo riproduce un jingle e o avanza a una stanza
  successiva (nessuna esiste in questo esempio, quindi ricade sul
  ramo tabella-record/riavvio) o mostra la tabella dei record e riavvia il gioco.
- **Mostri** — atterrare sopra un `obj_monstre` o `obj_monstre_volant`
  (`vspeed > 0` e sopra il mostro) lo uccide e assegna 50 punti;
  colpirne uno di lato o da sotto costa una vita e riavvia la stanza.
  Nota: la collisione con `obj_monstre_volant` non ha effetto (il
  mostro volante non può ferire né essere ferito) finché non è stato
  raccolto `obj_power` — vedi Cose da modificare.
- **Condizione di sconfitta** — toccare `obj_mortel` (una zona di
  morte istantanea invisibile) o un mostro nel modo sbagliato costa
  una vita e riavvia la stanza; esaurire le vite (`no_more_lives`)
  mostra la tabella dei record e riavvia l'intero gioco. Vite iniziali:
  3 (impostazioni `project.json`).

## Struttura del progetto

| File | Scopo |
| --- | --- |
| `project.json` | Manifesto del progetto — impostazioni finestra/stanza, copie di risorse incorporate. |
| `rooms/niveau_01.json` | L'unica stanza: 800×640, 194 istanze + 125 tessere di sfondo. Fonte di verità per il contenuto della stanza (la lista `instances` incorporata di `project.json` è vuota, stesso schema di plateforme_2). |
| `objects/*.json` | File collaterali per oggetto per tutti e 15 gli oggetti; identici alle copie incorporate in `project.json` a questa data (verificato byte per byte, a differenza del file stanza di plateforme_2). |
| `sprites/` | 18 risorse sprite (strisce cammino/volo, sprite morte, blocchi piattaforma, collezionabili, uscita, marcatore). |
| `sounds/` | 4 effetti sonori (morte mostro, morte giocatore, raccolta bonus, livello completato). |
| `backgrounds/` | Set di tessere neve (`tuiles_neige.png`, sorgente automatica per le 125 tessere della stanza) e uno sfumato verticale (`fond_degrade.png`) come sfondo della stanza. |
| `CREDITS.txt` | Avviso di licenza per la grafica sprite/sfondo (vedi Risorse sotto). |

## Oggetti

15 oggetti, raggruppati per ruolo. Conteggi di posizionamento nella
stanza (di 194 istanze) mostrati dove l'oggetto appare in
`niveau_01`; gli oggetti "generati a runtime" appaiono solo tramite
`change_instance` durante il gioco.

| Oggetto | Ruolo | Eventi chiave |
| --- | --- | --- |
| `obj_pingus` | Giocatore — movimento, salto, gravità, tutta la gestione di collisioni/sconfitta/vittoria | create, step, keyboard (left/right/up), keyboard_release, collision_with_obj_brique/obj_monstre/obj_monstre_volant/obj_mortel/obj_bonus/obj_power/obj_sortie/obj_marqueur, game_start, no_more_lives |
| `obj_brique` | Blocco piattaforma solido base, 32×32 (109 posizionati) | nessuno (solo flag solido) |
| `obj_brique_h` | Variante larga piattaforma, 32×16, figlio di `obj_brique` (15 posizionati) | nessuno |
| `obj_brique_v` | Variante stretta piattaforma, 16×32, figlio di `obj_brique`; definita ma non posizionata in `niveau_01` | nessuno |
| `obj_brique_c` | Piccola variante piattaforma, 16×16, figlio di `obj_brique` (1 posizionato) | nessuno |
| `obj_monstre` | Mostro terrestre — pattuglia sinistra/destra, inverte al contatto con un muro (3 posizionati) | create, collision_with_obj_brique |
| `obj_monstre_mort` | Cadavere mostro generato a runtime dopo un'uccisione a calpestio; eredita `obj_brique` (diventa un gradino solido) | create |
| `obj_monstre_volant` | Mostro volante — pattuglia verso destra, rimbalza sui muri (2 posizionati) | create, collision_with_obj_brique |
| `obj_monstre_volant_mort` | Cadavere mostro volante generato a runtime; cade con gravità limitata, atterra su piattaforme/marcatori | step, collision_with_obj_brique, collision_with_obj_marqueur |
| `obj_mortel` | Zona di pericolo invisibile a morte istantanea (4 posizionate) | nessuno (gestito dall'evento di collisione di `obj_pingus`) |
| `obj_splat` | Animazione di morte giocatore generata a runtime, riavvia la stanza alla fine dell'animazione | create, animation_end |
| `obj_bonus` | Collezionabile minore, +5 punteggio, frame di riposo casuale (52 posizionati) | create |
| `obj_power` | Collezionabile maggiore, +20 punteggio; determina anche se i mostri volanti possono ferire/essere uccisi (1 posizionato) | create |
| `obj_sortie` | Uscita del livello — riproduce un jingle, poi stanza successiva o tabella record + riavvio (1 posizionata) | nessuno (gestito dall'evento di collisione di `obj_pingus`) |
| `obj_marqueur` | Marcatore di design della stanza invisibile e non solido; le collisioni non hanno esplicitamente effetto (5 posizionati) | nessuno |

## Risorse

18 sprite, 4 suoni, 2 sfondi. La grafica di sprite/sfondi è adattata
dal progetto Pingus (GPL-3.0-or-later) — vedi `CREDITS.txt` per
l'attribuzione completa e i termini di licenza; questa README non
riafferma né estende quelle dichiarazioni.

## Cose da modificare

- Il test di calpestio tra `obj_pingus` e
  `obj_monstre`/`obj_monstre_volant` era `vspeed > 0 and y < other.y+8`,
  che una caduta veloce poteva superare (la finestra di 8px era
  controllata contro la posizione *dopo il movimento*) e costava una
  vita su ciò che sembrava un calpestio pulito. Ora è
  `vspeed > 0 and y - vspeed < other.y+8`, che controlla la finestra
  contro la posizione precedente al movimento.
- Il collezionabile `obj_power` blocca silenziosamente ogni
  interazione con `obj_monstre_volant` (tramite un
  `if_object_exists(obj_power, not_flag=true)` intorno alla logica di
  calpestio/morte in `obj_pingus`) — varrebbe la pena renderlo visibile
  ai giocatori (es. un cambio di sprite/palette) piuttosto che una
  regola invisibile.
- La velocità orizzontale del giocatore è un fisso `hspeed = 4`;
  l'impulso di salto è `vspeed = -10`; la gravità di caduta è `0,5`
  con un tetto di velocità terminale a `vspeed = 24`.
- La dimensione della stanza è 800×640 a `room_speed = 30`.

## Stato dell'esportazione

Questo esempio è elencato nella lista `SAMPLES` di
`tools/smoke_run_samples.py`, quindi riceve un passaggio smoke senza
interfaccia grafica (il vero ciclo di gioco eseguito per ~180 frame
con input da tastiera iniettato) a ogni esecuzione di quell'harness.
Nessuna verifica per target di esportazione specifico (Kivy/HTML5) è
stata fatta specificamente per questo esempio. È esposto nella scheda
Welcome dell'IDE come "Platform — Level 3" (`widgets/welcome_tab.py`).
