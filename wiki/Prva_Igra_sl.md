# Ustvarite svojo prvo igro

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

[Nazaj na zacetno stran](Home_sl)

V tem vodichu boste ustvarili preprosto igro za ucenje osnov pyGM.

## Pregled

Ustvarili bomo preprosto igro z:
- Igralnim likom, ki se lahko premika
- Zbirljivim objektom
- Sistemom tock

## Korak 1: Ustvarite nov projekt

1. Zazenite pyGM
2. Izberite "Nov projekt"
3. Vnesite ime projekta
4. Izberite lokacijo za shranjevanje

## Korak 2: Ustvarite sprite

### Sprite igralca
1. Desni klik na "Spriti" v drevesu virov
2. Izberite "Nov sprite"
3. Uporabite vgrajeni urejevalnik ali uvozite sliko
4. Poimenujte ga "spr_igralec"

### Sprite zbirljivega objekta
1. Ustvarite se en sprite
2. Poimenujte ga "spr_kovanec"

## Korak 3: Ustvarite objekte

### Objekt igralca
1. Desni klik na "Objekti"
2. Izberite "Nov objekt"
3. Poimenujte ga "obj_igralec"
4. Dodelite "spr_igralec" kot sprite

### Dodajte premikanje
1. Dodajte dogodek "Pritisk tipke"
2. Uporabite akcije za premikanje:
   - Puscica gor: Premik navzgor
   - Puscica dol: Premik navzdol
   - Puscica levo: Premik levo
   - Puscica desno: Premik desno

### Objekt kovanca
1. Ustvarite "obj_kovanec"
2. Dodelite "spr_kovanec"
3. Dodajte dogodek trka z igralcem
4. Akcija: Unicite instanco in dodajte tocke

## Korak 4: Ustvarite sobo

1. Desni klik na "Sobe"
2. Izberite "Nova soba"
3. Poimenujte jo "rm_nivo1"
4. Postavite objekte:
   - Enega igralca
   - Vec kovancev

## Korak 5: Testirajte igro

1. Kliknite "Zazeni igro" ali pritisnite F5
2. Testirajte premikanje
3. Zbirajte kovance

## Ideje za razsiritev

- Dodajte ovire
- Implementirajte casovni sistem
- Ustvarite razlicne nivoje
- Dodajte zvocne ucinke

## Naslednji koraki

- [Poglobite se v dogodke in akcije](Dogodki_in_Akcije_sl)
- [Naucite se vizualnega programiranja](Vizualno_Programiranje_sl)
- [Izvoz iger](Izvoz_Iger_sl)
