# Dogodki in akcije

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Nazaj na začetno stran](Home_sl)

Dogodki in akcije tvorijo srce igralne logike v pyGM.

## Koncept

### Dogodki
Dogodki so prožilci, ki se odzivajo na določene situacije:
- Zagon igre
- Pritisk tipke
- Trk
- Časovnik

### Akcije
Akcije so odzivi na dogodke:
- Premik
- Ustvarjanje/Uničenje
- Spreminjanje vrednosti
- Predvajanje zvokov

## Kategorije dogodkov

### Dogodki ustvarjanja
- **Create**: Enkrat ob ustvarjanju instance
- **Destroy**: Ob brisanju instance
- **Room Start**: Ob vstopu v sobo

### Dogodki Step
- **Step**: Vsak okvir
- **Begin Step**: Pred preverjanjem trkov
- **End Step**: Po preverjanju trkov

### Dogodki vnosa
- **Tipkovnica**: Pritisk/spust tipk
- **Miška**: Kliki in premikanje

### Dogodki trkov
- Stik z drugimi objekti
- Stik s stenami
- Preverjanja območij

### Dogodki risanja
- **Draw**: Normalno risanje
- **Draw GUI**: Elementi vmesnika

### Ostali dogodki
- **Alarm**: Dogodki na osnovi časovnika
- **Animation End**: Animacija sprita končana

## Knjižnica akcij

### Premikanje
- `move_towards_point`: Premik proti točki
- `set_speed`: Nastavi hitrost
- `set_direction`: Nastavi smer
- `bounce`: Odbij se

### Instance
- `create_instance`: Ustvari novo instanco
- `destroy_instance`: Izbriši instanco
- `set_sprite`: Spremeni sprite

### Spremenljivke
- `set_variable`: Nastavi vrednost
- `test_variable`: Pogojno preverjanje

### Zvok
- `play_sound`: Predvajaj zvok
- `stop_sound`: Ustavi zvok
- `set_volume`: Spremeni glasnost

### Soba
- `goto_room`: Spremeni sobo
- `restart_room`: Ponovno zaženi sobo
- `next_room`: Naslednja soba

### Risanje
- `draw_sprite`: Nariši sprite
- `draw_text`: Prikaži besedilo
- `draw_rectangle`: Nariši pravokotnik

## Pogoji in nadzor toka

### Pogojne akcije
```
Če Spremenljivka == Vrednost
  Izvedi akcijo
Sicer
  Alternativna akcija
```

### Zanke
- Ponovi akcije
- Za vse instance

## Najboljše prakse

1. **Uporabite Step zmerno**: Samo ko je potrebno
2. **Optimizirajte trke**: Upoštevajte lastnost Solid
3. **Grupirajte dogodke**: Povezana logika skupaj
4. **Uporabite alarme**: Za časovno določene akcije

## Glej tudi

- [Urejevalnik objektov](Urejevalnik_Objektov_sl)
- [Vizualno programiranje](Vizualno_Programiranje_sl)
- [FAQ](FAQ_sl)
