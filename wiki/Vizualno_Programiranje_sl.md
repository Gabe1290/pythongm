# Vizualno programiranje

> [English](Visual-Programming) | [Français](Programmation_Visuelle_fr) | [Deutsch](Visuelle_Programmierung_de) | [Italiano](Programmazione_Visuale_it) | [Español](Programacion_Visual_es) | [Português](Programacao_Visual_pt) | [Slovenščina](Vizualno_Programiranje_sl) | [Українська](Vizualne_Prohramuvannya_uk) | [Русский](Vizualnoe_Programmirovanie_ru)

---

[Nazaj na začetno stran](Home_sl)

pyGM ponuja sistem vizualnega programiranja za enostaven razvoj iger brez kode.

## Pregled

Z vizualnim programiranjem lahko:
- Ustvarjate igralno logiko s povleci in spusti
- Povezujete bloke za kompleksna obnašanja
- Razvijate brez znanja programiranja

## Urejevalnik Blockly

### Vmesnik
1. **Paleta blokov**: Razpoložljivi bloki po kategorijah
2. **Delovno področje**: Tukaj povezujete bloke
3. **Orodna vrstica**: Shrani, Naloži, Izbriši

### Kategorije blokov
- **Logika**: Če/Potem, primerjave, logične vrednosti
- **Zanke**: Ponavljanja
- **Matematika**: Izračuni
- **Besedilo**: Operacije z besedilom
- **Spremenljivke**: Shranjevanje vrednosti
- **Funkcije**: Ponovno uporabni bloki
- **Igra**: Akcije specifične za pyGM

## Uporaba blokov

### Dodajanje bloka
1. Kliknite na kategorijo
2. Povlecite blok na delovno področje
3. Povežite ga z drugimi bloki

### Povezovanje blokov
- Bloki se samodejno zaskočijo
- Pazite na ujemajoče oblike
- Gnezdenje blokov je mogoče

### Nastavitev bloka
- Izpolnite vnosna polja
- Izberite možnosti iz spustnega menija
- Vstavite podbloke

## Primeri

### Preprosto premikanje
```
Ko [puščica desno] pritisnjena
  Nastavi x na (x + 5)
```

### Pogojna logika
```
Če <Življenja <= 0> potem
  Prikaži sporočilo "Game Over"
  Pojdi v sobo [rm_gameover]
```

### Zanka
```
Ponovi [10] krat
  Ustvari instanco [obj_kovanec] na položaju (Naključno 0-800, Naključno 0-600)
```

## Igralni bloki

### Premikanje
- **Premakni na**: Premik na položaj
- **Nastavi hitrost**: Hitrost premikanja
- **Nastavi smer**: Smer premikanja

### Instance
- **Ustvari instanco**: Generiraj nov objekt
- **Uniči**: Izbriši objekt
- **Za vse**: Vse instance vrste

### Spremenljivke
- **Nastavi spremenljivko**: Shrani vrednost
- **Spremeni spremenljivko**: Spremeni vrednost
- **Pridobi spremenljivko**: Pridobi vrednost

### Dogodki
- **Ko tipka**: Vnos s tipkovnice
- **Ko trk**: Stik objektov
- **Ko časovnik**: Na osnovi časa

## Nasveti

1. **Začnite majhno**: Najprej preprosti projekti
2. **Testirajte**: Redno zaganjajte
3. **Organizirajte**: Logično grupirajte bloke
4. **Komentarji**: Dodajajte opombe

## Od blokov do kode

Urejevalnik Blockly lahko tudi generira kodo:
1. Vizualno se naučite konceptov programiranja
2. Oglejte si generirano kodo
3. Kasneje preklopite na Python

## Glej tudi

- [Ustvarite svojo prvo igro](Prva_Igra_sl)
- [Dogodki in akcije](Dogodki_in_Akcije_sl)
- [FAQ](FAQ_sl)
