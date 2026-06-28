# Vizualno programiranje

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Nazaj na zacetno stran](Home_sl)

pyGM ponuja sistem vizualnega programiranja za enostaven razvoj iger brez kode.

## Pregled

Z vizualnim programiranjem lahko:
- Ustvarjate igralno logiko s povleci in spusti
- Povezujete bloke za kompleksna obnasanja
- Razvijate brez znanja programiranja

## Urejevalnik Blockly

### Vmesnik
1. **Paleta blokov**: Razpolozljivi bloki po kategorijah
2. **Delovno podrocje**: Tukaj povezujete bloke
3. **Orodna vrstica**: Shrani, Nalozi, Izbrisi

### Kategorije blokov
- **Logika**: Ce/Potem, primerjave, logicne vrednosti
- **Zanke**: Ponavljanja
- **Matematika**: Izracuni
- **Besedilo**: Operacije z besedilom
- **Spremenljivke**: Shranjevanje vrednosti
- **Funkcije**: Ponovno uporabni bloki
- **Igra**: Akcije specificne za pyGM

## Uporaba blokov

### Dodajanje bloka
1. Kliknite na kategorijo
2. Povlecite blok na delovno podrocje
3. Povezite ga z drugimi bloki

### Povezovanje blokov
- Bloki se samodejno zaskocijo
- Pazite na ujemajocse oblike
- Gnezdenje blokov je mogoce

### Nastavitev bloka
- Izpolnite vnosna polja
- Izberite moznosti iz spustnega menija
- Vstavite podbloke

## Primeri

### Preprosto premikanje
```
Ko [puscica desno] pritisnjena
  Nastavi x na (x + 5)
```

### Pogojna logika
```
Ce <Zivljenja <= 0> potem
  Prikazi sporocilo "Game Over"
  Pojdi v sobo [rm_gameover]
```

### Zanka
```
Ponovi [10] krat
  Ustvari instanco [obj_kovanec] na polozaju (Nakljucno 0-800, Nakljucno 0-600)
```

## Igralni bloki

### Premikanje
- **Premakni na**: Premik na polozaj
- **Nastavi hitrost**: Hitrost premikanja
- **Nastavi smer**: Smer premikanja

### Instance
- **Ustvari instanco**: Generiraj nov objekt
- **Unici**: Izbrisi objekt
- **Za vse**: Vse instance vrste

### Spremenljivke
- **Nastavi spremenljivko**: Shrani vrednost
- **Spremeni spremenljivko**: Spremeni vrednost
- **Pridobi spremenljivko**: Pridobi vrednost

### Dogodki
- **Ko tipka**: Vnos s tipkovnice
- **Ko trk**: Stik objektov
- **Ko casovnik**: Na osnovi casa

## Nasveti

1. **Zacnite majhno**: Najprej preprosti projekti
2. **Testirajte**: Redno zaganjajte
3. **Organizirajte**: Logicno grupirajte bloke
4. **Komentarji**: Dodajajte opombe

## Od blokov do kode

Urejevalnik Blockly lahko tudi generira kodo:
1. Vizualno se naucite konceptov programiranja
2. Oglejte si generirano kodo
3. Kasneje preklopite na Python

## Glej tudi

- [Ustvarite svojo prvo igro](Prva_Igra_sl)
- [Dogodki in akcije](Dogodki_in_Akcije_sl)
- [FAQ](FAQ_sl)
