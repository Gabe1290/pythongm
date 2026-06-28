# Editor Oggetti

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Torna alla Home](Home_it)

L'Editor Oggetti e lo strumento centrale per definire il comportamento degli elementi di gioco.

## Panoramica

Gli oggetti sono i mattoni del tuo gioco. Definiscono:
- Aspetto (Sprite)
- Comportamento (Eventi e Azioni)
- Proprieta fisiche
- Interazioni

## Interfaccia dell'Editor

### Aree principali
1. **Lista oggetti**: Tutti gli oggetti nel progetto
2. **Pannello proprieta**: Impostazioni di base
3. **Lista eventi**: Eventi definiti
4. **Editor azioni**: Azioni per gli eventi

## Proprieta dell'oggetto

### Generali
- **Nome**: Identificatore univoco (es. obj_giocatore)
- **Sprite**: Grafica assegnata
- **Visibile**: Se l'oggetto viene renderizzato
- **Persistente**: Sopravvive ai cambi di stanza

### Fisica
- **Solido**: Collide con altri oggetti
- **Profondita**: Ordine di disegno
- **Oggetto genitore**: Ereditarieta delle proprieta

## Lavorare con gli eventi

### Aggiungere un evento
1. Clicca su "Aggiungi Evento"
2. Seleziona il tipo di evento
3. Aggiungi azioni

### Tipi di evento
- **Create**: Alla creazione dell'istanza
- **Step**: Ogni frame
- **Draw**: Per il disegno
- **Tastiera**: Input da tastiera
- **Mouse**: Interazioni con il mouse
- **Collisione**: Al contatto con altri oggetti

## Usare le azioni

### Aggiungere azioni
1. Seleziona un evento
2. Trascina azioni dalla libreria
3. Configura i parametri

### Azioni comuni
- Muovere in una direzione
- Impostare variabile
- Creare/distruggere istanza
- Riprodurre suono
- Cambiare stanza

## Best Practice

1. **Nomi chiari**: Usa prefissi come "obj_"
2. **Modularita**: Oggetti piccoli e riutilizzabili
3. **Usa l'ereditarieta**: Oggetti genitori per comportamenti comuni
4. **Documentazione**: Commenti negli eventi complessi

## Vedi anche

- [Eventi e Azioni](Eventi_e_Azioni_it)
- [Programmazione Visuale](Programmazione_Visuale_it)
- [Editor Stanze](Editor_Stanze_it)
