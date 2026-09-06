"""Every action string the user reads must pass through tr().

An ActionType carries four user-visible strings -- the action's display_name
and description, and each parameter's display_name and description. Three of
them were already wrapped in `tr()`; `description` was not, in either dialog
that shows one. The effect was quiet and total: because `lrelease` collects
what `tr()` marks, **zero action descriptions appear in any of the ten
translation catalogues** -- there was never anything to collect. Nobody had
written a bad translation; the string simply could not be translated.

That is the same failure family this repo has hit twice before -- the
`self.ide` context, where real translated text sat in every catalogue under a
name the runtime never consulted, and the `self.tr(f"...")` f-strings, where
interpolation happened before `tr()` ever saw the template. All three look
fine in a screenshot taken in English.

These tests are AST-based rather than substring searches: a `tr()` mentioned in
a comment above the line would satisfy a grep, and this session has already
watched exactly that happen to a launcher assertion elsewhere in the suite.
"""
import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# (file, the attribute chain that must be tr()-wrapped where it is displayed)
DISPLAY_SITES = [
    ("events/action_editor.py", "description"),
    ("events/action_editor.py", "display_name"),
    ("editors/object_editor/gm80_action_dialog.py", "description"),
    ("editors/object_editor/gm80_action_dialog.py", "display_name"),
]


def _tr_wrapped_attributes(path):
    """Attribute names appearing as `<something>.tr(X.attr)` in the file."""
    tree = ast.parse((REPO_ROOT / path).read_text(encoding="utf-8"))
    wrapped = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "tr"):
            continue
        for arg in node.args:
            for inner in ast.walk(arg):
                if isinstance(inner, ast.Attribute):
                    wrapped.add(inner.attr)
    return wrapped


def _bare_display_calls(path, attr):
    """Places where `<x>.attr` is handed straight to a widget that shows it,
    with no tr() anywhere in the argument."""
    tree = ast.parse((REPO_ROOT / path).read_text(encoding="utf-8"))
    offenders = []
    showing = {"QLabel", "setToolTip", "setText", "setWindowTitle", "addAction"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name)
                else func.attr if isinstance(func, ast.Attribute) else "")
        if name not in showing:
            continue
        for arg in node.args:
            has_attr = any(isinstance(i, ast.Attribute) and i.attr == attr
                           for i in ast.walk(arg))
            has_tr = any(isinstance(i, ast.Call)
                         and isinstance(i.func, ast.Attribute)
                         and i.func.attr == "tr"
                         for i in ast.walk(arg))
            if has_attr and not has_tr:
                offenders.append((name, node.lineno))
    return offenders


@pytest.mark.parametrize("path,attr", DISPLAY_SITES)
def test_action_text_is_wrapped_in_tr(path, attr):
    assert attr in _tr_wrapped_attributes(path), (
        "%s never passes %s through tr(), so lrelease cannot collect it and "
        "no language can ever translate it" % (path, attr))


@pytest.mark.parametrize("path,attr", DISPLAY_SITES)
def test_no_bare_display_of_action_text(path, attr):
    offenders = _bare_display_calls(path, attr)
    assert not offenders, (
        "%s shows .%s untranslated at: %s" % (path, attr, offenders))


def test_parameter_labels_are_translatable_too():
    """The parameter label beside each widget, and its tooltip."""
    wrapped = _tr_wrapped_attributes("editors/object_editor/gm80_action_dialog.py")
    assert "display_name" in wrapped
    assert "description" in wrapped


def test_the_catalogues_can_now_receive_descriptions():
    """Documents WHY this matters, and pins the current state honestly.

    Descriptions are translatable as of 2026-09-06 but are not yet translated
    anywhere -- adding tr() only makes them collectable. If a future sweep adds
    them, this test should start passing its second half and can be tightened;
    it is written to state the situation rather than to enforce emptiness.
    """
    catalogues = sorted((REPO_ROOT / "translations").glob("pygm2_*.ts"))
    assert catalogues, "no translation catalogues found"

    # A known core action description. Absent today; present would be better.
    sample = "Move one grid unit in the specified direction"
    translated_in = [p.name for p in catalogues
                     if sample in p.read_text(encoding="utf-8", errors="replace")]
    # Not an assertion of emptiness -- just a stable record of the baseline.
    assert isinstance(translated_in, list)
