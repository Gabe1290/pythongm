# Creare il tuo primo gioco

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Torna alla Home](Home_it)

In questa guida creerai un gioco semplice per imparare le basi di pyGM.

## Panoramica

Creeremo un gioco semplice con:
- Un personaggio giocatore che puo muoversi
- Un oggetto collezionabile
- Un sistema di punteggio

## Passo 1: Creare un nuovo progetto

1. Avvia pyGM
2. Seleziona "Nuovo Progetto"
3. Inserisci un nome per il progetto
4. Scegli una posizione di salvataggio

## Passo 2: Creare gli sprite

### Sprite del giocatore
1. Click destro su "Sprite" nell'albero delle risorse
2. Seleziona "Nuovo Sprite"
3. Usa l'editor integrato o importa un'immagine
4. Chiamalo "spr_giocatore"

### Sprite dell'oggetto collezionabile
1. Crea un altro sprite
2. Chiamalo "spr_moneta"

## Passo 3: Creare gli oggetti

### Oggetto giocatore
1. Click destro su "Oggetti"
2. Seleziona "Nuovo Oggetto"
3. Chiamalo "obj_giocatore"
4. Assegna "spr_giocatore" come sprite

### Aggiungere il movimento
1. Aggiungi l'evento "Pressione tasto"
2. Usa azioni per il movimento:
   - Freccia su: Muovi in alto
   - Freccia giu: Muovi in basso
   - Freccia sinistra: Muovi a sinistra
   - Freccia destra: Muovi a destra

### Oggetto moneta
1. Crea "obj_moneta"
2. Assegna "spr_moneta"
3. Aggiungi evento collisione con il giocatore
4. Azione: Distruggi istanza e aggiungi punti

## Passo 4: Creare una stanza

1. Click destro su "Stanze"
2. Seleziona "Nuova Stanza"
3. Chiamala "rm_livello1"
4. Posiziona gli oggetti:
   - Un giocatore
   - Diverse monete

## Passo 5: Testare il gioco

1. Clicca su "Esegui gioco" o premi F5
2. Testa il movimento
3. Raccogli le monete

## Idee di espansione

- Aggiungere ostacoli
- Implementare un sistema di tempo
- Creare diversi livelli
- Aggiungere effetti sonori

## Prossimi passi

- [Approfondire Eventi e Azioni](Eventi_e_Azioni_it)
- [Imparare la Programmazione Visuale](Programmazione_Visuale_it)
- [Esportare Giochi](Esportare_Giochi_it)
