#!/usr/bin/env python3
"""Generate wiki/Beginner-Preset[_<lang>].md and Intermediate-Preset[_<lang>].md
from the live Blockly preset configs (config/blockly_config.py's PRESETS registry).

The hand-written pages had drifted badly from the code — they described a
"Beginner: 4 events, 17 actions" preset that hadn't matched
BlocklyConfig.get_beginner() in a long time (missing whole events like Draw/
Alarm/No More Lives and a dozen-plus actions like set_gravity/bounce/
reverse_horizontal/test_variable). The preset genuinely restricts BOTH the
Blockly visual-block palette AND the structured Events/Actions panel's "Add
Event"/"Add Action" menus (editors/object_editor/object_events_panel.py's
show_add_event_menu()/get_actions_by_category() calls both take the current
project's blockly_config and filter on it) — every wiki tutorial is written
for the structured panel, so this list is exactly what a project on this
preset shows there too, not a Blockly-only concern. Which preset a project
uses: `Preferences > IDE Edition` sets the default for *new* projects
(default edition is Beginner -> this preset), `Tools > Configure Action
Blocks...` changes the *current* project's preset at any time.

This regenerates both pages straight from get_available_events()/
get_actions_by_category() — the SAME functions the app itself calls to
filter both the Blockly picker and the structured panel — so they can never
silently drift again: re-run this whenever a preset's enable_block() calls
change.

    py -3.12 tools/gen_preset_docs.py            # English
    py -3.12 tools/gen_preset_docs.py fr         # + French

Localized editions reuse tools/action_ref_i18n.py's LANGS table (the same
one Full-Action-Reference.md's generator uses) for action/category names,
plus its "events" sub-table for event names. Anything missing falls back to
English and is reported at the end of the run.
"""
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from events.plugin_loader import load_all_plugins  # noqa: E402

load_all_plugins()
from config.blockly_config import PRESETS  # noqa: E402
from events.event_types import get_available_events  # noqa: E402
from events.action_types import get_actions_by_category  # noqa: E402
from tools.action_ref_i18n import LANGS  # noqa: E402

ACTION_CATEGORY_ORDER = [
    "Movement", "Grid", "Instance", "Score", "Timing", "Room", "Audio",
    "Game", "Control", "Views", "3D View",
]
EVENT_CATEGORY_ORDER = ["Object", "Input", "Collision", "Step", "Timing", "Drawing", "Room", "Game", "Other"]

PAGE_CHROME = {
    "en": {
        "beginner_title": "Beginner Preset",
        "intermediate_title": "Intermediate Preset",
        "nav": "*[Home](Home) | [Preset Guide](Preset-Guide) | {other_link}*",
        "autogen": "> **Auto-generated** from `config/blockly_config.py`'s "
                   "`get_{preset}()` by `tools/gen_preset_docs.py` — do not edit by "
                   "hand; re-run the generator after changing the preset.",
        "scope_note": "> **What this actually restricts:** this preset filters BOTH "
                       "the Blockly visual-block palette *and* the structured "
                       "Events/Actions panel's \"Add Event\"/\"Add Action\" menus — "
                       "whichever editor you use, only the events/actions listed "
                       "below appear. Which preset a *project* uses is set two ways: "
                       "**`Preferences > IDE Edition`** picks the default for *new* "
                       "projects (Beginner edition -> this preset; existing projects "
                       "are never changed by switching edition), and "
                       "**`Tools > Configure Action Blocks...`** changes the preset "
                       "for the *currently open* project at any time. The IDE's "
                       "default edition is Beginner, so a fresh install's new "
                       "projects start on this exact list.",
        "overview": "Overview",
        "overview_text": "This preset enables **{n_events}** event types and "
                          "**{n_actions}** action types.",
        "events_h": "Events",
        "actions_h": "Actions",
        "c_event": "Event", "c_block": "Block Name", "c_category": "Category", "c_desc": "Description",
        "c_action": "Action", "c_params": "Parameters",
        "none": "—",
        "see_also": "See Also",
        "sa_preset": "- [Preset Guide](Preset-Guide) — what presets are and how to change one",
        "sa_events": "- [Event Reference](Event-Reference) — full description of every event",
        "sa_actions": "- [Full Action Reference](Full-Action-Reference) — full parameter details for every action",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "the next tier up",
        "beginner_desc": "the tier below this one",
    },
    "de": {
        "beginner_title": "Anfänger-Preset",
        "intermediate_title": "Fortgeschrittenen-Preset",
        "nav": "*[Startseite](Home_de) | [Preset-Leitfaden](Preset-Guide_de) | {other_link}*",
        "autogen": "> **Automatisch generiert** aus `get_{preset}()` in "
                   "`config/blockly_config.py` von `tools/gen_preset_docs.py` — "
                   "nicht von Hand bearbeiten; nach Änderungen am Preset den "
                   "Generator erneut ausführen.",
        "scope_note": "> **Was dieses Preset tatsächlich einschränkt:** Dieses "
                       "Preset filtert SOWOHL die visuelle Blockly-Blockpalette "
                       "ALS AUCH die Menüs „Ereignis hinzufügen“/„Aktion "
                       "hinzufügen“ des strukturierten "
                       "Ereignisse/Aktionen-Panels — unabhängig vom verwendeten "
                       "Editor erscheinen nur die unten aufgeführten Ereignisse/"
                       "Aktionen. Das Preset eines *Projekts* wird auf zwei Arten "
                       "festgelegt: **`Einstellungen > IDE Edition`** legt den "
                       "Standard für *neue* Projekte fest (Edition Anfänger -> "
                       "dieses Preset; bestehende Projekte werden durch einen "
                       "Editionswechsel nie verändert), und **`Werkzeuge > "
                       "Aktionsblöcke konfigurieren...`** ändert das Preset des "
                       "*aktuell geöffneten* Projekts jederzeit. Die "
                       "Standard-Edition der IDE ist Anfänger, daher starten "
                       "neue Projekte einer Neuinstallation genau auf dieser Liste.",
        "overview": "Übersicht",
        "overview_text": "Dieses Preset aktiviert **{n_events}** Ereignistypen und "
                          "**{n_actions}** Aktionstypen.",
        "events_h": "Ereignisse",
        "actions_h": "Aktionen",
        "c_event": "Ereignis", "c_block": "Blockname", "c_category": "Kategorie", "c_desc": "Beschreibung",
        "c_action": "Aktion", "c_params": "Parameter",
        "none": "—",
        "see_also": "Siehe auch",
        "sa_preset": "- [Preset-Leitfaden](Preset-Guide_de) — was Presets sind und wie man sie ändert",
        "sa_events": "- [Ereignisreferenz](Event-Reference_de) — vollständige Beschreibung jedes Ereignisses",
        "sa_actions": "- [Vollständige Aktionsreferenz](Full-Action-Reference_de) — vollständige Parameterdetails für jede Aktion",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "die nächsthöhere Stufe",
        "beginner_desc": "die Stufe darunter",
    },
    "it": {
        "beginner_title": "Preset Principiante",
        "intermediate_title": "Preset Intermedio",
        "nav": "*[Home](Home_it) | [Guida ai Preset](Preset-Guide_it) | {other_link}*",
        "autogen": "> **Generato automaticamente** da `get_{preset}()` in "
                   "`config/blockly_config.py` da `tools/gen_preset_docs.py` — "
                   "non modificare a mano; rilancia il generatore dopo aver "
                   "cambiato il preset.",
        "scope_note": "> **Cosa restringe davvero questo preset:** questo "
                       "preset filtra SIA la tavolozza di blocchi visivi "
                       "Blockly SIA i menu \"Aggiungi Evento\"/\"Aggiungi "
                       "Azione\" del pannello strutturato Eventi/Azioni — "
                       "qualunque editor tu usi, appaiono solo gli eventi/le "
                       "azioni elencati qui sotto. Il preset di un *progetto* "
                       "si imposta in due modi: **`Preferenze > IDE Edition`** "
                       "sceglie il predefinito per i *nuovi* progetti "
                       "(edizione Principiante -> questo preset; i progetti "
                       "esistenti non vengono mai modificati cambiando "
                       "edizione), e **`Strumenti > Configura blocchi "
                       "azione...`** cambia il preset del progetto "
                       "*attualmente aperto* in qualsiasi momento. L'edizione "
                       "predefinita dell'IDE è Principiante, quindi i nuovi "
                       "progetti di un'installazione pulita partono esattamente "
                       "su questa lista.",
        "overview": "Panoramica",
        "overview_text": "Questo preset abilita **{n_events}** tipi di eventi e "
                          "**{n_actions}** tipi di azioni.",
        "events_h": "Eventi",
        "actions_h": "Azioni",
        "c_event": "Evento", "c_block": "Nome Blocco", "c_category": "Categoria", "c_desc": "Descrizione",
        "c_action": "Azione", "c_params": "Parametri",
        "none": "—",
        "see_also": "Vedi Anche",
        "sa_preset": "- [Guida ai Preset](Preset-Guide_it) — cosa sono i preset e come cambiarli",
        "sa_events": "- [Riferimento Eventi](Event-Reference_it) — descrizione completa di ogni evento",
        "sa_actions": "- [Riferimento Completo delle Azioni](Full-Action-Reference_it) — dettagli completi dei parametri per ogni azione",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "il livello superiore",
        "beginner_desc": "il livello sotto questo",
    },
    "es": {
        "beginner_title": "Preajuste Principiante",
        "intermediate_title": "Preajuste Intermedio",
        "nav": "*[Inicio](Home_es) | [Guía de Preajustes](Preset-Guide_es) | {other_link}*",
        "autogen": "> **Generado automáticamente** a partir de `get_{preset}()` en "
                   "`config/blockly_config.py` por `tools/gen_preset_docs.py` — "
                   "no editar a mano; vuelve a ejecutar el generador después de "
                   "cambiar el preajuste.",
        "scope_note": "> **Qué restringe realmente este preajuste:** este "
                       "preajuste filtra TANTO la paleta de bloques visuales "
                       "Blockly COMO los menús \"Añadir Evento\"/\"Añadir "
                       "Acción\" del panel estructurado Eventos/Acciones — "
                       "sea cual sea el editor que uses, solo aparecen los "
                       "eventos/acciones listados abajo. El preajuste de un "
                       "*proyecto* se define de dos formas: "
                       "**`Preferencias > IDE Edition`** elige el "
                       "predeterminado para los proyectos *nuevos* (edición "
                       "Principiante -> este preajuste; los proyectos "
                       "existentes nunca cambian al cambiar de edición), y "
                       "**`Herramientas > Configurar bloques de acción...`** "
                       "cambia el preajuste del proyecto *actualmente "
                       "abierto* en cualquier momento. La edición "
                       "predeterminada del IDE es Principiante, así que los "
                       "proyectos nuevos de una instalación limpia empiezan "
                       "exactamente en esta lista.",
        "overview": "Resumen",
        "overview_text": "Este preajuste habilita **{n_events}** tipos de eventos y "
                          "**{n_actions}** tipos de acciones.",
        "events_h": "Eventos",
        "actions_h": "Acciones",
        "c_event": "Evento", "c_block": "Nombre del Bloque", "c_category": "Categoría", "c_desc": "Descripción",
        "c_action": "Acción", "c_params": "Parámetros",
        "none": "—",
        "see_also": "Ver También",
        "sa_preset": "- [Guía de Preajustes](Preset-Guide_es) — qué son los preajustes y cómo cambiarlos",
        "sa_events": "- [Referencia de Eventos](Event-Reference_es) — descripción completa de cada evento",
        "sa_actions": "- [Referencia Completa de Acciones](Full-Action-Reference_es) — detalles completos de los parámetros de cada acción",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "el siguiente nivel",
        "beginner_desc": "el nivel por debajo de este",
    },
    "pt": {
        "beginner_title": "Preset Iniciante",
        "intermediate_title": "Preset Intermediário",
        "nav": "*[Início](Home_pt) | [Guia de Presets](Preset-Guide_pt) | {other_link}*",
        "autogen": "> **Gerado automaticamente** a partir de `get_{preset}()` em "
                   "`config/blockly_config.py` por `tools/gen_preset_docs.py` — "
                   "não edite manualmente; execute o gerador novamente após "
                   "alterar o preset.",
        "scope_note": "> **O que este preset realmente restringe:** este "
                       "preset filtra TANTO a paleta de blocos visuais Blockly "
                       "QUANTO os menus \"Adicionar Evento\"/\"Adicionar Ação\" "
                       "do painel estruturado Eventos/Ações — qualquer editor "
                       "que você use, só aparecem os eventos/ações listados "
                       "abaixo. O preset de um *projeto* é definido de duas "
                       "formas: **`Preferências > IDE Edition`** escolhe o "
                       "padrão para *novos* projetos (edição Iniciante -> "
                       "este preset; projetos existentes nunca são alterados "
                       "ao trocar de edição), e **`Ferramentas > Configurar "
                       "Blocos de Ação...`** altera o preset do projeto "
                       "*atualmente aberto* a qualquer momento. A edição "
                       "padrão do IDE é Iniciante, então novos projetos de "
                       "uma instalação limpa começam exatamente nesta lista.",
        "overview": "Visão Geral",
        "overview_text": "Este preset habilita **{n_events}** tipos de eventos e "
                          "**{n_actions}** tipos de ações.",
        "events_h": "Eventos",
        "actions_h": "Ações",
        "c_event": "Evento", "c_block": "Nome do Bloco", "c_category": "Categoria", "c_desc": "Descrição",
        "c_action": "Ação", "c_params": "Parâmetros",
        "none": "—",
        "see_also": "Veja Também",
        "sa_preset": "- [Guia de Presets](Preset-Guide_pt) — o que são presets e como alterar um",
        "sa_events": "- [Referência de Eventos](Event-Reference_pt) — descrição completa de cada evento",
        "sa_actions": "- [Referência Completa de Ações](Full-Action-Reference_pt) — detalhes completos de parâmetros de cada ação",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "o próximo nível",
        "beginner_desc": "o nível abaixo deste",
    },
    "sl": {
        "beginner_title": "Preset za Začetnike",
        "intermediate_title": "Vmesni Preset",
        "nav": "*[Domov](Home_sl) | [Vodnik po Prednastavitvah](Preset-Guide_sl) | {other_link}*",
        "autogen": "> **Samodejno ustvarjeno** iz `get_{preset}()` v "
                   "`config/blockly_config.py` s `tools/gen_preset_docs.py` — "
                   "ne urejajte ročno; po spremembi presetov znova zaženite "
                   "generator.",
        "scope_note": "> **Kaj ta preset dejansko omejuje:** ta preset filtrira "
                       "TAKO vizualno paleto blokov Blockly KOT menija "
                       "\"Dodaj dogodek\"/\"Dodaj dejanje\" v strukturirani "
                       "plošči Dogodki/Dejanja — ne glede na to, kateri "
                       "urejevalnik uporabljate, se prikažejo samo spodaj "
                       "navedeni dogodki/dejanja. Preset *projekta* je "
                       "nastavljen na dva načina: **`Nastavitve > IDE "
                       "Edition`** izbere privzeto vrednost za *nove* "
                       "projekte (izdaja Začetnik -> ta preset; obstoječi "
                       "projekti se z zamenjavo izdaje nikoli ne spremenijo), "
                       "in **`Orodja > Nastavi akcijske bloke...`** kadar "
                       "koli spremeni preset *trenutno odprtega* projekta. "
                       "Privzeta izdaja IDE-ja je Začetnik, zato se novi "
                       "projekti sveže namestitve začnejo prav na tem seznamu.",
        "overview": "Pregled",
        "overview_text": "Ta preset omogoča **{n_events}** vrst dogodkov in "
                          "**{n_actions}** vrst dejanj.",
        "events_h": "Dogodki",
        "actions_h": "Dejanja",
        "c_event": "Dogodek", "c_block": "Ime Bloka", "c_category": "Kategorija", "c_desc": "Opis",
        "c_action": "Dejanje", "c_params": "Parametri",
        "none": "—",
        "see_also": "Glej Tudi",
        "sa_preset": "- [Vodnik po Prednastavitvah](Preset-Guide_sl) — kaj so preseti in kako jih spremeniti",
        "sa_events": "- [Referenca Dogodkov](Event-Reference_sl) — popoln opis vsakega dogodka",
        "sa_actions": "- [Popolna Referenca Dejanj](Full-Action-Reference_sl) — popolni podatki parametrov za vsako dejanje",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "naslednja stopnja",
        "beginner_desc": "stopnja pod to",
    },
    "fr": {
        "beginner_title": "Préréglage Débutant",
        "intermediate_title": "Préréglage Intermédiaire",
        "nav": "*[Accueil](Home_fr) | [Guide des Préréglages](Preset-Guide_fr) | {other_link}*",
        "autogen": "> **Généré automatiquement** à partir de `get_{preset}()` dans "
                   "`config/blockly_config.py` par `tools/gen_preset_docs.py` — ne "
                   "pas modifier à la main ; relancez le générateur après avoir changé "
                   "le préréglage.",
        "scope_note": "> **Ce que ce préréglage restreint réellement :** ce préréglage "
                       "filtre À LA FOIS la palette de blocs visuels Blockly ET les "
                       "menus « Ajouter un événement »/« Ajouter une action » du "
                       "panneau structuré — quel que soit l'éditeur utilisé, seuls "
                       "les événements/actions listés ci-dessous apparaissent. Le "
                       "préréglage d'un *projet* se règle de deux façons : "
                       "**`Préférences > Édition de l'IDE`** choisit le préréglage "
                       "par défaut des *nouveaux* projets (édition Débutant -> ce "
                       "préréglage ; les projets existants ne sont jamais modifiés en "
                       "changeant l'édition), et **`Outils > Configurer les blocs "
                       "d'action...`** change le préréglage du projet *actuellement "
                       "ouvert* à tout moment. L'édition par défaut de l'IDE est "
                       "Débutant, donc les nouveaux projets d'une installation "
                       "fraîche démarrent exactement sur cette liste.",
        "overview": "Aperçu",
        "overview_text": "Ce préréglage active **{n_events}** types d'événements et "
                          "**{n_actions}** types d'actions.",
        "events_h": "Événements",
        "actions_h": "Actions",
        "c_event": "Événement", "c_block": "Nom du bloc", "c_category": "Catégorie", "c_desc": "Description",
        "c_action": "Action", "c_params": "Paramètres",
        "none": "—",
        "see_also": "Voir aussi",
        "sa_preset": "- [Guide des Préréglages](Preset-Guide_fr) — ce que sont les préréglages et comment en changer",
        "sa_events": "- [Référence des Événements](Event-Reference_fr) — description complète de chaque événement",
        "sa_actions": "- [Référence Complète des Actions](Full-Action-Reference_fr) — détails complets des paramètres de chaque action",
        "sa_other": "- [{other_title}]({other_link}) — {other_desc}",
        "intermediate_desc": "le niveau supérieur",
        "beginner_desc": "le niveau en dessous de celui-ci",
    },
}


def event_desc(ev, lang: str, missing: set) -> str:
    en = ev.description or ""
    if lang == "en" or not en:
        return en
    entry = LANGS.get(lang, {}).get("events", {}).get(ev.name)
    if not entry or not entry.get("desc"):
        missing.add(f"event.desc:{ev.name}")
        return en
    return entry["desc"]


def category_label(cat: str, lang: str, missing: set) -> str:
    if lang == "en":
        return cat
    t = LANGS.get(lang, {}).get("categories", {}).get(cat)
    if t is None:
        missing.add(f"category:{cat}")
        return cat
    return t


def action_display(a, lang: str, missing: set) -> str:
    en = a.display_name or a.name
    if lang == "en":
        return en
    entry = LANGS.get(lang, {}).get("actions", {}).get(a.name)
    if not entry or not entry.get("display"):
        missing.add(f"action.display:{a.name}")
        return en
    return entry["display"]


def param_summary(a) -> str:
    params = list(getattr(a, "parameters", []) or [])
    if not params:
        return "—"
    return ", ".join(f"`{p.name}`" for p in params)


def build(preset_key: str, lang: str) -> tuple[str, set]:
    chrome = PAGE_CHROME.get(lang, PAGE_CHROME["en"])
    missing = set()
    config = PRESETS[preset_key]

    events = get_available_events(config)
    events = [e for e in events if not e.name.startswith("thymio_")]
    actions_by_cat = get_actions_by_category(config)
    n_actions = sum(len(v) for v in actions_by_cat.values())

    other_key = "intermediate" if preset_key == "beginner" else "beginner"
    other_link = "Intermediate-Preset" if preset_key == "beginner" else "Beginner-Preset"
    if lang != "en":
        other_link += f"_{lang}"
    other_title = chrome[f"{other_key}_title"]
    other_desc = chrome[f"{other_key}_desc"]

    out = [
        f"# {chrome[f'{preset_key}_title']}",
        "",
        chrome["nav"].format(other_link=f"[{other_title}]({other_link})"),
        "",
        chrome["autogen"].format(preset=preset_key),
        "",
        chrome["scope_note"],
        "",
        f"## {chrome['overview']}",
        "",
        chrome["overview_text"].format(n_events=len(events), n_actions=n_actions),
        "",
        "---",
        "",
        f"## {chrome['events_h']}",
        "",
        f"| {chrome['c_event']} | {chrome['c_block']} | {chrome['c_category']} | {chrome['c_desc']} |",
        "|-------|------------|----------|-------------|",
    ]
    ev_by_cat: dict[str, list] = {}
    for e in events:
        ev_by_cat.setdefault(e.category, []).append(e)
    ev_ordered = [c for c in EVENT_CATEGORY_ORDER if c in ev_by_cat]
    ev_ordered += sorted(c for c in ev_by_cat if c not in EVENT_CATEGORY_ORDER)
    for cat in ev_ordered:
        for e in sorted(ev_by_cat[cat], key=lambda x: x.display_name or x.name):
            cat_label = category_label(cat, lang, missing)
            out.append(f"| {e.display_name} | `{e.name}` | {cat_label} | {event_desc(e, lang, missing)} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"## {chrome['actions_h']}")
    out.append("")
    ordered_cats = [c for c in ACTION_CATEGORY_ORDER if c in actions_by_cat]
    ordered_cats += sorted(c for c in actions_by_cat if c not in ACTION_CATEGORY_ORDER)
    for cat in ordered_cats:
        cat_label = category_label(cat, lang, missing)
        out.append(f"### {cat_label}")
        out.append("")
        out.append(f"| {chrome['c_action']} | {chrome['c_block']} | {chrome['c_params']} |")
        out.append("|--------|------------|------------|")
        for a in sorted(actions_by_cat[cat], key=lambda x: x.display_name or x.name):
            out.append(f"| {action_display(a, lang, missing)} | `{a.name}` | {param_summary(a)} |")
        out.append("")
    out.append("---")
    out.append("")
    out += [
        f"## {chrome['see_also']}",
        "",
        chrome["sa_preset"],
        chrome["sa_events"],
        chrome["sa_actions"],
        chrome["sa_other"].format(other_title=other_title, other_link=other_link, other_desc=other_desc),
        "",
    ]
    return "\n".join(out), missing


def out_name(preset_key: str, lang: str) -> str:
    base = "Beginner-Preset" if preset_key == "beginner" else "Intermediate-Preset"
    return f"{base}.md" if lang == "en" else f"{base}_{lang}.md"


def main():
    langs = sys.argv[1:] or ["en"]
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    for lang in langs:
        for preset_key in ("beginner", "intermediate"):
            md, missing = build(preset_key, lang)
            target = REPO / "wiki" / out_name(preset_key, lang)
            target.write_text(md, encoding="utf-8")
            print(f"Wrote {target} ({len(md.splitlines())} lines)")
            if missing:
                print(f"  [{lang}] {len(missing)} untranslated strings fell back to English:")
                for k in sorted(missing):
                    print(f"    - {k}")


if __name__ == "__main__":
    main()
