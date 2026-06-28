# Urejevalnik objektov

> [English](Object-Editor) | [Français](Editeur_Objets_fr) | [Deutsch](Objekt_Editor_de) | [Italiano](Editor_Oggetti_it) | [Español](Editor_Objetos_es) | [Português](Editor_Objetos_pt) | [Slovenščina](Urejevalnik_Objektov_sl) | [Українська](Redaktor_Obiektiv_uk) | [Русский](Redaktor_Obektov_ru)

---

[Nazaj na zacetno stran](Home_sl)

Urejevalnik objektov je osrednje orodje za dolocanje obnasanja igralnih elementov.

## Pregled

Objekti so gradniki vase igre. Dolocajo:
- Videz (Sprite)
- Obnasanje (Dogodki in akcije)
- Fizikalne lastnosti
- Interakcije

## Vmesnik urejevalnika

### Glavna podrocja
1. **Seznam objektov**: Vsi objekti v projektu
2. **Plosca lastnosti**: Osnovne nastavitve
3. **Seznam dogodkov**: Definirani dogodki
4. **Urejevalnik akcij**: Akcije za dogodke

## Lastnosti objekta

### Splosne
- **Ime**: Edinstveni identifikator (npr. obj_igralec)
- **Sprite**: Dodeljena grafika
- **Viden**: Ali se objekt izrisuje
- **Trajen**: Prezivi menjave sob

### Fizika
- **Trden**: Trci z drugimi objekti
- **Globina**: Vrstni red risanja
- **Nadrejeni objekt**: Dedovanje lastnosti

## Delo z dogodki

### Dodajanje dogodka
1. Kliknite "Dodaj dogodek"
2. Izberite vrsto dogodka
3. Dodajte akcije

### Vrste dogodkov
- **Create**: Ob ustvarjanju instance
- **Step**: Vsak okvir
- **Draw**: Za risanje
- **Tipkovnica**: Vnos s tipkovnice
- **Miska**: Interakcije z misko
- **Trk**: Ob dotiku z drugimi objekti

## Uporaba akcij

### Dodajanje akcij
1. Izberite dogodek
2. Povlecite akcije iz knjiznice
3. Nastavite parametre

### Pogoste akcije
- Premik v smeri
- Nastavi spremenljivko
- Ustvari/unici instanco
- Predvajaj zvok
- Menjaj sobo

## Najboljse prakse

1. **Jasna poimenovanja**: Uporabite predpone kot "obj_"
2. **Modularnost**: Majhni, ponovno uporabni objekti
3. **Uporabite dedovanje**: Nadrejeni objekti za skupno obnasanje
4. **Dokumentacija**: Komentarji v kompleksnih dogodkih

## Glej tudi

- [Dogodki in akcije](Dogodki_in_Akcije_sl)
- [Vizualno programiranje](Vizualno_Programiranje_sl)
- [Urejevalnik sob](Urejevalnik_Sob_sl)
