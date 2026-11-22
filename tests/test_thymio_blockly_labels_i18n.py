"""Thymio blocks in the Blockly workspace follow the IDE language (2026-11-22).

docs/THYMIO_BLOCKS_I18N_2026-11-22.md U2/U3: the 28 Thymio block definitions in
blockly_blocks.js were hard-coded English. Every label, tooltip and drop-down
label now goes through thymioMsg("English"), looked up in THYMIO_BLOCK_MESSAGES
(blockly_i18n.js) for the five languages the workspace supports. There is no
Node in CI, so this runs the REAL two files in Qt's own JavaScript engine
against a small Blockly stand-in that records what each block shows.
"""
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6

BLOCKLY = ROOT / "editors" / "object_editor" / "blockly"
LANGS = ("fr", "de", "it", "pl", "uk")
# Translations that are the same word as the English (checked by hand).
SAME_WORD = {("fr", "3 - Central"), ("fr", "5 - Collision"),
             ("fr", "ms"), ("de", "ms"), ("it", "ms"), ("pl", "ms")}

STUB = r'''
var window = {location: {search: '?lang=LANG'}};
function URLSearchParams(q){ this.q = q; }
URLSearchParams.prototype.get = function(k){ var m = new RegExp('[?&]' + k + '=([^&]*)').exec(this.q); return m ? m[1] : null; };
var console = {log: function(){}, warn: function(){}, error: function(){}};
var document = {addEventListener: function(){}, getElementById: function(){ return null; }};
var Blockly = {Blocks: {}, Msg: {}, FieldDropdown: function(o){ this.options = o; }, FieldTextInput: function(t){ this.text = t; },
  FieldNumber: function(){}, FieldCheckbox: function(){}, FieldVariable: function(){}, FieldImage: function(){}, FieldColour: function(){},
  FieldLabelSerializable: function(){}, FieldLabel: function(){}, Extensions: {register: function(){}},
  defineBlocksWithJsonArray: function(){}, ALIGN_RIGHT: 1, ALIGN_LEFT: 0, ALIGN_CENTRE: 2,
  inputs: {Align: {RIGHT: 1, LEFT: 0, CENTRE: 2}}, utils: {}};
function makeInput(rec){ var inp = {
  appendField: function(f){ if (typeof f === 'string') rec.push({label: f});
                            else if (f && f.options) rec.push({options: f.options}); return inp; },
  setCheck: function(){ return inp; }, setAlign: function(){ return inp; }}; return inp; }
function build(type){ var rec = []; var b = {
  appendValueInput: function(){ return makeInput(rec); }, appendDummyInput: function(){ return makeInput(rec); },
  appendStatementInput: function(){ return makeInput(rec); }, setPreviousStatement: function(){}, setNextStatement: function(){},
  setColour: function(){}, setTooltip: function(t){ rec.push({tooltip: t}); }, setInputsInline: function(){}, setOutput: function(){},
  setHelpUrl: function(){}, jsonInit: function(){}, setDeletable: function(){}, setMovable: function(){},
  getField: function(){ return null; }, setOnChange: function(){}};
  Blockly.Blocks[type].init.call(b); return JSON.stringify(rec); }
'''


def _engine(lang):
    from PySide6.QtQml import QJSEngine
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])          # never a bare QCoreApplication (CLAUDE.md)
    eng = QJSEngine()
    eng.evaluate(STUB.replace("LANG", lang))
    for name in ("blockly_i18n.js", "blockly_blocks.js"):
        result = eng.evaluate((BLOCKLY / name).read_text(encoding="utf-8"), name)
        assert not result.isError(), (name, result.toString())
    return eng


TYPES = sorted(set(re.findall(r"Blockly\.Blocks\['(thymio_[a-z0-9_]+)'\]",
                              (BLOCKLY / "blockly_blocks.js").read_text(encoding="utf-8"))))


def _blocks(lang):
    eng = _engine(lang)
    return {t: json.loads(eng.evaluate(f"build('{t}')").toString()) for t in TYPES}


@pytest.fixture(scope="module")
def built():
    return {lang: _blocks(lang) for lang in ("en",) + LANGS}


def _texts(rec):
    out = []
    for item in rec:
        out += [item[k] for k in ("label", "tooltip") if k in item]
        out += [o[0] for o in item.get("options", [])]
    return out


def test_all_28_thymio_blocks_are_built(built):
    assert len(TYPES) == 28 and all(built["en"][t] for t in TYPES)


@pytest.mark.parametrize("lang", LANGS)
def test_no_label_tooltip_or_option_is_left_in_english(built, lang):
    left = []
    for t in TYPES:
        for en, tr in zip(_texts(built["en"][t]), _texts(built[lang][t])):
            if re.search(r"[A-Za-z]", en) and en == tr and (lang, en) not in SAME_WORD:
                left.append((t, en))
    assert not left, (lang, left[:10])


@pytest.mark.parametrize("lang", LANGS)
def test_dropdown_values_never_change(built, lang):
    """Saved workspaces and the generated code depend on the VALUES."""
    def values(rec):
        return [[o[1] for o in item["options"]] for item in rec if "options" in item]
    assert {t: values(built[lang][t]) for t in TYPES} == {t: values(built["en"][t]) for t in TYPES}


def test_french_labels_as_a_user_sees_them(built):
    fr = built["fr"]
    assert {"label": "Avancer à la vitesse"} in fr["thymio_move_forward"]
    assert {"tooltip": "Éteindre toutes les LED"} in fr["thymio_leds_off"]
    options = next(i["options"] for i in fr["thymio_read_button"] if "options" in i)
    assert options[0] == ["avant", "forward"]


def test_english_is_the_original_text(built):
    assert {"label": "Move forward at speed"} in built["en"]["thymio_move_forward"]
    assert {"tooltip": "Turn off all LEDs"} in built["en"]["thymio_leds_off"]
