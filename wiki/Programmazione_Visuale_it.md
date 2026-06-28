# Programmazione Visuale

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Torna alla Home](Home_it)

pyGM offre un sistema di programmazione visuale per lo sviluppo di giochi facile senza codice.

## Panoramica

Con la programmazione visuale puoi:
- Creare logica di gioco con drag-and-drop
- Connettere blocchi per comportamenti complessi
- Sviluppare senza conoscenze di programmazione

## L'Editor Blockly

### Interfaccia
1. **Palette blocchi**: Blocchi disponibili per categoria
2. **Area di lavoro**: Qui connetti i blocchi
3. **Barra strumenti**: Salva, Carica, Elimina

### Categorie di blocchi
- **Logica**: Se/Allora, confronti, valori booleani
- **Cicli**: Ripetizioni
- **Matematica**: Calcoli
- **Testo**: Operazioni sul testo
- **Variabili**: Memorizzare valori
- **Funzioni**: Blocchi riutilizzabili
- **Gioco**: Azioni specifiche di pyGM

## Usare i blocchi

### Aggiungere un blocco
1. Clicca su una categoria
2. Trascina un blocco nell'area di lavoro
3. Connettilo ad altri blocchi

### Connettere blocchi
- I blocchi si agganciano automaticamente
- Fai attenzione alle forme corrispondenti
- E possibile annidare blocchi

### Configurare un blocco
- Compila i campi di input
- Scegli opzioni dal dropdown
- Inserisci sottoblocchi

## Esempi

### Movimento semplice
```
Quando [freccia destra] premuto
  Imposta x a (x + 5)
```

### Logica condizionale
```
Se <Vite <= 0> allora
  Mostra messaggio "Game Over"
  Vai alla stanza [rm_gameover]
```

### Ciclo
```
Ripeti [10] volte
  Crea istanza [obj_moneta] alla posizione (Casuale 0-800, Casuale 0-600)
```

## Blocchi di gioco

### Movimento
- **Muovi a**: Muovi alla posizione
- **Imposta velocita**: Velocita di movimento
- **Imposta direzione**: Direzione di movimento

### Istanze
- **Crea istanza**: Genera nuovo oggetto
- **Distruggi**: Elimina oggetto
- **Per tutti**: Tutte le istanze di un tipo

### Variabili
- **Imposta variabile**: Memorizza valore
- **Modifica variabile**: Cambia valore
- **Ottieni variabile**: Recupera valore

### Eventi
- **Quando tasto**: Input da tastiera
- **Quando collisione**: Contatto oggetti
- **Quando timer**: Basato sul tempo

## Suggerimenti

1. **Inizia in piccolo**: Prima progetti semplici
2. **Testa**: Esegui regolarmente
3. **Organizza**: Raggruppa i blocchi logicamente
4. **Commenti**: Aggiungi note

## Dai blocchi al codice

L'editor Blockly puo anche generare codice:
1. Impara i concetti di programmazione visualmente
2. Guarda il codice generato
3. Passa a Python in seguito

## Vedi anche

- [Creare il tuo primo gioco](Primo_Gioco_it)
- [Eventi e Azioni](Eventi_e_Azioni_it)
- [FAQ](FAQ_it)
