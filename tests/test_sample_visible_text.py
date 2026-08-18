"""Sample text that is shown to a player must actually be shown.

`ActionExecutor._parse_value` treats any string containing an arithmetic
operator (`* + - / %`) as an EXPRESSION, so a `draw_text` reading
"W A S D  -  Move" is evaluated rather than displayed -- and renders as `0`.
The escape hatch is to wrap the string in double quotes, which `_parse_value`
returns verbatim.

This bit block_world_1's help overlay the first time it was drawn. Existing
samples had only ever escaped it by accident: "Lives:" and "M = map" contain
`:` and `=`, which are not operators, so they fell through as literals. The
first sample text to contain a dash was the first to break.

So this guard is about the next sample as much as this one: it fails on any
displayed string that `_parse_value` would evaluate instead of print.
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

OPERATORS = ("*", "+", "-", "/", "%")

# Parameters whose value reaches the screen as text.
TEXT_PARAMS = ("text", "message", "caption", "health_label", "score_label",
               "objective_label")

# ...of which only these are run through _parse_value, and so only these need
# the defensive quoting. Verified against the handlers: draw_text and
# draw_scaled_text parse their `text`; show_message, draw_score's caption and
# the DOOM labels are used verbatim. Quoting one of THOSE is a bug in the
# other direction -- the quote characters get drawn on screen, which is
# exactly what happened to views_1's opening message.
EVALUATED_PARAMS = ("text",)

# `comment` is authoring metadata -- never drawn, never parsed.
NOT_DISPLAYED = {"comment"}

SAMPLES = sorted(p.parent.name
                 for p in (REPO_ROOT / "samples").glob("*/project.json"))


def _displayed_strings(node, out):
    if isinstance(node, dict):
        action = node.get("action")
        if action and action not in NOT_DISPLAYED:
            for key, value in (node.get("parameters") or {}).items():
                if key in EVALUATED_PARAMS and isinstance(value, str) and value.strip():
                    out.append((action, key, value))
                # Translations reach the screen through exactly the same path,
                # so they face exactly the same trap -- and French prose is far
                # more likely to contain a hyphen than the English was.
                if (key.endswith("_translations")
                        and key[:-len("_translations")] in EVALUATED_PARAMS
                        and isinstance(value, dict)):
                    for lang, translated in value.items():
                        if isinstance(translated, str) and translated.strip():
                            out.append(("%s[%s]" % (action, lang), key, translated))
        for value in node.values():
            _displayed_strings(value, out)
    elif isinstance(node, list):
        for value in node:
            _displayed_strings(value, out)
    return out


def _would_be_evaluated(value):
    """Mirrors _parse_value's decision: a quoted string is returned verbatim;
    otherwise an operator routes it to the expression evaluator."""
    if value.startswith('"'):
        return False
    if any(op in value for op in OPERATORS):
        # A bare number is fine -- it is meant to be numeric.
        try:
            float(value)
        except ValueError:
            return True
    return False


def test_there_are_samples_to_check():
    assert SAMPLES, "no samples found -- the glob is wrong"


@pytest.mark.parametrize("sample", SAMPLES)
def test_displayed_text_is_not_eaten_by_the_expression_evaluator(sample):
    project = json.loads(
        (REPO_ROOT / "samples" / sample / "project.json").read_text(
            encoding="utf-8"))
    offenders = [
        "%s.%s = %r" % (action, key, value)
        for action, key, value in _displayed_strings(project, [])
        if _would_be_evaluated(value)
    ]
    assert not offenders, (
        "%s has on-screen text containing an arithmetic operator and no "
        "surrounding double quotes; _parse_value will evaluate it and the "
        "player will see a number. Wrap it in \\\" quotes:\n  %s"
        % (sample, "\n  ".join(offenders)))


@pytest.mark.parametrize("sample", SAMPLES)
def test_the_side_files_agree_too(sample):
    """Samples store object definitions twice. The embedded copy is what the
    test above reads, so check the side files carry the same fix."""
    objects_dir = REPO_ROOT / "samples" / sample / "objects"
    if not objects_dir.is_dir():
        pytest.skip("no object side files")
    offenders = []
    for path in sorted(objects_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        offenders += ["%s: %s.%s = %r" % (path.name, action, key, value)
                      for action, key, value in _displayed_strings(data, [])
                      if _would_be_evaluated(value)]
    assert not offenders, "\n  ".join(offenders)


def _verbatim_strings(node, out):
    """Display params used verbatim, plus their translations."""
    verbatim = tuple(p for p in TEXT_PARAMS if p not in EVALUATED_PARAMS)
    if isinstance(node, dict):
        action = node.get("action")
        if action and action not in NOT_DISPLAYED:
            for key, value in (node.get("parameters") or {}).items():
                if key in verbatim and isinstance(value, str):
                    out.append((action, key, value))
                if (key.endswith("_translations")
                        and key[:-len("_translations")] in verbatim
                        and isinstance(value, dict)):
                    for lang, t in value.items():
                        if isinstance(t, str):
                            out.append(("%s[%s]" % (action, lang), key, t))
        for value in node.values():
            _verbatim_strings(value, out)
    elif isinstance(node, list):
        for value in node:
            _verbatim_strings(value, out)
    return out


@pytest.mark.parametrize("sample", SAMPLES)
def test_verbatim_text_is_not_defensively_quoted(sample):
    """The opposite trap. show_message, draw_score's caption and the DOOM
    labels are NOT expression-evaluated, so wrapping them in double quotes
    does not protect anything -- it draws the quote characters on screen.
    views_1's opening message shipped like that for exactly one commit."""
    offenders = []
    for path in [REPO_ROOT / "samples" / sample / "project.json"] + sorted(
            (REPO_ROOT / "samples" / sample / "objects").glob("*.json")
            if (REPO_ROOT / "samples" / sample / "objects").is_dir() else []):
        data = json.loads(path.read_text(encoding="utf-8"))
        for action, key, value in _verbatim_strings(data, []):
            v = value.strip()
            if len(v) > 1 and v.startswith('"') and v.endswith('"'):
                offenders.append("%s: %s.%s = %r" % (path.name, action, key, value))
    assert not offenders, (
        "verbatim display text wrapped in quotes; the quotes get drawn:\n  "
        + "\n  ".join(offenders))
