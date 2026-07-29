# Eventi e Azioni

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Torna alla Home](Home_it)

Eventi e Azioni formano il cuore della logica di gioco in pyGM.

## Concetto

### Eventi
Gli eventi sono trigger che reagiscono a situazioni specifiche:
- Avvio del gioco
- Pressione tasti
- Collisione
- Timer

### Azioni
Le azioni sono le risposte agli eventi:
- Muovere
- Creare/Distruggere
- Modificare valori
- Riprodurre suoni

## Categorie di eventi

### Eventi di creazione
- **Create**: Una volta alla creazione dell'istanza
- **Destroy**: All'eliminazione dell'istanza
- **Room Start**: All'ingresso in una stanza

### Eventi Step
- **Step**: Ogni frame
- **Begin Step**: Prima del controllo collisioni
- **End Step**: Dopo il controllo collisioni

### Eventi di input
- **Tastiera**: Pressione/rilascio tasti
- **Mouse**: Click e movimento

### Eventi di collisione
- Contatto con altri oggetti
- Contatto con muri
- Controlli di area

### Eventi di disegno
- **Draw**: Disegno normale
- **Draw GUI**: Elementi dell'interfaccia

### Altri eventi
- **Alarm**: Eventi basati su timer
- **Animation End**: Animazione sprite terminata

## Libreria delle azioni

### Movimento
- `move_towards_point`: Muovi verso un punto
- `set_speed`: Imposta velocità
- `set_direction`: Imposta direzione
- `bounce`: Rimbalza

### Istanze
- `create_instance`: Crea nuova istanza
- `destroy_instance`: Elimina istanza
- `set_sprite`: Cambia sprite

### Variabili
- `set_variable`: Imposta valore
- `test_variable`: Controllo condizionale

### Audio
- `play_sound`: Riproduci suono
- `stop_sound`: Ferma suono
- `set_volume`: Cambia volume

### Stanza
- `goto_room`: Cambia stanza
- `restart_room`: Riavvia stanza
- `next_room`: Stanza successiva

### Disegno
- `draw_sprite`: Disegna sprite
- `draw_text`: Mostra testo
- `draw_rectangle`: Disegna rettangolo

## Condizioni e controllo del flusso

### Azioni condizionali
```
Se Variabile == Valore
  Esegui azione
Altrimenti
  Azione alternativa
```

### Cicli
- Ripetere azioni
- Per tutte le istanze

## Best Practice

1. **Usa Step con parsimonia**: Solo quando necessario
2. **Ottimizza le collisioni**: Considera la proprietà Solid
3. **Raggruppa gli eventi**: Logica correlata insieme
4. **Usa gli alarm**: Per azioni temporizzate

## Vedi anche

- [Editor Oggetti](Editor_Oggetti_it)
- [Programmazione Visuale](Programmazione_Visuale_it)
- [FAQ](FAQ_it)
