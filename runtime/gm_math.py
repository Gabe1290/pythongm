"""GameMaker math functions available in expressions, plus the numeric
comparison-code normalisation every action passes through.

Shared by the action executor's expression evaluator and the condition
evaluator (runtime/action_flow.py). Lives in its own module because
action_executor imports action_flow, so action_flow cannot import back.
Mirrored by the HTML5 export (engine.js gmSafeMath) and the Kivy export
(GameObject.sqrt/ln/log10/exp) -- see docs/BLOCKLY_BLOCK_AUDIT_2026-10-08.md
B6b.
"""

import math


# GameMaker math functions for expressions (Blockly audit B6b). A domain
# error (sqrt of a negative, ln/log10 of <= 0, exp overflow) gives 0 for that
# call, matching the HTML5 and Kivy exports, rather than failing the whole
# expression.
def _gm_math(fn):
    def safe(x):
        try:
            result = fn(float(x))
        except (ValueError, OverflowError, TypeError):
            return 0
        return result if math.isfinite(result) else 0
    return safe


# Text a GameMaker import or a hand-edited project uses for "no". A missing
# value is the parameter's default instead (Blockly audit B17).
_FALSE_TEXT = {"0", "false", "no", ""}


def param_is_true(value, default=True):
    """Read a boolean action parameter the way GameMaker means it.

    The GMK import stores checkboxes as the TEXT "0"/"1"; plain truthiness
    read "0" as true (any non-empty string is), so e.g. change_instance's
    "perform events: no" ran the events anyway (Blockly audit B17).
    False, 0, "0", "false", "no" and "" are false; None means `default`.
    """
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in _FALSE_TEXT
    return bool(value)


def normalize_gm_operation(action_name, parameters):
    """Translate a numeric GameMaker comparison code in ``operation`` to the
    operator name every engine compares by (Blockly audit B18). Uses the GMK
    importer's own table, so there is one source for the codes."""
    from importers.gmk_mappings import GM_COMPARISON_OPS, GM_OPERATION_ACTIONS
    if action_name not in GM_OPERATION_ACTIONS or not isinstance(parameters, dict):
        return parameters
    code = str(parameters.get("operation", "")).strip()
    if code in GM_COMPARISON_OPS:
        return {**parameters, "operation": GM_COMPARISON_OPS[code]}
    return parameters


GM_MATH_FUNCTIONS = {
    'sqrt': _gm_math(math.sqrt),
    'ln': _gm_math(math.log),
    'log10': _gm_math(math.log10),
    'exp': _gm_math(math.exp),
}

