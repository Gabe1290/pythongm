"""Every string the micro:bit export dialogs ask Qt to translate has a real translation
in every shipped language (they resolve in the PyGameMakerIDE context, since the
dialogs call ``ide.tr``)."""
import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    ROOT / "extensions" / "microbit" / "export" / "__init__.py",
    ROOT / "extensions" / "microbit" / "__init__.py",
]
LANGS = ["fr", "de", "es", "it", "pt", "ru", "sl", "uk", "ja", "zh"]
# split-shipping languages carry the IDE strings in the _core file
QM = {l: ROOT / "translations" / (f"pygm2_{l}_core.qm" if l in ("de", "it", "ru", "sl", "uk")
                                  else f"pygm2_{l}.qm") for l in LANGS}


def _ide_tr_strings():
    out = []
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "tr" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "ide" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                out.append(node.args[0].value)
    return sorted(set(out))


STRINGS = _ide_tr_strings()
# "original" is spelled the same in es/pt, so this label is identical there
UNCHANGED_OK = {"V1 (original, 2016-2020)"}


def _translator(lang):
    from PySide6.QtCore import QTranslator
    t = QTranslator()
    assert t.load(str(QM[lang])), QM[lang]
    return t


def test_found_the_strings():
    assert len(STRINGS) >= 36


@pytest.mark.parametrize("lang", LANGS)
def test_every_string_is_translated(lang):
    t = _translator(lang)
    missing, same = [], []
    for s in STRINGS:
        tr = t.translate("PyGameMakerIDE", s)
        if not tr:
            missing.append(s)
        elif tr == s and s not in UNCHANGED_OK:
            same.append(s)
    assert not missing, f"{lang}: untranslated: {missing}"
    assert not same, f"{lang}: identical to English: {same}"


@pytest.mark.parametrize("lang", LANGS)
def test_placeholders_newlines_and_mnemonic_preserved(lang):
    t = _translator(lang)
    for s in STRINGS:
        tr = t.translate("PyGameMakerIDE", s)
        assert re.findall(r"\{\d\}", s) == re.findall(r"\{\d\}", tr), (lang, s)
        assert s.count("\n") == tr.count("\n"), (lang, s)
        assert s.startswith("\n") == tr.startswith("\n"), (lang, s)
        if "&micro:bit" in s:
            assert "&" in tr, (lang, s)
