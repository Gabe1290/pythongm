# Dogodki in akcije

> [English](Events-and-Actions) | [Français](Evenements_Actions_fr) | [Deutsch](Events_und_Aktionen_de) | [Italiano](Eventi_e_Azioni_it) | [Español](Eventos_y_Acciones_es) | [Português](Eventos_e_Acoes_pt) | [Slovenščina](Dogodki_in_Akcije_sl) | [Українська](Podii_ta_Dii_uk) | [Русский](Sobytiya_i_Deystviya_ru)

---

[Nazaj na zacetno stran](Home_sl)

Dogodki in akcije tvorijo srce igralne logike v pyGM.

## Koncept

### Dogodki
Dogodki so prozilci, ki se odzivajo na dolocene situacije:
- Zagon igre
- Pritisk tipke
- Trk
- Casovnik

### Akcije
Akcije so odzivi na dogodke:
- Premik
- Ustvarjanje/Unicenje
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
- **Miska**: Kliki in premikanje
- **Gamepad**: Vnos krmilnika

### Dogodki trkov
- Stik z drugimi objekti
- Stik s stenami
- Preverjanja obmocij

### Dogodki risanja
- **Draw**: Normalno risanje
- **Draw GUI**: Elementi vmesnika
- **Draw Begin/End**: Pred/Po risanju

### Ostali dogodki
- **Alarm**: Dogodki na osnovi casovnika
- **Animation End**: Animacija sprita koncana
- **User Events**: Uporabnisko definirani dogodki

## Knjiznica akcij

### Premikanje
- `move_towards`: Premik proti tocki
- `set_speed`: Nastavi hitrost
- `set_direction`: Nastavi smer
- `bounce`: Odbij se

### Instance
- `instance_create`: Ustvari novo instanco
- `instance_destroy`: Izbrisi instanco
- `change_sprite`: Spremeni sprite

### Spremenljivke
- `set_variable`: Nastavi vrednost
- `add_to_variable`: Dodaj vrednost
- `if_variable`: Pogojno preverjanje

### Zvok
- `play_sound`: Predvajaj zvok
- `stop_sound`: Ustavi zvok
- `set_volume`: Spremeni glasnost

### Soba
- `goto_room`: Spremeni sobo
- `restart_room`: Ponovno zazeni sobo
- `goto_next_room`: Naslednja soba

### Risanje
- `draw_sprite`: Narisi sprite
- `draw_text`: Prikazi besedilo
- `draw_rectangle`: Narisi pravokotnik

## Pogoji in nadzor toka

### Pogojne akcije
```
Ce Spremenljivka == Vrednost
  Izvedi akcijo
Sicer
  Alternativna akcija
```

### Zanke
- Ponovi akcije
- Za vse instance

## Najboljse prakse

1. **Uporabite Step zmerno**: Samo ko je potrebno
2. **Optimizirajte trke**: Upostevajte lastnost Solid
3. **Grupirajte dogodke**: Povezana logika skupaj
4. **Uporabite alarme**: Za casovno dolocene akcije

## Glej tudi

- [Urejevalnik objektov](Urejevalnik_Objektov_sl)
- [Vizualno programiranje](Vizualno_Programiranje_sl)
- [FAQ](FAQ_sl)
