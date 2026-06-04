#!/usr/bin/env python3
"""Add translations for the strict-Python condition guards.

When obj_pingus' "land on monster" condition was fixed, three teaching
guards were added to the IDE:

* ``ActionConfigDialog`` (Test Expression action) and
  ``ConditionalActionEditor`` (Configure If Condition) now warn when an
  expression uses C/GML operators (``&&`` / ``||`` / ``!``) instead of the
  Python ``and`` / ``or`` / ``not``.
* ``ConditionalActionEditor`` warns when a whole expression is pasted into
  the ``variable_compare`` Variable field, and shows an inline hint.
* The custom-expression label/placeholder changed from "GML" to "Python".

All those strings are wrapped in ``tr()`` but had no entries in the .ts
files, so non-English IDEs showed them in English. This script inserts the
messages into both contexts of every pygm2_*.ts that has them, skipping any
source already present, then recompiles the touched .ts to .qm.

Idempotent — safe to re-run. Mirrors scripts/add_tutorial_dock_translations.py.
"""

import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"


def find_lrelease() -> str:
    home = Path.home()
    candidates = [
        home / ".local/lib/python3.11/site-packages/PySide6/lrelease",
        home / ".local/lib/python3.12/site-packages/PySide6/lrelease",
        home / ".local/lib/python3.10/site-packages/PySide6/lrelease",
        ROOT / "venv/lib/python3.12/site-packages/PySide6/lrelease",
        ROOT / "venv/lib/python3.11/site-packages/PySide6/lrelease",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    # Fall back to PySide6's packaged tool via import.
    try:
        import PySide6
        p = Path(PySide6.__file__).parent / "lrelease"
        if p.exists():
            return str(p)
    except Exception:
        pass
    raise SystemExit("Could not find a working PySide6 lrelease.")


# --- Source strings (must byte-match the tr() literals in the code) ---------
USE_OPS = "Use Python operators"
WARN_VSPEED = (
    "This expression uses C-style operators that Python does not understand:"
    "\n\n    {fixes}\n\n"
    "Please use the Python operators instead (and / or / not), "
    'e.g. "vspeed > 0 and y < other.y".'
)
WARN_XY = WARN_VSPEED.replace(
    "vspeed > 0 and y < other.y", "x > 100 and y < 200")
LABEL = "Custom Python Expression:"
PLACEHOLDER = (
    "Enter any Python expression that evaluates to true/false"
    "\nExample: x > 100 and y < 200"
)
LOOKS = "That looks like an expression"
VARMSG = (
    'The Variable field expects a single variable name (e.g. "vspeed"), '
    "not a whole expression.\n\n"
    'To test something like "vspeed > 0 and y < other.y", set Condition Type '
    'to "expression" and type it in the expression box.'
)
HINT = (
    "A single variable name (e.g. vspeed). For a formula like "
    '"vspeed > 0 and y < other.y", set Condition Type to "expression".'
)

CONTEXTS = {
    "ActionConfigDialog": [USE_OPS, WARN_VSPEED],
    "ConditionalActionEditor": [LABEL, PLACEHOLDER, USE_OPS, WARN_XY,
                                LOOKS, VARMSG, HINT],
}

# Per-language translations. The Python keywords (and / or / not), code
# examples and the {fixes} placeholder are intentionally kept literal. The
# Condition-Type dropdown label differs per language (de=Ausdruck,
# it=espressione, others=expression) and is baked into VARMSG/HINT below.
TR = {
    "fr": {
        USE_OPS: "Utilisez les opérateurs Python",
        WARN_VSPEED: (
            "Cette expression utilise des opérateurs de style C que Python ne "
            "comprend pas :\n\n    {fixes}\n\n"
            "Utilisez plutôt les opérateurs Python (and / or / not), "
            'par exemple "vspeed > 0 and y < other.y".'),
        LABEL: "Expression Python personnalisée :",
        PLACEHOLDER: ("Entrez une expression Python qui s'évalue à vrai/faux"
                      "\nExemple : x > 100 and y < 200"),
        LOOKS: "Cela ressemble à une expression",
        VARMSG: ('Le champ Variable attend un seul nom de variable '
                 '(par exemple "vspeed"), pas une expression complète.\n\n'
                 'Pour tester quelque chose comme "vspeed > 0 and y < other.y", '
                 'réglez le Type de condition sur "expression" et saisissez-le '
                 "dans la zone d'expression."),
        HINT: ("Un seul nom de variable (par exemple vspeed). Pour une formule "
               'comme "vspeed > 0 and y < other.y", réglez le Type de condition '
               'sur "expression".'),
    },
    "de": {
        USE_OPS: "Python-Operatoren verwenden",
        WARN_VSPEED: (
            "Dieser Ausdruck verwendet Operatoren im C-Stil, die Python nicht "
            "versteht:\n\n    {fixes}\n\n"
            "Verwenden Sie stattdessen die Python-Operatoren (and / or / not), "
            'z. B. "vspeed > 0 and y < other.y".'),
        LABEL: "Benutzerdefinierter Python-Ausdruck:",
        PLACEHOLDER: ("Geben Sie einen beliebigen Python-Ausdruck ein, der "
                      "wahr/falsch ergibt\nBeispiel: x > 100 and y < 200"),
        LOOKS: "Das sieht wie ein Ausdruck aus",
        VARMSG: ('Das Feld "Variable" erwartet einen einzelnen Variablennamen '
                 '(z. B. "vspeed"), keinen ganzen Ausdruck.\n\n'
                 'Um etwas wie "vspeed > 0 and y < other.y" zu testen, setzen '
                 'Sie den Bedingungstyp auf "Ausdruck" und geben Sie ihn im '
                 "Ausdrucksfeld ein."),
        HINT: ("Ein einzelner Variablenname (z. B. vspeed). Für eine Formel "
               'wie "vspeed > 0 and y < other.y" setzen Sie den Bedingungstyp '
               'auf "Ausdruck".'),
    },
    "es": {
        USE_OPS: "Usa los operadores de Python",
        WARN_VSPEED: (
            "Esta expresión usa operadores de estilo C que Python no entiende:"
            "\n\n    {fixes}\n\n"
            "Usa los operadores de Python en su lugar (and / or / not), "
            'por ejemplo "vspeed > 0 and y < other.y".'),
        LABEL: "Expresión Python personalizada:",
        PLACEHOLDER: ("Introduce cualquier expresión Python que se evalúe como "
                      "verdadero/falso\nEjemplo: x > 100 and y < 200"),
        LOOKS: "Eso parece una expresión",
        VARMSG: ('El campo Variable espera un único nombre de variable '
                 '(por ejemplo "vspeed"), no una expresión completa.\n\n'
                 'Para probar algo como "vspeed > 0 and y < other.y", establece '
                 'el Tipo de condición en "expression" y escríbelo en el cuadro '
                 "de expresión."),
        HINT: ("Un único nombre de variable (por ejemplo vspeed). Para una "
               'fórmula como "vspeed > 0 and y < other.y", establece el Tipo de '
               'condición en "expression".'),
    },
    "it": {
        USE_OPS: "Usa gli operatori Python",
        WARN_VSPEED: (
            "Questa espressione usa operatori in stile C che Python non "
            "comprende:\n\n    {fixes}\n\n"
            "Usa invece gli operatori Python (and / or / not), "
            'ad esempio "vspeed > 0 and y < other.y".'),
        LABEL: "Espressione Python personalizzata:",
        PLACEHOLDER: ("Inserisci una qualsiasi espressione Python che "
                      "restituisca vero/falso\nEsempio: x > 100 and y < 200"),
        LOOKS: "Sembra un'espressione",
        VARMSG: ('Il campo Variabile richiede un singolo nome di variabile '
                 '(ad esempio "vspeed"), non un\'intera espressione.\n\n'
                 'Per testare qualcosa come "vspeed > 0 and y < other.y", '
                 'imposta il Tipo di condizione su "espressione" e digitalo '
                 "nella casella dell'espressione."),
        HINT: ("Un singolo nome di variabile (ad esempio vspeed). Per una "
               'formula come "vspeed > 0 and y < other.y", imposta il Tipo di '
               'condizione su "espressione".'),
    },
    "ru": {
        USE_OPS: "Используйте операторы Python",
        WARN_VSPEED: (
            "В этом выражении используются операторы в стиле C, которые Python "
            "не понимает:\n\n    {fixes}\n\n"
            "Используйте вместо них операторы Python (and / or / not), "
            'например "vspeed > 0 and y < other.y".'),
        LABEL: "Пользовательское выражение Python:",
        PLACEHOLDER: ("Введите любое выражение Python, дающее истину/ложь"
                      "\nПример: x > 100 and y < 200"),
        LOOKS: "Это похоже на выражение",
        VARMSG: ('Поле "Переменная" ожидает одно имя переменной '
                 '(например "vspeed"), а не целое выражение.\n\n'
                 'Чтобы проверить что-то вроде "vspeed > 0 and y < other.y", '
                 'установите Тип условия в "expression" и введите его в поле '
                 "выражения."),
        HINT: ("Одно имя переменной (например vspeed). Для формулы вроде "
               '"vspeed > 0 and y < other.y" установите Тип условия в '
               '"expression".'),
    },
    "sl": {
        USE_OPS: "Uporabite operatorje Python",
        WARN_VSPEED: (
            "Ta izraz uporablja operatorje v slogu C, ki jih Python ne razume:"
            "\n\n    {fixes}\n\n"
            "Namesto njih uporabite operatorje Python (and / or / not), "
            'na primer "vspeed > 0 and y < other.y".'),
        LABEL: "Lasten izraz Python:",
        PLACEHOLDER: ("Vnesite poljuben izraz Python, ki se ovrednoti kot "
                      "resnično/neresnično\nPrimer: x > 100 and y < 200"),
        LOOKS: "To je videti kot izraz",
        VARMSG: ('Polje "Spremenljivka" pričakuje eno ime spremenljivke '
                 '(na primer "vspeed"), ne celega izraza.\n\n'
                 'Če želite preveriti nekaj takega kot '
                 '"vspeed > 0 and y < other.y", nastavite Vrsto pogoja na '
                 '"expression" in ga vnesite v polje za izraz.'),
        HINT: ("Eno ime spremenljivke (na primer vspeed). Za formulo kot "
               '"vspeed > 0 and y < other.y" nastavite Vrsto pogoja na '
               '"expression".'),
    },
    "uk": {
        USE_OPS: "Використовуйте оператори Python",
        WARN_VSPEED: (
            "У цьому виразі використовуються оператори у стилі C, які Python не "
            "розуміє:\n\n    {fixes}\n\n"
            "Використовуйте натомість оператори Python (and / or / not), "
            'наприклад "vspeed > 0 and y < other.y".'),
        LABEL: "Власний вираз Python:",
        PLACEHOLDER: ("Введіть будь-який вираз Python, що дає істину/хибність"
                      "\nПриклад: x > 100 and y < 200"),
        LOOKS: "Це схоже на вираз",
        VARMSG: ('Поле "Змінна" очікує одне ім\'я змінної '
                 '(наприклад "vspeed"), а не цілий вираз.\n\n'
                 'Щоб перевірити щось на кшталт "vspeed > 0 and y < other.y", '
                 'встановіть Тип умови на "expression" і введіть його в поле '
                 "виразу."),
        HINT: ("Одне ім'я змінної (наприклад vspeed). Для формули на кшталт "
               '"vspeed > 0 and y < other.y" встановіть Тип умови на '
               '"expression".'),
    },
}


def lang_of(ts_path: Path) -> str:
    return ts_path.stem.split("_")[1]


def message_block(source: str, translation: str) -> str:
    return (
        "        <message>\n"
        f"            <source>{escape(source)}</source>\n"
        f"            <translation>{escape(translation)}</translation>\n"
        "        </message>\n"
    )


def insert_into_context(text: str, context: str, sources, table) -> tuple:
    """Return (new_text, added_count) for one context block."""
    m = re.search(
        rf"(<context>\s*<name>{re.escape(context)}</name>)(.*?)(</context>)",
        text, re.S)
    if not m:
        return text, 0
    head, body, tail = m.group(1), m.group(2), m.group(3)
    existing = set(re.findall(r"<source>(.*?)</source>", body, re.S))
    additions = ""
    added = 0
    for src in sources:
        if escape(src) in existing or src in existing:
            continue
        additions += message_block(src, table[src])
        added += 1
    if not added:
        return text, 0
    new_block = head + "\n" + additions + body + tail
    return text[:m.start()] + new_block + text[m.end():], added


def process(ts_path: Path) -> bool:
    table = TR.get(lang_of(ts_path))
    if table is None:
        return False
    # WARN_XY is the same message as WARN_VSPEED with a different code example;
    # derive its translation so the table only carries one copy.
    table = dict(table)
    table[WARN_XY] = table[WARN_VSPEED].replace(
        "vspeed > 0 and y < other.y", "x > 100 and y < 200")
    text = ts_path.read_text(encoding="utf-8")
    total = 0
    for context, sources in CONTEXTS.items():
        text, added = insert_into_context(text, context, sources, table)
        total += added
    if total:
        ts_path.write_text(text, encoding="utf-8")
        print(f"  +    {ts_path.name}: added {total} message(s)")
        return True
    print(f"  ok   {ts_path.name}: already up to date")
    return False


def should_compile(ts_path: Path) -> bool:
    """Compile only the .qm the language manager will actually load.

    Split *_<group>.ts is compiled only when that language already uses a
    split set (pygm2_<lang>_core.qm exists); otherwise compiling it would
    create a split .qm that hijacks the loader away from the monolithic one.
    Monolithic pygm2_<lang>.ts is always safe.
    """
    parts = ts_path.stem.split("_")
    if len(parts) <= 2:
        return True
    lang = parts[1]
    if (TRANS / f"pygm2_{lang}_core.qm").exists():
        return True
    print(f"  skip {ts_path.with_suffix('.qm').name}: "
          f"'{lang}' uses the monolithic .qm (no split set)")
    return False


def main() -> int:
    lrelease = find_lrelease()
    print(f"Using lrelease: {lrelease}\n")
    ts_files = sorted(
        p for p in TRANS.glob("pygm2_*.ts")
        if "<name>ConditionalActionEditor</name>" in p.read_text(encoding="utf-8")
        or "<name>ActionConfigDialog</name>" in p.read_text(encoding="utf-8"))
    print(f"Found {len(ts_files)} candidate .ts file(s)\n")
    touched = [ts for ts in ts_files if process(ts)]
    print()
    for ts in touched:
        if not should_compile(ts):
            continue
        qm = ts.with_suffix(".qm")
        subprocess.run([lrelease, str(ts), "-qm", str(qm)],
                       check=True, capture_output=True, text=True)
        print(f"  qm   {qm.name}")
    print(f"\nDone. {len(touched)} file(s) updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
