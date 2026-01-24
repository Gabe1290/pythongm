# Celotna Referenca Akcij

*[Domov](Home_sl) | [Vodnik po Presetih](Preset-Guide_sl) | [Referenca Dogodkov](Event-Reference_sl)*

Ta stran dokumentira vse razpoložljive akcije v PyGameMaker. Akcije so ukazi, ki se izvršijo, ko se sprožijo dogodki.

## Kategorije Akcij

- [Akcije Gibanja](#akcije-gibanja)
- [Akcije Instance](#akcije-instance)
- [Akcije Točk, Življenj in Zdravja](#akcije-točk-življenj-in-zdravja)
- [Akcije Sobe](#akcije-sobe)
- [Akcije Časovnega Nadzora](#akcije-časovnega-nadzora)
- [Zvočne Akcije](#zvočne-akcije)
- [Akcije Risanja](#akcije-risanja)
- [Akcije Nadzora Toka](#akcije-nadzora-toka)
- [Izhodne Akcije](#izhodne-akcije)

---

## Akcije Gibanja

### Nastavi Horizontalno Hitrost
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_hspeed` |
| **Ikona** | ↔️ |
| **Preset** | Začetnik |

**Opis:** Nastavi hitrost horizontalnega gibanja.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 0 | Hitrost v pikslih/frame. Pozitivno=desno, Negativno=levo |

---

### Nastavi Vertikalno Hitrost
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_vspeed` |
| **Ikona** | ↕️ |
| **Preset** | Začetnik |

**Opis:** Nastavi hitrost vertikalnega gibanja.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 0 | Hitrost v pikslih/frame. Pozitivno=dol, Negativno=gor |

---

### Ustavi Gibanje
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `stop_movement` |
| **Ikona** | 🛑 |
| **Preset** | Začetnik |

**Opis:** Ustavi vse gibanje (nastavi hspeed in vspeed na 0).

**Parametri:** Brez

---

### Skoči na Pozicijo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `jump_to_position` |
| **Ikona** | 📍 |
| **Preset** | Začetnik |

**Opis:** Takoj se premakne na določeno pozicijo.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Število | 0 | Ciljna koordinata X |
| `y` | Število | 0 | Ciljna koordinata Y |

---

### Fiksno Gibanje
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `move_fixed` |
| **Ikona** | ➡️ |
| **Preset** | Napredni |

**Opis:** Premakne se v eno od 8 fiksnih smeri.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `directions` | Izbira | right | Smer(i) gibanja |
| `speed` | Število | 4 | Hitrost gibanja |

**Možnosti smeri:** left, right, up, down, up-left, up-right, down-left, down-right, stop

---

### Prosto Gibanje
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `move_free` |
| **Ikona** | 🧭 |
| **Preset** | Napredni |

**Opis:** Premakne se v katero koli smer (0-360 stopinj).

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `direction` | Število | 0 | Smer v stopinjah (0=desno, 90=gor) |
| `speed` | Število | 4 | Hitrost gibanja |

---

### Premakni se Proti
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `move_towards` |
| **Ikona** | 🎯 |
| **Preset** | Srednji |

**Opis:** Premakne se proti ciljni poziciji.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Izraz | 0 | Ciljni X (lahko uporablja izraze kot `other.x`) |
| `y` | Izraz | 0 | Ciljni Y |
| `speed` | Število | 4 | Hitrost gibanja |

---

### Nastavi Hitrost
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_speed` |
| **Ikona** | ⚡ |
| **Preset** | Napredni |

**Opis:** Nastavi velikost hitrosti (ohrani smer).

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `speed` | Število | 0 | Velikost hitrosti |

---

### Nastavi Smer
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_direction` |
| **Ikona** | 🧭 |
| **Preset** | Napredni |

**Opis:** Nastavi smer gibanja (ohrani hitrost).

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `direction` | Število | 0 | Smer v stopinjah |

---

### Obrni Horizontalno
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `reverse_horizontal` |
| **Ikona** | ↔️ |
| **Preset** | Napredni |

**Opis:** Obrne horizontalno smer (pomnoži hspeed z -1).

**Parametri:** Brez

---

### Obrni Vertikalno
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `reverse_vertical` |
| **Ikona** | ↕️ |
| **Preset** | Napredni |

**Opis:** Obrne vertikalno smer (pomnoži vspeed z -1).

**Parametri:** Brez

---

### Nastavi Gravitacijo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_gravity` |
| **Ikona** | ⬇️ |
| **Preset** | Platformer |

**Opis:** Uporabi gravitacijo na instanco.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `direction` | Število | 270 | Smer gravitacije (270=dol) |
| `gravity` | Število | 0.5 | Moč gravitacije |

---

### Nastavi Trenje
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_friction` |
| **Ikona** | 🛑 |
| **Preset** | Napredni |

**Opis:** Uporabi trenje (postopno upočasnjevanje).

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `friction` | Število | 0.1 | Količina trenja |

---

## Akcije Instance

### Uniči Instanco
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `destroy_instance` |
| **Ikona** | 💥 |
| **Preset** | Začetnik |

**Opis:** Odstrani instanco iz igre.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `target` | Izbira | self | `self` ali `other` (v dogodkih trčenja) |

---

### Ustvari Instanco
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `create_instance` |
| **Ikona** | ✨ |
| **Preset** | Začetnik |

**Opis:** Ustvari novo instanco objekta.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `object` | Objekt | - | Tip objekta za ustvarjanje |
| `x` | Število | 0 | Pozicija X |
| `y` | Število | 0 | Pozicija Y |

---

### Nastavi Sprite
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_sprite` |
| **Ikona** | 🖼️ |
| **Preset** | Napredni |

**Opis:** Spremeni sprite instance.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `sprite` | Sprite | - | Nov sprite |

---

## Akcije Točk, Življenj in Zdravja

### Nastavi Točke
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_score` |
| **Ikona** | 🏆 |
| **Preset** | Začetnik |

**Opis:** Nastavi ali spremeni točke.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 0 | Vrednost točk |
| `relative` | Logično | false | Če je res, doda k trenutnim točkam |

---

### Dodaj Točke (Bližnjica)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `add_score` |
| **Ikona** | ➕🏆 |
| **Preset** | Začetnik |

**Opis:** Doda točke k rezultatu.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 10 | Točke za dodajanje (negativno za odštevanje) |

---

### Nastavi Življenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_lives` |
| **Ikona** | ❤️ |
| **Preset** | Srednji |

**Opis:** Nastavi ali spremeni število življenj.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 3 | Vrednost življenj |
| `relative` | Logično | false | Če je res, doda k trenutnim življenjem |

**Opomba:** Sproži dogodek `no_more_lives`, ko doseže 0.

---

### Dodaj Življenja (Bližnjica)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `add_lives` |
| **Ikona** | ➕❤️ |
| **Preset** | Srednji |

**Opis:** Doda ali odstrani življenja.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 1 | Življenja za dodajanje (negativno za odštevanje) |

---

### Nastavi Zdravje
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_health` |
| **Ikona** | 💚 |
| **Preset** | Srednji |

**Opis:** Nastavi ali spremeni zdravje (0-100).

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 100 | Vrednost zdravja |
| `relative` | Logično | false | Če je res, doda k trenutnemu zdravju |

**Opomba:** Sproži dogodek `no_more_health`, ko doseže 0.

---

### Dodaj Zdravje (Bližnjica)
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `add_health` |
| **Ikona** | ➕💚 |
| **Preset** | Srednji |

**Opis:** Doda ali odstrani zdravje.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `value` | Število | 10 | Zdravje za dodajanje (negativno za škodo) |

---

### Nariši Točke
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_score` |
| **Ikona** | 🖼️🏆 |
| **Preset** | Začetnik |

**Opis:** Prikaže točke na zaslonu.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Število | 10 | Pozicija X |
| `y` | Število | 10 | Pozicija Y |
| `caption` | Niz | "Score: " | Besedilo pred točkami |

---

### Nariši Življenja
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_lives` |
| **Ikona** | 🖼️❤️ |
| **Preset** | Srednji |

**Opis:** Prikaže življenja na zaslonu.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Število | 10 | Pozicija X |
| `y` | Število | 30 | Pozicija Y |
| `sprite` | Sprite | - | Neobvezen sprite ikone življenja |

---

### Nariši Vrstico Zdravja
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_health_bar` |
| **Ikona** | 📊💚 |
| **Preset** | Srednji |

**Opis:** Nariše vrstico zdravja.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x1` | Število | 10 | Levi X |
| `y1` | Število | 50 | Zgornji Y |
| `x2` | Število | 110 | Desni X |
| `y2` | Število | 60 | Spodnji Y |
| `back_color` | Barva | gray | Barva ozadja |
| `bar_color` | Barva | green | Barva vrstice |

---

## Akcije Sobe

### Naslednja Soba
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `next_room` |
| **Ikona** | ➡️ |
| **Preset** | Začetnik |

**Opis:** Pojdi v naslednjo sobo v vrstnem redu sob.

**Parametri:** Brez

---

### Prejšnja Soba
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `previous_room` |
| **Ikona** | ⬅️ |
| **Preset** | Začetnik |

**Opis:** Pojdi v prejšnjo sobo v vrstnem redu sob.

**Parametri:** Brez

---

### Ponovno Zaženi Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `restart_room` |
| **Ikona** | 🔄 |
| **Preset** | Začetnik |

**Opis:** Ponovno zažene trenutno sobo.

**Parametri:** Brez

---

### Pojdi v Sobo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `goto_room` |
| **Ikona** | 🚪 |
| **Preset** | Začetnik |

**Opis:** Pojdi v določeno sobo.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `room` | Soba | - | Ciljna soba |

---

### Če Naslednja Soba Obstaja
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `if_next_room_exists` |
| **Ikona** | ❓➡️ |
| **Preset** | Začetnik |

**Opis:** Pogojno - izvede akcije samo če obstaja naslednja soba.

| Parameter | Tip | Opis |
|-----------|-----|------|
| `then_actions` | Seznam Akcij | Akcije če naslednja soba obstaja |
| `else_actions` | Seznam Akcij | Akcije če ni naslednje sobe |

---

### Če Prejšnja Soba Obstaja
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `if_previous_room_exists` |
| **Ikona** | ❓⬅️ |
| **Preset** | Začetnik |

**Opis:** Pogojno - izvede akcije samo če obstaja prejšnja soba.

| Parameter | Tip | Opis |
|-----------|-----|------|
| `then_actions` | Seznam Akcij | Akcije če prejšnja soba obstaja |
| `else_actions` | Seznam Akcij | Akcije če ni prejšnje sobe |

---

## Akcije Časovnega Nadzora

### Nastavi Alarm
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_alarm` |
| **Ikona** | ⏰ |
| **Preset** | Srednji |

**Opis:** Nastavi alarm, ki se sproži po zamiku.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `alarm` | Število | 0 | Številka alarma (0-11) |
| `steps` | Število | 60 | Koraki do sprožitve alarma |

**Opomba:** Pri 60 FPS, 60 korakov = 1 sekunda.

---

## Zvočne Akcije

### Predvajaj Zvok
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `play_sound` |
| **Ikona** | 🔊 |
| **Preset** | Srednji |

**Opis:** Predvaja zvočni učinek.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `sound` | Zvok | - | Zvočni vir |
| `loop` | Logično | false | Ponavljaj zvok v zanki |

---

### Predvajaj Glasbo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `play_music` |
| **Ikona** | 🎵 |
| **Preset** | Srednji |

**Opis:** Predvaja glasbo v ozadju.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `sound` | Zvok | - | Glasbeni vir |
| `loop` | Logično | true | Ponavljaj glasbo v zanki |

---

### Ustavi Glasbo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `stop_music` |
| **Ikona** | 🔇 |
| **Preset** | Srednji |

**Opis:** Ustavi vso predvajano glasbo.

**Parametri:** Brez

---

### Nastavi Glasnost
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_volume` |
| **Ikona** | 🔉 |
| **Preset** | Napredni |

**Opis:** Nastavi glasnost zvoka.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `volume` | Število | 1.0 | Raven glasnosti (0.0 do 1.0) |

---

## Akcije Risanja

### Nariši Besedilo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_text` |
| **Ikona** | 📝 |
| **Preset** | Napredni |

**Opis:** Nariše besedilo na zaslon.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Število | 0 | Pozicija X |
| `y` | Število | 0 | Pozicija Y |
| `text` | Niz | "" | Besedilo za risanje |
| `color` | Barva | white | Barva besedila |

---

### Nariši Pravokotnik
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_rectangle` |
| **Ikona** | ⬛ |
| **Preset** | Napredni |

**Opis:** Nariše pravokotnik.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x1` | Število | 0 | Levi X |
| `y1` | Število | 0 | Zgornji Y |
| `x2` | Število | 32 | Desni X |
| `y2` | Število | 32 | Spodnji Y |
| `color` | Barva | white | Barva polnila |
| `outline` | Logično | false | Samo obroba |

---

### Nariši Krog
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `draw_circle` |
| **Ikona** | ⚪ |
| **Preset** | Napredni |

**Opis:** Nariše krog.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `x` | Število | 0 | Središče X |
| `y` | Število | 0 | Središče Y |
| `radius` | Število | 16 | Polmer |
| `color` | Barva | white | Barva polnila |
| `outline` | Logično | false | Samo obroba |

---

### Nastavi Alfo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `set_alpha` |
| **Ikona** | 👻 |
| **Preset** | Napredni |

**Opis:** Nastavi prosojnost risanja.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `alpha` | Število | 1.0 | Prosojnost (0.0=nevidno, 1.0=neprosojno) |

---

## Akcije Nadzora Toka

### Če Trčenje Pri
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `if_collision_at` |
| **Ikona** | 🎯 |
| **Preset** | Napredni |

**Opis:** Preveri trčenje na poziciji.

| Parameter | Tip | Opis |
|-----------|-----|------|
| `x` | Izraz | Pozicija X za preverjanje |
| `y` | Izraz | Pozicija Y za preverjanje |
| `object_type` | Izbira | `any` ali `solid` |
| `then_actions` | Seznam Akcij | Če je trčenje najdeno |
| `else_actions` | Seznam Akcij | Če ni trčenja |

---

## Izhodne Akcije

### Prikaži Sporočilo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `show_message` |
| **Ikona** | 💬 |
| **Preset** | Začetnik |

**Opis:** Prikaže pojavno sporočilo.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `message` | Niz | "Hello!" | Besedilo sporočila |

**Opomba:** Igra se zaustavi med prikazom sporočila.

---

### Izvedi Kodo
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `execute_code` |
| **Ikona** | 💻 |
| **Preset** | Začetnik |

**Opis:** Izvede prilagojeno Python kodo.

| Parameter | Tip | Privzeto | Opis |
|-----------|-----|----------|------|
| `code` | Koda | "" | Python koda za izvajanje |

**Opozorilo:** Napredna funkcija. Uporabljajte previdno.

---

### Končaj Igro
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `end_game` |
| **Ikona** | 🚪 |
| **Preset** | Napredni |

**Opis:** Konča igro in zapre okno.

**Parametri:** Brez

---

### Ponovno Zaženi Igro
| Lastnost | Vrednost |
|----------|----------|
| **Ime** | `restart_game` |
| **Ikona** | 🔄 |
| **Preset** | Napredni |

**Opis:** Ponovno zažene igro od prve sobe.

**Parametri:** Brez

---

## Akcije po Presetu

| Preset | Število Akcij | Kategorije |
|--------|---------------|------------|
| **Začetnik** | 17 | Gibanje, Instanca, Točke, Soba, Izhod |
| **Srednji** | 29 | + Življenja, Zdravje, Zvok, Časovni Nadzor |
| **Napredni** | 40+ | + Risanje, Nadzor Toka, Igra |

---

## Glejte Tudi

- [Referenca Dogodkov](Event-Reference_sl) - Celoten seznam dogodkov
- [Preset za Začetnike](Beginner-Preset_sl) - Osnovne akcije za začetnike
- [Srednji Preset](Intermediate-Preset_sl) - Dodatne akcije
- [Dogodki in Akcije](Events-and-Actions_sl) - Pregled osnovnih konceptov
